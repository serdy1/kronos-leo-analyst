import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEBATES_PATH = path.resolve(__dirname, "../src/data/debates.ts");
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const FIXED_USDTRY = 47.98;
const TARGET_STOCKS = ["FROTO", "ANHYT", "PGSUS", "THYAO", "KCHOL"];
const LATEST_CLOSING_PRICES = { FROTO: 80.20, KCHOL: 222.40, PGSUS: 149.50 };
async function fetchStockData(ticker) {
  const prices = { ...LATEST_CLOSING_PRICES, ANHYT: 85.20, THYAO: 295.75 };
  const price = prices[ticker] || 100;
  return { ticker, price, currency: "TRY", usdTry: FIXED_USDTRY, priceUSD: price / FIXED_USDTRY, change: "0.00", volume: "1.2M", timestamp: new Date().toISOString() };
}
async function callGemini(prompt) {
  const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { temperature: 0.8, responseMimeType: "application/json" } }) });
  const data = await response.json();
  if (data.candidates?.[0]?.content?.parts?.[0]?.text) return JSON.parse(data.candidates[0].content.parts[0].text);
  throw new Error("Invalid response from Gemini API");
}
async function generateDailyDebate() {
  if (!GEMINI_API_KEY) process.exit(1);
  const dayOfYear = Math.floor((new Date() - new Date(new Date().getFullYear(), 0, 0)) / 86400000);
  const ticker = TARGET_STOCKS[dayOfYear % TARGET_STOCKS.length];
  const stock = await fetchStockData(ticker);
  const debate = await callGemini(`Generate a Turkish investment debate for ${ticker}. Latest close: ${stock.price} TRY. Fixed USD/TRY: ${FIXED_USDTRY}. USD equivalent: ${stock.priceUSD.toFixed(4)}. Return strict JSON with date, ticker, context, messages.`);
  let existing = [];
  if (fs.existsSync(DEBATES_PATH)) { const match = fs.readFileSync(DEBATES_PATH, "utf8").match(/export const debates: DebateSession\[\] = (\[[\s\S]*\]);/); if (match) existing = JSON.parse(match[1]); }
  fs.writeFileSync(DEBATES_PATH, `export interface DebateMessage { agentId: number; agentName: string; message: string; timestamp: string; stance: "bullish" | "bearish" | "neutral"; }\nexport interface DebateSession { date: string; ticker: string; context: string; messages: DebateMessage[]; }\nexport const debates: DebateSession[] = ${JSON.stringify([debate, ...existing].slice(0, 7), null, 2)};`);
}
generateDailyDebate().catch((error) => { console.error(error); process.exit(1); });
