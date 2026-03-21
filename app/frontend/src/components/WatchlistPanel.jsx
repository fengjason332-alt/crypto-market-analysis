/**
 * WatchlistPanel — User's tracked assets + mock portfolio
 *
 * Features:
 *   - Add/remove coins from watchlist
 *   - Input mock holdings amount per coin
 *   - Show portfolio value calculation
 *   - Mini sparkline per coin
 */

import { useState } from "react";
import { Star, Plus, X, Wallet } from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import { useLanguage } from "../hooks/useLanguage";
import { useWatchlist } from "../hooks/useWatchlist";
import { useMarketData } from "../hooks/useMarketData";
import { formatUSD, formatPercent } from "../utils/formatters";

function Sparkline({ data, color, positive }) {
  const chartData = data.slice(-30).map((d) => ({ v: d.price }));
  const strokeColor = positive ? "#00b075" : "#f6465d";

  return (
    <ResponsiveContainer width={80} height={32}>
      <AreaChart data={chartData}>
        <Area
          type="monotone"
          dataKey="v"
          stroke={strokeColor}
          strokeWidth={1.5}
          fill={strokeColor}
          fillOpacity={0.1}
          dot={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export default function WatchlistPanel() {
  const { t } = useLanguage();
  const { watchlist, holdings, addCoin, removeCoin, updateHolding } = useWatchlist();
  const { snapshots, getHistory, availableCoins, coinMeta } = useMarketData(watchlist);
  const [showAdd, setShowAdd] = useState(false);

  // Portfolio value
  const portfolioValue = snapshots.reduce((sum, s) => {
    const amount = holdings[s.symbol] || 0;
    return sum + amount * s.price;
  }, 0);

  const addableCoins = availableCoins.filter((c) => !watchlist.includes(c));

  return (
    <div className="max-w-3xl mx-auto">
      {/* Portfolio summary */}
      <div className="card mb-6 bg-gradient-to-r from-accent-blue/5 to-accent-purple/5">
        <div className="flex items-center gap-3 mb-3">
          <Wallet size={18} className="text-accent-blue" />
          <span className="text-sm font-semibold text-text-primary">
            {t("watchlist.portfolio_value")}
          </span>
        </div>
        <div className="text-3xl font-bold text-text-primary">
          {formatUSD(portfolioValue)}
        </div>
      </div>

      {/* Watchlist header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="section-title mb-0 flex items-center gap-2">
          <Star size={18} className="text-accent-yellow" />
          {t("watchlist.title")}
        </h2>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="btn-ghost flex items-center gap-1.5 text-xs"
        >
          <Plus size={14} />
          {t("watchlist.add")}
        </button>
      </div>

      {/* Add coin dropdown */}
      {showAdd && addableCoins.length > 0 && (
        <div className="card mb-4 p-3">
          <div className="flex flex-wrap gap-2">
            {addableCoins.map((coin) => (
              <button
                key={coin}
                onClick={() => {
                  addCoin(coin);
                  setShowAdd(false);
                }}
                className="flex items-center gap-2 px-3 py-2 rounded-lg
                           bg-bg-hover text-text-secondary text-sm font-medium
                           hover:text-text-primary transition-colors"
              >
                <span style={{ color: coinMeta[coin]?.color }}>
                  {coinMeta[coin]?.icon}
                </span>
                {coin}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Watchlist items */}
      {snapshots.length === 0 ? (
        <div className="card text-center text-text-muted text-sm py-12">
          {t("watchlist.empty")}
        </div>
      ) : (
        <div className="space-y-3">
          {snapshots.map((snap) => {
            const history = getHistory(snap.symbol);
            const isPositive = snap.change24h >= 0;
            const amount = holdings[snap.symbol] || 0;

            return (
              <div key={snap.symbol} className="card flex items-center gap-4">
                {/* Coin info */}
                <div className="flex items-center gap-3 w-32">
                  <span
                    className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                    style={{
                      backgroundColor: `${snap.color}20`,
                      color: snap.color,
                    }}
                  >
                    {snap.icon}
                  </span>
                  <div>
                    <div className="text-sm font-semibold text-text-primary">
                      {snap.symbol}
                    </div>
                    <div className="text-xs text-text-muted">{snap.name}</div>
                  </div>
                </div>

                {/* Price */}
                <div className="w-28 text-right">
                  <div className="text-sm font-semibold text-text-primary">
                    {formatUSD(snap.price)}
                  </div>
                  <div
                    className={`text-xs font-medium ${
                      isPositive ? "text-accent-green" : "text-accent-red"
                    }`}
                  >
                    {formatPercent(snap.change24h)}
                  </div>
                </div>

                {/* Sparkline */}
                <div className="flex-shrink-0">
                  <Sparkline data={history} positive={isPositive} />
                </div>

                {/* Holdings input */}
                <div className="flex-1 max-w-[140px]">
                  <label className="text-xs text-text-muted block mb-1">
                    {t("watchlist.amount")}
                  </label>
                  <input
                    type="number"
                    value={amount || ""}
                    onChange={(e) => updateHolding(snap.symbol, e.target.value)}
                    placeholder="0.00"
                    className="w-full bg-bg-primary border border-bg-border rounded-lg
                               px-3 py-1.5 text-sm text-text-primary
                               focus:border-accent-blue focus:outline-none transition-colors"
                  />
                </div>

                {/* Value */}
                <div className="w-24 text-right">
                  <div className="text-sm font-medium text-text-primary">
                    {amount > 0 ? formatUSD(amount * snap.price) : "—"}
                  </div>
                </div>

                {/* Remove */}
                <button
                  onClick={() => removeCoin(snap.symbol)}
                  className="p-1.5 rounded-md text-text-muted hover:text-accent-red
                             hover:bg-accent-red/10 transition-colors"
                >
                  <X size={14} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
