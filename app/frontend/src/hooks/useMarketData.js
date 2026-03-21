/**
 * useMarketData — Hook for accessing coin market data
 *
 * Currently reads from mockData.js.
 * To integrate with a real API later, just change the data source here.
 * All components will update automatically since they consume this hook.
 */

import { useMemo } from "react";
import { COIN_DATA, COIN_META, getLatestSnapshot, ONCHAIN_DATA } from "../data/mockData";

export function useMarketData(selectedCoins = ["BTC", "ETH", "SOL"]) {
  const snapshots = useMemo(
    () => selectedCoins.map(getLatestSnapshot).filter(Boolean),
    [selectedCoins]
  );

  const getHistory = (symbol, days = null) => {
    const data = COIN_DATA[symbol] || [];
    if (!days) return data;
    return data.slice(-days);
  };

  const getOnChain = (symbol) => ONCHAIN_DATA[symbol] || null;

  const availableCoins = Object.keys(COIN_META);

  return { snapshots, getHistory, getOnChain, availableCoins, coinMeta: COIN_META };
}
