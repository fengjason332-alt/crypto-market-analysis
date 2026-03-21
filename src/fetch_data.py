"""
fetch_data.py — 加密货币历史数据采集模块
==========================================

功能：从 CoinGecko API 拉取 BTC、ETH、SOL 的历史价格数据，保存为 CSV 文件。

CoinGecko API 文档：https://www.coingecko.com/en/api/documentation
- 免费版：不需要 API Key
- 限制：每分钟约 10-30 次请求（免费版）
- 我们使用的接口：/coins/{id}/market_chart

使用方法：
    python src/fetch_data.py                  # 拉取全部三个币种（默认365天）
    python src/fetch_data.py --days 730       # 拉取过去730天的数据
    python src/fetch_data.py --coins btc eth  # 只拉取 BTC 和 ETH

前置依赖：
    pip install requests pandas

作者：Jason
日期：2026-03
"""

# ============================================================
# 第一部分：导入库
# ============================================================

import requests      # 发送 HTTP 请求（就像浏览器访问网页一样）
import pandas as pd  # 数据处理的瑞士军刀（表格操作、CSV读写等）
import time          # 控制请求间隔，避免被 API 限流
import os            # 文件和目录操作（创建 data/ 文件夹）
import argparse      # 解析命令行参数（让脚本更灵活）
from datetime import datetime  # 时间戳转换为人类可读的日期


# ============================================================
# 第二部分：配置常量
# ============================================================

# CoinGecko API 的基础 URL（所有请求都以这个开头）
BASE_URL = "https://api.coingecko.com/api/v3"

# 币种映射：我们项目里用的简称 → CoinGecko 用的 ID
# 你可以在 https://api.coingecko.com/api/v3/coins/list 查到所有可用的币种 ID
COIN_MAP = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
}

# 数据保存路径（相对于项目根目录）
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# 请求之间的等待秒数（防止触发 CoinGecko 的频率限制）
REQUEST_DELAY = 2


# ============================================================
# 第三部分：核心函数
# ============================================================

def fetch_coin_data(coin_id: str, vs_currency: str = "usd", days: int = 365) -> dict:
    """
    从 CoinGecko 拉取单个币种的历史市场数据。

    这个函数做的事情就像：
    1. 拼接一个 URL（相当于在浏览器地址栏输入网址）
    2. 发送 GET 请求（相当于按回车键）
    3. 拿到返回的 JSON 数据（相当于看到了网页内容）

    参数说明：
        coin_id (str): CoinGecko 的币种标识符，如 "bitcoin"
        vs_currency (str): 计价货币，默认 "usd"（美元）
        days (int): 拉取过去多少天的数据，默认 365 天

    返回：
        dict: API 返回的原始 JSON 数据，包含 prices, market_caps, total_volumes 三个字段

    可能的错误：
        requests.exceptions.HTTPError: API 返回了错误状态码（如 429 表示请求太频繁）
        requests.exceptions.ConnectionError: 网络连接失败
    """

    # 第 1 步：拼接 API 的完整 URL
    # CoinGecko 的 market_chart 接口格式：
    # https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=365
    url = f"{BASE_URL}/coins/{coin_id}/market_chart"

    # 第 2 步：设置查询参数（URL 里 ? 后面的部分）
    params = {
        "vs_currency": vs_currency,  # 计价货币
        "days": days,                # 天数
        "interval": "daily",         # 数据粒度：每天一条（不加这个可能返回小时级数据）
    }

    # 第 3 步：发送请求
    print(f"  正在请求 {coin_id} 的 {days} 天历史数据...")
    response = requests.get(url, params=params, timeout=30)

    # 第 4 步：检查响应状态
    # HTTP 状态码 200 = 成功，404 = 找不到，429 = 请求太频繁
    # raise_for_status() 会在状态码不是 200 时自动抛出异常
    response.raise_for_status()

    # 第 5 步：把 JSON 字符串解析成 Python 字典
    # 返回的数据结构大概长这样：
    # {
    #   "prices": [[1609459200000, 29000.5], [1609545600000, 32000.1], ...],
    #   "market_caps": [[1609459200000, 540000000000], ...],
    #   "total_volumes": [[1609459200000, 35000000000], ...]
    # }
    # 注意：时间戳是毫秒级的 Unix 时间戳（从1970年1月1日开始计算的毫秒数）
    data = response.json()
    print(f"  ✓ 成功获取 {len(data.get('prices', []))} 条数据")

    return data


