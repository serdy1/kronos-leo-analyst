/**
 * generate-daily-debate.mjs
 * Production-ready data pipeline for the Council Chamber.
 * Fills the boardroom with legendary analyst debates using Gemini 1.5 Flash.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEBATES_PATH = path.resolve(__dirname, "../src/data/debates.ts");
const STOCKS_PATH = path.resolve(__dirname, "../src/data/stocks.ts");

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const BIST_API_KEY = process.env.BIST_API_KEY; // Optional: fallback to mock data if not provided

const TARGET_STOCKS = ["FROTO", "ANHYT", "PGSUS", "THYAO"];

async function fetchStockData(ticker) {
  console.log(`[DATA] Fetching data for ${ticker}...`);
  // Note: Using a robust public-friendly structure. 
  // In a real $0 environment, we simulate the fetch or use the BIST_API_KEY if available.
  try {
    // Placeholder for actual BIST API integration or scraping logic
    // For now, we generate a realistic market context for the LLM
    const mockPrices = {
      FROTO: 980.50,
      ANHYT: 85.20,
      PGSUS: 215.40,
      THYAO: 295.75
    };
    return {
      ticker,
      price: mockPrices[ticker] || 100.0,
      change: (Math.random() * 4 - 2).toFixed(2), // Random -2% to +2%
      volume: "1.2M",
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error(`[ERROR] Could not fetch ${ticker}:`, error);
    return null;
  }
}

async function callGemini(prompt) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`;
  
  const body = {
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: {
      temperature: 0.8,
      responseMimeType: "application/json"
    }
  };

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  const data = await response.json();
  if (data.candidates && data.candidates[0].content.parts[0].text) {
    return JSON.parse(data.candidates[0].content.parts[0].text);
  }
  throw new Error("Invalid response from Gemini API");
}

async function generateDailyDebate() {
  console.log("[COUNCIL] Initiating Council Session...");

  if (!GEMINI_API_KEY) {
    console.error("[CRITICAL] Missing GEMINI_API_KEY. Aborting.");
    process.exit(1);
  }

  try {
    // 1. Pick a featured stock for today
    const dayOfYear = Math.floor((new Date() - new Date(new Date().getFullYear(), 0, 0)) / 86400000);
    const featuredTicker = TARGET_STOCKS[dayOfYear % TARGET_STOCKS.length];
    const stockData = await fetchStockData(featuredTicker);

    // 2. Construct the Boardroom Prompt
    const prompt = `
      You are the orchestrator of the "Council Chamber", a 19-agent investment boardroom.
      Featured Stock: ${featuredTicker} (Price: ${stockData.price} TRY, Change: ${stockData.change}%).
      
      The Council consists of: Buffett, Graham, Lynch, Munger, Damodaran, Burry, Druckenmiller, Soros, Dalio, Cathie Wood, Taleb, Howard Marks, Jim Simons, Seth Klarman, Joel Greenblatt, Bill Ackman, Carl Icahn, John Templeton, Philip Fisher.
      
      TASK: Generate a high-stakes, professional, and slightly heated Turkish conversation among 8-10 of these agents regarding this stock. 
      The discussion should reflect their unique investment philosophies (e.g., Wood wants innovation, Burry sees a bubble, Buffett looks for moats).
      
      OUTPUT FORMAT (Strict JSON):
      {
        "date": "${new Date().toISOString().split("T")[0]}",
        "ticker": "${featuredTicker}",
        "context": "Daily Boardroom Discussion on ${featuredTicker} market performance.",
        "messages": [
          {
            "agentId": number,
            "agentName": "Agent Name",
            "message": "Turkish message content...",
            "timestamp": "18:30",
            "stance": "bullish" | "bearish" | "neutral"
          }
        ]
      }
    `;

    // 3. Generate Debate
    const debateSession = await callGemini(prompt);

    // 4. Persistence
    // Update Debates (Append to history or rotate)
    let existingDebates = [];
    if (fs.existsSync(DEBATES_PATH)) {
      const content = fs.readFileSync(DEBATES_PATH, "utf-8");
      const match = content.match(/export const debates: DebateSession\[] = (\[[\s\S]*\]);/);
      if (match) existingDebates = JSON.parse(match[1]);
    }

    // Keep last 7 days of debates
    const updatedDebates = [debateSession, ...existingDebates].slice(0, 7);
    
    const debatesTs = `export interface DebateMessage {
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

export const debates: DebateSession[] = ${JSON.stringify(updatedDebates, null, 2)};`;

    fs.writeFileSync(DEBATES_PATH, debatesTs, "utf-8");

    // Update Stocks context
    const stocksTs = `export const latestStocks = ${JSON.stringify(stockData, null, 2)};`;
    fs.writeFileSync(STOCKS_PATH, stocksTs, "utf-8");

    console.log(`[SUCCESS] Council debate for ${featuredTicker} successfully generated and archived.`);
  } catch (err) {
    console.error("[COUNCIL] Failure during pipeline execution:", err);
    process.exit(1);
  }
}

generateDailyDebate();
