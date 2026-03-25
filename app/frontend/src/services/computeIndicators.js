/**
 * computeIndicators.js — 技术指标计算
 *
 * 从 mockData.js 中提取出来的纯计算逻辑。
 * 给定原始 price history，计算 SMA、EMA、RSI、MACD、Bollinger Bands 等。
 *
 * 被 useMarketData hook 调用：
 * - 对 CoinGecko 真实数据计算指标
 * - 对 mock 数据也可以用（保持一致性）
 */

/**
 * 计算指数移动平均线 (EMA)
 */
function exponentialMA(arr, index, span) {
  const k = 2 / (span + 1);
  let ema = arr[0];
  for (let i = 1; i <= Math.min(index, arr.length - 1); i++) {
    ema = arr[i] * k + ema * (1 - k);
  }
  return ema;
}

/**
 * 计算相对强弱指标 (RSI)
 */
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

/**
 * 给原始价格数据添加所有技术指标。
 *
 * @param {Array} history - 原始数据数组，每项至少包含 { date, price, volume, marketCap }
 * @returns {Array} 带有全部指标的数据数组
 */
export function addIndicators(history) {
  if (!history || history.length === 0) return [];

  const prices = history.map((d) => d.price);

  return history.map((d, i) => {
    // SMA 20
    const sma20Window = prices.slice(Math.max(0, i - 19), i + 1);
    const sma20 = sma20Window.reduce((a, b) => a + b, 0) / sma20Window.length;

    // SMA 50
    const sma50Window = prices.slice(Math.max(0, i - 49), i + 1);
    const sma50 = sma50Window.reduce((a, b) => a + b, 0) / sma50Window.length;

    // EMA 12 & 26
    const ema12 = exponentialMA(prices, i, 12);
    const ema26 = exponentialMA(prices, i, 26);

    // MACD
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
