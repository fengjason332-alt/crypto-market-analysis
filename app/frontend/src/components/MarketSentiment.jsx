/**
 * MarketSentiment — Fear & Greed gauge
 *
 * Displays a semicircular gauge showing overall market mood
 * derived from RSI and price changes across all tracked coins.
 */

import { useLanguage } from "../hooks/useLanguage";
import { computeSentiment, sentimentAngle } from "../utils/sentiment";

export default function MarketSentiment({ snapshots }) {
  const { t } = useLanguage();
  const sentiment = computeSentiment(
    snapshots.map((s) => ({ rsi: s.rsi, change24h: s.change24h }))
  );

  const angle = sentimentAngle(sentiment.score);

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-primary mb-5 flex items-center gap-2">
        <span>🎭</span>
        {t("insights.sentiment")}
      </h3>

      {/* Gauge */}
      <div className="flex justify-center mb-4">
        <div className="relative w-48 h-24">
          {/* Background arc */}
          <svg viewBox="0 0 200 100" className="w-full h-full">
            {/* Track */}
            <path
              d="M 10 95 A 90 90 0 0 1 190 95"
              fill="none"
              stroke="#2b2f36"
              strokeWidth="12"
              strokeLinecap="round"
            />
            {/* Colored segments */}
            <path
              d="M 10 95 A 90 90 0 0 1 70 15"
              fill="none"
              stroke="#f6465d"
              strokeWidth="12"
              strokeLinecap="round"
              opacity="0.6"
            />
            <path
              d="M 70 15 A 90 90 0 0 1 130 15"
              fill="none"
              stroke="#fcd535"
              strokeWidth="12"
              strokeLinecap="round"
              opacity="0.6"
            />
            <path
              d="M 130 15 A 90 90 0 0 1 190 95"
              fill="none"
              stroke="#00b075"
              strokeWidth="12"
              strokeLinecap="round"
              opacity="0.6"
            />
          </svg>

          {/* Needle */}
          <div
            className="absolute bottom-0 left-1/2 origin-bottom"
            style={{
              transform: `translateX(-50%) rotate(${angle}deg)`,
              transition: "transform 0.8s cubic-bezier(0.4, 0, 0.2, 1)",
            }}
          >
            <div className="w-0.5 h-16 bg-text-primary rounded-full mx-auto" />
            <div className="w-3 h-3 bg-text-primary rounded-full -mt-0.5 mx-auto" />
          </div>

          {/* Score text */}
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-2 text-center">
            <div className="text-3xl font-bold" style={{ color: sentiment.color }}>
              {sentiment.score}
            </div>
          </div>
        </div>
      </div>

      {/* Label */}
      <div className="text-center">
        <span
          className="text-sm font-semibold uppercase tracking-wider"
          style={{ color: sentiment.color }}
        >
          {t(`insights.${sentiment.label}`)}
        </span>
      </div>

      {/* Legend */}
      <div className="flex justify-between mt-4 pt-3 border-t border-bg-border text-xs text-text-muted">
        <span>{t("insights.fear")} (0)</span>
        <span>{t("insights.neutral")} (50)</span>
        <span>{t("insights.greed")} (100)</span>
      </div>
    </div>
  );
}
