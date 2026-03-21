/**
 * sentiment.js — Market sentiment scoring engine
 *
 * Derives a 0–100 "Fear & Greed" style score from:
 *   - Average RSI across tracked coins
 *   - Average 24h price change
 *
 * Score mapping:
 *   0–30  → Fear    (red)
 *   30–70 → Neutral (yellow)
 *   70–100 → Greed  (green)
 */

/**
 * Compute sentiment score from an array of coin snapshots.
 *
 * @param {Array<{rsi: number, change24h: number}>} coins
 * @returns {{ score: number, label: string, color: string }}
 */
export function computeSentiment(coins) {
  if (!coins || coins.length === 0) {
    return { score: 50, label: "neutral", color: "#fcd535" };
  }

  // ---- Component 1: RSI contribution (0–100) ----
  // Average RSI directly maps to 0–100 range
  const avgRSI =
    coins.reduce((sum, c) => sum + (c.rsi ?? 50), 0) / coins.length;

  // ---- Component 2: Price change contribution (0–100) ----
  // Map average 24h change from [-10%, +10%] → [0, 100]
  const avgChange =
    coins.reduce((sum, c) => sum + (c.change24h ?? 0), 0) / coins.length;
  const changeScore = Math.min(100, Math.max(0, (avgChange + 0.1) * 500));

  // ---- Weighted combination ----
  // RSI is more reliable, so give it 60% weight
  const score = Math.round(avgRSI * 0.6 + changeScore * 0.4);
  const clamped = Math.min(100, Math.max(0, score));

  return {
    score: clamped,
    ...getLabel(clamped),
  };
}

function getLabel(score) {
  if (score < 30) {
    return { label: "fear", color: "#f6465d" };
  }
  if (score < 70) {
    return { label: "neutral", color: "#fcd535" };
  }
  return { label: "greed", color: "#00b075" };
}

/**
 * Get a descriptive gauge position for the sentiment dial.
 * Returns a rotation angle (-90 to +90 degrees).
 */
export function sentimentAngle(score) {
  return ((score / 100) * 180) - 90;
}
