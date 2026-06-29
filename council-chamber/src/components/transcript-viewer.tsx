import { useRef, useEffect } from "react";
import { TrendingUp, TrendingDown, Minus, MessageSquare, Loader2 } from "lucide-react";
import { DebateMessage } from "../data/debates";
import { agents } from "../data/agents";

interface TranscriptViewerProps {
  messages: DebateMessage[];
  activeStock: {
    ticker: string;
    price: number;
  };
  isStreaming: boolean;
}

function StanceIcon({ stance }: { stance: "bullish" | "bearish" | "neutral" }) {
  switch (stance) {
    case "bullish":
      return <TrendingUp className="w-3 h-3 text-emerald-400" />;
    case "bearish":
      return <TrendingDown className="w-3 h-3 text-rose-400" />;
    case "neutral":
      return <Minus className="w-3 h-3 text-amber-400" />;
  }
}

function StanceBadge({ stance }: { stance: "bullish" | "bearish" | "neutral" }) {
  if (stance === "bullish") {
    return (
      <span className="text-[9px] bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 px-1.5 py-0.5 rounded font-mono font-bold tracking-wider">
        BOĞA
      </span>
    );
  }
  if (stance === "bearish") {
    return (
      <span className="text-[9px] bg-rose-950/60 text-rose-400 border border-rose-800/60 px-1.5 py-0.5 rounded font-mono font-bold tracking-wider">
        AYI
      </span>
    );
  }
  return (
    <span className="text-[9px] bg-amber-950/60 text-amber-400 border border-amber-800/60 px-1.5 py-0.5 rounded font-mono font-bold tracking-wider">
      NÖTR
    </span>
  );
}

export function TranscriptViewer({ messages, activeStock, isStreaming }: TranscriptViewerProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isStreaming]);

  return (
    <div className="border border-slate-800 rounded-xl bg-[#080d16] overflow-hidden h-full flex flex-col shadow-xl">
      
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-slate-900/80 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-emerald-400" />
          <span className="text-sm text-white font-bold tracking-wider font-mono">TRANSCRIPT</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
          <span>{activeStock.ticker}</span>
          <span className="w-1 h-1 rounded-full bg-slate-600" />
          <span>{new Date().toLocaleDateString("tr-TR")}</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-emerald-400">RECV</span>
        </div>
      </div>

      {/* Context bar */}
      <div className="px-4 py-2 bg-[#050a12] border-b border-slate-800/60">
        <span className="text-xs text-slate-500 font-mono">
          <span className="text-emerald-400">$</span>{" "}
          {activeStock.ticker} · Anlık piyasa analizi başlatıldı
        </span>
      </div>

      {/* Messages Feed */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[420px] max-h-[560px]"
      >
        {messages.length === 0 && !isStreaming && (
          <div className="flex flex-col items-center justify-center h-40 text-slate-600 font-mono text-xs gap-3">
            <MessageSquare className="w-8 h-8 opacity-30" />
            <span>Konuşma akışı bekleniyor...</span>
          </div>
        )}

        {messages.map((msg, i) => {
          const agent = agents.find((a) => a.id === msg.agentId);

          return (
            <div
              key={i}
              className="fade-in-up"
              style={{ animationDelay: `${i * 0.05}s` }}
            >
              <div className="flex items-start gap-3">
                {/* Avatar */}
                <div
                  className={`flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center border text-[11px] font-bold ${
                    agent ? agent.color : "text-slate-400 bg-slate-800 border-slate-700"
                  }`}
                >
                  {agent ? (
                    <i className={`fa-solid ${agent.icon}`} />
                  ) : (
                    msg.agentName.split(" ").map((s) => s[0]).join("").slice(0, 2)
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  {/* Name row */}
                  <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                    <span className="text-sm font-bold text-white leading-none">{msg.agentName}</span>
                    <StanceBadge stance={msg.stance} />
                    <div className="flex items-center gap-1 ml-auto">
                      <StanceIcon stance={msg.stance} />
                      <span className="text-[10px] text-slate-600 font-mono">
                        {new Date(msg.timestamp).toLocaleTimeString("tr-TR")}
                      </span>
                    </div>
                  </div>

                  {/* Message bubble */}
                  <div
                    className={`p-3 rounded-lg border text-sm text-slate-300 leading-relaxed ${
                      msg.stance === "bullish"
                        ? "bg-emerald-950/20 border-emerald-900/40"
                        : msg.stance === "bearish"
                        ? "bg-rose-950/20 border-rose-900/40"
                        : "bg-slate-900/40 border-slate-800/40"
                    }`}
                  >
                    {msg.message}
                  </div>
                </div>
              </div>
            </div>
          );
        })}

        {/* Streaming indicator */}
        {isStreaming && (
          <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-950/20 border border-blue-900/30">
            <Loader2 className="w-4 h-4 text-blue-400 animate-spin flex-shrink-0" />
            <span className="text-xs text-blue-400 font-mono">
              Sıradaki analist hazırlanıyor
              <span className="cursor-blink"> _</span>
            </span>
          </div>
        )}

        {/* Transcript end */}
        {!isStreaming && messages.length > 0 && (
          <div className="flex items-center gap-2 text-xs text-slate-600 font-mono pt-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            TRANSCRIPT_END // {messages.length} STATEMENT(S) LOGGED
          </div>
        )}
      </div>
    </div>
  );
}
