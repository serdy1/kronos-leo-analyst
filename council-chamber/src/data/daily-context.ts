export interface KapDisclosure {
  company: string;
  title: string;
  date: string;
  url: string;
}

export interface BofaFlowData {
  date: string;
  akdBuying: number;
  akdSelling: number;
  netPosition: number;
}

export interface InsiderTransaction {
  company: string;
  insider: string;
  type: "buy" | "sell";
  shares: number;
  value: number;
  date: string;
}

export interface MacroEvent {
  title: string;
  date: string;
  impact: "high" | "medium" | "low";
  description: string;
}

export interface AnalystConsensus {
  ticker: string;
  targetPrice: number;
  currentPrice: number;
  rating: "AL" | "TUT" | "SAT";
  updatedDate: string;
}

export interface DailyContext {
  date: string;
  kapDisclosures: KapDisclosure[];
  bofaFlows: BofaFlowData[];
  insiderTransactions: InsiderTransaction[];
  macroEvents: MacroEvent[];
  analystConsensus: AnalystConsensus[];
}

export const dailyContext: DailyContext = {
  date: "2026-06-28",
  kapDisclosures: [
    {
      company: "FROTO",
      title: "2026 Yılı 1. Çeyrek Finansal Raporu - Net Kar 4.2 Milyar TL",
      date: "2026-06-28",
      url: "https://kap.org.tr/Bildirim/123456",
    },
    {
      company: "ANHYT",
      title: "Hisse Geri Alım Programı Başlatılması - 50 Milyon TL",
      date: "2026-06-27",
      url: "https://kap.org.tr/Bildirim/123457",
    },
    {
      company: "PGSUS",
      title: "Mayıs 2026 Trafik Verileri - Yolcu Sayısı %14 Arttı",
      date: "2026-06-26",
      url: "https://kap.org.tr/Bildirim/123458",
    },
  ],
  bofaFlows: [
    { date: "2026-06-28", akdBuying: 45_000_000, akdSelling: 28_000_000, netPosition: 17_000_000 },
    { date: "2026-06-25", akdBuying: 38_000_000, akdSelling: 42_000_000, netPosition: -4_000_000 },
    { date: "2026-06-24", akdBuying: 52_000_000, akdSelling: 31_000_000, netPosition: 21_000_000 },
  ],
  insiderTransactions: [
    { company: "FROTO", insider: "Ali Koç", type: "buy", shares: 25000, value: 23_750_000, date: "2026-06-25" },
    { company: "PGSUS", insider: "Mehmet Nane", type: "sell", shares: 10000, value: 2_152_000, date: "2026-06-24" },
  ],
  macroEvents: [
    {
      title: "TCMB Faiz Kararı - Politika Faizi %30'a İndirildi",
      date: "2026-06-25",
      impact: "high",
      description: "Türkiye Cumhuriyet Merkez Bankası beklentiler dahilinde faizi 250 baz puan indirdi.",
    },
    {
      title: "ABD Çekirdek PCE - Mayıs 2026",
      date: "2026-06-26",
      impact: "high",
      description: "ABD çekirdek enflasyonu aylık %0.2, yıllık %2.6 olarak gerçekleşti.",
    },
  ],
  analystConsensus: [
    { ticker: "FROTO", targetPrice: 1120, currentPrice: 954.50, rating: "AL", updatedDate: "2026-06-28" },
    { ticker: "ANHYT", targetPrice: 95, currentPrice: 78.35, rating: "AL", updatedDate: "2026-06-27" },
    { ticker: "PGSUS", targetPrice: 260, currentPrice: 215.20, rating: "AL", updatedDate: "2026-06-26" },
    { ticker: "NFLX", targetPrice: 750, currentPrice: 692.45, rating: "AL", updatedDate: "2026-06-28" },
  ],
};
