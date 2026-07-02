export interface StockQuote {
  ticker: string;
  name: string;
  sector: string;
  price: number;
  targetPrice: number;
  currency: string;
  change: number;
}

export interface StockData {
  quotes: StockQuote[];
  lastUpdated: string;
}

export const stocks: StockData = {
  quotes: [
    { ticker: "THYAO", name: "Türk Hava Yolları", sector: "Havacılık", price: 330.75, targetPrice: 442.82, currency: "₺", change: 0.68 },
    { ticker: "FROTO", name: "Ford Otosan", sector: "Otomotiv", price: 1120.25, targetPrice: 1450.00, currency: "₺", change: -1.45 },
    { ticker: "PGSUS", name: "Pegasus", sector: "Havacılık", price: 242.10, targetPrice: 310.50, currency: "₺", change: 1.20 },
    { ticker: "ANHYT", name: "Anadolu Hayat", sector: "Sigorta", price: 102.50, targetPrice: 145.00, currency: "₺", change: 2.15 },
    { ticker: "DOAS", name: "Doğuş Otomotiv", sector: "Otomotiv", price: 185.30, targetPrice: 280.00, currency: "₺", change: 0.38 },
    { ticker: "KCHOL", name: "Koç Holding", sector: "Holding", price: 224.10, targetPrice: 290.00, currency: "₺", change: 0.85 },
    { ticker: "NFLX", name: "Netflix Inc.", sector: "Teknoloji / Medya", price: 73.85, targetPrice: 102.50, currency: "$", change: -0.90 },
  ],
  lastUpdated: new Date().toISOString(),
};
