/**
 * MetricCard — OKX-style crypto summary card
 *
 * Shows: coin name, price, 24h change, sub-stats (RSI, volume, market cap).
 * Used in the Markets overview page.
 */

import { formatUSD, formatCompact, formatPercent } from "../utils/formatters";

export default function MetricCard({ snapshot }) {
  if (!snapshot) return null;

  const { symbol, name, color, icon, price, change24h, rsi, volume, marketCap } = snapshot;
  const isPositive = change24h >= 0;

  return (
    <div className="card group">
      {/* Header: icon + name */}
      <div className="flex items-center gap-2.5 mb-3">
        <span
          className="w-9 h-9 rounded-full flex items-center justify-center text-lg font-bold"
          style={{ backgroundColor: `${color}20`, color }}
        >
          {icon}
        </span>
        <div>
          <span className="text-sm font-semibold text-text-primary">{symbol}</span>
          <span className="text-xs text-text-muted ml-1.5">/ USD</span>
        </div>
      </div>

      {/* Price */}
      <div className="text-2xl font-bold text-text-primary tracking-tight mb-1">
        {formatUSD(price)}
      </div>

      {/* 24h change */}
      <span
        className={`text-sm font-semibold ${
          isPositive ? "text-accent-green" : "text-accent-red"
        }`}
      >
        {formatPercent(change24h)}
      </span>

      {/* Sub stats */}
      <div className="flex gap-5 mt-3 pt-3 border-t border-bg-border">
        <div className="text-xs text-text-muted">
          RSI{" "}
          <span
            className={`font-medium ${
              rsi > 70
                ? "text-accent-red"
                : rsi < 30
                ? "text-accent-green"
                : "text-text-secondary"
            }`}
          >
            {rsi?.toFixed(1)}
          </span>
        </div>
        <div className="text-xs text-text-muted">
          Vol <span className="text-text-secondary font-medium">{formatCompact(volume)}</span>
        </div>
        <div className="text-xs text-text-muted">
          MCap <span className="text-text-secondary font-medium">{formatCompact(marketCap)}</span>
        </div>
      </div>
    </div>
  );
}
