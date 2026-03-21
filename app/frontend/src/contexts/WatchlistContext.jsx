/**
 * WatchlistContext — Persistent watchlist & mock portfolio
 *
 * Stores:
 *   - watchlist: array of coin symbols ["BTC", "ETH"]
 *   - holdings: { BTC: 0.5, ETH: 2.0 } — mock portfolio amounts
 *
 * Persisted in localStorage so it survives page reloads.
 */

import { createContext, useState, useCallback, useMemo } from "react";

const STORAGE_KEY = "cryptoscope_watchlist";
const HOLDINGS_KEY = "cryptoscope_holdings";

function loadJSON(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export const WatchlistContext = createContext(null);

export function WatchlistProvider({ children }) {
  const [watchlist, setWatchlistState] = useState(() =>
    loadJSON(STORAGE_KEY, ["BTC", "ETH", "SOL"])
  );
  const [holdings, setHoldingsState] = useState(() =>
    loadJSON(HOLDINGS_KEY, { BTC: 0, ETH: 0, SOL: 0 })
  );

  const setWatchlist = useCallback((next) => {
    setWatchlistState(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  }, []);

  const setHoldings = useCallback((next) => {
    setHoldingsState(next);
    localStorage.setItem(HOLDINGS_KEY, JSON.stringify(next));
  }, []);

  const addCoin = useCallback(
    (symbol) => {
      if (!watchlist.includes(symbol)) {
        const next = [...watchlist, symbol];
        setWatchlist(next);
        setHoldings({ ...holdings, [symbol]: 0 });
      }
    },
    [watchlist, holdings, setWatchlist, setHoldings]
  );

  const removeCoin = useCallback(
    (symbol) => {
      setWatchlist(watchlist.filter((s) => s !== symbol));
      const next = { ...holdings };
      delete next[symbol];
      setHoldings(next);
    },
    [watchlist, holdings, setWatchlist, setHoldings]
  );

  const updateHolding = useCallback(
    (symbol, amount) => {
      setHoldings({ ...holdings, [symbol]: parseFloat(amount) || 0 });
    },
    [holdings, setHoldings]
  );

  const isWatched = useCallback(
    (symbol) => watchlist.includes(symbol),
    [watchlist]
  );

  const value = useMemo(
    () => ({
      watchlist,
      holdings,
      addCoin,
      removeCoin,
      updateHolding,
      isWatched,
    }),
    [watchlist, holdings, addCoin, removeCoin, updateHolding, isWatched]
  );

  return (
    <WatchlistContext.Provider value={value}>
      {children}
    </WatchlistContext.Provider>
  );
}
