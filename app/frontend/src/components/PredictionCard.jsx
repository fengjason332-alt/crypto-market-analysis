/**
 * PredictionCard — AI direction forecast display
 *
 * Shows a probabilistic 24h price direction prediction
 * with confidence level and visual indicator.
 *
 * Visually distinct from AIInsightCard: uses a gradient
 * background and larger typography for the prediction.
 */

import { ArrowUpRight, ArrowDownRight, Shield } from "lucide-react";
import { useLanguage } from "../hooks/useLanguage";
import { predictDirection } from "../utils/predictions";

const CONFIDENCE_COLORS = {
  high: "text-accent-green",
  medium: "text-accent-yellow",
  low: "text-text-muted",
};

export default function PredictionCard({ symbol, snapshot, color }) {
  const { t } = useLanguage();

  if (!snapshot) return null;

  const prediction = predictDirection({
    rsi: snapshot.rsi,
    price: snapshot.price,
    sma20: snapshot.sma20,
    macdHistogram: snapshot.macdHistogram,
    dailyReturn: snapshot.dailyReturn,
  });

  const isUp = prediction.direction === "up";
  const Arrow = isUp ? ArrowUpRight : ArrowDownRight;
  const dirColor = isUp ? "#00b075" : "#f6465d";
  const bgGradient = isUp
    ? "from-accent-green/5 to-transparent"
    : "from-accent-red/5 to-transparent";

  return (
    <div className={`card bg-gradient-to-br ${bgGradient} border-bg-border`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <span className="text-base">🔮</span>
          <span className="text-sm font-semibold text-text-primary">
            {symbol} — {t("insights.next_24h")}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <Shield size={13} className={CONFIDENCE_COLORS[prediction.confidence]} />
          <span className={`text-xs font-medium ${CONFIDENCE_COLORS[prediction.confidence]}`}>
            {prediction.confidence.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Main prediction display */}
      <div className="flex items-center gap-4 mb-4">
        <div
          className="w-14 h-14 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: `${dirColor}15` }}
        >
          <Arrow size={28} style={{ color: dirColor }} />
        </div>
        <div>
          <div className="text-3xl font-bold tracking-tight" style={{ color: dirColor }}>
            {prediction.probability}%
          </div>
          <div className="text-xs text-text-muted mt-0.5">
            {t("insights.probability")}
          </div>
        </div>
      </div>

      {/* Probability bar */}
      <div className="relative h-2 bg-bg-border rounded-full overflow-hidden">
        <div
          className="absolute top-0 left-0 h-full rounded-full transition-all duration-700"
          style={{
            width: `${prediction.probability}%`,
            backgroundColor: dirColor,
          }}
        />
      </div>

      {/* Footer note */}
      <p className="text-xs text-text-muted mt-3 leading-relaxed">
        Based on RSI, SMA, MACD momentum analysis. Not financial advice.
      </p>
    </div>
  );
}
