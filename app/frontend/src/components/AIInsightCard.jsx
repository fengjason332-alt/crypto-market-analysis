/**
 * AIInsightCard — Actionable trading signal display
 *
 * Turns raw indicators into human-readable insights with
 * color-coded direction badges (Bullish / Bearish / Neutral).
 *
 * Props:
 *   symbol   — e.g. "BTC"
 *   snapshot — latest coin data with indicators
 */

import { TrendingUp, TrendingDown, Minus, Zap } from "lucide-react";
import { useLanguage } from "../hooks/useLanguage";
import { generateSignals, overallDirection } from "../utils/signals";

const DIRECTION_CONFIG = {
  bullish: {
    badge: "badge-green",
    Icon: TrendingUp,
    bg: "bg-accent-green/5",
    border: "border-accent-green/20",
  },
  bearish: {
    badge: "badge-red",
    Icon: TrendingDown,
    bg: "bg-accent-red/5",
    border: "border-accent-red/20",
  },
  neutral: {
    badge: "badge-yellow",
    Icon: Minus,
    bg: "bg-accent-yellow/5",
    border: "border-accent-yellow/20",
  },
};

export default function AIInsightCard({ symbol, snapshot }) {
  const { t } = useLanguage();

  if (!snapshot) return null;

  const signals = generateSignals({
    rsi: snapshot.rsi,
    price: snapshot.price,
    sma20: snapshot.sma20,
    macdLine: snapshot.macdLine,
    macdSignal: snapshot.macdSignal,
  });

  const direction = overallDirection(signals);
  const config = DIRECTION_CONFIG[direction];

  return (
    <div className={`card ${config.bg} border ${config.border}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Zap size={16} className="text-accent-yellow" />
          <span className="text-sm font-semibold text-text-primary">
            {symbol} — {t("insights.signals")}
          </span>
        </div>
        <span className={config.badge}>
          <config.Icon size={12} />
          {t(`insights.${direction}`)}
        </span>
      </div>

      {/* Signal list */}
      <div className="space-y-3">
        {signals.map((signal, i) => {
          const sConfig = DIRECTION_CONFIG[signal.direction];
          return (
            <div key={i} className="flex items-start gap-3">
              <div
                className={`mt-0.5 w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0
                  ${signal.direction === "bullish" ? "bg-accent-green/15" : ""}
                  ${signal.direction === "bearish" ? "bg-accent-red/15" : ""}
                  ${signal.direction === "neutral" ? "bg-accent-yellow/15" : ""}
                `}
              >
                <sConfig.Icon
                  size={13}
                  className={`
                    ${signal.direction === "bullish" ? "text-accent-green" : ""}
                    ${signal.direction === "bearish" ? "text-accent-red" : ""}
                    ${signal.direction === "neutral" ? "text-accent-yellow" : ""}
                  `}
                />
              </div>
              <div>
                <span className="text-xs font-medium text-text-muted uppercase tracking-wide">
                  {signal.type}
                </span>
                <p className="text-sm text-text-secondary mt-0.5">
                  {t(signal.key)}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
