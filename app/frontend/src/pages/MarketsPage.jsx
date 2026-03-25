/**
 * MarketsPage — Market overview (OKX-style)
 *
 * Shows: metric cards, market table, price chart, volume chart.
 */

import { useLanguage } from "../hooks/useLanguage";
import { useMarketData } from "../hooks/useMarketData";
import MetricCard from "../components/MetricCard";
import PriceChart from "../components/PriceChart";
import { formatUSD, formatCompact, formatPercent } from "../utils/formatters";

export default function MarketsPage({ selectedCoins, timeDays }) {
  const { t } = useLanguage();
  const { snapshots, getHistory, coinMeta, loading, dataSource } = useMarketData(selectedCoins);

  return (
    <div>
      {/* Data source indicator */}
      {loading && (
        <div className="text-center text-text-muted text-sm py-4">
          Loading live market data from CoinGecko...
        </div>
      )}
      {!loading && dataSource === "live" && (
        <div className="text-center text-xs text-accent-green/60 py-2">
          ● Live data from CoinGecko
        </div>
      )}
      {!loading && dataSource === "mock" && (
        <div className="text-center text-xs text-accent-yellow/60 py-2">
          ● Using simulated data (API unavailable)
        </div>
      )}

      {/* Metric cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {snapshots.map((snap) => (
          <MetricCard key={snap.symbol} snapshot={snap} />
        ))}
      </div>

      {/* Market table */}
      <h3 className="section-title">{t("markets.hot_crypto")}</h3>
      <div className="card p-0 overflow-hidden mb-8">
        <table className="w-full">
          <thead>
            <tr className="border-b border-bg-border">
              <th className="text-left px-5 py-3 text-xs font-medium text-text-muted">Name</th>
              <th className="text-right px-5 py-3 text-xs font-medium text-text-muted">
                {t("markets.price")}
              </th>
              <th className="text-right px-5 py-3 text-xs font-medium text-text-muted">
                {t("markets.change")}
              </th>
              <th className="text-right px-5 py-3 text-xs font-medium text-text-muted">
                {t("markets.volume")}
              </th>
              <th className="text-right px-5 py-3 text-xs font-medium text-text-muted">
                {t("markets.market_cap")}
              </th>
              <th className="text-right px-5 py-3 text-xs font-medium text-text-muted">RSI</th>
            </tr>
          </thead>
          <tbody>
            {snapshots.map((snap) => {
              const isPos = snap.change24h >= 0;
              return (
                <tr
                  key={snap.symbol}
                  className="border-b border-bg-border/50 hover:bg-bg-hover transition-colors"
                >
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <span
                        className="w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold"
                        style={{
                          backgroundColor: `${snap.color}20`,
                          color: snap.color,
                        }}
                      >
                        {snap.icon}
                      </span>
                      <div>
                        <span className="text-sm font-semibold text-text-primary">
                          {snap.symbol}
                        </span>
                        <span className="text-xs text-text-muted ml-2">{snap.name}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-right text-sm font-semibold text-text-primary">
                    {formatUSD(snap.price)}
                  </td>
                  <td
                    className={`px-5 py-4 text-right text-sm font-semibold ${
                      isPos ? "text-accent-green" : "text-accent-red"
                    }`}
                  >
                    {formatPercent(snap.change24h)}
                  </td>
                  <td className="px-5 py-4 text-right text-sm text-text-secondary">
                    {formatCompact(snap.volume)}
                  </td>
                  <td className="px-5 py-4 text-right text-sm text-text-secondary">
                    {formatCompact(snap.marketCap)}
                  </td>
                  <td className="px-5 py-4 text-right">
                    <span
                      className={`text-sm font-medium ${
                        snap.rsi > 70
                          ? "text-accent-red"
                          : snap.rsi < 30
                          ? "text-accent-green"
                          : "text-text-secondary"
                      }`}
                    >
                      {snap.rsi?.toFixed(1)}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Price chart */}
      <h3 className="section-title">{t("markets.price_trend")}</h3>
      <PriceChart
        data={getHistory(selectedCoins[0], timeDays)}
        lines={selectedCoins.map((c) => ({
          key: "price",
          color: coinMeta[c]?.color || "#fff",
          name: c,
        }))}
        height={420}
      />
    </div>
  );
}
