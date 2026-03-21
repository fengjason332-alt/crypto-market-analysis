/**
 * signals.js — Rule-based trading signal engine
 *
 * Generates actionable signals from technical indicators.
 * Returns an array of signal objects for each coin.
 *
 * Each signal: { type, direction, key, priority }
 *   type:      "rsi" | "trend" | "macd"
 *   direction: "bullish" | "bearish" | "neutral"
 *   key:       i18n key for the explanation text
 *   priority:  1 (high) to 3 (low) — for sorting
 */

export function generateSignals(coinData) {
  if (!coinData) return [];

  const { rsi, price, sma20, macdLine, macdSignal } = coinData;
  const signals = [];

  // ---- RSI signals ----
  if (rsi != null) {
    if (rsi < 30) {
      signals.push({
        type: "rsi",
        direction: "bullish",
        key: "insights.signal_oversold_buy",
        priority: 1,
      });
    } else if (rsi > 70) {
      signals.push({
        type: "rsi",
        direction: "bearish",
        key: "insights.signal_overbought_sell",
        priority: 1,
      });
    }
  }

  // ---- Trend signals (Price vs SMA20) ----
  if (price != null && sma20 != null) {
    if (price < sma20) {
      signals.push({
        type: "trend",
        direction: "bearish",
        key: "insights.signal_downtrend",
        priority: 2,
      });
    } else {
      signals.push({
        type: "trend",
        direction: "bullish",
        key: "insights.signal_uptrend",
        priority: 2,
      });
    }
  }

  // ---- MACD signals ----
  if (macdLine != null && macdSignal != null) {
    if (macdLine > macdSignal) {
      signals.push({
        type: "macd",
        direction: "bullish",
        key: "insights.signal_macd_bullish",
        priority: 2,
      });
    } else {
      signals.push({
        type: "macd",
        direction: "bearish",
        key: "insights.signal_macd_bearish",
        priority: 2,
      });
    }
  }

  // If no signals generated, add neutral
  if (signals.length === 0) {
    signals.push({
      type: "neutral",
      direction: "neutral",
      key: "insights.signal_neutral",
      priority: 3,
    });
  }

  return signals.sort((a, b) => a.priority - b.priority);
}

/**
 * Compute an overall direction from multiple signals.
 * Simple majority vote weighted by priority.
 */
export function overallDirection(signals) {
  if (!signals.length) return "neutral";

  let score = 0;
  for (const s of signals) {
    const weight = 4 - s.priority; // priority 1 → weight 3
    if (s.direction === "bullish") score += weight;
    else if (s.direction === "bearish") score -= weight;
  }

  if (score >= 2) return "bullish";
  if (score <= -2) return "bearish";
  return "neutral";
}
