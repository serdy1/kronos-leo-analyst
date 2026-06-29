import { DebateMessage } from "../data/debates";
import { analysts } from "../data/agents";

interface TranscriptViewerProps {
  messages: DebateMessage[];
  currentSpeaker: string | null;
}

function getEmotionColor(emotion: string): string {
  if (emotion.includes("Bullish")) return "text-emerald-400 bg-emerald-950/60 border-emerald-800";
  if (emotion.includes("Bearish")) return "text-red-400 bg-red-950/60 border-red-800";
  return "text-yellow-400 bg-yellow-950/60 border-yellow-800";
}

function findSpeakerId(name: string): string | undefined {
  const found = analysts.find(
    (a) => a.name.toLowerCase() === name.toLowerCase()
  );
  if (found) return found.id;

  const partial = analysts.find(
    (a) =>
      name.toLowerCase().includes(a.name.split(" ")[0].toLowerCase()) ||
      a.name.split(" ")[0].toLowerCase().includes(name.toLowerCase())
  );
  return partial?.id;
}

export function TranscriptViewer({ messages, currentSpeaker }: TranscriptViewerProps) {
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-600 text-xs">
        <div className="text-center">
          <i className="fa-solid fa-comments text-2xl mb-2 opacity-30" />
          <p>Henüz tartışma kaydı yok</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      {messages.map((msg, idx) => {
        const speakerId = findSpeakerId(msg.speaker);
        const agent = analysts.find((a) => a.id === speakerId);
        const isSpeaking = currentSpeaker === speakerId;

        return (
          <div
            key={idx}
            className={`flex gap-3 p-3 rounded-xl border transition-all duration-500 ${
              isSpeaking
                ? "bg-slate-800/80 border-slate-600/60 shadow-md shadow-blue-900/10"
                : "bg-slate-800/30 border-slate-700/30"
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border text-xs ${
                agent
                  ? `${agent.bgColor} ${agent.textColor} ${agent.borderColor}`
                  : "bg-slate-800 text-slate-400 border-slate-600"
              }`}
            >
              <i className={`fa-solid ${agent?.icon || "fa-user"} text-[10px]`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs font-bold ${agent?.textColor || "text-slate-300"}`}>
                  {msg.speaker}
                </span>
                <span
                  className={`text-[9px] px-1.5 py-0.5 rounded-full border font-medium ${getEmotionColor(
                    msg.emotion
                  )}`}
                >
                  {msg.emotion}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">{msg.message}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
