import { Analyst } from "../data/agents";

interface BoardroomTableProps {
  activeAgents: Analyst[];
  currentSpeaker: string | null;
}

export function BoardroomTable({ activeAgents, currentSpeaker }: BoardroomTableProps) {
  const centerX = 50;
  const centerY = 45;
  const radiusX = 36;
  const radiusY = 16;

  return (
    <div className="relative w-full h-full overflow-hidden">
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 55" preserveAspectRatio="xMidYMid slice">
        <defs>
          <radialGradient id="tableGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#1e3a5f" stopOpacity="0.6" />
            <stop offset="60%" stopColor="#0f1b33" stopOpacity="0.3" />
            <stop offset="100%" stopColor="transparent" stopOpacity="0" />
          </radialGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="1" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* center ellipse glow */}
        <ellipse cx={centerX} cy={centerY} rx={radiusX + 8} ry={radiusY + 8} fill="url(#tableGlow)" />

        {/* table ellipse */}
        <ellipse cx={centerX} cy={centerY} rx={radiusX} ry={radiusY} fill="#0f172a" stroke="#334155" strokeWidth="0.8" />
        <ellipse cx={centerX} cy={centerY} rx={radiusX - 3} ry={radiusY - 3} fill="none" stroke="#1e293b" strokeWidth="0.4" />
        <ellipse cx={centerX} cy={centerY} rx={radiusX - 6} ry={radiusY - 6} fill="none" stroke="#1e293b" strokeWidth="0.3" />

        {/* table divider line */}
        <line x1={centerX - radiusX} y1={centerY} x2={centerX + radiusX} y2={centerY} stroke="#1e293b" strokeWidth="0.4" />

        {/* decorative diamond */}
        <rect x={centerX - 1.5} y={centerY - 1.5} width={3} height={3} fill="#475569" transform={`rotate(45 ${centerX} ${centerY})`} />
      </svg>

      {/* seats */}
      {activeAgents.length > 0 &&
        activeAgents.slice(0, 5).map((agent, i) => {
          const angle = (i / 5) * Math.PI * 2 - Math.PI / 2;
          const x = centerX + radiusX * Math.cos(angle);
          const y = centerY + radiusY * Math.sin(angle);
          const isSpeaker = currentSpeaker === agent.id;
          const topHalf = Math.sin(angle) < 0;

          return (
            <div
              key={agent.id}
              className={`absolute transition-all duration-700 ${
                isSpeaker ? "z-30 scale-110" : "z-10"
              }`}
              style={{
                left: `${x}%`,
                top: `${y}%`,
                transform: `translate(-50%, -50%) ${isSpeaker ? "scale(1.15)" : topHalf ? "scale(0.95)" : "scale(1)"}`,
              }}
            >
              {/* ping aura for speaker */}
              {isSpeaker && (
                <div className="absolute inset-0 rounded-full animate-ping bg-blue-500/30" style={{ width: 44, height: 44, left: -2, top: -2 }} />
              )}
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm border-2 transition-all duration-500 relative ${
                  agent.bgColor} ${agent.borderColor} ${
                  isSpeaker
                    ? "shadow-lg shadow-blue-500/40 ring-1 ring-blue-400"
                    : "shadow-md shadow-black/30"
                }`}
              >
                <i className={`fa-solid ${agent.icon} ${agent.textColor}`} />
              </div>
              <div
                className={`text-center mt-1 transition-colors duration-500 ${
                  isSpeaker ? agent.textColor : "text-slate-500"
                }`}
              >
                <div className={`text-[9px] font-bold leading-tight ${isSpeaker ? "" : "text-slate-400"}`}>
                  {agent.name.split(" ")[0]}
                </div>
                <div className="text-[7px] text-slate-600 truncate max-w-[80px]">
                  {agent.title}
                </div>
              </div>
            </div>
          );
        })}

      {/* center label */}
      <div
        className="absolute text-center"
        style={{ left: `${centerX}%`, top: `${centerY}%`, transform: "translate(-50%, -50%)" }}
      >
        <div className="text-[10px] font-bold text-slate-600 tracking-widest uppercase">Konsey</div>
        <div className="text-[8px] text-slate-700 font-mono">MASASI</div>
      </div>
    </div>
  );
}
