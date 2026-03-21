"""
ml_model.py — 机器学习价格预测模块
====================================

功能：用机器学习模型预测加密货币价格走势。

模型：
1. Linear Regression — 线性回归（基线模型）
2. Random Forest     — 随机森林（集成学习）
3. LSTM (可选)       — 长短期记忆网络（深度学习）

特征工程：
- 技术指标作为特征（SMA, EMA, RSI, MACD, Bollinger Bands）
- 滞后特征（过去 N 天的价格和收益率）
- 时间特征（星期几、月份）

使用方法：
    python src/ml_model.py                   # 预测全部币种
    python src/ml_model.py --coin btc        # 只预测 BTC
    python src/ml_model.py --days 30         # 预测未来 30 天趋势

作者：Jason
日期：2026-03
"""

import pandas as pd
import numpy as np
import os
import argparse
import warnings
from datetime import datetime

# scikit-learn 模型和工具
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    mean_absolute_percentage_error,
)

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

warnings.filterwarnings("ignore")


# ============================================================
# 配置
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
INDICATOR_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "indicators")
IMAGES_DIR = os.path.join(PROJECT_ROOT, "images")

SUPPORTED_COINS = ["btc", "eth", "sol"]

COLORS = {
    "BTC": "#F7931A",
    "ETH": "#627EEA",
    "SOL": "#9945FF",
}

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
# 特征工程
# ============================================================

def create_features(df: pd.DataFrame, target_col: str = "price",
                    lag_days: list = None) -> pd.DataFrame:
    """
    从原始数据创建 ML 特征。

    特征类型：
    1. 滞后特征 — 过去 N 天的价格（让模型看到历史趋势）
    2. 滚动统计 — 过去 N 天的均值、标准差
    3. 技术指标 — 已经在 indicators.py 中计算好的
    4. 时间特征 — 星期几、月份等

    参数：
        df: 包含技术指标的数据
        target_col: 预测目标列
        lag_days: 滞后天数列表

    返回：
        DataFrame: 包含所有特征的数据（已去除 NaN 行）
    """
    if lag_days is None:
        lag_days = [1, 3, 7, 14, 30]

    df = df.copy()

    # 确保 date 是 datetime 类型
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])

    # ---- 1. 滞后特征 ----
    # 让模型知道"昨天/上周/上个月的价格是多少"
    for lag in lag_days:
        df[f"price_lag_{lag}"] = df[target_col].shift(lag)
        df[f"return_lag_{lag}"] = df["daily_return"].shift(lag)

    # ---- 2. 滚动统计特征 ----
    for window in [7, 14, 30]:
        df[f"rolling_mean_{window}"] = df[target_col].rolling(window).mean()
        df[f"rolling_std_{window}"] = df[target_col].rolling(window).std()
        df[f"rolling_min_{window}"] = df[target_col].rolling(window).min()
        df[f"rolling_max_{window}"] = df[target_col].rolling(window).max()

    # ---- 3. 价格变化率特征 ----
    for period in [1, 7, 30]:
        df[f"price_change_{period}d"] = df[target_col].pct_change(periods=period)

    # ---- 4. 时间特征 ----
    df["day_of_week"] = df["date"].dt.dayofweek     # 0=周一, 6=周日
    df["month"] = df["date"].dt.month
    df["day_of_month"] = df["date"].dt.day

    # ---- 5. 目标变量 ----
    # 预测明天的价格
    df["target"] = df[target_col].shift(-1)

    # 去除含 NaN 的行（滞后特征导致开头几行没有值）
    df = df.dropna()

    return df


def get_feature_columns(df: pd.DataFrame) -> list:
    """获取所有特征列名（排除非特征列）。"""
    exclude_cols = {
        "date", "symbol", "target", "price", "market_cap",
        "total_volume", "daily_return", "log_return"
    }
    return [c for c in df.columns if c not in exclude_cols]


# ============================================================
# 模型训练与评估
# ============================================================

def compute_metrics(y_true, y_pred) -> dict:
    """计算四个标准回归指标，返回字典。"""
    return {
        "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
        "mae": mean_absolute_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred),
        "mape": mean_absolute_percentage_error(y_true, y_pred) * 100,
    }


