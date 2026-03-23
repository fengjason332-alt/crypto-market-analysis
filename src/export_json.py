"""
export_json.py — 导出数据给 React 前端使用
=============================================

功能：
1. 读取 pipeline 生成的指标 CSV（历史数据）
2. 通过 OKX API 获取最新价格和 K 线（实时数据）
3. 合并后输出 JSON 到 app/frontend/public/data/

React 前端直接 fetch 这些 JSON，不再用 mockData.js。

使用方法：
    python src/export_json.py                  # 导出全部
    python src/export_json.py --coin btc       # 只导出 BTC

作者：Jason
日期：2026-03
"""

import pandas as pd
import numpy as np
import json
import os
import argparse
import requests
from datetime import datetime


# ============================================================
# 配置
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
INDICATOR_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "indicators")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "app", "frontend", "public", "data")

SUPPORTED_COINS = ["btc", "eth", "sol"]

# OKX API 配置
OKX_BASE_URL = "https://www.okx.com/api/v5"
OKX_PAIRS = {
    "btc": "BTC-USDT",
    "eth": "ETH-USDT",
    "sol": "SOL-USDT",
}

COIN_META = {
    "btc": {"name": "Bitcoin", "symbol": "BTC", "color": "#F7931A", "icon": "B"},
    "eth": {"name": "Ethereum", "symbol": "ETH", "color": "#627EEA", "icon": "E"},
    "sol": {"name": "Solana", "symbol": "SOL", "color": "#9945FF", "icon": "S"},
}


# ============================================================
# 技术指标计算（独立版，不依赖 indicators.py）
# ============================================================

def calc_sma(prices, window):
    """简单移动平均线"""
    return prices.rolling(window=window, min_periods=1).mean()


