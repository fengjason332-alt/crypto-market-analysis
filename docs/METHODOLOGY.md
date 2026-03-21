# Methodology

## Dataset

- **Source:** CoinGecko API (`/coins/{id}/market_chart`)
- **Assets:** BTC, ETH, SOL
- **Period:** 365 days of daily data
- **Fields:** price, market_cap, total_volume

## Target Variable

Next-day closing price, defined as:

```python
df["target"] = df["price"].shift(-1)
```

Each row's features use data from "today and before" to predict "tomorrow's" price.

## Baseline

**Naive forecast:** predict tomorrow's price = today's price.

This is the standard benchmark for financial time series (see [Hyndman & Athanasopoulos, FPP3 §5.2](https://otexts.com/fpp3/simple-methods.html)). If an ML model cannot outperform this baseline, it is not adding predictive value.

## Evaluation

**Default mode:** chronological 80/20 train/test split. The first 80% of data (by date) trains the model; the last 20% is held out for testing. No random shuffling.

**Walk-forward mode (`--cv` flag):** `TimeSeriesSplit` with 5 folds. Each fold expands the training window and rolls the test window forward. Scaler is re-fit on each fold independently to prevent information leakage.

**Metrics:** RMSE, MAE, R², MAPE.

## Models

| Model | Type | Key Hyperparameters |
|-------|------|-------------------|
| Naive Baseline | Heuristic | None |
| Linear Regression | Linear | Default |
| Ridge Regression | Linear | alpha=1.0 |
| Random Forest | Ensemble | n_estimators=100, max_depth=10 |
| Gradient Boosting | Ensemble | n_estimators=100, max_depth=5, lr=0.1 |

## Leakage Prevention

- Target is `shift(-1)` (future data), features are `shift(+n)` or rolling windows (past data only)
- Train/test split is chronological, never random
- `StandardScaler` is fit on training data only; test data uses `transform()`
- In walk-forward CV, scaler is re-fit per fold

## React Frontend "AI" Modules

The following UI features in the CryptoScope React app are **rule-based heuristics, not machine learning models:**

| UI Label | Actual Implementation | File |
|----------|----------------------|------|
| "AI Signals" | RSI/trend/MACD threshold rules | `src/utils/signals.js` |
| "Market Sentiment" | Weighted average of RSI + 24h change | `src/utils/sentiment.js` |
| "AI Prediction" | Multi-factor heuristic scoring | `src/utils/predictions.js` |
| "On-Chain Data" | Static mock data | `src/data/mockData.js` |

These modules are intentionally structured to be swapped with real API endpoints or ML model inference later. The current implementation demonstrates product surface area and UX thinking, not predictive accuracy.
