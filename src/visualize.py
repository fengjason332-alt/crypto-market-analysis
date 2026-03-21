"""
visualize.py — 数据可视化模块
==============================

功能：生成加密货币分析图表，保存到 images/ 目录。

图表类型：
1. 价格走势图（多币种对比）
2. 成交量柱状图
3. RSI 指标图
4. MACD 指标图
5. 布林带图
6. 日收益率分布图
7. 综合仪表盘（多图合一）

使用方法：
    python src/visualize.py                # 生成全部图表
    python src/visualize.py --coin btc     # 只生成 BTC 的图表

依赖：matplotlib, seaborn, pandas

作者：Jason
日期：2026-03
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import os
import argparse
from datetime import datetime


# ============================================================
# 配置
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
INDICATOR_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "indicators")
CLEANED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")
IMAGES_DIR = os.path.join(PROJECT_ROOT, "images")

SUPPORTED_COINS = ["btc", "eth", "sol"]

# 配色方案
COLORS = {
    "BTC": "#F7931A",   # 比特币经典橙色
    "ETH": "#627EEA",   # 以太坊蓝色
    "SOL": "#9945FF",   # Solana 紫色
}

# 全局图表样式
plt.rcParams.update({
    "figure.facecolor": "#1a1a2e",
    "axes.facecolor": "#16213e",
    "axes.edgecolor": "#e94560",
    "axes.labelcolor": "#eee",
    "text.color": "#eee",
    "xtick.color": "#aaa",
    "ytick.color": "#aaa",
    "grid.color": "#2a2a4a",
    "grid.alpha": 0.5,
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
    "font.size": 10,
})


# ============================================================
# 图表函数
# ============================================================

def plot_price_comparison(save: bool = True) -> plt.Figure:
    """
    多币种价格走势对比图。

    使用双轴（BTC 价格太高，和 ETH/SOL 不在一个量级）。
    """
    fig, ax1 = plt.subplots(figsize=(14, 6))

    for coin in SUPPORTED_COINS:
        filepath = os.path.join(INDICATOR_DATA_DIR, f"{coin}_indicators.csv")
        if not os.path.exists(filepath):
            continue
        df = pd.read_csv(filepath, parse_dates=["date"])
        color = COLORS.get(coin.upper(), "#fff")
        ax1.plot(df["date"], df["price"], label=coin.upper(),
                 color=color, linewidth=1.5, alpha=0.9)

    ax1.set_title("Crypto Price Comparison", fontsize=16, fontweight="bold")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Price (USD)")
    ax1.legend(loc="upper left", framealpha=0.3)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)

    if save:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        fig.savefig(os.path.join(IMAGES_DIR, "price_comparison.png"))
        print("  ✓ 保存: price_comparison.png")

    plt.close(fig)
    return fig


def plot_rsi(coin: str = "btc", save: bool = True) -> plt.Figure:
    """
    RSI 指标图。

    显示价格和 RSI(14)，标注超买（>70）和超卖（<30）区域。
    """
    filepath = os.path.join(INDICATOR_DATA_DIR, f"{coin}_indicators.csv")
    df = pd.read_csv(filepath, parse_dates=["date"])
    color = COLORS.get(coin.upper(), "#fff")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                    height_ratios=[2, 1], sharex=True)

    # 上半部分：价格
    ax1.plot(df["date"], df["price"], color=color, linewidth=1.5)
    ax1.set_title(f"{coin.upper()} Price & RSI(14)", fontsize=16, fontweight="bold")
    ax1.set_ylabel("Price (USD)")
    ax1.grid(True, alpha=0.3)

    # 下半部分：RSI
    ax2.plot(df["date"], df["rsi_14"], color="#e94560", linewidth=1.2)
    ax2.axhline(y=70, color="#ff6b6b", linestyle="--", alpha=0.7, label="Overbought (70)")
    ax2.axhline(y=30, color="#51cf66", linestyle="--", alpha=0.7, label="Oversold (30)")
    ax2.axhline(y=50, color="#aaa", linestyle=":", alpha=0.5)

    # 填充超买/超卖区域
    ax2.fill_between(df["date"], 70, 100, alpha=0.1, color="#ff6b6b")
    ax2.fill_between(df["date"], 0, 30, alpha=0.1, color="#51cf66")

    ax2.set_ylabel("RSI")
    ax2.set_ylim(0, 100)
    ax2.legend(loc="upper right", framealpha=0.3)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)

    plt.tight_layout()

    if save:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        fig.savefig(os.path.join(IMAGES_DIR, f"{coin}_rsi.png"))
        print(f"  ✓ 保存: {coin}_rsi.png")

    plt.close(fig)
    return fig


def plot_macd(coin: str = "btc", save: bool = True) -> plt.Figure:
    """
    MACD 指标图。

    显示 MACD 线、信号线和柱状图（Histogram）。
    """
    filepath = os.path.join(INDICATOR_DATA_DIR, f"{coin}_indicators.csv")
    df = pd.read_csv(filepath, parse_dates=["date"])
    color = COLORS.get(coin.upper(), "#fff")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                    height_ratios=[2, 1], sharex=True)

    # 上半部分：价格 + 均线
    ax1.plot(df["date"], df["price"], color=color, linewidth=1.5, label="Price")
    ax1.plot(df["date"], df["ema_12"], color="#51cf66", linewidth=0.8, alpha=0.7, label="EMA(12)")
    ax1.plot(df["date"], df["ema_26"], color="#ff6b6b", linewidth=0.8, alpha=0.7, label="EMA(26)")
    ax1.set_title(f"{coin.upper()} Price & MACD", fontsize=16, fontweight="bold")
    ax1.set_ylabel("Price (USD)")
    ax1.legend(loc="upper left", framealpha=0.3)
    ax1.grid(True, alpha=0.3)

    # 下半部分：MACD
    ax2.plot(df["date"], df["macd_line"], color="#00d2ff", linewidth=1.2, label="MACD")
    ax2.plot(df["date"], df["macd_signal"], color="#ff6b6b", linewidth=1.0, label="Signal")

    # Histogram 柱状图（正值绿色，负值红色）
    hist = df["macd_histogram"]
    ax2.bar(df["date"], hist, color=np.where(hist >= 0, "#51cf66", "#ff6b6b"),
            alpha=0.6, width=1.5)

    ax2.axhline(y=0, color="#aaa", linestyle="-", alpha=0.3)
    ax2.set_ylabel("MACD")
    ax2.legend(loc="upper left", framealpha=0.3)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)

    plt.tight_layout()

    if save:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        fig.savefig(os.path.join(IMAGES_DIR, f"{coin}_macd.png"))
        print(f"  ✓ 保存: {coin}_macd.png")

    plt.close(fig)
    return fig


def plot_bollinger_bands(coin: str = "btc", save: bool = True) -> plt.Figure:
    """
    布林带图。

    显示价格在布林带通道中的位置。
    """
    filepath = os.path.join(INDICATOR_DATA_DIR, f"{coin}_indicators.csv")
    df = pd.read_csv(filepath, parse_dates=["date"])
    color = COLORS.get(coin.upper(), "#fff")

    fig, ax = plt.subplots(figsize=(14, 7))

    # 布林带
    ax.fill_between(df["date"], df["bb_upper"], df["bb_lower"],
                    alpha=0.15, color="#627EEA", label="Bollinger Band")
    ax.plot(df["date"], df["bb_upper"], color="#627EEA", linewidth=0.7, alpha=0.5)
    ax.plot(df["date"], df["bb_lower"], color="#627EEA", linewidth=0.7, alpha=0.5)
    ax.plot(df["date"], df["bb_middle"], color="#627EEA", linewidth=0.8,
            linestyle="--", alpha=0.7, label="SMA(20)")

    # 价格线
    ax.plot(df["date"], df["price"], color=color, linewidth=1.5, label="Price")

    ax.set_title(f"{coin.upper()} Bollinger Bands (20, 2)", fontsize=16, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.legend(loc="upper left", framealpha=0.3)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)

    if save:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        fig.savefig(os.path.join(IMAGES_DIR, f"{coin}_bollinger.png"))
        print(f"  ✓ 保存: {coin}_bollinger.png")

    plt.close(fig)
    return fig


def plot_returns_distribution(save: bool = True) -> plt.Figure:
    """
    日收益率分布对比图（直方图 + KDE 密度曲线）。

    可以看出哪个币种波动最大（分布越宽 = 波动越大）。
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    for coin in SUPPORTED_COINS:
        filepath = os.path.join(INDICATOR_DATA_DIR, f"{coin}_indicators.csv")
        if not os.path.exists(filepath):
            continue
        df = pd.read_csv(filepath)
        returns = df["daily_return"].dropna()
        color = COLORS.get(coin.upper(), "#fff")

        ax.hist(returns, bins=80, alpha=0.3, color=color, density=True, label=f"{coin.upper()}")
        returns.plot.kde(ax=ax, color=color, linewidth=2)

    ax.axvline(x=0, color="#aaa", linestyle="--", alpha=0.5)
    ax.set_title("Daily Return Distribution", fontsize=16, fontweight="bold")
    ax.set_xlabel("Daily Return")
    ax.set_ylabel("Density")
    ax.set_xlim(-0.15, 0.15)
    ax.legend(framealpha=0.3)
    ax.grid(True, alpha=0.3)

    if save:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        fig.savefig(os.path.join(IMAGES_DIR, "returns_distribution.png"))
        print("  ✓ 保存: returns_distribution.png")

    plt.close(fig)
    return fig


