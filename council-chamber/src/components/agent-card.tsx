import { X } from "lucide-react";
import type { Analyst } from "../data/agents";

interface AgentCardProps {
  analyst: Analyst;
  onClose: () => void;
}

export function AgentCard({ analyst, onClose }: AgentCardProps) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-md mx-4 border bg-[#090d16] rounded-xl p-6 fade-in-up shadow-2xl"
        onClick={(e) => e.stopPropagation()}
        style={{ borderColor: "rgba(59,130,246,0.3)", boxShadow: "0 0 40px rgba(59,130,246,0.1)" }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-slate-500 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-4 mb-5">
          <div className={`w-14 h-14 rounded-xl flex items-center justify-center border ${analyst.color}`}>
            <i className={`fa-solid ${analyst.icon} text-xl`} />
          </div>
          <div>
            <h3 className="text-white font-bold text-lg">{analyst.name}</h3>
            <p className="text-slate-400 text-xs font-mono tracking-wide">{analyst.title}</p>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-4">
          <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
            <span className="text-slate-500 text-[10px] uppercase tracking-widest font-mono block mb-2">
              Yatırım Felsefesi
            </span>
            <p className="text-slate-300 text-sm leading-relaxed">{analyst.philosophy}</p>
          </div>

          <div className="pt-3 border-t border-slate-800/50 flex items-center justify-between">
            <span className="text-slate-500 text-[10px] uppercase tracking-widest font-mono">
              Analist ID
            </span>
            <p className="text-emerald-400 text-sm font-mono font-bold">
              ANALYST_{String(analyst.id).padStart(2, "0")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
