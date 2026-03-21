"""
correlation.py — 相关性分析模块
================================

功能：分析不同加密货币之间的价格和收益率相关性。

分析内容：
1. 价格相关性矩阵（Pearson 相关系数）
2. 收益率相关性矩阵
3. 滚动相关性（观察相关性如何随时间变化）
4. 热力图可视化
5. 统计摘要报告

核心概念：
- 相关系数 = 1 → 完全正相关（同涨同跌）
- 相关系数 = 0 → 无相关性（各走各的）
- 相关系数 = -1 → 完全负相关（一涨一跌）

使用方法：
    python src/correlation.py

作者：Jason
日期：2026-03
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime


# ============================================================
# 配置
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CLEANED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")
IMAGES_DIR = os.path.join(PROJECT_ROOT, "images")

# 图表样式
plt.rcParams.update({
    "figure.facecolor": "#1a1a2e",
    "axes.facecolor": "#16213e",
    "axes.edgecolor": "#e94560",
    "axes.labelcolor": "#eee",
    "text.color": "#eee",
    "xtick.color": "#aaa",
    "ytick.color": "#aaa",
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
})


# ============================================================
# 核心函数
# ============================================================

def load_wide_table() -> pd.DataFrame:
    """加载宽表数据（由 clean_data.py 生成）。"""
    filepath = os.path.join(CLEANED_DATA_DIR, "wide_table.csv")
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"找不到 {filepath}，请先运行 clean_data.py"
        )
    df = pd.read_csv(filepath, parse_dates=["date"])
    return df


def compute_price_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算价格相关性矩阵。

    注意：直接对价格做相关性分析可能有误导性，
    因为所有资产可能都有上涨趋势（伪相关）。
    收益率相关性更有意义。
    """
    price_cols = [c for c in df.columns if c.endswith("_price")]
    corr = df[price_cols].corr()
    corr.index = [c.replace("_price", "") for c in corr.index]
    corr.columns = [c.replace("_price", "") for c in corr.columns]
    return corr


