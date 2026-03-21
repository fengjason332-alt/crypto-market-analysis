"""
test_indicators.py — 技术指标单元测试
=====================================

运行方式：
    cd crypto-market-analysis
    pytest tests/ -v

测试目标：验证核心金融指标的行为符合定义。
"""

import pandas as pd
import numpy as np
import sys
import os

# 让 pytest 找到 src/ 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from indicators import sma, ema, rsi, macd, bollinger_bands, add_all_indicators


def test_rsi_all_gains():
    """价格连续上涨 → RSI 应接近 100。"""
    prices = pd.Series([100 + i * 2 for i in range(30)])
    result = rsi(prices, period=14)
    assert result.iloc[-1] > 90, (
        f"RSI should be >90 for all-gains series, got {result.iloc[-1]}"
    )


def test_rsi_all_losses():
    """价格连续下跌 → RSI 应接近 0。"""
    prices = pd.Series([200 - i * 2 for i in range(30)])
    result = rsi(prices, period=14)
    assert result.iloc[-1] < 10, (
        f"RSI should be <10 for all-losses series, got {result.iloc[-1]}"
    )


def test_sma_constant_series():
    """常数序列 → SMA 应等于该常数。"""
    prices = pd.Series([50.0] * 30)
    result = sma(prices, window=20)
    assert abs(result.iloc[-1] - 50.0) < 0.01, (
        f"SMA of constant series should be 50, got {result.iloc[-1]}"
    )


def test_macd_constant_series():
    """常数序列 → MACD line 和 histogram 应接近 0。"""
    prices = pd.Series([100.0] * 50)
    result = macd(prices)
    assert abs(result["macd_line"].iloc[-1]) < 0.01, (
        f"MACD line should be ~0, got {result['macd_line'].iloc[-1]}"
    )
    assert abs(result["macd_histogram"].iloc[-1]) < 0.01, (
        f"MACD histogram should be ~0, got {result['macd_histogram'].iloc[-1]}"
    )


def test_bollinger_bands_constant():
    """常数序列 → 上轨和下轨应收敛到同一个值。"""
    prices = pd.Series([75.0] * 30)
    result = bollinger_bands(prices, window=20)
    assert abs(result["bb_upper"].iloc[-1] - 75.0) < 0.01
    assert abs(result["bb_lower"].iloc[-1] - 75.0) < 0.01


def test_no_nans_after_warmup():
    """100 天数据加指标后，第 50 天之后不应有 NaN。"""
    n = 100
    prices = [50000 + np.sin(i / 10) * 2000 + np.random.normal(0, 200)
              for i in range(n)]
    df = pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=n),
        "price": prices,
        "market_cap": [p * 19e6 for p in prices],
        "total_volume": [p * 1e4 for p in prices],
        "daily_return": pd.Series(prices).pct_change(),
        "log_return": np.log(
            pd.Series(prices) / pd.Series(prices).shift(1)
        ),
        "symbol": "BTC",
    })
    result = add_all_indicators(df)
    tail = result.iloc[50:]
    nan_count = tail.isna().sum().sum()
    assert nan_count == 0, (
        f"Found {nan_count} NaN values after row 50. "
        f"Columns: {tail.columns[tail.isna().any()].tolist()}"
    )