def train_and_evaluate(df: pd.DataFrame, coin: str = "BTC") -> dict:
    """
    训练多个模型并评估性能。

    使用时间序列分割（不能用未来数据预测过去）：
    - 前 80% 数据用于训练
    - 后 20% 数据用于测试

    返回：
        dict: {模型名: {metrics, predictions, model}}
    """
    feature_cols = get_feature_columns(df)
    X = df[feature_cols].values
    y = df["target"].values
    dates = df["date"].values

    # 时间序列分割（不能随机打乱！）
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    dates_test = dates[split_idx:]

    # 特征标准化（让所有特征在同一量级）
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 定义模型
    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
        ),
    }

    results = {}

    # ---- Naive Baseline: "明天的价格 = 今天的价格" ----
    y_pred_naive = df["price"].values[split_idx : split_idx + len(y_test)]

    naive_rmse = np.sqrt(mean_squared_error(y_test, y_pred_naive))
    naive_mae = mean_absolute_error(y_test, y_pred_naive)
    naive_r2 = r2_score(y_test, y_pred_naive)
    naive_mape = mean_absolute_percentage_error(y_test, y_pred_naive) * 100

    results["▶ Naive Baseline"] = {
        "rmse": naive_rmse,
        "mae": naive_mae,
        "r2": naive_r2,
        "mape": naive_mape,
        "y_test": y_test,
        "y_pred": y_pred_naive,
        "dates": dates_test,
        "model": None,
    }

    print(f"\n  ▶ Naive Baseline (tomorrow = today):")
    print(f"    RMSE:  ${naive_rmse:,.2f}")
    print(f"    MAE:   ${naive_mae:,.2f}")
    print(f"    R²:    {naive_r2:.4f}")
    print(f"    MAPE:  {naive_mape:.2f}%")

    for name, model in models.items():
        print(f"\n  训练 {name}...")

        # 树模型用原始数据，线性模型用标准化数据
        if "Forest" in name or "Boosting" in name:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
        else:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)

        # 评估指标
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred) * 100

        results[name] = {
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "mape": mape,
            "y_test": y_test,
            "y_pred": y_pred,
            "dates": dates_test,
            "model": model,
        }

        print(f"    RMSE:  ${rmse:,.2f}")
        print(f"    MAE:   ${mae:,.2f}")
        print(f"    R²:    {r2:.4f}")
        print(f"    MAPE:  {mape:.2f}%")

    return results


