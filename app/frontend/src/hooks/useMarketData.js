/**
 * useMarketData — Hook for accessing coin market data
 *
 * 数据优先级：
 * 1. 尝试从 CoinGecko API 获取真实数据
 * 2. 如果 API 失败（频率限制、网络错误等），回退到 mockData.js
 *
 * 所有组件通过这个 hook 获取数据，不直接接触 API 或 mock。
 * 切换数据源对组件完全透明。
 */

import { useState, useEffect, useMemo, useCallback, useRef } from "react";
import { fetchAllCoins } from "../services/coingecko";
import { addIndicators } from "../services/computeIndicators";
import { COIN_DATA, COIN_META, getLatestSnapshot, ONCHAIN_DATA } from "../data/mockData";

// 数据源标记
const SOURCE_LIVE = "live";
const SOURCE_MOCK = "mock";

export function useMarketData(selectedCoins = ["BTC", "ETH", "SOL"]) {
  const [liveData, setLiveData] = useState({}); // { BTC: [...], ETH: [...], ... }
  const [dataSource, setDataSource] = useState(SOURCE_MOCK); // "live" or "mock"
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const fetchedRef = useRef(false); // 防止重复请求

  // 启动时获取真实数据
  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;

    async function loadLiveData() {
      setLoading(true);
      setError(null);

      try {
        const allCoins = ["BTC", "ETH", "SOL"];
        const result = await fetchAllCoins(allCoins);

        // 检查是否所有币都成功获取
        const successCoins = {};
        let hasAnyData = false;

        for (const symbol of allCoins) {
          if (result[symbol] && result[symbol].length > 0) {
            // 对真实数据计算技术指标
            successCoins[symbol] = addIndicators(result[symbol]);
            hasAnyData = true;
          }
        }

        if (hasAnyData) {
          setLiveData(successCoins);
          setDataSource(SOURCE_LIVE);
          console.log("[useMarketData] Using LIVE data from CoinGecko");
        } else {
          setDataSource(SOURCE_MOCK);
          console.log("[useMarketData] All API calls failed, using MOCK data");
        }
      } catch (err) {
        console.error("[useMarketData] Failed to fetch live data:", err);
        setError(err.message);
        setDataSource(SOURCE_MOCK);
        console.log("[useMarketData] Falling back to MOCK data");
      } finally {
        setLoading(false);
      }
    }

    loadLiveData();
  }, []);

  /**
   * 获取指定币种的完整历史数据。
   * 优先返回真实数据，如果该币种没有真实数据则回退到 mock。
   */
  const getHistory = useCallback(
    (symbol, days = null) => {
      // 优先用真实数据
      let data;
      if (liveData[symbol] && liveData[symbol].length > 0) {
        data = liveData[symbol];
      } else {
        // 回退到 mock
        data = COIN_DATA[symbol] || [];
      }

      if (!days) return data;
      return data.slice(-days);
    },
    [liveData]
  );

  /**
   * 获取选中币种的最新快照（用于 MetricCard、市场表格等）。
   */
  const snapshots = useMemo(() => {
    return selectedCoins.map((symbol) => {
      const history = getHistory(symbol);
      if (!history || history.length === 0) return null;

      const latest = history[history.length - 1];
      const prev = history.length > 1 ? history[history.length - 2] : latest;
      const change24h = (latest.price - prev.price) / prev.price;

      return {
        symbol,
        ...latest,
        change24h,
        ...COIN_META[symbol],
      };
    }).filter(Boolean);
  }, [selectedCoins, getHistory]);

  /**
   * 获取链上数据（目前仍然是 mock，未来可接入 Glassnode 等 API）。
   */
  const getOnChain = useCallback(
    (symbol) => ONCHAIN_DATA[symbol] || null,
    []
  );

  const availableCoins = Object.keys(COIN_META);

  return {
    snapshots,
    getHistory,
    getOnChain,
    availableCoins,
    coinMeta: COIN_META,
    // 新增：让 UI 可以显示数据源状态
    dataSource,
    loading,
    error,
  };
}
