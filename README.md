# Crypto Market Analysis

A Python-based project for analyzing cryptocurrency market data — combining data science, financial modeling, and crypto market insights.

## Project Structure

```
crypto-market-analysis/
├── app/
│   └── dashboard.py        # Phase 7: Streamlit 交互式仪表盘
├── data/
│   ├── cleaned/            # 清洗后的数据
│   └── indicators/         # 带技术指标的数据
├── images/                 # 生成的图表
├── notebooks/              # Jupyter notebooks
├── src/
│   ├── fetch_data.py       # Phase 1: 数据采集（CoinGecko API）
│   ├── clean_data.py       # Phase 2: 数据清洗与预处理
│   ├── indicators.py       # Phase 3: 技术指标（RSI, MACD, Bollinger Bands）
│   ├── visualize.py        # Phase 4: 数据可视化
│   ├── correlation.py      # Phase 5: 相关性分析
│   └── ml_model.py         # Phase 6: ML 价格预测
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/fengjason332-alt/crypto-market-analysis.git
cd crypto-market-analysis
```

### 2. Create & activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Pipeline — 按顺序运行

```bash
# Phase 1: 拉取数据
python src/fetch_data.py

# Phase 2: 清洗数据
python src/clean_data.py

# Phase 3: 计算技术指标
python src/indicators.py

# Phase 4: 生成图表
python src/visualize.py

# Phase 5: 相关性分析
python src/correlation.py

# Phase 6: ML 价格预测
python src/ml_model.py

# Phase 7: 启动仪表盘
streamlit run app/dashboard.py
```

## Tech Stack

- **Python 3.10+**
- **pandas / numpy** — data processing
- **matplotlib / seaborn / plotly** — visualization
- **scikit-learn** — machine learning (Linear Regression, Random Forest, Gradient Boosting)
- **streamlit** — interactive web dashboard
- **requests / ccxt** — crypto market data APIs

## Features

- Fetch historical price data for BTC, ETH, SOL from CoinGecko
- Data cleaning: handle missing values, duplicates, outliers
- Technical indicators: SMA, EMA, RSI(14), MACD, Bollinger Bands
- Correlation analysis: price/return correlation, rolling correlation
- ML models: price prediction with 4 models and performance comparison
- Interactive Streamlit dashboard with real-time charts

## Author

Jason Feng — University of Utah, Game Design & CS
