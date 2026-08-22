import { FIXED_USDTRY, StockQuote, stocks } from "./stocks";

const YAHOO_SYMBOLS: Record<string, string> = {
  FROTO: "FROTO.IS", KCHOL: "KCHOL.IS", PGSUS: "PGSUS.IS", THYAO: "THYAO.IS", ANHYT: "ANHYT.IS", DOAS: "DOAS.IS", NFLX: "NFLX",
};

export async function fetchLiveQuotes(): Promise<StockQuote[]> {
  try {
    const results = await Promise.all(stocks.quotes.map(async (quote) => {
      const symbol = encodeURIComponent(YAHOO_SYMBOLS[quote.ticker] ?? quote.ticker);
      const response = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?range=1d&interval=1d`, { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`Yahoo Finance ${response.status}`);
      const json = await response.json();
      const meta = json.chart?.result?.[0]?.meta;
      const price = Number(meta?.regularMarketPrice ?? meta?.previousClose);
      if (!Number.isFinite(price) || price <= 0) throw new Error("Invalid quote");
      return { ...quote, price, change: Number(meta?.regularMarketChangePercent ?? quote.change) };
    }));
    return results;
  } catch {
    return stocks.quotes;
  }
}

export { FIXED_USDTRY };
