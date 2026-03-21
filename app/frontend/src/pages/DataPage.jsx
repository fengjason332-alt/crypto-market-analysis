/**
 * DataPage — Raw data explorer with download
 */

import { useState, useMemo } from "react";
import { Download } from "lucide-react";
import { useLanguage } from "../hooks/useLanguage";
import { useMarketData } from "../hooks/useMarketData";

export default function DataPage({ selectedCoins, timeDays }) {
  const { t } = useLanguage();
  const { getHistory, coinMeta } = useMarketData(selectedCoins);
  const [activeCoin, setActiveCoin] = useState(selectedCoins[0] || "BTC");

  const history = getHistory(activeCoin, timeDays);
  const columns = history.length > 0 ? Object.keys(history[0]) : [];

  const DEFAULT_COLS = ["date", "price", "volume", "rsi", "macdLine", "dailyReturn"];
  const [visibleCols, setVisibleCols] = useState(
    columns.filter((c) => DEFAULT_COLS.includes(c))
  );

  // Update visible columns when coin changes
  useMemo(() => {
    if (columns.length > 0 && visibleCols.length === 0) {
      setVisibleCols(columns.filter((c) => DEFAULT_COLS.includes(c)));
    }
  }, [columns]);

  const toggleCol = (col) => {
    setVisibleCols((prev) =>
      prev.includes(col) ? prev.filter((c) => c !== col) : [...prev, col]
    );
  };

  const downloadCSV = () => {
    const header = visibleCols.join(",");
    const rows = history.map((row) =>
      visibleCols.map((col) => row[col] ?? "").join(",")
    );
    const csv = [header, ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${activeCoin.toLowerCase()}_data.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
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

        <button onClick={downloadCSV} className="btn-primary flex items-center gap-2">
          <Download size={14} />
          {t("data.download")}
        </button>
      </div>

      {/* Column selector */}
      <div className="mb-4">
        <span className="text-xs text-text-muted mb-2 block">{t("data.columns")}</span>
        <div className="flex flex-wrap gap-1.5">
          {columns.map((col) => (
            <button
              key={col}
              onClick={() => toggleCol(col)}
              className={`px-2.5 py-1 rounded-md text-xs font-medium transition-colors
                ${
                  visibleCols.includes(col)
                    ? "bg-accent-blue/15 text-accent-blue"
                    : "bg-bg-card text-text-muted hover:text-text-secondary"
                }`}
            >
              {col}
            </button>
          ))}
        </div>
      </div>

      {/* Data table */}
      <div className="card p-0 overflow-auto max-h-[600px]">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-bg-card z-10">
            <tr className="border-b border-bg-border">
              {visibleCols.map((col) => (
                <th
                  key={col}
                  className="text-left px-4 py-3 text-xs font-medium text-text-muted whitespace-nowrap"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {history
              .slice()
              .reverse()
              .slice(0, 200)
              .map((row, i) => (
                <tr
                  key={i}
                  className="border-b border-bg-border/30 hover:bg-bg-hover/50 transition-colors"
                >
                  {visibleCols.map((col) => (
                    <td
                      key={col}
                      className="px-4 py-2.5 text-text-secondary whitespace-nowrap font-mono text-xs"
                    >
                      {typeof row[col] === "number"
                        ? row[col] > 1000
                          ? row[col].toLocaleString("en-US", {
                              maximumFractionDigits: 2,
                            })
                          : row[col].toFixed(4)
                        : row[col]}
                    </td>
                  ))}
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      <div className="text-xs text-text-muted mt-3">
        {history.length} {t("data.rows")} · Showing latest 200
      </div>
    </div>
  );
}