def plot_predictions(results: dict, coin: str = "btc") -> None:
    """
    绘制预测 vs 实际价格对比图。

    每个模型一条线，看谁拟合得最好。
    """
    color = COLORS.get(coin.upper(), "#fff")
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()

    for i, (name, res) in enumerate(results.items()):
        if i >= len(axes):
            break
        ax = axes[i]
        dates = pd.to_datetime(res["dates"])

        ax.plot(dates, res["y_test"], color="#eee",
                linewidth=1.5, alpha=0.8, label="Actual")
        ax.plot(dates, res["y_pred"], color=color,
                linewidth=1.5, alpha=0.9, label="Predicted")

        ax.set_title(f"{name}\nR²={res['r2']:.3f}  MAPE={res['mape']:.1f}%",
                     fontsize=11, fontweight="bold")
        ax.legend(loc="upper left", framealpha=0.3, fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax.tick_params(axis="x", rotation=45)

    plt.suptitle(f"{coin.upper()} Price Prediction — Model Comparison",
                 fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()

    os.makedirs(IMAGES_DIR, exist_ok=True)
    fig.savefig(os.path.join(IMAGES_DIR, f"{coin}_predictions.png"))
    print(f"\n  ✓ 保存: {coin}_predictions.png")
    plt.close(fig)


def plot_feature_importance(model, feature_names: list, coin: str = "btc",
                            top_n: int = 15) -> None:
    """绘制随机森林的特征重要性排名。"""
    if not hasattr(model, "feature_importances_"):
        return

    importances = model.feature_importances_
    indices = np.argsort(importances)[-top_n:]

    fig, ax = plt.subplots(figsize=(10, 8))

    ax.barh(range(len(indices)), importances[indices],
            color="#e94560", alpha=0.8)
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([feature_names[i] for i in indices])
    ax.set_title(f"{coin.upper()} — Top {top_n} Feature Importance (Random Forest)",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Importance")
    ax.grid(True, alpha=0.3, axis="x")

    os.makedirs(IMAGES_DIR, exist_ok=True)
    fig.savefig(os.path.join(IMAGES_DIR, f"{coin}_feature_importance.png"))
    print(f"  ✓ 保存: {coin}_feature_importance.png")
    plt.close(fig)


# ============================================================
# Walk-Forward Cross-Validation
# ============================================================

def walk_forward_evaluate(df: pd.DataFrame, coin: str = "BTC", n_splits: int = 5) -> dict:
    """
    Walk-forward 滚动窗口交叉验证。

    与单次 80/20 分割的区别：
    - 做 n_splits 次分割，每次训练窗口扩大，测试窗口滚动前进
    - 每个 fold 独立 fit scaler（防止信息泄漏）
    - 输出 mean ± std，比单一数字更可靠

    使用方式：python src/ml_model.py --cv
    """
    feature_cols = get_feature_columns(df)
    X = df[feature_cols].values
    y = df["target"].values

    tscv = TimeSeriesSplit(n_splits=n_splits)

    model_configs = {
        "Linear Regression": lambda: LinearRegression(),
        "Ridge Regression": lambda: Ridge(alpha=1.0),
        "Random Forest": lambda: RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        ),
        "Gradient Boosting": lambda: GradientBoostingRegressor(
            n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
        ),
    }

    all_model_names = ["▶ Naive Baseline"] + list(model_configs.keys())
    cv_results = {name: {"rmse": [], "mae": [], "r2": [], "mape": []}
                  for name in all_model_names}

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        print(f"\n  --- Fold {fold + 1}/{n_splits} "
              f"(Train: {len(train_idx)}, Test: {len(test_idx)}) ---")

        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # 每个 fold 重新 fit scaler（防止未来数据泄漏）
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Naive baseline: 用当前行的 price 作为"明天"的预测
        y_pred_naive = df["price"].values[test_idx]
        for k, v in compute_metrics(y_test, y_pred_naive).items():
            cv_results["▶ Naive Baseline"][k].append(v)

        # 训练每个 ML 模型
        for name, model_fn in model_configs.items():
            model = model_fn()

            if "Forest" in name or "Boosting" in name:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            else:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)

            for k, v in compute_metrics(y_test, y_pred).items():
                cv_results[name][k].append(v)

    # 打印汇总表
    print(f"\n{'=' * 80}")
    print(f"  {coin.upper()} — Walk-Forward CV Summary ({n_splits} folds)")
    print(f"{'=' * 80}")
    print(f"  {'Model':<25} {'RMSE':>14} {'MAE':>14} {'R²':>12} {'MAPE':>10}")
    print(f"  {'-' * 75}")

    for name in all_model_names:
        r = cv_results[name]
        print(f"  {name:<25} "
              f"${np.mean(r['rmse']):>8,.0f}±{np.std(r['rmse']):>4,.0f}  "
              f"${np.mean(r['mae']):>8,.0f}±{np.std(r['mae']):>4,.0f}  "
              f"{np.mean(r['r2']):>6.3f}±{np.std(r['r2']):.3f}  "
              f"{np.mean(r['mape']):>5.1f}±{np.std(r['mape']):.1f}%")

    print(f"{'=' * 80}")
    return cv_results


# ============================================================
# 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="加密货币 ML 价格预测")
    parser.add_argument("--coin", type=str, default=None, help="指定币种")
    parser.add_argument("--cv", action="store_true",
                        help="启用 walk-forward cross-validation（默认关闭）")

    args = parser.parse_args()
    coins = [args.coin] if args.coin else SUPPORTED_COINS

    print("=" * 50)
    print("ML 价格预测工具")
    print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    for coin in coins:
        print(f"\n{'='*50}")
        print(f"预测 {coin.upper()}")
        print("=" * 50)

        try:
            # 读取带指标的数据
            filepath = os.path.join(INDICATOR_DATA_DIR, f"{coin}_indicators.csv")
            df = pd.read_csv(filepath, parse_dates=["date"])
            print(f"  读取了 {len(df)} 行数据")

            # 创建特征
            print("\n[特征工程]")
            df_features = create_features(df)
            feature_cols = get_feature_columns(df_features)
            print(f"  特征数量: {len(feature_cols)}")
            print(f"  样本数量: {len(df_features)}")

            if args.cv:
                # Walk-Forward Cross-Validation 模式
                print("\n[Walk-Forward Cross-Validation]")
                cv_results = walk_forward_evaluate(df_features, coin)
            else:
                # 默认：单次 80/20 分割
                print("\n[模型训练]")
                results = train_and_evaluate(df_features, coin)

                # 可视化
                print("\n[生成图表]")
                plot_predictions(results, coin)

                # 特征重要性（使用随机森林模型）
                if "Random Forest" in results:
                    rf_model = results["Random Forest"]["model"]
                    plot_feature_importance(rf_model, feature_cols, coin)

            # 打印模型对比（仅在非 CV 模式下）
            if not args.cv:
                print(f"\n[{coin.upper()} 模型对比]")
                print(f"{'模型':<25} {'RMSE':>12} {'MAE':>12} {'R²':>8} {'MAPE':>8}")
                print("-" * 65)
                for name, res in sorted(results.items(), key=lambda x: x[1]["mape"]):
                    print(f"{name:<25} ${res['rmse']:>10,.2f} ${res['mae']:>10,.2f} "
                          f"{res['r2']:>7.4f} {res['mape']:>6.2f}%")

        except FileNotFoundError:
            print(f"  ✗ 找不到 {coin} 指标数据，请先运行 indicators.py")
        except Exception as e:
            print(f"  ✗ 错误: {e}")

    print("\n" + "=" * 50)
    print("ML 预测完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
