/**
 * TechnicalPage — Technical analysis charts
 *
 * Shows RSI, MACD, Bollinger Bands for a selected coin.
 */

import { useState } from "react";
import { useLanguage } from "../hooks/useLanguage";
import { useMarketData } from "../hooks/useMarketData";
import PriceChart from "../components/PriceChart";
import IndicatorInfo from "../components/IndicatorInfo";

export default function TechnicalPage({ selectedCoins, timeDays }) {
  const { t } = useLanguage();
  const { getHistory, coinMeta } = useMarketData(selectedCoins);
  const [activeCoin, setActiveCoin] = useState(selectedCoins[0] || "BTC");

  const history = getHistory(activeCoin, timeDays);
  const color = coinMeta[activeCoin]?.color || "#fff";

  return (
    <div>
      {/* Coin selector */}
      <div className="flex items-center gap-2 mb-6">
        {selectedCoins.map((coin) => (
          <button
            key={coin}
            onClick={() => setActiveCoin(coin)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
              ${
                activeCoin === coin
                  ? "bg-bg-hover text-text-primary border border-bg-border"
                  : "text-text-muted hover:text-text-secondary"
              }`}
          >
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: coinMeta[coin]?.color }}
            />
            {coin}
          </button>
        ))}
      </div>

      {/* Price + SMA */}
      <h3 className="section-title" style={{ position: "relative" }}>
        {activeCoin} — Price & Moving Averages
        <IndicatorInfo indicatorKey="sma" />
      </h3>
      <PriceChart
        data={history}
        lines={[
          { key: "price", color, width: 2, name: "Price" },
          { key: "sma20", color: "#848e9c", width: 1, dash: true, name: "SMA(20)" },
          { key: "sma50", color: "#5e6673", width: 1, dash: true, name: "SMA(50)" },
        ]}
        height={380}
      />

      {/* RSI */}
      <h3 className="section-title mt-8" style={{ position: "relative" }}>
        {activeCoin} — RSI (14)
        <IndicatorInfo indicatorKey="rsi" />
      </h3>
      <PriceChart
        data={history}
        lines={[{ key: "rsi", color: "#e94560", width: 1.5, name: "RSI(14)" }]}
        referenceLines={[
          { y: 70, color: "#f6465d", label: t("technical.overbought"), dash: true },
          { y: 30, color: "#00b075", label: t("technical.oversold"), dash: true },
          { y: 50, color: "#2b2f36", dash: true },
        ]}
        yDomain={[0, 100]}
        height={280}
        formatY={(v) => v}
      />

      {/* MACD */}
      <h3 className="section-title mt-8" style={{ position: "relative" }}>
        {activeCoin} — MACD (12, 26, 9)
        <IndicatorInfo indicatorKey="macd" />
      </h3>
      <PriceChart
        data={history.map((d) => ({
          ...d,
          // Color the histogram visually
          macdHistPositive: d.macdHistogram >= 0 ? d.macdHistogram : 0,
          macdHistNegative: d.macdHistogram < 0 ? d.macdHistogram : 0,
        }))}
        lines={[
          { key: "macdLine", color: "#00d2ff", width: 1.5, name: "MACD" },
          { key: "macdSignal", color: "#ff6b6b", width: 1, name: "Signal" },
        ]}
        referenceLines={[{ y: 0, color: "#2b2f36" }]}
        height={280}
        formatY={(v) => v.toFixed(0)}
      />

      {/* Bollinger Bands */}
      <h3 className="section-title mt-8" style={{ position: "relative" }}>
        {activeCoin} — Bollinger Bands (20, 2)
        <IndicatorInfo indicatorKey="bollinger" />
      </h3>
      <PriceChart
        data={history}
        lines={[
          { key: "price", color, width: 2, name: "Price" },
          { key: "bbMiddle", color: "#627EEA", width: 1, dash: true, name: "SMA(20)" },
        ]}
        areas={[
          { key: "bbUpper", color: "#627EEA", opacity: 0.05 },
          { key: "bbLower", color: "#627EEA", opacity: 0.05 },
        ]}
        height={380}
      />
    </div>
  );
}