def compute_return_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算日收益率相关性矩阵。

    这个比价格相关性更有实际参考价值：
    - 如果两个币的收益率高度相关，说明它们"同涨同跌"
    - 对于投资组合分散风险很重要
    """
    return_cols = [c for c in df.columns if c.endswith("_return")]
    corr = df[return_cols].dropna().corr()
    corr.index = [c.replace("_return", "") for c in corr.index]
    corr.columns = [c.replace("_return", "") for c in corr.columns]
    return corr


def compute_rolling_correlation(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """
    计算滚动相关性（观察相关性随时间的变化）。

    参数：
        df: 宽表数据
        window: 滚动窗口大小（天数）

    返回：
        DataFrame: 各币种对之间的滚动相关系数
    """
    return_cols = [c for c in df.columns if c.endswith("_return")]
    returns = df[["date"] + return_cols].dropna()

    pairs = []
    for i in range(len(return_cols)):
        for j in range(i + 1, len(return_cols)):
            col1, col2 = return_cols[i], return_cols[j]
            name1 = col1.replace("_return", "")
            name2 = col2.replace("_return", "")
            pair_name = f"{name1} vs {name2}"

            rolling_corr = returns[col1].rolling(window=window).corr(returns[col2])
            pairs.append((pair_name, rolling_corr))

    result = pd.DataFrame({"date": returns["date"]})
    for pair_name, corr_series in pairs:
        result[pair_name] = corr_series.values

    return result


# ============================================================
# 可视化函数
# ============================================================

def plot_correlation_heatmap(corr: pd.DataFrame, title: str, filename: str) -> None:
    """绘制相关性热力图。"""
    fig, ax = plt.subplots(figsize=(8, 6))

    sns.heatmap(
        corr,
        annot=True,
        fmt=".3f",
        cmap="RdYlGn",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=2,
        linecolor="#1a1a2e",
        annot_kws={"size": 14, "fontweight": "bold"},
        ax=ax,
    )

    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

    os.makedirs(IMAGES_DIR, exist_ok=True)
    fig.savefig(os.path.join(IMAGES_DIR, filename))
    print(f"  ✓ 保存: {filename}")
    plt.close(fig)


def plot_rolling_correlation(rolling_df: pd.DataFrame, window: int = 30) -> None:
    """绘制滚动相关性图。"""
    fig, ax = plt.subplots(figsize=(14, 6))

    pair_colors = ["#F7931A", "#627EEA", "#9945FF"]
    pair_cols = [c for c in rolling_df.columns if c != "date"]

    for i, col in enumerate(pair_cols):
        color = pair_colors[i % len(pair_colors)]
        ax.plot(rolling_df["date"], rolling_df[col],
                label=col, color=color, linewidth=1.5)

    ax.axhline(y=0, color="#aaa", linestyle="--", alpha=0.3)
    ax.axhline(y=0.5, color="#51cf66", linestyle=":", alpha=0.3)
    ax.axhline(y=-0.5, color="#ff6b6b", linestyle=":", alpha=0.3)

    ax.set_title(f"Rolling Correlation ({window}-day window)",
                 fontsize=16, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Correlation")
    ax.set_ylim(-1, 1)
    ax.legend(framealpha=0.3)
    ax.grid(True, alpha=0.3)

    os.makedirs(IMAGES_DIR, exist_ok=True)
    fig.savefig(os.path.join(IMAGES_DIR, "rolling_correlation.png"))
    print(f"  ✓ 保存: rolling_correlation.png")
    plt.close(fig)


def generate_stats_report(df: pd.DataFrame) -> str:
    """
    生成统计摘要报告。

    包括：
    - 每个币种的平均收益率、波动率、最大回撤
    - 夏普比率（衡量风险调整后的收益）
    """
    return_cols = [c for c in df.columns if c.endswith("_return")]
    price_cols = [c for c in df.columns if c.endswith("_price")]

    report_lines = [
        "=" * 60,
        "加密货币统计摘要报告",
        f"生成日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"数据范围: {df['date'].min().strftime('%Y-%m-%d')} ~ {df['date'].max().strftime('%Y-%m-%d')}",
        "=" * 60,
        "",
    ]

    for pcol, rcol in zip(price_cols, return_cols):
        name = pcol.replace("_price", "")
        returns = df[rcol].dropna()
        prices = df[pcol].dropna()

        # 基本统计
        avg_return = returns.mean()
        volatility = returns.std()
        annualized_return = avg_return * 365
        annualized_vol = volatility * np.sqrt(365)

        # 夏普比率（假设无风险利率 = 4.5%，当前美国国债利率）
        risk_free_daily = 0.045 / 365
        sharpe = (avg_return - risk_free_daily) / volatility * np.sqrt(365) if volatility > 0 else 0

        # 最大回撤
        cummax = prices.cummax()
        drawdown = (prices - cummax) / cummax
        max_drawdown = drawdown.min()

        # 总收益
        total_return = (prices.iloc[-1] / prices.iloc[0] - 1)

        report_lines.extend([
            f"━━━ {name} ━━━",
            f"  当前价格:       ${prices.iloc[-1]:,.2f}",
            f"  总收益率:       {total_return:+.2%}",
            f"  日均收益率:     {avg_return:.4%}",
            f"  年化收益率:     {annualized_return:.2%}",
            f"  日波动率:       {volatility:.4%}",
            f"  年化波动率:     {annualized_vol:.2%}",
            f"  夏普比率:       {sharpe:.3f}",
            f"  最大回撤:       {max_drawdown:.2%}",
            "",
        ])

    report = "\n".join(report_lines)
    return report


# ============================================================
# 命令行入口
# ============================================================

def main():
    print("=" * 50)
    print("相关性分析工具")
    print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    try:
        df = load_wide_table()
        print(f"加载数据: {len(df)} 行")
    except FileNotFoundError as e:
        print(f"✗ {e}")
        return

    # 1. 价格相关性
    print("\n[1/4] 计算价格相关性")
    price_corr = compute_price_correlation(df)
    print(price_corr)
    plot_correlation_heatmap(price_corr, "Price Correlation", "price_correlation.png")

    # 2. 收益率相关性
    print("\n[2/4] 计算收益率相关性")
    return_corr = compute_return_correlation(df)
    print(return_corr)
    plot_correlation_heatmap(return_corr, "Daily Return Correlation", "return_correlation.png")

    # 3. 滚动相关性
    print("\n[3/4] 计算滚动相关性")
    rolling = compute_rolling_correlation(df, window=30)
    plot_rolling_correlation(rolling, window=30)

    # 4. 统计报告
    print("\n[4/4] 生成统计报告")
    report = generate_stats_report(df)
    print(report)

    # 保存报告
    report_path = os.path.join(IMAGES_DIR, "stats_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✓ 报告保存到 {report_path}")

    print("\n" + "=" * 50)
    print("相关性分析完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
