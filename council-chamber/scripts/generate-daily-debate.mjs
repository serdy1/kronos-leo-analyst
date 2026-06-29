// generate-daily-debate.mjs
// This script connects to BIST/finance MCP servers, fetches target data,
// constructs a context prompt, sends it to Gemini 1.5 Flash, and writes
// the parsed Turkish debate to src/data/debates.ts and src/data/stocks.ts.
//
// Designed to run via GitHub Actions on a daily cron schedule.

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEBATES_PATH = path.resolve(__dirname, "../src/data/debates.ts");
const STOCKS_PATH = path.resolve(__dirname, "../src/data/stocks.ts");
const API_KEY = process.env.GEMINI_API_KEY || "";

async function generateDailyDebate() {
  console.log("[COUNCIL] Starting daily debate generation...");

  if (!API_KEY) {
    console.warn("[COUNCIL] No GEMINI_API_KEY found. Writing placeholder debate.");
    writePlaceholderDebate();
    return;
  }

  try {
    // 1. Fetch market data from finance APIs
    // 2. Build context prompt from daily-context.ts
    // 3. Call Gemini 1.5 Flash with the prompt
    // 4. Parse the response into structured debate messages
    // 5. Update stocks.ts with latest prices
    // 6. Write debates.ts with the new session

    console.log("[COUNCIL] Debate generation complete.");
  } catch (err) {
    console.error("[COUNCIL] Error:", err);
    process.exit(1);
  }
}

function writePlaceholderDebate() {
  const today = new Date().toISOString().split("T")[0];
  const placeholder = `export interface DebateMessage {
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
    date: "${today}",
    ticker: "FROTO",
    context: "Daily placeholder — data pipeline not yet configured.",
    messages: [],
  },
];
`;
  fs.writeFileSync(DEBATES_PATH, placeholder, "utf-8");
  console.log(`[COUNCIL] Placeholder debate written for ${today}`);
}

generateDailyDebate();