def parse_to_dataframe(raw_data: dict, coin_symbol: str) -> pd.DataFrame:
    """
    把 API 返回的原始 JSON 数据转换成整洁的 pandas DataFrame。

    这个函数做的事情：
    - 把嵌套的列表 [[时间戳, 值], ...] 变成有列名的表格
    - 把毫秒时间戳转成 "2025-01-15" 格式的日期
    - 合并价格、市值、成交量到一张表里
    - 添加币种标识列（方便后续合并分析）

    参数说明：
        raw_data (dict): fetch_coin_data() 返回的原始数据
        coin_symbol (str): 币种简称，如 "btc"（会写进 CSV 的 symbol 列）

    返回：
        pd.DataFrame: 整理好的表格，列包括：
            - date: 日期（如 2025-01-15）
            - price: 收盘价（美元）
            - market_cap: 市值（美元）
            - total_volume: 24小时成交量（美元）
            - symbol: 币种简称
    """

    # 第 1 步：分别提取三组数据
    # 每组都是 [[时间戳, 值], [时间戳, 值], ...] 的格式
    prices = raw_data["prices"]
    market_caps = raw_data["market_caps"]
    total_volumes = raw_data["total_volumes"]

    # 第 2 步：创建 DataFrame
    # pd.DataFrame(data, columns=[列名]) 是创建表格最常用的方式
    df_price = pd.DataFrame(prices, columns=["timestamp", "price"])
    df_mcap = pd.DataFrame(market_caps, columns=["timestamp", "market_cap"])
    df_vol = pd.DataFrame(total_volumes, columns=["timestamp", "total_volume"])

    # 第 3 步：把毫秒时间戳转成日期
    # pd.to_datetime() 是 pandas 处理时间的核心函数
    # unit="ms" 告诉它输入是毫秒级时间戳
    # .dt.date 只保留日期部分（去掉时分秒）
    df_price["date"] = pd.to_datetime(df_price["timestamp"], unit="ms").dt.date

    # 第 4 步：合并三张表
    # merge() 就像 Excel 的 VLOOKUP —— 按时间戳把三张表对齐合并
    df = df_price.merge(df_mcap, on="timestamp", how="left")
    df = df.merge(df_vol, on="timestamp", how="left")

    # 第 5 步：清理和添加列
    df["symbol"] = coin_symbol.upper()  # 添加币种标识，如 "BTC"
    df = df.drop(columns=["timestamp"])  # 删掉原始时间戳列（已经有 date 列了）

    # 第 6 步：整理列的顺序（让 CSV 看起来更清晰）
    df = df[["date", "symbol", "price", "market_cap", "total_volume"]]

    # 第 7 步：按日期排序（确保是从旧到新）
    df = df.sort_values("date").reset_index(drop=True)

    return df


def save_to_csv(df: pd.DataFrame, coin_symbol: str) -> str:
    """
    把 DataFrame 保存为 CSV 文件。

    参数说明：
        df (pd.DataFrame): 要保存的数据
        coin_symbol (str): 币种简称，用于文件命名

    返回：
        str: 保存的文件路径
    """

    # 确保 data/ 目录存在（如果不存在就创建）
    # exist_ok=True 表示：如果目录已经存在，不报错
    os.makedirs(DATA_DIR, exist_ok=True)

    # 拼接文件路径：data/btc.csv
    filepath = os.path.join(DATA_DIR, f"{coin_symbol.lower()}.csv")

    # 保存为 CSV
    # index=False 表示不保存 pandas 自动生成的行号（0, 1, 2, ...）
    df.to_csv(filepath, index=False)

    print(f"  ✓ 已保存到 {filepath}（共 {len(df)} 行）")
    return filepath


