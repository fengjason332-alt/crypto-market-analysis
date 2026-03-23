/**
 * mockData.js — Data layer for CryptoScope frontend
 *
 * This module loads REAL data from the Python pipeline + OKX API:
 *   src/export_json.py → public/data/market_data.json
 *
 * How to refresh data:
 *   python src/export_json.py
 *
 * If market_data.json is not available (e.g. first run), falls back
 * to generated mock data so the UI still works.
 */

// ---- Coin metadata ----
export const COIN_META = {
  BTC: { name: "Bitcoin", color: "#F7931A", icon: "₿" },
  ETH: { name: "Ethereum", color: "#627EEA", icon: "Ξ" },
  SOL: { name: "Solana", color: "#9945FF", icon: "◎" },
};

// ---- State: holds loaded data ----
let _loaded = false;
let _coinData = {};
let _latestSnapshots = {};

// ---- Load real data from JSON ----
async function loadRealData() {
  try {
    const resp = await fetch("/data/market_data.json");
    if (!resp.ok) throw new Error("fetch failed");
    const raw = await resp.json();

    for (const [symbol, coinObj] of Object.entries(raw)) {
      // History array
      _coinData[symbol] = coinObj.history || [];

      // Latest snapshot
      const latest = coinObj.latest || {};
      const hist = coinObj.history || [];
      const prev = hist.length > 1 ? hist[hist.length - 2] : latest;
      const change24h = latest.change24h ?? (
        prev.price > 0 ? (latest.price - prev.price) / prev.price : 0
      );

      _latestSnapshots[symbol] = {
        symbol,
        ...latest,
        change24h,
        ...(COIN_META[symbol] || coinObj.meta || {}),
      };
    }

    _loaded = true;
    console.log(
      "✅ CryptoScope: Loaded real data from pipeline",
      Object.keys(raw).map(k => `${k}: ${raw[k].history?.length} days`).join(", ")
    );
    return true;
  } catch (e) {
    console.warn("⚠ CryptoScope: market_data.json not found, using fallback data.", e.message);
    generateFallbackData();
    return false;
  }
}

// ---- Fallback: generate mock data if JSON not available ----
function generateFallbackData() {
  const configs = [
    ["BTC", 69000, 0.025],
    ["ETH", 2100, 0.035],
    ["SOL", 145, 0.05],
  ];

  for (const [symbol, base, vol] of configs) {
    const history = generatePriceHistory(base, 365, vol);
    const withIndicators = computeIndicators(history);
    _coinData[symbol] = withIndicators;

    const latest = withIndicators[withIndicators.length - 1];
    const prev = withIndicators[withIndicators.length - 2] || latest;
    _latestSnapshots[symbol] = {
      symbol,
      ...latest,
      change24h: (latest.price - prev.price) / prev.price,
      ...COIN_META[symbol],
    };
  }

  _loaded = true;
  console.log("📊 CryptoScope: Using generated fallback data");
}

function generatePriceHistory(basePrice, days = 365, volatility = 0.03) {
  const data = [];
  let price = basePrice;
  const now = new Date();
  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
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

function computeIndicators(history) {
  const prices = history.map(d => d.price);
  return history.map((d, i) => {
    const sma20w = prices.slice(Math.max(0, i - 19), i + 1);
    const sma20 = sma20w.reduce((a, b) => a + b, 0) / sma20w.length;
    const sma50w = prices.slice(Math.max(0, i - 49), i + 1);
    const sma50 = sma50w.reduce((a, b) => a + b, 0) / sma50w.length;
    const k12 = 2 / 13, k26 = 2 / 27;
    let ema12 = prices[0], ema26 = prices[0];
    for (let j = 1; j <= i; j++) { ema12 = prices[j] * k12 + ema12 * (1 - k12); ema26 = prices[j] * k26 + ema26 * (1 - k26); }
    const macdLine = ema12 - ema26;
    const macdSignal = macdLine * 0.8;
    const macdHistogram = macdLine - macdSignal;
    let rsi = 50;
    if (i >= 14) { let g = 0, l = 0; for (let j = i - 13; j <= i; j++) { const diff = prices[j] - prices[j - 1]; if (diff > 0) g += diff; else l -= diff; } rsi = l === 0 ? 100 : 100 - 100 / (1 + g / l); }
    const bbStd = Math.sqrt(sma20w.reduce((s, p) => s + (p - sma20) ** 2, 0) / sma20w.length);
    const dailyReturn = i > 0 ? (prices[i] - prices[i - 1]) / prices[i - 1] : 0;
    return { ...d, sma20: +sma20.toFixed(2), sma50: +sma50.toFixed(2), rsi: +rsi.toFixed(1), macdLine: +macdLine.toFixed(2), macdSignal: +macdSignal.toFixed(2), macdHistogram: +macdHistogram.toFixed(2), bbUpper: +(sma20 + 2 * bbStd).toFixed(2), bbMiddle: +sma20.toFixed(2), bbLower: +(sma20 - 2 * bbStd).toFixed(2), dailyReturn: +dailyReturn.toFixed(4) };
  });
}

// ---- Public API (same interface as before) ----
export const COIN_DATA = new Proxy({}, {
  get(_, symbol) { return _coinData[symbol] || []; }
});

export function getLatestSnapshot(symbol) {
  return _latestSnapshots[symbol] || null;
}

// On-chain data (still mock — would need a dedicated API like Glassnode)
export const ONCHAIN_DATA = {
  BTC: {
    activeAddresses: 924_531, activeAddressesChange: 0.032,
    exchangeInflow: 12_450, exchangeInflowUSD: 862_000_000,
    exchangeOutflow: 15_200, exchangeOutflowUSD: 1_051_000_000,
    whaleTransactions: 847, whaleTransactionsChange: -0.05,
  },
  ETH: {
    activeAddresses: 512_872, activeAddressesChange: 0.018,
    exchangeInflow: 89_300, exchangeInflowUSD: 189_000_000,
    exchangeOutflow: 102_400, exchangeOutflowUSD: 217_000_000,
    whaleTransactions: 1_234, whaleTransactionsChange: 0.12,
  },
  SOL: {
    activeAddresses: 1_234_567, activeAddressesChange: 0.075,
    exchangeInflow: 3_200_000, exchangeInflowUSD: 464_000_000,
    exchangeOutflow: 2_800_000, exchangeOutflowUSD: 406_000_000,
    whaleTransactions: 312, whaleTransactionsChange: -0.02,
  },
};

// ---- Initialize: load real data on import ----
export const dataReady = loadRealData();
