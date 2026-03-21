"""
dashboard.py — Crypto Market Analysis Dashboard
=================================================

Sleek, dark-themed dashboard inspired by OKX / Binance market UI.
Supports English (default), Chinese, and Spanish.

Launch:
    streamlit run app/dashboard.py

Author: Jason Feng
Date: 2026-03
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

# ============================================================
# Config
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
INDICATOR_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "indicators")
CLEANED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")

COINS = {
    "BTC": {"color": "#F7931A", "name": "Bitcoin"},
    "ETH": {"color": "#627EEA", "name": "Ethereum"},
    "SOL": {"color": "#9945FF", "name": "Solana"},
}

# ============================================================
# i18n — Internationalization
# ============================================================

TRANSLATIONS = {
    "en": {
        "page_title": "Crypto Market Analysis",
        "nav_markets": "Markets",
        "nav_technical": "Technical",
        "nav_correlation": "Correlation",
        "nav_data": "Data",
        "select_coins": "Assets",
        "time_range": "Period",
        "time_all": "All",
        "time_30": "30D",
        "time_90": "90D",
        "time_180": "180D",
        "time_365": "1Y",
        "price": "Price",
        "change_24h": "24h Change",
        "volume_24h": "24h Volume",
        "market_cap": "Market Cap",
        "rsi": "RSI(14)",
        "price_trend": "Price Trend",
        "volume": "Volume",
        "overbought": "Overbought",
        "oversold": "Oversold",
        "select_asset": "Select Asset",
        "return_corr": "Return Correlation",
        "rolling_corr": "Rolling Correlation",
        "window_size": "Window (days)",
        "stats_summary": "Statistics",
        "coin_col": "Asset",
        "current_price": "Price",
        "total_return": "Total Return",
        "annual_vol": "Annual Vol",
        "sharpe": "Sharpe",
        "max_drawdown": "Max Drawdown",
        "rows": "rows",
        "select_columns": "Columns",
        "download_csv": "Download CSV",
        "no_data": "No data available. Run the data pipeline first.",
        "no_coins": "Select at least one asset.",
        "dominance": "BTC Dominance",
        "hot_crypto": "Hot Crypto",
        "overview": "Overview",
        "built_by": "Built by Jason Feng · University of Utah",
    },
    "zh": {
        "page_title": "加密货币市场分析",
        "nav_markets": "市场",
        "nav_technical": "技术分析",
        "nav_correlation": "相关性",
        "nav_data": "数据",
        "select_coins": "币种",
        "time_range": "时间",
        "time_all": "全部",
        "time_30": "30天",
        "time_90": "90天",
        "time_180": "180天",
        "time_365": "1年",
        "price": "价格",
        "change_24h": "24h 涨跌",
        "volume_24h": "24h 成交量",
        "market_cap": "市值",
        "rsi": "RSI(14)",
        "price_trend": "价格走势",
        "volume": "成交量",
        "overbought": "超买",
        "oversold": "超卖",
        "select_asset": "选择币种",
        "return_corr": "收益率相关性",
        "rolling_corr": "滚动相关性",
        "window_size": "窗口（天）",
        "stats_summary": "统计摘要",
        "coin_col": "币种",
        "current_price": "价格",
        "total_return": "总收益",
        "annual_vol": "年化波动",
        "sharpe": "夏普比率",
        "max_drawdown": "最大回撤",
        "rows": "行",
        "select_columns": "选择列",
        "download_csv": "下载 CSV",
        "no_data": "暂无数据，请先运行数据管道。",
        "no_coins": "请至少选择一个币种。",
        "dominance": "BTC 占比",
        "hot_crypto": "热门币种",
        "overview": "概览",
        "built_by": "Jason Feng 制作 · 犹他大学",
    },
    "es": {
        "page_title": "Análisis del Mercado Cripto",
        "nav_markets": "Mercados",
        "nav_technical": "Técnico",
        "nav_correlation": "Correlación",
        "nav_data": "Datos",
        "select_coins": "Activos",
        "time_range": "Período",
        "time_all": "Todo",
        "time_30": "30D",
        "time_90": "90D",
        "time_180": "180D",
        "time_365": "1A",
        "price": "Precio",
        "change_24h": "Cambio 24h",
        "volume_24h": "Volumen 24h",
        "market_cap": "Cap. Mercado",
        "rsi": "RSI(14)",
        "price_trend": "Tendencia de Precio",
        "volume": "Volumen",
        "overbought": "Sobrecompra",
        "oversold": "Sobreventa",
        "select_asset": "Seleccionar Activo",
        "return_corr": "Correlación de Retornos",
        "rolling_corr": "Correlación Móvil",
        "window_size": "Ventana (días)",
        "stats_summary": "Estadísticas",
        "coin_col": "Activo",
        "current_price": "Precio",
        "total_return": "Retorno Total",
        "annual_vol": "Vol. Anual",
        "sharpe": "Sharpe",
        "max_drawdown": "Máx. Drawdown",
        "rows": "filas",
        "select_columns": "Columnas",
        "download_csv": "Descargar CSV",
        "no_data": "Sin datos. Ejecute el pipeline primero.",
        "no_coins": "Seleccione al menos un activo.",
        "dominance": "Dominio BTC",
        "hot_crypto": "Cripto Caliente",
        "overview": "Resumen",
        "built_by": "Hecho por Jason Feng · Universidad de Utah",
    },
}


def t(key: str) -> str:
    """Get translated string for current language."""
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


# ============================================================
# Page config & custom CSS
# ============================================================

st.set_page_config(
    page_title="Crypto Market Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# OKX-inspired dark theme CSS
st.markdown("""
<style>
    /* ---- Global ---- */
    .stApp {
        background-color: #121212 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
    }
    header[data-testid="stHeader"] {
        background-color: #121212 !important;
    }

    /* ---- Top navbar ---- */
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #2a2a2a;
        margin-bottom: 24px;
    }
    .top-bar-left {
        display: flex;
        align-items: center;
        gap: 32px;
    }
    .top-bar .brand {
        font-size: 22px;
        font-weight: 700;
        color: #fff;
        letter-spacing: -0.5px;
    }
    .nav-links {
        display: flex;
        gap: 8px;
    }
    .nav-link {
        padding: 6px 16px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        color: #888;
        cursor: pointer;
        text-decoration: none;
        transition: all 0.15s;
        border: none;
        background: transparent;
    }
    .nav-link:hover {
        color: #fff;
        background: #2a2a2a;
    }
    .nav-link.active {
        color: #fff;
        background: #2a2a2a;
    }

    /* ---- Language switcher ---- */
    .lang-switcher {
        display: flex;
        gap: 0;
        background: #1e1e1e;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #2a2a2a;
    }
    .lang-btn {
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 500;
        color: #888;
        border: none;
        background: transparent;
        cursor: pointer;
        transition: all 0.15s;
    }
    .lang-btn:hover { color: #fff; }
    .lang-btn.active {
        color: #fff;
        background: #333;
    }

    /* ---- Metric cards (OKX hot crypto style) ---- */
    .metric-row {
        display: flex;
        gap: 16px;
        margin-bottom: 24px;
    }
    .metric-card {
        flex: 1;
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 20px 24px;
        transition: border-color 0.2s;
    }
    .metric-card:hover {
        border-color: #444;
    }
    .metric-card .coin-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }
    .metric-card .coin-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
    .metric-card .coin-name {
        font-size: 16px;
        font-weight: 600;
        color: #fff;
    }
    .metric-card .coin-pair {
        font-size: 13px;
        color: #666;
        margin-left: 4px;
    }
    .metric-card .price-value {
        font-size: 28px;
        font-weight: 700;
        color: #fff;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    .metric-card .change-pos {
        color: #00b075;
        font-size: 14px;
        font-weight: 600;
    }
    .metric-card .change-neg {
        color: #f6465d;
        font-size: 14px;
        font-weight: 600;
    }
    .metric-card .sub-stats {
        display: flex;
        gap: 20px;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #2a2a2a;
    }
    .metric-card .sub-stat {
        font-size: 12px;
        color: #666;
    }
    .metric-card .sub-stat span {
        color: #aaa;
        font-weight: 500;
    }

    /* ---- Market table (OKX style) ---- */
    .market-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 16px;
    }
    .market-table th {
        text-align: left;
        padding: 12px 16px;
        font-size: 13px;
        font-weight: 500;
        color: #666;
        border-bottom: 1px solid #2a2a2a;
    }
    .market-table td {
        padding: 16px;
        font-size: 14px;
        color: #eee;
        border-bottom: 1px solid #1e1e1e;
    }
    .market-table tr:hover {
        background: #1a1a1a;
    }
    .market-table .price-col {
        font-weight: 600;
        font-size: 15px;
    }

    /* ---- Section headers ---- */
    .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #fff;
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
    }

    /* ---- Tabs (OKX style pill tabs) ---- */
    .pill-tabs {
        display: flex;
        gap: 8px;
        margin-bottom: 20px;
        padding: 4px;
        background: #1a1a1a;
        border-radius: 10px;
        display: inline-flex;
    }
    .pill-tab {
        padding: 8px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        color: #888;
        cursor: pointer;
        transition: all 0.15s;
    }
    .pill-tab.active {
        color: #fff;
        background: #333;
    }

    /* ---- Hide default Streamlit chrome ---- */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ---- Plotly chart container ---- */
    .chart-container {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }

    /* ---- Override Streamlit defaults ---- */
    .stSelectbox label, .stMultiSelect label, .stSlider label {
        color: #888 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    .stDataFrame {
        border: 1px solid #2a2a2a;
        border-radius: 8px;
    }
    div[data-testid="stMetric"] {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 16px;
    }
    div[data-testid="stMetric"] label {
        color: #888 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #fff !important;
    }

    /* ---- Tabs styling ---- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background: #1a1a1a;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        color: #888;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #333 !important;
        color: #fff !important;
    }
    .stTabs [data-baseweb="tab-border"] { display: none; }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# Session state init
# ============================================================

if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "page" not in st.session_state:
    st.session_state.page = "markets"


# ============================================================
# Data loading
# ============================================================

@st.cache_data
def load_indicator_data(coin: str) -> pd.DataFrame:
    filepath = os.path.join(INDICATOR_DATA_DIR, f"{coin.lower()}_indicators.csv")
    if not os.path.exists(filepath):
        return pd.DataFrame()
    return pd.read_csv(filepath, parse_dates=["date"])


@st.cache_data
def load_wide_table() -> pd.DataFrame:
    filepath = os.path.join(CLEANED_DATA_DIR, "wide_table.csv")
    if not os.path.exists(filepath):
        return pd.DataFrame()
    return pd.read_csv(filepath, parse_dates=["date"])


# ============================================================
# Plotly chart theme (consistent OKX-dark look)
# ============================================================

CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#1a1a1a",
    plot_bgcolor="#1a1a1a",
    font=dict(color="#aaa", size=12),
    xaxis=dict(gridcolor="#2a2a2a", showline=False),
    yaxis=dict(gridcolor="#2a2a2a", showline=False),
    margin=dict(l=0, r=0, t=40, b=0),
    hovermode="x unified",
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=11),
    ),
)


def apply_chart_style(fig, height=450):
    fig.update_layout(**CHART_LAYOUT, height=height)
    return fig


# ============================================================
# Helper: time filter
# ============================================================

TIME_KEYS = ["time_all", "time_30", "time_90", "time_180", "time_365"]
TIME_DAYS = {"time_all": None, "time_30": 30, "time_90": 90, "time_180": 180, "time_365": 365}


def filter_by_time(df: pd.DataFrame, time_key: str) -> pd.DataFrame:
    if df.empty or time_key == "time_all":
        return df
    days = TIME_DAYS.get(time_key)
    if days:
        cutoff = df["date"].max() - pd.Timedelta(days=days)
        return df[df["date"] >= cutoff]
    return df


# ============================================================
# Top bar with language switcher
# ============================================================

def render_top_bar():
    c1, c2, c3 = st.columns([6, 2, 2])

    with c1:
        st.markdown(
            '<div style="font-size:22px;font-weight:700;color:#fff;padding:8px 0;">'
            '📊 CryptoScope</div>',
            unsafe_allow_html=True,
        )

    with c3:
        langs = {"en": "EN", "zh": "中文", "es": "ES"}
        cols = st.columns(len(langs))
        for i, (code, label) in enumerate(langs.items()):
            with cols[i]:
                if st.button(
                    label,
                    key=f"lang_{code}",
                    use_container_width=True,
                    type="primary" if st.session_state.lang == code else "secondary",
                ):
                    st.session_state.lang = code
                    st.rerun()


# ============================================================
# Page: Markets (OKX-style overview)
# ============================================================

def render_markets(selected_coins, time_key):
    # --- Metric cards row ---
    cols = st.columns(len(selected_coins))
    for i, coin in enumerate(selected_coins):
        df = load_indicator_data(coin)
        if df.empty:
            with cols[i]:
                st.warning(t("no_data"))
            continue

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        pct = (latest["price"] - prev["price"]) / prev["price"]
        change_class = "change-pos" if pct >= 0 else "change-neg"
        sign = "+" if pct >= 0 else ""
        color = COINS[coin]["color"]

        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="coin-header">
                    <span class="coin-dot" style="background:{color};"></span>
                    <span class="coin-name">{coin}</span>
                    <span class="coin-pair">/ USD</span>
                </div>
                <div class="price-value">${latest["price"]:,.2f}</div>
                <span class="{change_class}">{sign}{pct:.2%}</span>
                <div class="sub-stats">
                    <div class="sub-stat">RSI <span>{latest["rsi_14"]:.1f}</span></div>
                    <div class="sub-stat">{t("volume_24h")} <span>${latest["total_volume"]/1e9:.2f}B</span></div>
                    <div class="sub-stat">{t("market_cap")} <span>${latest["market_cap"]/1e9:.1f}B</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # --- Market table ---
    st.markdown(f'<div class="section-title">{t("hot_crypto")}</div>', unsafe_allow_html=True)

    table_rows = []
    for coin in selected_coins:
        df = load_indicator_data(coin)
        if df.empty:
            continue
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        pct = (latest["price"] - prev["price"]) / prev["price"]

        table_rows.append({
            t("coin_col"): coin,
            "Name": COINS[coin]["name"],
            t("price"): f"${latest['price']:,.2f}",
            t("change_24h"): f"{pct:+.2%}",
            t("volume_24h"): f"${latest['total_volume']/1e9:.2f}B",
            t("market_cap"): f"${latest['market_cap']/1e9:.1f}B",
            t("rsi"): f"{latest['rsi_14']:.1f}",
        })

    if table_rows:
        st.dataframe(
            pd.DataFrame(table_rows),
            use_container_width=True,
            hide_index=True,
        )

    # --- Price chart ---
    st.markdown(f'<div class="section-title">{t("price_trend")}</div>', unsafe_allow_html=True)

    fig = go.Figure()
    for coin in selected_coins:
        df = filter_by_time(load_indicator_data(coin), time_key)
        if df.empty:
            continue
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["price"],
            name=coin,
            line=dict(color=COINS[coin]["color"], width=2),
            hovertemplate="%{y:$,.2f}<extra>" + coin + "</extra>",
        ))

    fig = apply_chart_style(fig, 420)
    fig.update_layout(
        yaxis_title=t("price") + " (USD)",
        yaxis_tickprefix="$",
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Volume chart ---
    st.markdown(f'<div class="section-title">{t("volume")}</div>', unsafe_allow_html=True)

    fig_vol = go.Figure()
    for coin in selected_coins:
        df = filter_by_time(load_indicator_data(coin), time_key)
        if df.empty:
            continue
        fig_vol.add_trace(go.Bar(
            x=df["date"], y=df["total_volume"],
            name=coin,
            marker_color=COINS[coin]["color"],
            opacity=0.7,
            hovertemplate="%{y:$,.0f}<extra>" + coin + "</extra>",
        ))

    fig_vol = apply_chart_style(fig_vol, 300)
    fig_vol.update_layout(barmode="group", yaxis_tickprefix="$")
    st.plotly_chart(fig_vol, use_container_width=True)


# ============================================================
# Page: Technical Analysis
# ============================================================

def render_technical(selected_coins, time_key):
    st.markdown(f'<div class="section-title">{t("nav_technical")}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 4])
    with col1:
        coin = st.selectbox(t("select_asset"), selected_coins, label_visibility="collapsed")

    df = filter_by_time(load_indicator_data(coin), time_key)
    if df.empty:
        st.info(t("no_data"))
        return

    color = COINS[coin]["color"]

    # ---- RSI ----
    fig_rsi = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.65, 0.35], vertical_spacing=0.06,
    )

    fig_rsi.add_trace(go.Candlestick(
        x=df["date"],
        open=df["price"].shift(1).fillna(df["price"]),
        high=df[["price", "sma_7"]].max(axis=1),
        low=df[["price", "sma_7"]].min(axis=1),
        close=df["price"],
        name=t("price"),
        increasing_line_color="#00b075",
        decreasing_line_color="#f6465d",
    ), row=1, col=1)

    fig_rsi.add_trace(go.Scatter(
        x=df["date"], y=df["sma_20"],
        name="SMA(20)", line=dict(color="#888", width=1, dash="dot"),
    ), row=1, col=1)

    fig_rsi.add_trace(go.Scatter(
        x=df["date"], y=df["rsi_14"],
        name="RSI(14)", line=dict(color="#e94560", width=1.5),
    ), row=2, col=1)

    fig_rsi.add_hline(y=70, line_dash="dash", line_color="#f6465d",
                      opacity=0.4, row=2, col=1,
                      annotation_text=t("overbought"),
                      annotation_font_color="#f6465d")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="#00b075",
                      opacity=0.4, row=2, col=1,
                      annotation_text=t("oversold"),
                      annotation_font_color="#00b075")

    fig_rsi.add_hrect(y0=70, y1=100, fillcolor="#f6465d", opacity=0.05, row=2, col=1)
    fig_rsi.add_hrect(y0=0, y1=30, fillcolor="#00b075", opacity=0.05, row=2, col=1)

    fig_rsi = apply_chart_style(fig_rsi, 550)
    fig_rsi.update_layout(title=f"{coin} — {t('price')} & RSI(14)", xaxis_rangeslider_visible=False)
    fig_rsi.update_yaxes(title_text=t("price"), row=1, col=1, tickprefix="$")
    fig_rsi.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
    st.plotly_chart(fig_rsi, use_container_width=True)

    # ---- MACD ----
    fig_macd = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.6, 0.4], vertical_spacing=0.06,
    )

    fig_macd.add_trace(go.Scatter(
        x=df["date"], y=df["price"], name=t("price"),
        line=dict(color=color, width=2),
    ), row=1, col=1)
    fig_macd.add_trace(go.Scatter(
        x=df["date"], y=df["ema_12"], name="EMA(12)",
        line=dict(color="#00b075", width=1, dash="dot"),
    ), row=1, col=1)
    fig_macd.add_trace(go.Scatter(
        x=df["date"], y=df["ema_26"], name="EMA(26)",
        line=dict(color="#f6465d", width=1, dash="dot"),
    ), row=1, col=1)

    fig_macd.add_trace(go.Scatter(
        x=df["date"], y=df["macd_line"], name="MACD",
        line=dict(color="#00d2ff", width=1.5),
    ), row=2, col=1)
    fig_macd.add_trace(go.Scatter(
        x=df["date"], y=df["macd_signal"], name="Signal",
        line=dict(color="#ff6b6b", width=1),
    ), row=2, col=1)

    hist_colors = ["#00b075" if v >= 0 else "#f6465d" for v in df["macd_histogram"]]
    fig_macd.add_trace(go.Bar(
        x=df["date"], y=df["macd_histogram"], name="Histogram",
        marker_color=hist_colors, opacity=0.6,
    ), row=2, col=1)

    fig_macd = apply_chart_style(fig_macd, 550)
    fig_macd.update_layout(title=f"{coin} — MACD (12, 26, 9)")
    fig_macd.update_yaxes(title_text=t("price"), row=1, col=1, tickprefix="$")
    fig_macd.update_yaxes(title_text="MACD", row=2, col=1)
    st.plotly_chart(fig_macd, use_container_width=True)

    # ---- Bollinger Bands ----
    fig_bb = go.Figure()

    fig_bb.add_trace(go.Scatter(
        x=df["date"], y=df["bb_upper"], name="Upper",
        line=dict(color="rgba(98,126,234,0.4)", width=1),
    ))
    fig_bb.add_trace(go.Scatter(
        x=df["date"], y=df["bb_lower"], name="Lower",
        line=dict(color="rgba(98,126,234,0.4)", width=1),
        fill="tonexty", fillcolor="rgba(98,126,234,0.08)",
    ))
    fig_bb.add_trace(go.Scatter(
        x=df["date"], y=df["bb_middle"], name="SMA(20)",
        line=dict(color="#627EEA", width=1, dash="dash"),
    ))
    fig_bb.add_trace(go.Scatter(
        x=df["date"], y=df["price"], name=t("price"),
        line=dict(color=color, width=2),
    ))

    fig_bb = apply_chart_style(fig_bb, 450)
    fig_bb.update_layout(title=f"{coin} — Bollinger Bands (20, 2)")
    fig_bb.update_yaxes(tickprefix="$")
    st.plotly_chart(fig_bb, use_container_width=True)


# ============================================================
# Page: Correlation
# ============================================================

def render_correlation(selected_coins, time_key):
    st.markdown(f'<div class="section-title">{t("nav_correlation")}</div>', unsafe_allow_html=True)

    wide = filter_by_time(load_wide_table(), time_key)
    if wide.empty:
        st.info(t("no_data"))
        return

    return_cols = [c for c in wide.columns if c.endswith("_return")]
    price_cols = [c for c in wide.columns if c.endswith("_price")]

    # ---- Correlation heatmap ----
    st.markdown(f'<div class="section-title">{t("return_corr")}</div>', unsafe_allow_html=True)

    if return_cols:
        corr = wide[return_cols].dropna().corr()
        labels = [c.replace("_return", "") for c in corr.index]

        fig_heat = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=labels, y=labels,
            colorscale=[[0, "#f6465d"], [0.5, "#1a1a1a"], [1, "#00b075"]],
            zmin=-1, zmax=1,
            text=np.round(corr.values, 3),
            texttemplate="%{text}",
            textfont=dict(size=16, color="#fff"),
        ))
        fig_heat = apply_chart_style(fig_heat, 380)
        fig_heat.update_layout(xaxis_side="bottom")
        st.plotly_chart(fig_heat, use_container_width=True)

    # ---- Rolling correlation ----
    st.markdown(f'<div class="section-title">{t("rolling_corr")}</div>', unsafe_allow_html=True)
    window = st.slider(t("window_size"), 7, 90, 30)

    fig_roll = go.Figure()
    pair_colors = ["#F7931A", "#627EEA", "#9945FF"]
    return_filtered = [c for c in return_cols if c.replace("_return", "") in selected_coins]
    idx = 0
    for i in range(len(return_filtered)):
        for j in range(i + 1, len(return_filtered)):
            col1, col2 = return_filtered[i], return_filtered[j]
            n1, n2 = col1.replace("_return", ""), col2.replace("_return", "")
            rc = wide[col1].rolling(window).corr(wide[col2])
            fig_roll.add_trace(go.Scatter(
                x=wide["date"], y=rc,
                name=f"{n1} / {n2}",
                line=dict(width=2, color=pair_colors[idx % len(pair_colors)]),
            ))
            idx += 1

    fig_roll.add_hline(y=0, line_dash="dash", line_color="#444", opacity=0.5)
    fig_roll = apply_chart_style(fig_roll, 380)
    fig_roll.update_layout(yaxis_range=[-1, 1], yaxis_title="Correlation")
    st.plotly_chart(fig_roll, use_container_width=True)

    # ---- Stats table ----
    st.markdown(f'<div class="section-title">{t("stats_summary")}</div>', unsafe_allow_html=True)

    stats = []
    for pcol in sorted(price_cols):
        rcol = pcol.replace("_price", "_return")
        if rcol not in wide.columns:
            continue
        name = pcol.replace("_price", "")
        prices = wide[pcol].dropna()
        returns = wide[rcol].dropna()
        if len(prices) < 2:
            continue

        total_ret = prices.iloc[-1] / prices.iloc[0] - 1
        ann_vol = returns.std() * np.sqrt(365)
        sharpe = ((returns.mean() - 0.045 / 365) / returns.std() * np.sqrt(365)
                  if returns.std() > 0 else 0)
        max_dd = ((prices - prices.cummax()) / prices.cummax()).min()

        stats.append({
            t("coin_col"): name,
            t("current_price"): f"${prices.iloc[-1]:,.2f}",
            t("total_return"): f"{total_ret:+.2%}",
            t("annual_vol"): f"{ann_vol:.2%}",
            t("sharpe"): f"{sharpe:.3f}",
            t("max_drawdown"): f"{max_dd:.2%}",
        })

    if stats:
        st.dataframe(pd.DataFrame(stats), use_container_width=True, hide_index=True)


# ============================================================
# Page: Data
# ============================================================

def render_data(selected_coins, time_key):
    st.markdown(f'<div class="section-title">{t("nav_data")}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 4])
    with col1:
        coin = st.selectbox(t("select_asset"), selected_coins,
                            key="data_coin", label_visibility="collapsed")

    df = filter_by_time(load_indicator_data(coin), time_key)
    if df.empty:
        st.info(t("no_data"))
        return

    st.caption(f"{coin} — {len(df)} {t('rows')}")

    default_cols = ["date", "price", "total_volume", "daily_return",
                    "rsi_14", "macd_line", "bb_upper", "bb_lower"]
    show_cols = st.multiselect(
        t("select_columns"),
        df.columns.tolist(),
        default=[c for c in default_cols if c in df.columns],
    )

    if show_cols:
        display_df = df[show_cols].copy()
        display_df = display_df.sort_values("date", ascending=False) if "date" in show_cols else display_df
        st.dataframe(display_df.head(200), use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False)
    st.download_button(
        label=f"⬇ {t('download_csv')} — {coin}",
        data=csv,
        file_name=f"{coin.lower()}_data.csv",
        mime="text/csv",
    )


# ============================================================
# Main
# ============================================================

def main():
    render_top_bar()

    # Navigation tabs + controls in one row
    tab_labels = [t("nav_markets"), t("nav_technical"), t("nav_correlation"), t("nav_data")]
    tabs = st.tabs(tab_labels)

    # Sidebar-style controls (inline)
    with st.sidebar:
        st.markdown(f"### {t('select_coins')}")
        selected = st.multiselect(
            t("select_coins"), list(COINS.keys()),
            default=list(COINS.keys()),
            label_visibility="collapsed",
        )
        st.markdown(f"### {t('time_range')}")
        time_options = {t(k): k for k in TIME_KEYS}
        time_label = st.radio(
            t("time_range"),
            list(time_options.keys()),
            horizontal=True,
            label_visibility="collapsed",
        )
        time_key = time_options[time_label]

        st.markdown("---")
        st.caption(t("built_by"))

    if not selected:
        st.warning(t("no_coins"))
        return

    with tabs[0]:
        render_markets(selected, time_key)
    with tabs[1]:
        render_technical(selected, time_key)
    with tabs[2]:
        render_correlation(selected, time_key)
    with tabs[3]:
        render_data(selected, time_key)


if __name__ == "__main__":
    main()
