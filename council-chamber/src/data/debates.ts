export interface DebateMessage {
  agentId: number;
  agentName: string;
  message: string;
  timestamp: string;
  stance: "bullish" | "bearish" | "neutral";
}

export interface DebateSession {
  date: string;
  ticker: string;
  context: string;
  messages: DebateMessage[];
}

export const debates: DebateSession[] = [
  {
    date: "2026-06-29",
    ticker: "FROTO",
    context: "Daily placeholder — data pipeline not yet configured.",
    messages: [],
  },
];
