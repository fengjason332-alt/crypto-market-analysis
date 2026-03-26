/**
 * IndicatorInfo — Expandable indicator explanation
 *
 * Shows a small "+" button next to an indicator name.
 * Click to expand a brief explanation panel.
 * Click again (or click "-") to collapse.
 *
 * Props:
 *   indicatorKey — string key to look up the explanation (e.g. "rsi", "macd")
 */

import { useState } from "react";

const INDICATOR_EXPLANATIONS = {
  sma: {
    name: "SMA — Simple Moving Average",
    short: "Average closing price over the past N days.",
    detail:
      "SMA smooths out daily price fluctuations to reveal the underlying trend. When price is above the SMA, the trend is generally up; when below, the trend is generally down. A shorter SMA (like 20-day) reacts faster to price changes, while a longer SMA (like 50-day) shows the bigger picture. When the short-term SMA crosses above the long-term SMA, it's called a 'golden cross' (bullish signal).",
  },
  rsi: {
    name: "RSI — Relative Strength Index",
    short: "Measures momentum on a 0–100 scale.",
    detail:
      "RSI compares the magnitude of recent gains to recent losses over a 14-day period. Above 70 is considered 'overbought' — the price may have risen too fast and could pull back. Below 30 is 'oversold' — the price may have dropped too far and could bounce. Think of it like a spring: the more stretched it gets, the more likely it snaps back.",
  },
  macd: {
    name: "MACD — Moving Average Convergence Divergence",
    short: "Tracks the gap between fast and slow moving averages to gauge momentum.",
    detail:
      "MACD is calculated as EMA(12) minus EMA(26). When the fast average pulls ahead of the slow average, MACD goes positive — momentum is building upward. The Signal line (EMA of MACD itself) acts as a trigger: when MACD crosses above Signal, that's a bullish signal; below is bearish. The Histogram bars show the distance between MACD and Signal — growing bars mean accelerating momentum.",
  },
  bollinger: {
    name: "Bollinger Bands",
    short: "A price channel built from SMA ± 2 standard deviations.",
    detail:
      "The middle band is the 20-day SMA. The upper and lower bands are 2 standard deviations above and below. About 95% of the time, price stays inside the bands. When price touches the upper band, it may be overextended; touching the lower band suggests it may be oversold. When the bands squeeze tight (narrow), it often means a big move is coming — like the calm before a storm.",
  },
};

export default function IndicatorInfo({ indicatorKey }) {
  const [expanded, setExpanded] = useState(false);

  const info = INDICATOR_EXPLANATIONS[indicatorKey];
  if (!info) return null;

  return (
    <span style={{ position: "relative", display: "inline-flex", alignItems: "center" }}>
      {/* Toggle button */}
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          marginLeft: "8px",
          width: "20px",
          height: "20px",
          borderRadius: "50%",
          border: "1px solid #2b2f36",
          background: expanded ? "#22262e" : "transparent",
          color: expanded ? "#eaecef" : "#5e6673",
          fontSize: "13px",
          fontWeight: 600,
          cursor: "pointer",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          transition: "all 0.15s",
          fontFamily: "inherit",
          lineHeight: 1,
          padding: 0,
          flexShrink: 0,
        }}
        title={expanded ? "Hide explanation" : "What is this?"}
      >
        {expanded ? "−" : "+"}
      </button>

      {/* Explanation panel */}
      {expanded && (
        <div
          style={{
            position: "absolute",
            top: "calc(100% + 8px)",
            left: 0,
            zIndex: 30,
            width: "340px",
            background: "#1a1d23",
            border: "1px solid #2b2f36",
            borderRadius: "10px",
            padding: "14px 16px",
            boxShadow: "0 12px 40px rgba(0,0,0,0.4)",
          }}
        >
          {/* Header */}
          <div
            style={{
              fontSize: "13px",
              fontWeight: 600,
              color: "#eaecef",
              marginBottom: "6px",
            }}
          >
            {info.name}
          </div>

          {/* Short description */}
          <div
            style={{
              fontSize: "12px",
              color: "#F7931A",
              marginBottom: "8px",
              fontWeight: 500,
            }}
          >
            {info.short}
          </div>

          {/* Detailed explanation */}
          <div
            style={{
              fontSize: "12px",
              color: "#848e9c",
              lineHeight: 1.7,
            }}
          >
            {info.detail}
          </div>

          {/* Close hint */}
          <div
            style={{
              fontSize: "11px",
              color: "#5e6673",
              marginTop: "10px",
              paddingTop: "8px",
              borderTop: "1px solid #2b2f36",
              textAlign: "right",
            }}
          >
            Click + again to close
          </div>
        </div>
      )}
    </span>
  );
}
