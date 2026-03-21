/**
 * App.jsx — Root component
 *
 * Composes: TopBar → active page → sidebar controls.
 * Manages global state: selected coins, time range, active tab.
 */

import { useState } from "react";
import TopBar from "./components/Layout/TopBar";
import MarketsPage from "./pages/MarketsPage";
import TechnicalPage from "./pages/TechnicalPage";
import InsightsPage from "./pages/InsightsPage";
import DataPage from "./pages/DataPage";
import WatchlistPanel from "./components/WatchlistPanel";
import { useLanguage } from "./hooks/useLanguage";

const TIME_OPTIONS = [
  { key: "all", days: null },
  { key: "30d", days: 30 },
  { key: "90d", days: 90 },
  { key: "180d", days: 180 },
  { key: "1y", days: 365 },
];

const AVAILABLE_COINS = ["BTC", "ETH", "SOL"];

export default function App() {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState("markets");
  const [selectedCoins, setSelectedCoins] = useState(["BTC", "ETH", "SOL"]);
  const [timeKey, setTimeKey] = useState("all");

  const timeDays = TIME_OPTIONS.find((o) => o.key === timeKey)?.days || null;

  const toggleCoin = (coin) => {
    setSelectedCoins((prev) =>
      prev.includes(coin)
        ? prev.filter((c) => c !== coin)
        : [...prev, coin]
    );
  };

  return (
    <div className="min-h-screen bg-bg-primary">
      <TopBar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Sub-controls bar */}
      <div className="max-w-[1400px] mx-auto px-6 py-4 flex items-center justify-between">
        {/* Coin toggles */}
        <div className="flex items-center gap-1.5">
          <span className="text-xs text-text-muted mr-2">{t("common.assets")}:</span>
          {AVAILABLE_COINS.map((coin) => (
            <button
              key={coin}
              onClick={() => toggleCoin(coin)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all
                ${
                  selectedCoins.includes(coin)
                    ? "bg-bg-hover text-text-primary border border-bg-border"
                    : "text-text-muted hover:text-text-secondary"
                }`}
            >
              {coin}
            </button>
          ))}
        </div>

        {/* Time range */}
        <div className="flex items-center gap-1 bg-bg-card rounded-lg p-1">
          {TIME_OPTIONS.map(({ key }) => (
            <button
              key={key}
              onClick={() => setTimeKey(key)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all
                ${
                  timeKey === key
                    ? "bg-bg-hover text-text-primary"
                    : "text-text-muted hover:text-text-secondary"
                }`}
            >
              {t(`time.${key}`)}
            </button>
          ))}
        </div>
      </div>

      {/* Main content */}
      <main className="max-w-[1400px] mx-auto px-6 pb-16">
        {selectedCoins.length === 0 ? (
          <div className="card text-center text-text-muted py-16">
            {t("markets.no_data")}
          </div>
        ) : (
          <>
            {activeTab === "markets" && (
              <MarketsPage selectedCoins={selectedCoins} timeDays={timeDays} />
            )}
            {activeTab === "technical" && (
              <TechnicalPage selectedCoins={selectedCoins} timeDays={timeDays} />
            )}
            {activeTab === "insights" && (
              <InsightsPage selectedCoins={selectedCoins} />
            )}
            {activeTab === "watchlist" && <WatchlistPanel />}
            {activeTab === "data" && (
              <DataPage selectedCoins={selectedCoins} timeDays={timeDays} />
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center text-xs text-text-muted py-8 border-t border-bg-border">
        CryptoScope · Built by Jason Feng · University of Utah · 2026
      </footer>
    </div>
  );
}