def calc_rsi(prices, period=14):
    """RSI 指标"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def calc_macd(prices, fast=12, slow=26, signal=9):
    """MACD 指标"""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calc_bollinger(prices, window=20, num_std=2):
    """布林带"""
    sma = prices.rolling(window=window, min_periods=1).mean()
    std = prices.rolling(window=window, min_periods=1).std().fillna(0)
    return sma + num_std * std, sma, sma - num_std * std


def add_indicators_to_df(df):
    """给 DataFrame 添加所有技术指标"""
    prices = df["price"]

    df["sma20"] = calc_sma(prices, 20).round(2)
    df["sma50"] = calc_sma(prices, 50).round(2)
    df["rsi"] = calc_rsi(prices, 14).round(1)

    macd_line, macd_signal, macd_hist = calc_macd(prices)
    df["macdLine"] = macd_line.round(2)
    df["macdSignal"] = macd_signal.round(2)
    df["macdHistogram"] = macd_hist.round(2)

    bb_upper, bb_middle, bb_lower = calc_bollinger(prices)
    df["bbUpper"] = bb_upper.round(2)
    df["bbMiddle"] = bb_middle.round(2)
    df["bbLower"] = bb_lower.round(2)

    df["dailyReturn"] = prices.pct_change().round(4).fillna(0)

    return df


# ============================================================
# OKX API 获取实时数据
# ============================================================

def fetch_okx_ticker(pair):
    """获取实时价格"""
    try:
        url = f"{OKX_BASE_URL}/market/ticker?instId={pair}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("code") == "0" and data.get("data"):
            t = data["data"][0]
            return {
                "price": float(t["last"]),
                "volume24h": float(t["vol24h"]) if "vol24h" in t else float(t.get("volCcy24h", 0)),
                "change24h": float(t.get("sodUtc8", 0)),
                "high24h": float(t["high24h"]),
                "low24h": float(t["low24h"]),
            }
    except Exception as e:
        print(f"  ⚠ OKX ticker 获取失败 ({pair}): {e}")
    return None


def fetch_okx_candles(pair, bar="1D", limit=100):
    """获取 K 线数据"""
    try:
        url = f"{OKX_BASE_URL}/market/candles?instId={pair}&bar={bar}&limit={limit}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("code") == "0" and data.get("data"):
            rows = []
            for c in data["data"]:
                rows.append({
                    "date": datetime.fromtimestamp(int(c[0]) / 1000).strftime("%Y-%m-%d"),
                    "price": float(c[4]),       # close
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "volume": float(c[5]),       # volume in coin
                    "volumeUSD": float(c[7]) if len(c) > 7 else float(c[5]) * float(c[4]),
                })
            rows.sort(key=lambda x: x["date"])
            return rows
    except Exception as e:
        print(f"  ⚠ OKX K线 获取失败 ({pair}): {e}")
    return None


# ============================================================
# 数据处理
# ============================================================

def load_pipeline_data(coin):
    """加载 pipeline 生成的指标 CSV"""
    filepath = os.path.join(INDICATOR_DATA_DIR, f"{coin}_indicators.csv")
    if not os.path.exists(filepath):
        return None
    df = pd.read_csv(filepath, parse_dates=["date"])
    return df


def build_coin_json(coin):
    """
    构建单个币种的完整 JSON 数据。

    优先级：
    1. 如果有 pipeline CSV → 用 CSV（长历史 + 完整指标）
    2. 如果没有 CSV → 用 OKX K 线（近 100 天）+ 自算指标
    3. 实时价格总是从 OKX 获取
    """
    pair = OKX_PAIRS[coin]
    meta = COIN_META[coin]

    print(f"\n  [{coin.upper()}] 开始构建数据...")

    # 尝试加载 pipeline 历史数据
    pipeline_df = load_pipeline_data(coin)

    if pipeline_df is not None:
        print(f"  ✓ Pipeline 数据: {len(pipeline_df)} 天")
        df = pipeline_df.copy()
        # 标准化列名
        df = df.rename(columns={
            "sma_7": "sma7", "sma_20": "sma20", "sma_50": "sma50",
            "rsi_14": "rsi",
            "macd_line": "macdLine", "macd_signal": "macdSignal",
            "macd_histogram": "macdHistogram",
            "bb_upper": "bbUpper", "bb_middle": "bbMiddle", "bb_lower": "bbLower",
            "daily_return": "dailyReturn",
            "total_volume": "volume",
        })
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    else:
        # Fallback: 用 OKX K 线数据
        print(f"  ⚠ 无 Pipeline 数据，使用 OKX K 线...")
        candles = fetch_okx_candles(pair, "1D", 100)
        if candles:
            df = pd.DataFrame(candles)
            df = add_indicators_to_df(df)
            print(f"  ✓ OKX K线: {len(df)} 天")
        else:
            print(f"  ✗ 无法获取 {coin.upper()} 数据")
            return None

    # 获取实时价格
    ticker = fetch_okx_ticker(pair)

    # 构建 history 数组
    keep_cols = ["date", "price", "volume", "sma20", "sma50", "rsi",
                 "macdLine", "macdSignal", "macdHistogram",
                 "bbUpper", "bbMiddle", "bbLower", "dailyReturn",
                 "market_cap", "marketCap"]

    available_cols = [c for c in keep_cols if c in df.columns]
    history_df = df[available_cols].copy()

    # 标准化 marketCap 列名
    if "market_cap" in history_df.columns and "marketCap" not in history_df.columns:
        history_df = history_df.rename(columns={"market_cap": "marketCap"})

    # 填充 NaN
    history_df = history_df.ffill().fillna(0)

    history = history_df.to_dict(orient="records")

    # 构建最新快照
    latest = history[-1] if history else {}
    if ticker:
        latest["price"] = ticker["price"]
        latest["high24h"] = ticker["high24h"]
        latest["low24h"] = ticker["low24h"]
        print(f"  ✓ 实时价格: ${ticker['price']:,.2f}")

    # 计算 24h change
    if len(history) >= 2:
        prev_price = history[-2].get("price", latest.get("price", 0))
        if prev_price > 0:
            latest["change24h"] = round((latest["price"] - prev_price) / prev_price, 4)

    result = {
        "meta": meta,
        "latest": latest,
        "history": history,
        "source": "pipeline+okx" if pipeline_df is not None else "okx",
        "updatedAt": datetime.now().isoformat(),
    }

    return result


def export_all(coins):
    """导出所有币种数据为 JSON"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_data = {}

    for coin in coins:
        data = build_coin_json(coin)
        if data:
            # 单独保存每个币
            filepath = os.path.join(OUTPUT_DIR, f"{coin}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            print(f"  ✓ 已保存: {filepath}")
            all_data[coin.upper()] = data

    # 保存合并文件（React 只需要 fetch 一个文件）
    combined_path = os.path.join(OUTPUT_DIR, "market_data.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False)
    print(f"\n  ✓ 合并文件: {combined_path}")

    return all_data


# ============================================================
# 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="导出数据给 React 前端")
    parser.add_argument("--coin", type=str, default=None, help="指定币种")
    args = parser.parse_args()

    coins = [args.coin.lower()] if args.coin else SUPPORTED_COINS

    print("=" * 50)
    print("📦 数据导出工具")
    print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    export_all(coins)

    print("\n" + "=" * 50)
    print("✅ 导出完成！React 前端可加载 public/data/market_data.json")
    print("=" * 50)


if __name__ == "__main__":
    main()
