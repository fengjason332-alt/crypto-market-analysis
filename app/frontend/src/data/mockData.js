/**
 * mockData.js — Static mock data for development
 *
 * In production, replace these with API calls to your Python backend
 * or directly to CoinGecko / CCXT / on-chain APIs.
 *
 * Structure mirrors what the Python pipeline produces:
 *   src/fetch_data.py → src/clean_data.py → src/indicators.py
 */

// ---- Coin metadata ----
export const COIN_META = {
  BTC: { name: "Bitcoin", color: "#F7931A", icon: "₿" },
  ETH: { name: "Ethereum", color: "#627EEA", icon: "Ξ" },
  SOL: { name: "Solana", color: "#9945FF", icon: "◎" },
  XRP: { name: "XRP", color: "#00AAE4", icon: "✕" },
  BNB: { name: "BNB", color: "#F0B90B", icon: "◆" },
};

// ---- Generate price history (sine wave + trend + noise) ----
function generatePriceHistory(basePrice, days = 365, volatility = 0.03) {
  const data = [];
  let price = basePrice;
  const now = new Date();

  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    // Sine wave for cyclical patterns + random noise
    const trend = Math.sin(i / 60) * basePrice * 0.15;
    const noise = (Math.random() - 0.48) * basePrice * volatility;
    price = Math.max(price * 0.5, price + noise + trend * 0.01);

    const volume = basePrice * 1e6 * (0.5 + Math.random());
    const marketCap = price * (basePrice > 10000 ? 19.5e6 : 120e6);

    data.push({
      date: date.toISOString().split("T")[0],
      price: Math.round(price * 100) / 100,
      volume: Math.round(volume),
      marketCap: Math.round(marketCap),
    });
  }

  return data;
}

// ---- Compute technical indicators from price history ----
function computeIndicators(history) {
  const prices = history.map((d) => d.price);

  return history.map((d, i) => {
    // SMA 20
    const sma20Window = prices.slice(Math.max(0, i - 19), i + 1);
    const sma20 = sma20Window.reduce((a, b) => a + b, 0) / sma20Window.length;

    // SMA 50
    const sma50Window = prices.slice(Math.max(0, i - 49), i + 1);
    const sma50 = sma50Window.reduce((a, b) => a + b, 0) / sma50Window.length;

    // EMA 12 & 26 (simplified)
    const ema12 = exponentialMA(prices, i, 12);
    const ema26 = exponentialMA(prices, i, 26);
    const macdLine = ema12 - ema26;
    const macdSignal = exponentialMA(
      history.map((_, j) => exponentialMA(prices, j, 12) - exponentialMA(prices, j, 26)),
      i,
      9
    );
    const macdHistogram = macdLine - macdSignal;

    // RSI 14
    const rsi = computeRSI(prices, i, 14);

    // Bollinger Bands
    const bbWindow = prices.slice(Math.max(0, i - 19), i + 1);
    const bbMean = bbWindow.reduce((a, b) => a + b, 0) / bbWindow.length;
    const bbStd = Math.sqrt(
      bbWindow.reduce((sum, p) => sum + (p - bbMean) ** 2, 0) / bbWindow.length
    );
    const bbUpper = bbMean + 2 * bbStd;
    const bbLower = bbMean - 2 * bbStd;

    // Daily return
    const dailyReturn = i > 0 ? (prices[i] - prices[i - 1]) / prices[i - 1] : 0;

    return {
      ...d,
      sma20: Math.round(sma20 * 100) / 100,
      sma50: Math.round(sma50 * 100) / 100,
      ema12: Math.round(ema12 * 100) / 100,
      ema26: Math.round(ema26 * 100) / 100,
      rsi: Math.round(rsi * 10) / 10,
      macdLine: Math.round(macdLine * 100) / 100,
      macdSignal: Math.round(macdSignal * 100) / 100,
      macdHistogram: Math.round(macdHistogram * 100) / 100,
      bbUpper: Math.round(bbUpper * 100) / 100,
      bbMiddle: Math.round(bbMean * 100) / 100,
      bbLower: Math.round(bbLower * 100) / 100,
      dailyReturn: Math.round(dailyReturn * 10000) / 10000,
    };
  });
}

function exponentialMA(arr, index, span) {
  const k = 2 / (span + 1);
  let ema = arr[0];
  for (let i = 1; i <= Math.min(index, arr.length - 1); i++) {
    ema = arr[i] * k + ema * (1 - k);
  }
  return ema;
}

function computeRSI(prices, index, period) {
  if (index < period) return 50;
  let gains = 0;
  let losses = 0;
  for (let i = index - period + 1; i <= index; i++) {
    const diff = prices[i] - prices[i - 1];
    if (diff > 0) gains += diff;
    else losses -= diff;
  }
  if (losses === 0) return 100;
  const rs = gains / losses;
  return 100 - 100 / (1 + rs);
}

// ---- Build full dataset ----
const BTC_HISTORY = generatePriceHistory(69000, 365, 0.025);
const ETH_HISTORY = generatePriceHistory(2100, 365, 0.035);
const SOL_HISTORY = generatePriceHistory(145, 365, 0.05);

export const COIN_DATA = {
  BTC: computeIndicators(BTC_HISTORY),
  ETH: computeIndicators(ETH_HISTORY),
  SOL: computeIndicators(SOL_HISTORY),
};

// ---- Latest snapshot for each coin ----
export function getLatestSnapshot(symbol) {
  const data = COIN_DATA[symbol];
  if (!data || data.length === 0) return null;
  const latest = data[data.length - 1];
  const prev = data.length > 1 ? data[data.length - 2] : latest;
  const change24h = (latest.price - prev.price) / prev.price;

  return {
    symbol,
    ...latest,
    change24h,
    ...COIN_META[symbol],
  };
}

// ---- On-chain mock data ----
export const ONCHAIN_DATA = {
  BTC: {
    activeAddresses: 924_531,
    activeAddressesChange: 0.032,
    exchangeInflow: 12_450,
    exchangeInflowUSD: 862_000_000,
    exchangeOutflow: 15_200,
    exchangeOutflowUSD: 1_051_000_000,
    whaleTransactions: 847,
    whaleTransactionsChange: -0.05,
  },
  ETH: {
    activeAddresses: 512_872,
    activeAddressesChange: 0.018,
    exchangeInflow: 89_300,
    exchangeInflowUSD: 189_000_000,
    exchangeOutflow: 102_400,
    exchangeOutflowUSD: 217_000_000,
    whaleTransactions: 1_234,
    whaleTransactionsChange: 0.12,
  },
  SOL: {
    activeAddresses: 1_234_567,
    activeAddressesChange: 0.075,
    exchangeInflow: 3_200_000,
    exchangeInflowUSD: 464_000_000,
    exchangeOutflow: 2_800_000,
    exchangeOutflowUSD: 406_000_000,
    whaleTransactions: 312,
    whaleTransactionsChange: -0.02,
  },
};
