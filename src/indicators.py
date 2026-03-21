"""
indicators.py — 技术指标计算模块
================================

功能：计算金融市场中常用的技术指标，帮助分析价格趋势和交易信号。

包含的指标：
1. SMA  — 简单移动平均线（Simple Moving Average）
2. EMA  — 指数移动平均线（Exponential Moving Average）
3. RSI  — 相对强弱指标（Relative Strength Index）
4. MACD — 移动平均收敛/发散指标（Moving Average Convergence Divergence）
5. Bollinger Bands — 布林带

使用方法：
    python src/indicators.py                   # 对全部币种计算指标
    python src/indicators.py --coins btc eth   # 只计算 BTC 和 ETH

作者：Jason
日期：2026-03
"""

import pandas as pd
import numpy as np
import os
import argparse
from datetime import datetime


# ============================================================
# 配置
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CLEANED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")
INDICATOR_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "indicators")

SUPPORTED_COINS = ["btc", "eth", "sol"]


# ============================================================
# 技术指标函数
# ============================================================

def sma(series: pd.Series, window: int = 20) -> pd.Series:
    """
    简单移动平均线 (SMA)。

    原理：过去 N 天价格的算术平均值。
    用途：判断趋势方向。价格在 SMA 上方 = 上涨趋势，下方 = 下跌趋势。

    参数：
        series: 价格序列
        window: 窗口大小（天数），默认 20 天

    示例：
        如果 window=7，那么今天的 SMA = (过去7天价格之和) / 7
    """
    return series.rolling(window=window, min_periods=1).mean()


def ema(series: pd.Series, span: int = 20) -> pd.Series:
    """
    指数移动平均线 (EMA)。

    原理：给近期数据更高的权重（最近的价格影响更大）。
    用途：比 SMA 对价格变化更敏感，更快反映趋势变化。

    参数：
        series: 价格序列
        span: 衰减跨度（天数），默认 20 天

    EMA vs SMA：
        SMA 对所有天数一视同仁，EMA 更看重最近的数据。
        短期交易者通常更喜欢 EMA，因为它反应更快。
    """
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    相对强弱指标 (RSI)。

    原理：衡量价格上涨和下跌的力度比。
    公式：RSI = 100 - (100 / (1 + RS))
          RS = 平均涨幅 / 平均跌幅

    用途：
        RSI > 70 → 超买（可能即将下跌）
        RSI < 30 → 超卖（可能即将上涨）
        RSI ≈ 50 → 中性

    参数：
        series: 价格序列
        period: 计算周期，默认 14 天（最常用的设置）
    """
    # 计算每日价格变化
    delta = series.diff()

    # 分离涨和跌
    gain = delta.where(delta > 0, 0.0)   # 涨了多少（跌的天记为 0）
    loss = (-delta).where(delta < 0, 0.0) # 跌了多少（涨的天记为 0）

    # 计算平均涨幅和跌幅（用 EMA 来平滑）
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    # 计算 RS 和 RSI
    rs = avg_gain / avg_loss
    rsi_values = 100 - (100 / (1 + rs))

    return rsi_values


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    MACD 指标（移动平均收敛/发散）。

    原理：用两条不同速度的 EMA 之差来判断趋势动量。

    三条线：
    1. MACD Line = 快线EMA(12) - 慢线EMA(26)
    2. Signal Line = MACD Line 的 EMA(9)
    3. Histogram = MACD Line - Signal Line

    交易信号：
    - MACD 上穿 Signal → 金叉（买入信号）
    - MACD 下穿 Signal → 死叉（卖出信号）
    - Histogram > 0 → 上涨动量
    - Histogram < 0 → 下跌动量

    参数：
        series: 价格序列
        fast: 快线周期（默认 12）
        slow: 慢线周期（默认 26）
        signal: 信号线周期（默认 9）
    """
    ema_fast = ema(series, span=fast)
    ema_slow = ema(series, span=slow)

    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, span=signal)
    histogram = macd_line - signal_line

    return pd.DataFrame({
        "macd_line": macd_line,
        "macd_signal": signal_line,
        "macd_histogram": histogram,
    })


def bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """
    布林带 (Bollinger Bands)。

    原理：用移动平均线 ± N倍标准差构建价格通道。

    三条线：
    1. 中轨 = SMA(20)
    2. 上轨 = SMA(20) + 2 × 标准差
    3. 下轨 = SMA(20) - 2 × 标准差

    用途：
    - 价格碰到上轨 → 可能超买
    - 价格碰到下轨 → 可能超卖
    - 带宽变窄 → 波动率降低，可能即将出现大波动
    - 带宽变宽 → 波动率增大

    参数：
        series: 价格序列
        window: SMA 窗口大小（默认 20）
        num_std: 标准差倍数（默认 2.0）
    """
    middle = sma(series, window)
    rolling_std = series.rolling(window=window, min_periods=1).std()

    upper = middle + (rolling_std * num_std)
    lower = middle - (rolling_std * num_std)

    # 布林带宽度（Bandwidth）：衡量波动率
    bandwidth = (upper - lower) / middle

    # %B：价格在布林带中的位置（0 = 下轨，1 = 上轨）
    percent_b = (series - lower) / (upper - lower)

    return pd.DataFrame({
        "bb_upper": upper,
        "bb_middle": middle,
        "bb_lower": lower,
        "bb_bandwidth": bandwidth,
        "bb_percent_b": percent_b,
    })


# ============================================================
# 组合函数：一次性计算所有指标
# ============================================================

def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    给 DataFrame 添加所有技术指标。

    输入的 df 需要有 'price' 列。

    返回新增列：
        sma_7, sma_20, sma_50       — 短/中/长期均线
        ema_12, ema_26              — 快/慢 EMA
        rsi_14                      — RSI
        macd_line, macd_signal, macd_histogram — MACD 三线
        bb_upper, bb_middle, bb_lower, bb_bandwidth, bb_percent_b — 布林带
    """
    df = df.copy()
    price = df["price"]

    # 移动平均线
    df["sma_7"] = sma(price, 7)
    df["sma_20"] = sma(price, 20)
    df["sma_50"] = sma(price, 50)
    df["ema_12"] = ema(price, 12)
    df["ema_26"] = ema(price, 26)

    # RSI
    df["rsi_14"] = rsi(price, 14)

    # MACD
    macd_df = macd(price)
    df = pd.concat([df, macd_df], axis=1)

    # 布林带
    bb_df = bollinger_bands(price)
    df = pd.concat([df, bb_df], axis=1)

    # 波动率（20日滚动标准差）
    df["volatility_20"] = df["daily_return"].rolling(window=20, min_periods=1).std()

    return df


# ============================================================
# 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="计算加密货币技术指标")
    parser.add_argument(
        "--coins", nargs="+", default=None,
        help="要计算的币种（默认: btc eth sol）"
    )

    args = parser.parse_args()
    coins = args.coins or SUPPORTED_COINS

    print("=" * 50)
    print("技术指标计算工具")
    print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"币种: {', '.join(coins)}")
    print("=" * 50)

    os.makedirs(INDICATOR_DATA_DIR, exist_ok=True)

    for coin in coins:
        print(f"\n[计算 {coin.upper()} 指标]")
        try:
            # 读取清洗后的数据
            filepath = os.path.join(CLEANED_DATA_DIR, f"{coin}_cleaned.csv")
            df = pd.read_csv(filepath, parse_dates=["date"])
            print(f"  读取了 {len(df)} 行数据")

            # 计算所有指标
            df = add_all_indicators(df)

            # 保存
            out_path = os.path.join(INDICATOR_DATA_DIR, f"{coin}_indicators.csv")
            df.to_csv(out_path, index=False)
            print(f"  ✓ 已保存到 {out_path}")
            print(f"  指标列: {[c for c in df.columns if c not in ['date','symbol','price','market_cap','total_volume','daily_return','log_return']]}")

        except FileNotFoundError:
            print(f"  ✗ 找不到清洗数据，请先运行 clean_data.py")
        except Exception as e:
            print(f"  ✗ 错误: {e}")

    print("\n" + "=" * 50)
    print("技术指标计算完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