def fetch_all(coins: list = None, days: int = 365) -> dict:
    """
    批量拉取多个币种的数据。这是主调度函数。

    参数说明：
        coins (list): 要拉取的币种列表，如 ["btc", "eth"]。默认拉取全部。
        days (int): 拉取天数

    返回：
        dict: {币种简称: DataFrame} 的字典
    """

    if coins is None:
        coins = list(COIN_MAP.keys())  # 默认拉取全部：btc, eth, sol

    results = {}

    for i, symbol in enumerate(coins):
        # 从映射表查找 CoinGecko 的 ID
        coin_id = COIN_MAP.get(symbol.lower())
        if coin_id is None:
            print(f"  ✗ 未知币种: {symbol}，跳过")
            continue

        print(f"\n[{i+1}/{len(coins)}] 处理 {symbol.upper()}...")

        try:
            # 拉取 → 解析 → 保存，三步走
            raw_data = fetch_coin_data(coin_id, days=days)
            df = parse_to_dataframe(raw_data, symbol)
            save_to_csv(df, symbol)
            results[symbol] = df

            # 两次请求之间暂停，避免被限流
            # 这在实际的 API 调用中非常重要！
            if i < len(coins) - 1:
                print(f"  等待 {REQUEST_DELAY} 秒（避免 API 限流）...")
                time.sleep(REQUEST_DELAY)

        except requests.exceptions.HTTPError as e:
            # API 返回了错误（如 429 Too Many Requests）
            print(f"  ✗ API 错误: {e}")
        except requests.exceptions.ConnectionError:
            # 网络连接失败
            print(f"  ✗ 网络连接失败，请检查网络")
        except Exception as e:
            # 其他未预料的错误
            print(f"  ✗ 未知错误: {e}")

    return results


# ============================================================
# 第四部分：命令行入口
# ============================================================

def main():
    """
    命令行入口函数。

    用法示例：
        python src/fetch_data.py                     # 全部币种，365天
        python src/fetch_data.py --days 730          # 全部币种，730天
        python src/fetch_data.py --coins btc eth     # 只拉 BTC 和 ETH
        python src/fetch_data.py --days 180 --coins sol  # SOL 最近180天
    """

    # argparse 是 Python 标准库里专门处理命令行参数的工具
    # 它能自动生成 --help 帮助文档
    parser = argparse.ArgumentParser(
        description="从 CoinGecko 拉取加密货币历史数据"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="拉取过去多少天的数据（默认: 365）"
    )
    parser.add_argument(
        "--coins",
        nargs="+",  # 允许传入多个值，如 --coins btc eth
        default=None,
        help="要拉取的币种（默认: btc eth sol）"
    )

    args = parser.parse_args()

    # 打印启动信息
    print("=" * 50)
    print("加密货币数据采集工具")
    print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"天数: {args.days}")
    print(f"币种: {', '.join(args.coins) if args.coins else '全部'}")
    print("=" * 50)

    # 开始采集
    results = fetch_all(coins=args.coins, days=args.days)

    # 打印总结
    print("\n" + "=" * 50)
    print("采集完成！")
    for symbol, df in results.items():
        date_range = f"{df['date'].iloc[0]} ~ {df['date'].iloc[-1]}"
        print(f"  {symbol.upper()}: {len(df)} 条数据 ({date_range})")
    print("=" * 50)


# 这个 if 判断是 Python 的惯用写法
# 意思是：只有直接运行这个文件时才执行 main()
# 如果被其他文件 import，就不会自动执行
if __name__ == "__main__":
    main()
