/**
 * predictions.js — Heuristic-based price direction forecasting
 *
 * Uses a combination of technical signals to produce a
 * probabilistic forecast for the next 24 hours.
 *
 * This is rule-based (NOT real ML). Structure is ready to
 * swap in an actual model endpoint later.
 *
 * Factors considered:
 *   1. RSI trend      — rising RSI = bullish momentum
 *   2. Price vs SMA   — above SMA = uptrend
 *   3. MACD histogram — positive = bullish momentum
 *   4. Recent returns  — positive streak = momentum
 */

/**
 * Generate a 24h price direction prediction.
 *
 * @param {Object} coinData - Latest indicator snapshot
 * @param {number} coinData.rsi
 * @param {number} coinData.price
 * @param {number} coinData.sma20
 * @param {number} coinData.macdHistogram
 * @param {number} coinData.dailyReturn
 * @returns {{ direction: "up"|"down", probability: number, confidence: "high"|"medium"|"low" }}
 */
export function predictDirection(coinData) {
  if (!coinData) {
    return { direction: "up", probability: 50, confidence: "low" };
  }

  const { rsi, price, sma20, macdHistogram, dailyReturn } = coinData;
  let bullishPoints = 0;
  let totalPoints = 0;

  // Factor 1: RSI position (weight: 2)
  if (rsi != null) {
    totalPoints += 2;
    if (rsi < 30) bullishPoints += 2;        // oversold → likely bounce
    else if (rsi < 50) bullishPoints += 1;    // below midline
    else if (rsi < 70) bullishPoints += 1.5;  // above midline, healthy
    // rsi > 70 → overbought, 0 bullish points
  }

  // Factor 2: Price vs SMA20 (weight: 2)
  if (price != null && sma20 != null) {
    totalPoints += 2;
    if (price > sma20) bullishPoints += 2;
    else if (price > sma20 * 0.98) bullishPoints += 1; // close to SMA
  }

  // Factor 3: MACD histogram (weight: 1.5)
  if (macdHistogram != null) {
    totalPoints += 1.5;
    if (macdHistogram > 0) bullishPoints += 1.5;
    else if (macdHistogram > -100) bullishPoints += 0.5;
  }

  // Factor 4: Recent return (weight: 1)
  if (dailyReturn != null) {
    totalPoints += 1;
    if (dailyReturn > 0) bullishPoints += 1;
    else if (dailyReturn > -0.02) bullishPoints += 0.3;
  }

  // Calculate probability
  const rawProb = totalPoints > 0 ? (bullishPoints / totalPoints) * 100 : 50;

  // Add some noise to avoid looking artificially precise
  const noise = (Math.sin(Date.now() / 100000) * 3);
  const probability = Math.round(Math.min(95, Math.max(5, rawProb + noise)));

  const direction = probability >= 50 ? "up" : "down";
  const displayProb = direction === "up" ? probability : 100 - probability;

  // Confidence based on how far from 50%
  const spread = Math.abs(probability - 50);
  let confidence;
  if (spread > 25) confidence = "high";
  else if (spread > 10) confidence = "medium";
  else confidence = "low";

  return { direction, probability: displayProb, confidence };
}
