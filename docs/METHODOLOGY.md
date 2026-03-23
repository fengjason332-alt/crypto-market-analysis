# Methodology

## Dataset

Historical daily data for BTC, ETH, and SOL fetched from the CoinGecko `/coins/{id}/market_chart` endpoint. Default period: 365 days. Each record includes: date, closing price (USD), market cap, and 24h trading volume.

Data source is free and requires no API key. Rate limiting is handled with explicit inter-request delays (`time.sleep`) in `src/fetch_data.py`.

## Target Variable

Next-day closing price, defined as:

```python
df["target"] = df["price"].shift(-1)
```

This means for each row, the model uses today's features to predict tomorrow's price. The `shift(-1)` pulls tomorrow's value into today's row as the label.

## Features

Four categories of features are engineered in `src/ml_model.py → create_features()`:

**Technical indicators** (computed in `src/indicators.py`):
- SMA(7), SMA(20), SMA(50) — Simple Moving Averages
- EMA(12), EMA(26) — Exponential Moving Averages
- RSI(14) — Relative Strength Index
- MACD(12, 26, 9) — MACD line, signal line, histogram
- Bollinger Bands(20, 2) — upper, middle, lower bands + bandwidth + %B

**Lag features**: Price and daily return from 1, 3, 7, 14, and 30 days ago.

**Rolling statistics**: 7/14/30-day rolling mean, std, min, max of price.

**Time features**: Day of week, month, day of month.

Total feature count is approximately 40+ after feature engineering. Rows with NaN values (caused by lag/rolling lookback periods) are dropped before training.

## Models

| Model | Type | Key Hyperparameters |
|---|---|---|
| **Naive Baseline** | Heuristic | tomorrow = today (no training) |
| Linear Regression | Baseline linear | default |
| Ridge Regression | Regularized linear | alpha=1.0 |
| Random Forest | Tree ensemble | 100 trees, max_depth=10 |
| Gradient Boosting | Boosted ensemble | 100 trees, lr=0.1, max_depth=5 |

The naive baseline predicts tomorrow's price as today's price. This is a standard benchmark in financial time-series forecasting. If an ML model cannot beat this, it has not learned a useful signal.

## Evaluation Methods

### Method 1: Chronological Split (default)

- First 80% of data → training set
- Last 20% of data → test set
- No random shuffling — this respects time ordering
- `StandardScaler` is fit only on the training set; test set uses `.transform()`

Run: `python src/ml_model.py`

### Method 2: Walk-Forward Cross-Validation (--cv flag)

- Uses `sklearn.model_selection.TimeSeriesSplit` with 5 folds
- Each fold independently fits its own `StandardScaler` (prevents leakage through scaler statistics)
- Reports mean ± standard deviation for each metric across folds
- More reliable than a single split because it tests the model across multiple time windows

Run: `python src/ml_model.py --cv`

### Metrics

| Metric | What It Measures |
|---|---|
| RMSE | Root Mean Squared Error — penalizes large errors more |
| MAE | Mean Absolute Error — average dollar error |
| R² | Coefficient of determination — proportion of variance explained |
| MAPE | Mean Absolute Percentage Error — error as % of actual price |

## Leakage Analysis

This pipeline has been reviewed for data leakage. Summary:

- ✅ Target uses `shift(-1)` — predicts future, does not use future as feature
- ✅ Train/test split is chronological — no random shuffling
- ✅ Scaler fits only on training data — test data uses `.transform()`
- ✅ Walk-forward CV refits scaler per fold — no cross-fold leakage
- ⚠️ `indicators.py` uses `min_periods=1` for rolling windows, meaning early rows have indicators based on incomplete windows. These are mostly removed by `dropna()` in feature engineering.

## About the React Frontend's "AI" Modules

The CryptoScope React frontend (`app/frontend/`) includes panels labeled "AI Signals," "AI Prediction," and "Market Sentiment." These are **not** trained ML models. They are:

- **AI Signals** (`src/utils/signals.js`): Rule-based engine that checks RSI thresholds, price vs SMA(20), and MACD crossovers. Outputs directional labels via priority-weighted vote.

- **AI Prediction** (`src/utils/predictions.js`): Heuristic scoring function that weights RSI, price vs SMA, MACD histogram, and recent returns. The code explicitly states it is rule-based and designed to be swapped for a real model endpoint later.

- **Market Sentiment** (`src/utils/sentiment.js`): Composite 0–100 score from average RSI and average 24h price change, mapped to Fear/Neutral/Greed labels.

These modules demonstrate product surface area and UX design, not ML capability. The actual ML work lives in `src/ml_model.py`.

## On-Chain Data

The on-chain metrics panel uses mock data. The component is structured for future API integration but no real on-chain data is currently fetched.
