"""
clean_data.py — 数据清洗与预处理模块
====================================

功能：
1. 读取 data/ 目录下的原始 CSV 文件
2. 处理缺失值（NaN）
3. 去除重复行
4. 类型转换（确保 date 是日期格式，数值列是 float）
5. 合并多个币种数据为一张宽表（方便后续分析）
6. 输出清洗后的数据到 data/cleaned/

使用方法：
    python src/clean_data.py                # 清洗全部币种
    python src/clean_data.py --coins btc    # 只清洗 BTC

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

# 项目根目录（从 src/ 上一层推算）
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CLEANED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")

# 支持的币种
SUPPORTED_COINS = ["btc", "eth", "sol"]


# ============================================================
# 核心函数
# ============================================================

def load_raw_data(coin_symbol: str) -> pd.DataFrame:
    """
    读取单个币种的原始 CSV 文件。

    参数：
        coin_symbol: 币种简称，如 "btc"

    返回：
        pd.DataFrame: 原始数据

    异常：
        FileNotFoundError: 如果 CSV 文件不存在
    """
    filepath = os.path.join(RAW_DATA_DIR, f"{coin_symbol.lower()}.csv")

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"找不到 {filepath}，请先运行 fetch_data.py 拉取数据"
        )

    df = pd.read_csv(filepath)
    print(f"  读取 {coin_symbol.upper()}: {len(df)} 行, {len(df.columns)} 列")
    return df


def clean_single_coin(df: pd.DataFrame, coin_symbol: str) -> pd.DataFrame:
    """
    清洗单个币种的数据。

    清洗步骤：
    1. 转换 date 列为 datetime 类型
    2. 按日期排序
    3. 去除完全重复的行
    4. 去除日期重复的行（保留最后一条）
    5. 处理缺失值（前向填充 + 后向填充）
    6. 处理异常值（价格为 0 或负数的替换为 NaN 再填充）
    7. 添加日收益率列 (daily_return)

    参数：
        df: 原始数据
        coin_symbol: 币种简称

    返回：
        pd.DataFrame: 清洗后的数据
    """
    df = df.copy()

    # 第 1 步：日期类型转换
    df["date"] = pd.to_datetime(df["date"])

    # 第 2 步：按日期排序
    df = df.sort_values("date").reset_index(drop=True)

    # 第 3 步：去除完全重复的行
    before = len(df)
    df = df.drop_duplicates()
    dupes_removed = before - len(df)
    if dupes_removed > 0:
        print(f"  去除了 {dupes_removed} 行完全重复数据")

    # 第 4 步：去除日期重复（保留最后出现的）
    before = len(df)
    df = df.drop_duplicates(subset=["date"], keep="last")
    date_dupes = before - len(df)
    if date_dupes > 0:
        print(f"  去除了 {date_dupes} 行日期重复数据")

    # 第 5 步：处理异常值（价格/市值/成交量不能为 0 或负数）
    numeric_cols = ["price", "market_cap", "total_volume"]
    for col in numeric_cols:
        if col in df.columns:
            invalid_count = (df[col] <= 0).sum()
            if invalid_count > 0:
                df.loc[df[col] <= 0, col] = np.nan
                print(f"  {col} 中有 {invalid_count} 个无效值（≤0），已标记为 NaN")

    # 第 6 步：填充缺失值
    # 先前向填充（用前一天的值），再后向填充（处理开头的 NaN）
    nan_count = df[numeric_cols].isna().sum().sum()
    if nan_count > 0:
        df[numeric_cols] = df[numeric_cols].ffill().bfill()
        print(f"  填充了 {nan_count} 个缺失值")

    # 第 7 步：添加日收益率
    # 日收益率 = (今天价格 - 昨天价格) / 昨天价格
    # pct_change() 会自动计算这个
    df["daily_return"] = df["price"].pct_change()

    # 第 8 步：添加对数收益率（金融分析中更常用）
    # 对数收益率 = ln(今天价格 / 昨天价格)
    # 优点：可以直接相加，更适合统计分析
    df["log_return"] = np.log(df["price"] / df["price"].shift(1))

    # 确保 symbol 列存在
    df["symbol"] = coin_symbol.upper()

    print(f"  ✓ 清洗完成: {len(df)} 行, 列: {list(df.columns)}")
    return df


def save_cleaned_data(df: pd.DataFrame, coin_symbol: str) -> str:
    """保存清洗后的数据为 CSV。"""
    os.makedirs(CLEANED_DATA_DIR, exist_ok=True)
    filepath = os.path.join(CLEANED_DATA_DIR, f"{coin_symbol.lower()}_cleaned.csv")
    df.to_csv(filepath, index=False)
    print(f"  ✓ 已保存到 {filepath}")
    return filepath


def merge_all_coins(coins: list = None) -> pd.DataFrame:
    """
    合并多个币种的清洗数据为一张长表。

    这张表可以直接用于可视化和分析：
    - 按 symbol 分组对比不同币种
    - 按 date 做时间序列分析

    返回：
        pd.DataFrame: 合并后的数据
    """
    if coins is None:
        coins = SUPPORTED_COINS

    all_dfs = []
    for coin in coins:
        try:
            filepath = os.path.join(CLEANED_DATA_DIR, f"{coin}_cleaned.csv")
            df = pd.read_csv(filepath, parse_dates=["date"])
            all_dfs.append(df)
        except FileNotFoundError:
            print(f"  跳过 {coin}（清洗文件不存在）")

    if not all_dfs:
        print("  没有找到任何清洗后的数据")
        return pd.DataFrame()

    merged = pd.concat(all_dfs, ignore_index=True)
    merged = merged.sort_values(["date", "symbol"]).reset_index(drop=True)

    # 保存合并后的数据
    merged_path = os.path.join(CLEANED_DATA_DIR, "all_coins_merged.csv")
    merged.to_csv(merged_path, index=False)
    print(f"\n✓ 合并数据已保存: {merged_path}（共 {len(merged)} 行）")

    return merged


def create_wide_table(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    将长表转换为宽表（每个币种的价格占一列）。

    宽表格式：
        date | BTC_price | ETH_price | SOL_price | BTC_return | ETH_return | SOL_return

    这种格式方便做相关性分析。
    """
    if merged_df.empty:
        return pd.DataFrame()

    # 用 pivot_table 转换
    price_wide = merged_df.pivot_table(
        index="date", columns="symbol", values="price"
    )
    price_wide.columns = [f"{col}_price" for col in price_wide.columns]

    return_wide = merged_df.pivot_table(
        index="date", columns="symbol", values="daily_return"
    )
    return_wide.columns = [f"{col}_return" for col in return_wide.columns]

    wide = price_wide.join(return_wide)
    wide = wide.reset_index()

    # 保存
    wide_path = os.path.join(CLEANED_DATA_DIR, "wide_table.csv")
    wide.to_csv(wide_path, index=False)
    print(f"✓ 宽表已保存: {wide_path}（{len(wide)} 行, {len(wide.columns)} 列）")

    return wide


# ============================================================
# 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="清洗加密货币数据")
    parser.add_argument(
        "--coins", nargs="+", default=None,
        help="要清洗的币种（默认: btc eth sol）"
    )

    args = parser.parse_args()
    coins = args.coins or SUPPORTED_COINS

    print("=" * 50)
    print("数据清洗工具")
    print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"币种: {', '.join(coins)}")
    print("=" * 50)

    # 清洗每个币种
    for coin in coins:
        print(f"\n[清洗 {coin.upper()}]")
        try:
            raw_df = load_raw_data(coin)
            cleaned_df = clean_single_coin(raw_df, coin)
            save_cleaned_data(cleaned_df, coin)
        except FileNotFoundError as e:
            print(f"  ✗ {e}")

    # 合并所有币种
    print("\n[合并数据]")
    merged = merge_all_coins(coins)

    if not merged.empty:
        print("\n[创建宽表]")
        create_wide_table(merged)

    print("\n" + "=" * 50)
    print("数据清洗完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
