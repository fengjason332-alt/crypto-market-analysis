/**
 * InsightsPage — AI-powered insights hub
 *
 * Combines all intelligence modules:
 *   - Market Sentiment gauge
 *   - AI Signals per coin
 *   - AI Predictions per coin
 *   - On-chain data per coin
 */

import { useState } from "react";
import { useLanguage } from "../hooks/useLanguage";
import { useMarketData } from "../hooks/useMarketData";
import MarketSentiment from "../components/MarketSentiment";
import AIInsightCard from "../components/AIInsightCard";
import PredictionCard from "../components/PredictionCard";
import OnChainPanel from "../components/OnChainPanel";

export default function InsightsPage({ selectedCoins }) {
  const { t } = useLanguage();
  const { snapshots, getOnChain, coinMeta } = useMarketData(selectedCoins);
  const [activeCoin, setActiveCoin] = useState(selectedCoins[0] || "BTC");

  const activeSnapshot = snapshots.find((s) => s.symbol === activeCoin);
  const activeOnChain = getOnChain(activeCoin);

  return (
    <div>
      {/* Top row: Sentiment + coin selector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Sentiment gauge */}
        <MarketSentiment snapshots={snapshots} />

        {/* Quick signal overview for all coins */}
        <div className="lg:col-span-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {snapshots.slice(0, 2).map((snap) => (
              <AIInsightCard
                key={snap.symbol}
                symbol={snap.symbol}
                snapshot={snap}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Coin selector for detailed view */}
      <div className="flex items-center gap-2 mb-6">
        <span className="text-sm text-text-muted mr-2">Deep dive:</span>
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

      {/* Detail row: Prediction + On-chain */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <PredictionCard
          symbol={activeCoin}
          snapshot={activeSnapshot}
          color={coinMeta[activeCoin]?.color}
        />
        <AIInsightCard symbol={activeCoin} snapshot={activeSnapshot} />
      </div>

      {/* On-chain section */}
      <OnChainPanel symbol={activeCoin} onchainData={activeOnChain} />
    </div>
  );
}
