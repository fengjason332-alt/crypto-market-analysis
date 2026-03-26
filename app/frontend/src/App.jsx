/**
 * App.jsx — Root component (vertical scroll layout)
 *
 * Layout: Hero → Markets → Technical → Insights → Watchlist → Data
 * All sections render on one page, scroll to navigate.
 * TopBar is sticky with anchor-link navigation.
 */

import { useState } from "react";
import TopBar from "./components/Layout/TopBar";
import HeroSection from "./components/HeroSection";
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
  const [selectedCoins, setSelectedCoins] = useState(["BTC", "ETH", "SOL"]);
  const [timeKey, setTimeKey] = useState("all");

  const timeDays = TIME_OPTIONS.find((o) => o.key === timeKey)?.days || null;

  const toggleCoin = (coin) => {
    setSelectedCoins((prev) =>
      prev.includes(coin) ? prev.filter((c) => c !== coin) : [...prev, coin]
    );
  };

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Sticky navigation */}
      <TopBar />

      {/* Hero landing section */}
      <HeroSection />

      {/* Controls bar */}
      <div
        id="controls"
        className="max-w-[1400px] mx-auto px-6 py-4 flex items-center justify-between"
        style={{ borderBottom: "1px solid #2b2f36" }}
      >
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

      {/* Main content — all sections stacked vertically */}
      <main className="max-w-[1400px] mx-auto px-6">
        {selectedCoins.length === 0 ? (
          <div className="card text-center text-text-muted py-16">
            {t("markets.no_data")}
          </div>
        ) : (
          <>
            {/* Markets Section */}
            <div id="section-markets" className="scroll-section">
              <h2 className="scroll-section-title">
                <span>📊</span> {t("nav.markets")}
              </h2>
              <MarketsPage selectedCoins={selectedCoins} timeDays={timeDays} />
            </div>

            {/* Technical Section */}
            <div id="section-technical" className="scroll-section">
              <h2 className="scroll-section-title">
                <span>📈</span> {t("nav.technical")}
              </h2>
              <TechnicalPage selectedCoins={selectedCoins} timeDays={timeDays} />
            </div>

            {/* Insights Section */}
            <div id="section-insights" className="scroll-section">
              <h2 className="scroll-section-title">
                <span>🤖</span> {t("nav.insights")}
              </h2>
              <InsightsPage selectedCoins={selectedCoins} />
            </div>

            {/* Watchlist Section */}
            <div id="section-watchlist" className="scroll-section">
              <h2 className="scroll-section-title">
                <span>⭐</span> {t("nav.watchlist")}
              </h2>
              <WatchlistPanel />
            </div>

            {/* Data Section */}
            <div id="section-data" className="scroll-section">
              <h2 className="scroll-section-title">
                <span>🗂</span> {t("nav.data")}
              </h2>
              <DataPage selectedCoins={selectedCoins} timeDays={timeDays} />
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center text-xs text-text-muted py-8 border-t border-bg-border mt-16">
        <div>CryptoScope · Built by Jason Feng · University of Utah · 2026</div>
        <div className="mt-1 text-text-muted/50">
          Data: CoinGecko API (live) with mock fallback · On-chain data is simulated
        </div>
      </footer>
    </div>
  );
}
