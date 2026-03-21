/**
 * OnChainPanel — On-chain metrics display
 *
 * Shows blockchain-native data: active addresses, exchange flows,
 * whale transactions. Currently uses mock data.
 *
 * Ready for future API integration:
 *   - Glassnode, CryptoQuant, or Dune Analytics
 *   - Just swap the data source in useMarketData hook
 */

import { Users, ArrowDownToLine, ArrowUpFromLine, Fish } from "lucide-react";
import { useLanguage } from "../hooks/useLanguage";
import { formatNumber, formatCompact, formatPercent } from "../utils/formatters";

function OnChainMetric({ icon: Icon, label, value, subValue, change, color }) {
  const isPositive = change >= 0;

  return (
    <div className="card">
      <div className="flex items-center gap-2.5 mb-3">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: `${color}15` }}
        >
          <Icon size={16} style={{ color }} />
        </div>
        <span className="text-xs font-medium text-text-muted uppercase tracking-wide">
          {label}
        </span>
      </div>

      <div className="text-xl font-bold text-text-primary mb-1">{value}</div>

      <div className="flex items-center gap-2">
        {subValue && (
          <span className="text-xs text-text-muted">{subValue}</span>
        )}
        {change != null && (
          <span
            className={`text-xs font-medium ${
              isPositive ? "text-accent-green" : "text-accent-red"
            }`}
          >
            {formatPercent(change)}
          </span>
        )}
      </div>
    </div>
  );
}

export default function OnChainPanel({ symbol, onchainData }) {
  const { t } = useLanguage();

  if (!onchainData) {
    return (
      <div className="card text-text-muted text-sm text-center py-8">
        No on-chain data available for {symbol}
      </div>
    );
  }

  const d = onchainData;

  return (
    <div>
      <h3 className="section-title flex items-center gap-2">
        <span>⛓</span>
        {symbol} — {t("insights.onchain")}
      </h3>

      <div className="grid grid-cols-2 gap-4">
        <OnChainMetric
          icon={Users}
          label={t("insights.active_addresses")}
          value={formatNumber(d.activeAddresses)}
          change={d.activeAddressesChange}
          color="#1e90ff"
        />
        <OnChainMetric
          icon={ArrowDownToLine}
          label={t("insights.exchange_inflow")}
          value={formatNumber(d.exchangeInflow)}
          subValue={formatCompact(d.exchangeInflowUSD)}
          color="#f6465d"
        />
        <OnChainMetric
          icon={ArrowUpFromLine}
          label={t("insights.exchange_outflow")}
          value={formatNumber(d.exchangeOutflow)}
          subValue={formatCompact(d.exchangeOutflowUSD)}
          color="#00b075"
        />
        <OnChainMetric
          icon={Fish}
          label={t("insights.whale_txns")}
          value={formatNumber(d.whaleTransactions)}
          change={d.whaleTransactionsChange}
          color="#9945ff"
        />
      </div>

      {/* Interpretation hint */}
      <div className="mt-4 px-4 py-3 bg-bg-card border border-bg-border rounded-lg">
        <p className="text-xs text-text-muted leading-relaxed">
          {d.exchangeOutflow > d.exchangeInflow
            ? `Net outflow detected — more ${symbol} leaving exchanges than entering. This often suggests accumulation (bullish).`
            : `Net inflow detected — more ${symbol} entering exchanges than leaving. This may indicate selling pressure (bearish).`}
        </p>
      </div>
    </div>
  );
}
