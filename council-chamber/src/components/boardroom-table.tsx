import { useState } from "react";
import { agents } from "../data/agents";
import { AgentCard } from "./agent-card";

interface BoardroomTableProps {
  activeStock: {
    ticker: string;
    price: number;
    currency?: string;
  };
  currentSpeaker: string | null;
  activeSessionAgentIds: number[];
}

export function BoardroomTable({ 
  activeStock, 
  currentSpeaker, 
  activeSessionAgentIds 
}: BoardroomTableProps) {
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null);

  const total = agents.length;
  const radiusX = 240; // Horizontal radius
  const radiusY = 75;  // Vertical radius for 3D ellipse perspective

  return (
    <>
      <div className="flex flex-col items-center justify-center py-6">
        <h4 className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-10">
          <i className="fa-solid fa-circle-nodes text-blue-500 mr-1.5" /> CANLI OTURUM ODASI
        </h4>
        
        <div className="boardroom-perspective w-full max-w-2xl h-72 flex items-center justify-center relative">
          
          {/* CENTER BOARDROOM TABLE */}
          <div className="boardroom-table w-80 h-28 bg-gradient-to-b from-amber-900 to-amber-950 border-4 border-amber-800 rounded-full flex items-center justify-center relative shadow-[0_25px_60px_rgba(0,0,0,0.8)] z-10">
            <div className="absolute inset-2 bg-slate-950/90 rounded-full border border-amber-900/40 flex flex-col items-center justify-center p-2 text-center">
              <span className="text-[10px] font-bold text-slate-400 tracking-wider uppercase font-mono">
                {activeStock.ticker} ANALİZİ
              </span>
              <span className="text-[10px] text-blue-400 font-mono mt-0.5">
                {activeStock.price.toFixed(2)} ₺
              </span>
            </div>
          </div>

          {/* CIRCULAR ANALYST SEATS */}
          {agents.map((agent, i) => {
            const angle = (i / total) * Math.PI * 2 - Math.PI / 2;
            const x = radiusX * Math.cos(angle);
            const y = radiusY * Math.sin(angle);

            const isSpeaking = currentSpeaker && agent.name.toLowerCase().includes(currentSpeaker.toLowerCase());
            const isAtTable = activeSessionAgentIds.includes(agent.id);

            // 3D layering z-index
            let zIndex = y < 0 ? 5 : 15;
            if (isSpeaking) zIndex = 30;

            return (
              <button
                key={agent.id}
                onClick={() => setSelectedAgent(agent.id)}
                className="absolute flex flex-col items-center transition-all duration-500 cursor-pointer group"
                style={{
                  left: `calc(50% + ${x}px)`,
                  top: `calc(50% + ${y}px)`,
                  transform: `translate(-50%, -50%) scale(${isSpeaking ? 1.15 : 1})`,
                  zIndex: zIndex,
                }}
              >
                {/* Seat Avatar Container */}
                <div 
                  className={`w-12 h-12 rounded-full flex items-center justify-center relative border transition-all duration-300 ${
                    isSpeaking
                      ? "bg-blue-900 border-blue-400 shadow-[0_0_20px_rgba(59,130,246,0.6)]"
                      : isAtTable
                      ? "bg-[#0f172a] border-blue-500/50"
                      : "bg-[#090d16] border-slate-800 hover:border-slate-600"
                  }`}
                >
                  {/* Analyst Icon inside */}
                  <div className={`w-9.5 h-9.5 rounded-full flex items-center justify-center border text-xs font-semibold ${agent.color}`}>
                    <i className={`fa-solid ${agent.icon} text-xs`} />
                  </div>

                  {/* Pulsing Neon Glow Ring for Speaker */}
                  {isSpeaking && (
                    <span className="absolute -inset-1 rounded-full border border-blue-400 animate-ping opacity-60 pointer-events-none" />
                  )}
                </div>

                {/* Name Label */}
                <div 
                  className={`mt-1.5 px-1.5 py-0.5 rounded text-[8px] font-bold tracking-tight whitespace-nowrap shadow-md font-mono ${
                    isSpeaking 
                      ? "bg-blue-500 text-white border border-blue-400"
                      : isAtTable
                      ? "bg-blue-950/80 text-blue-300 border border-blue-900/60"
                      : "bg-[#090d16] text-slate-400 border border-slate-800/80 group-hover:border-slate-500 group-hover:text-slate-200 transition-colors"
                  }`}
                >
                  {agent.name.split(" ")[0]}
                </div>
              </button>
            );
          })}

        </div>
      </div>

      {selectedAgent && (
        <AgentCard
          analyst={agents.find((a) => a.id === selectedAgent)!}
          onClose={() => setSelectedAgent(null)}
        />
      )}
    </>
  );
}
