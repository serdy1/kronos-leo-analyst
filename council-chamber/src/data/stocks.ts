export interface StockQuote {
  ticker: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  targetPrice?: number;
  buybackTarget?: number;
  currency?: string;
}

export interface StockData {
  quotes: StockQuote[];
  lastUpdated: string;
}

export const stocks: StockData = {
  quotes: [
    { ticker: "THYAO", name: "Türk Hava Yolları", price: 330.75, change: 2.25, changePercent: 0.68, targetPrice: 442.82 },
    { ticker: "FROTO", name: "Ford Otosan", price: 954.50, change: -14.00, changePercent: -1.45, targetPrice: 1120.00, buybackTarget: 900.00 },
    { ticker: "PGSUS", name: "Pegasus", price: 215.20, change: 5.80, changePercent: 2.77, targetPrice: 260.00 },
    { ticker: "ANHYT", name: "Anadolu Hayat", price: 78.35, change: -0.65, changePercent: -0.82, targetPrice: 95.00 },
    { ticker: "NFLX", name: "Netflix Inc.", price: 692.45, change: 15.30, changePercent: 2.26, targetPrice: 750.00, currency: "$" },
  ],
  lastUpdated: new Date().toISOString(),
};
