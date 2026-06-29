import { useState, useEffect } from "react";
import { stocks, StockQuote } from "./data/stocks";
import { debates, DebateMessage } from "./data/debates";
import { analysts, Analyst } from "./data/agents";
import { AgentDatabase } from "./components/agent-database";
import { StockTicker } from "./components/stock-ticker";
import { WelcomeDashboard } from "./components/welcome-dashboard";
import { BoardroomTable } from "./components/boardroom-table";
import { TranscriptViewer } from "./components/transcript-viewer";

function findSpeakerAgentIds(messages: DebateMessage[]): string[] {
  const ids: string[] = [];
  for (const msg of messages) {
    const found = analysts.find(
      (a) => a.name.toLowerCase() === msg.speaker.toLowerCase()
    );
    if (found && !ids.includes(found.id)) ids.push(found.id);
  }
  return ids;
}

export default function App() {
  const [activeTicker, setActiveTicker] = useState<string | null>(null);
  const [streamedMessages, setStreamedMessages] = useState<DebateMessage[]>([]);
  const [currentSpeaker, setCurrentSpeaker] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [systemTime, setSystemTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setSystemTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!activeTicker) {
      setStreamedMessages([]);
      setCurrentSpeaker(null);
      setIsStreaming(false);
      return;
    }

    const session = debates.find((d) => d.ticker === activeTicker);
    if (!session) return;

    setIsStreaming(true);
    setStreamedMessages([]);
    setCurrentSpeaker(null);

    const agentIds = findSpeakerAgentIds(session.messages);
    let idx = 0;
    const interval = setInterval(() => {
      if (idx < session.messages.length) {
        const nextMsg = session.messages[idx];
        setCurrentSpeaker(agentIds[idx] || null);
        setStreamedMessages((prev) => [...prev, nextMsg]);
        idx++;
      } else {
        clearInterval(interval);
        setIsStreaming(false);
        setCurrentSpeaker(null);
      }
    }, 3500);

    return () => clearInterval(interval);
  }, [activeTicker]);

  const activeStock = stocks.quotes.find((s) => s.ticker === activeTicker) || null;
  const activeSession = activeTicker ? debates.find((d) => d.ticker === activeTicker) : null;
  const activeAgentIds = activeSession ? findSpeakerAgentIds(activeSession.messages) : [];
  const activeAgents = activeAgentIds
    .map((id) => analysts.find((a) => a.id === id))
    .filter((a): a is Analyst => a !== undefined);

  const handleStockSelect = (stock: StockQuote) => {
    setActiveTicker(stock.ticker);
  };

  const formatTime = (d: Date) =>
    d.toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" });

  const formatDate = (d: Date) =>
    d.toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });

  const potential = activeStock
    ? ((activeStock.targetPrice - activeStock.price) / activeStock.price) * 100
    : 0;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-300 flex font-sans overflow-hidden">
      <AgentDatabase onSelect={() => {}} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="flex items-center justify-between px-4 py-2 bg-[#0a0f24] border-b border-slate-800 shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <i className="fa-solid fa-chess-king text-indigo-400 text-sm" />
              <span className="text-xs font-bold text-white tracking-wider uppercase">
                Konsey Odası
              </span>
            </div>
            <span className="text-[10px] text-slate-600 font-mono px-2 py-0.5 border border-slate-700 rounded">
              v2.0
            </span>
          </div>
          <div className="flex items-center gap-3 text-[10px] font-mono text-slate-500">
            <span className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              CANLI
            </span>
            <span>{formatDate(systemTime)}</span>
            <span className="text-slate-600">{formatTime(systemTime)}</span>
          </div>
        </header>

        <StockTicker activeTicker={activeTicker} onSelect={handleStockSelect} />

        <main className="flex-1 overflow-y-auto bg-[#040814]">
          {!activeStock && <WelcomeDashboard />}

          {activeStock && activeSession && (
            <div className="flex flex-col h-full">
              <div className="bg-[#040814]/95 backdrop-blur border-b border-slate-800 px-6 py-4">
                <div className="flex items-baseline gap-3 mb-1">
                  <h1 className="text-2xl font-bold text-white tracking-tight">
                    {activeStock.ticker}
                  </h1>
                  <span className="text-sm text-slate-400">{activeStock.name}</span>
                </div>
                <div className="flex items-center gap-4 mt-1">
                  <span className="text-xl font-mono text-slate-200">
                    {activeStock.currency}
                    {activeStock.price.toLocaleString("tr-TR", {
                      minimumFractionDigits: 2,
                    })}
                  </span>
                  <span
                    className={`text-xs font-mono font-semibold px-2 py-0.5 rounded border ${
                      activeStock.change >= 0
                        ? "bg-emerald-950/60 text-emerald-400 border-emerald-800"
                        : "bg-red-950/60 text-red-400 border-red-800"
                    }`}
                  >
                    {activeStock.change >= 0 ? "+" : ""}
                    {activeStock.change}%
                  </span>
                  <span className="text-xs text-slate-600">| Hedef: {activeStock.targetPrice.toLocaleString("tr-TR", { minimumFractionDigits: 2 })}</span>
                  <span className="text-xs text-emerald-500">
                    Potansiyel: +{potential.toFixed(1)}%
                  </span>
                </div>
              </div>

              <div className="flex-1 flex gap-6 p-6">
                <div className="flex-1 bg-slate-950/40 border border-slate-800/80 rounded-xl p-4 min-h-[400px] relative">
                  <BoardroomTable
                    activeAgents={activeAgents}
                    currentSpeaker={currentSpeaker}
                  />
                </div>
                <div className="w-[420px] shrink-0 bg-slate-950/40 border border-slate-800/80 rounded-xl flex flex-col">
                  <div className="px-4 py-2 border-b border-slate-800/60 flex items-center gap-2">
                    <i className="fa-solid fa-comment text-blue-400 text-[10px]" />
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                      Tartışma Kaydı
                    </span>
                    {isStreaming && (
                      <span className="ml-auto text-[10px] text-emerald-400 animate-pulse flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        Canlı
                      </span>
                    )}
                  </div>
                  <TranscriptViewer
                    messages={streamedMessages}
                    currentSpeaker={currentSpeaker}
                  />
                </div>
              </div>
            </div>
          )}
        </main>

        <footer className="border-t border-slate-800 px-4 py-2 bg-[#0a0f24] shrink-0">
          <div className="flex items-center justify-between text-[9px] text-slate-600 font-mono">
            <span>COUNCIL CHAMBER v2.0 // {analysts.length} ANALYST DATABASE</span>
            <span>UPDATED: {formatDate(systemTime)} {formatTime(systemTime)}</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
