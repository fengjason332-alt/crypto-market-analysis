"""
test_indicators.py — 技术指标单元测试
=====================================

运行方式：
    cd crypto-market-analysis
    pytest tests/ -v

测试策略：
- 用已知输入验证指标的数学行为
- 重点是边界情况和健全性检查
"""

import pandas as pd
import numpy as np
import sys
import os

# 让 pytest 能找到 src/ 下的模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from indicators import sma, ema, rsi, macd, bollinger_bands, add_all_indicators


class TestRSI:
    """RSI 相关测试。"""

    def test_rsi_all_gains_near_100(self):
        """价格连续上涨 30 天 → RSI 应该 > 90。"""
        prices = pd.Series([100 + i * 2 for i in range(30)])
        result = rsi(prices, period=14)
        assert result.iloc[-1] > 90, \
            f"RSI should be >90 for all-gains, got {result.iloc[-1]:.1f}"

    def test_rsi_all_losses_near_0(self):
        """价格连续下跌 30 天 → RSI 应该 < 10。"""
        prices = pd.Series([200 - i * 2 for i in range(30)])
        result = rsi(prices, period=14)
        assert result.iloc[-1] < 10, \
            f"RSI should be <10 for all-losses, got {result.iloc[-1]:.1f}"

    def test_rsi_range_0_to_100(self):
        """RSI 的输出值域应该在 [0, 100]。"""
        np.random.seed(42)
        prices = pd.Series(np.cumsum(np.random.randn(100)) + 100)
        result = rsi(prices, period=14).dropna()
        assert result.min() >= 0, f"RSI min {result.min():.1f} is below 0"
        assert result.max() <= 100, f"RSI max {result.max():.1f} is above 100"


class TestSMA:
    """SMA 相关测试。"""

    def test_sma_constant_series(self):
        """常数序列的 SMA 应该等于该常数。"""
        prices = pd.Series([50.0] * 30)
        result = sma(prices, window=20)
        assert abs(result.iloc[-1] - 50.0) < 0.01

    def test_sma_known_values(self):
        """手动验证：[1,2,3,4,5] 的 SMA(3) 最后一个值应该是 4.0。"""
        prices = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = sma(prices, window=3)
        assert abs(result.iloc[-1] - 4.0) < 0.01


class TestMACD:
    """MACD 相关测试。"""

    def test_macd_constant_series_near_zero(self):
        """常数序列 → EMA(12) ≈ EMA(26) → MACD line ≈ 0。"""
        prices = pd.Series([100.0] * 50)
        result = macd(prices)
        assert abs(result["macd_line"].iloc[-1]) < 0.01
        assert abs(result["macd_histogram"].iloc[-1]) < 0.01

    def test_macd_output_columns(self):
        """MACD 应该返回 3 列：macd_line, macd_signal, macd_histogram。"""
        prices = pd.Series([100 + i for i in range(50)])
        result = macd(prices)
        expected_cols = {"macd_line", "macd_signal", "macd_histogram"}
        assert set(result.columns) == expected_cols


class TestBollingerBands:
    """布林带相关测试。"""

    def test_bb_constant_series(self):
        """常数序列 → 标准差=0 → 上轨=中轨=下轨=该常数。"""
        prices = pd.Series([75.0] * 30)
        result = bollinger_bands(prices, window=20)
        last = result.iloc[-1]
        assert abs(last["bb_upper"] - 75.0) < 0.01
        assert abs(last["bb_middle"] - 75.0) < 0.01
        assert abs(last["bb_lower"] - 75.0) < 0.01

    def test_bb_upper_above_lower(self):
        """对任意波动序列，热身期之后上轨应始终 >= 下轨。"""
        np.random.seed(42)
        prices = pd.Series(np.cumsum(np.random.randn(100)) + 100)
        result = bollinger_bands(prices)
        # 跳过前 20 行热身期（rolling window=20 还没填满）
        tail = result.iloc[20:]
        assert (tail["bb_upper"] >= tail["bb_lower"]).all()


class TestAddAllIndicators:
    """整合测试：add_all_indicators 的输出质量。"""

    def test_no_nans_after_warmup(self):
        """100 天数据加完指标后，第 50 行之后不应有 NaN。"""
        n = 100
        prices = [50000 + np.sin(i / 10) * 2000 for i in range(n)]
        df = pd.DataFrame({
            "date": pd.date_range("2025-01-01", periods=n),
            "price": prices,
            "market_cap": [p * 19e6 for p in prices],
            "total_volume": [p * 1e4 for p in prices],
            "daily_return": pd.Series(prices).pct_change(),
            "log_return": np.log(pd.Series(prices) / pd.Series(prices).shift(1)),
            "symbol": "BTC",
        })
        result = add_all_indicators(df)
        tail = result.iloc[50:]
        nan_count = tail.isna().sum().sum()
        assert nan_count == 0, f"Found {nan_count} NaN values after row 50"

    def test_output_has_expected_columns(self):
        """add_all_indicators 应该添加 RSI、MACD、BB 等列。"""
        n = 60
        prices = [100 + i * 0.5 for i in range(n)]
        df = pd.DataFrame({
            "date": pd.date_range("2025-01-01", periods=n),
            "price": prices,
            "market_cap": [1e9] * n,
            "total_volume": [1e6] * n,
            "daily_return": pd.Series(prices).pct_change(),
            "log_return": [0.005] * n,
            "symbol": "TEST",
        })
        result = add_all_indicators(df)
        required_cols = ["rsi_14", "macd_line", "macd_signal",
                         "bb_upper", "bb_lower", "sma_20", "ema_12"]
        for col in required_cols:
            assert col in result.columns, f"Missing expected column: {col}"
