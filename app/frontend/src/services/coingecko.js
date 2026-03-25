/**
 * coingecko.js — CoinGecko API 服务层
 *
 * 负责：
 * 1. 调用 CoinGecko 免费 API 获取历史价格数据
 * 2. 将 API 返回的原始格式转换为前端组件期望的格式
 * 3. 内存缓存，避免重复请求触发频率限制
 *
 * CoinGecko 免费 API 不需要 API key。
 * 频率限制：每分钟约 10-30 次请求。
 */

const BASE_URL = "https://api.coingecko.com/api/v3";

// 币种简称 → CoinGecko ID 映射
const COIN_ID_MAP = {
  BTC: "bitcoin",
  ETH: "ethereum",
  SOL: "solana",
};

// 内存缓存：避免重复请求
// key: "BTC_365", value: { data: [...], timestamp: Date.now() }
const cache = {};
const CACHE_TTL = 5 * 60 * 1000; // 5 分钟缓存有效期

/**
 * 从 CoinGecko 获取单个币种的历史市场数据。
 *
 * @param {string} symbol - 币种简称，如 "BTC"
 * @param {number} days - 获取过去多少天的数据，默认 365
 * @returns {Promise<Array>} 处理后的数据数组，每项包含 date, price, volume, marketCap
 */
export async function fetchCoinHistory(symbol, days = 365) {
  const coinId = COIN_ID_MAP[symbol];
  if (!coinId) {
    throw new Error(`Unknown coin symbol: ${symbol}`);
  }

  // 检查缓存
  const cacheKey = `${symbol}_${days}`;
  const cached = cache[cacheKey];
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    console.log(`[CoinGecko] Cache hit for ${symbol}`);
    return cached.data;
  }

  // 调用 API
  const url = `${BASE_URL}/coins/${coinId}/market_chart?vs_currency=usd&days=${days}&interval=daily`;
  console.log(`[CoinGecko] Fetching ${symbol}...`);

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`CoinGecko API error: ${response.status} ${response.statusText}`);
  }

  const raw = await response.json();

  // 转换格式：CoinGecko 返回 [[timestamp, value], ...] → 我们需要 [{date, price, ...}, ...]
  const data = transformRawData(raw);

  // 写入缓存
  cache[cacheKey] = { data, timestamp: Date.now() };
  console.log(`[CoinGecko] Got ${data.length} days for ${symbol}`);

  return data;
}

/**
 * 批量获取多个币种的数据。
 * 请求之间加 1 秒延迟，避免触发频率限制。
 *
 * @param {string[]} symbols - 币种简称数组，如 ["BTC", "ETH", "SOL"]
 * @param {number} days - 天数
 * @returns {Promise<Object>} { BTC: [...], ETH: [...], SOL: [...] }
 */
export async function fetchAllCoins(symbols, days = 365) {
  const result = {};

  for (let i = 0; i < symbols.length; i++) {
    const symbol = symbols[i];
    try {
      result[symbol] = await fetchCoinHistory(symbol, days);

      // 两次请求之间等待 1.5 秒（避免频率限制）
      // 最后一个币不需要等
      if (i < symbols.length - 1) {
        await new Promise((resolve) => setTimeout(resolve, 1500));
      }
    } catch (err) {
      console.error(`[CoinGecko] Failed to fetch ${symbol}:`, err.message);
      result[symbol] = null; // 失败的币返回 null，调用方会用 mock 替代
    }
  }

  return result;
}

/**
 * 将 CoinGecko 原始数据转换为前端组件期望的格式。
 *
 * CoinGecko 返回：
 *   { prices: [[ts, price], ...], market_caps: [[ts, mcap], ...], total_volumes: [[ts, vol], ...] }
 *
 * 转换为：
 *   [{ date: "2025-01-15", price: 69420.50, volume: 35000000000, marketCap: 1350000000000 }, ...]
 */
function transformRawData(raw) {
  const prices = raw.prices || [];
  const marketCaps = raw.market_caps || [];
  const volumes = raw.total_volumes || [];

  // 以 prices 为基准（三个数组长度可能略有不同）
  return prices.map((item, i) => {
    const timestamp = item[0];
    const date = new Date(timestamp).toISOString().split("T")[0]; // "2025-01-15"

    return {
      date,
      price: Math.round(item[1] * 100) / 100,
      volume: Math.round((volumes[i]?.[1] || 0)),
      marketCap: Math.round((marketCaps[i]?.[1] || 0)),
    };
  });
}

/**
 * 获取可用的币种列表。
 */
export function getAvailableCoins() {
  return Object.keys(COIN_ID_MAP);
}
