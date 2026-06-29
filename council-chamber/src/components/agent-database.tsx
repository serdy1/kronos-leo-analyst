import { analysts, Analyst } from "../data/agents";

interface AgentDatabaseProps {
  onSelect: (agent: Analyst) => void;
}

const statusFilters = [
  { label: "Tümü", value: "all" },
  { label: "MASADA", value: "MASADA" },
  { label: "AKTİF", value: "AKTİF" },
  { label: "EMEKLİ", value: "EMEKLİ" },
];

export function AgentDatabase({ onSelect }: AgentDatabaseProps) {
  return (
    <div className="w-64 shrink-0 border-r border-slate-800 bg-[#0a0f24] flex flex-col overflow-hidden">
      <div className="p-3 border-b border-slate-800">
        <h2 className="text-sm font-semibold text-slate-300 tracking-wide flex items-center gap-2">
          <i className="fa-solid fa-users text-indigo-400" />
          Konsey Üyeleri
          <span className="ml-auto text-[10px] font-mono text-slate-500">19</span>
        </h2>
      </div>
      <div className="flex gap-1 px-3 py-2 border-b border-slate-800/60">
        {statusFilters.map((f) => (
          <button
            key={f.value}
            className="px-2.5 py-1 text-[10px] font-medium rounded-md bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 hover:text-slate-200 transition-colors"
          >
            {f.label}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {analysts.map((agent) => (
          <button
            key={agent.id}
            onClick={() => onSelect(agent)}
            className="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-slate-800/60 transition-colors border-b border-slate-800/30 text-left group"
          >
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs ${agent.bgColor} ${agent.textColor} ${agent.borderColor} border shrink-0`}
            >
              <i className={`fa-solid ${agent.icon}`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-medium text-slate-200 truncate">
                  {agent.name}
                </span>
              </div>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="text-[9px] text-slate-500 truncate">{agent.title}</span>
                <span
                  className={`text-[8px] font-semibold px-1 py-0.5 rounded ${
                    agent.badge === "MASADA"
                      ? "bg-emerald-950/60 text-emerald-400"
                      : agent.badge === "AKTİF"
                        ? "bg-blue-950/60 text-blue-400"
                        : "bg-slate-800 text-slate-500"
                  }`}
                >
                  {agent.badge}
                </span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
