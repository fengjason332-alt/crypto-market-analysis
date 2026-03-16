# Crypto Market Analysis

A Python-based project for analyzing cryptocurrency market data — combining data science, financial modeling, and crypto market insights.

## Project Structure

```
crypto-market-analysis/
├── app/            # Streamlit or Flask web app (dashboard/UI)
├── data/           # Raw and processed data (gitignored)
├── images/         # Charts and visual outputs
├── notebooks/      # Jupyter notebooks for exploration & analysis
├── src/            # Core Python modules and scripts
├── venv/           # Virtual environment (gitignored)
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
# or
venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Tech Stack

- **Python 3.10+**
- **pandas / numpy** — data processing
- **matplotlib / seaborn / plotly** — visualization
- **requests / ccxt** — crypto market data APIs
- **jupyter** — exploratory analysis

## Goals

- Fetch and analyze real-time and historical crypto price data
- Build financial indicators (RSI, MACD, Bollinger Bands, etc.)
- Visualize market trends and correlations
- Explore ML-based price prediction models

## Author

Jason Feng — University of Utah, Game Design & CS