def plot_volume_comparison(save: bool = True) -> plt.Figure:
    """多币种成交量对比图。"""
    fig, axes = plt.subplots(len(SUPPORTED_COINS), 1, figsize=(14, 4 * len(SUPPORTED_COINS)),
                              sharex=True)

    for i, coin in enumerate(SUPPORTED_COINS):
        filepath = os.path.join(INDICATOR_DATA_DIR, f"{coin}_indicators.csv")
        if not os.path.exists(filepath):
            continue
        df = pd.read_csv(filepath, parse_dates=["date"])
        color = COLORS.get(coin.upper(), "#fff")

        ax = axes[i] if len(SUPPORTED_COINS) > 1 else axes
        ax.bar(df["date"], df["total_volume"], color=color, alpha=0.7, width=1.5)
        ax.set_ylabel(f"{coin.upper()} Volume")
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1e9:.1f}B"))

    axes[0].set_title("Trading Volume Comparison", fontsize=16, fontweight="bold")
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)
    plt.tight_layout()

    if save:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        fig.savefig(os.path.join(IMAGES_DIR, "volume_comparison.png"))
        print("  ✓ 保存: volume_comparison.png")

    plt.close(fig)
    return fig


# ============================================================
# 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="生成加密货币分析图表")
    parser.add_argument("--coin", type=str, default=None, help="指定币种")

    args = parser.parse_args()

    print("=" * 50)
    print("图表生成工具")
    print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    os.makedirs(IMAGES_DIR, exist_ok=True)

    # 1. 价格对比
    print("\n[1/6] 价格走势对比图")
    plot_price_comparison()

    # 2. 成交量
    print("\n[2/6] 成交量对比图")
    plot_volume_comparison()

    # 3. 收益率分布
    print("\n[3/6] 收益率分布图")
    plot_returns_distribution()

    # 4-6. 每个币种的指标图
    coins = [args.coin] if args.coin else SUPPORTED_COINS
    for coin in coins:
        print(f"\n[{coin.upper()}] RSI / MACD / Bollinger Bands")
        try:
            plot_rsi(coin)
            plot_macd(coin)
            plot_bollinger_bands(coin)
        except FileNotFoundError:
            print(f"  ✗ {coin} 数据不存在，跳过")

    print("\n" + "=" * 50)
    print(f"图表全部保存到 {IMAGES_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()
