import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEBATES_PATH = path.resolve(__dirname, "../src/data/debates.ts");
const STOCKS_PATH = path.resolve(__dirname, "../src/data/stocks.ts");
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

const FIXED_USDTRY = 46.67;
const TARGET_STOCKS = ["FROTO", "ANHYT", "PGSUS", "THYAO", "KCHOL"];
const LATEST_CLOSING_PRICES = {
  FROTO: 80.20,
  KCHOL: 222.40,
  PGSUS: 149.50,
};

async function fetchStockData(ticker) {
  const mockPrices = {
    ...LATEST_CLOSING_PRICES,
    ANHYT: 85.20,
    THYAO: 295.75,
  };
  return {
    ticker,
    price: mockPrices[ticker] || 100.0,
    currency: "TRY",
    usdTry: FIXED_USDTRY,
    priceUSD: (mockPrices[ticker] || 100.0) / FIXED_USDTRY,
    change: "0.00",
    volume: "1.2M",
    timestamp: new Date().toISOString(),
  };
}

async function callGemini(prompt) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`;
  const response = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { temperature: 0.8, responseMimeType: "application/json" } }) });
  const data = await response.json();
  if (data.candidates?.[0]?.content?.parts?.[0]?.text) return JSON.parse(data.candidates[0].content.parts[0].text);
  throw new Error("Invalid response from Gemini API");
}

async function generateDailyDebate() {
  if (!GEMINI_API_KEY) { console.error("[CRITICAL] Missing GEMINI_API_KEY. Aborting."); process.exit(1); }
  try {
    const dayOfYear = Math.floor((new Date() - new Date(new Date().getFullYear(), 0, 0)) / 86400000);
    const featuredTicker = TARGET_STOCKS[dayOfYear % TARGET_STOCKS.length];
    const stockData = await fetchStockData(featuredTicker);
    const prompt = `You are the orchestrator of the Council Chamber investment boardroom. Featured Stock: ${featuredTicker} (latest closing price: ${stockData.price} TRY; USD/TRY: ${FIXED_USDTRY}; USD equivalent: ${stockData.priceUSD.toFixed(4)}). Generate a professional Turkish debate among 8-10 analysts. Return strict JSON with date, ticker, context, and messages (agentId, agentName, message, timestamp, stance).`;
    const debateSession = await callGemini(prompt);
    let existingDebates = [];
    if (fs.existsSync(DEBATES_PATH)) {
      const content = fs.readFileSync(DEBATES_PATH, "utf-8");
      const match = content.match(/export const debates: DebateSession\[\] = (\[[\s\S]*\]);/);
      if (match) existingDebates = JSON.parse(match[1]);
    }
    const debatesTs = `export interface DebateMessage { agentId: number; agentName: string; message: string; timestamp: string; stance: "bullish" | "bearish" | "neutral"; }\n\nexport interface DebateSession { date: string; ticker: string; context: string; messages: DebateMessage[]; }\n\nexport const debates: DebateSession[] = ${JSON.stringify([debateSession, ...existingDebates].slice(0, 7), null, 2)};`;
    fs.writeFileSync(DEBATES_PATH, debatesTs, "utf-8");
    console.log(`[SUCCESS] Debate generated for ${featuredTicker} using fixed USD/TRY ${FIXED_USDTRY}.`);
  } catch (err) { console.error("[COUNCIL] Failure during pipeline execution:", err); process.exit(1); }
}

generateDailyDebate();
