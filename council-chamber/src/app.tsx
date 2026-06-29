import { useState, useEffect } from "react";
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  Server, 
  Newspaper, 
  BookOpen, 
  Brain, 
  Terminal 
} from "lucide-react";
import { stocks } from "./data/stocks";
import { debates, DebateMessage } from "./data/debates";
import { agents } from "./data/agents";
import { BoardroomTable } from "./components/boardroom-table";
import { TranscriptViewer } from "./components/transcript-viewer";

export default function App() {
  const [activeTicker, setActiveTicker] = useState<string | null>(null);
  const [streamedMessages, setStreamedMessages] = useState<DebateMessage[]>([]);
  const [currentSpeaker, setCurrentSpeaker] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [systemTime, setSystemTime] = useState(new Date());

  // Clock Effect
  useEffect(() => {
    const timer = setInterval(() => {
      setSystemTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Streaming Debate Effect
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

    let idx = 0;
    const interval = setInterval(() => {
      if (idx < session.messages.length) {
        const nextMsg = session.messages[idx];
        setCurrentSpeaker(nextMsg.agentName);
        setStreamedMessages((prev) => [...prev, nextMsg]);
        idx++;
      } else {
        clearInterval(interval);
        setIsStreaming(false);
        setCurrentSpeaker(null);
      }
    }, 3500); // 3.5 seconds dramatic pause per speaker

    return () => clearInterval(interval);
  }, [activeTicker]);

  const activeStock = stocks.quotes.find((s) => s.ticker === activeTicker) || null;

  // Mock Indices
  const indices = [
    { name: "BIST 100", value: "10,248.50", change: "+1.38%", up: true },
    { name: "SPX 500", value: "5,422.10", change: "+0.45%", up: true },
    { name: "NASDAQ", value: "17,810.30", change: "-0.12%", up: false },
    { name: "Dolar/TL", value: "32.8850", change: "+0.15%", up: true },
    { name: "USD Index", value: "105.42", change: "-0.22%", up: false }
  ];

  // Identify active session agents
  const activeSession = debates.find((d) => d.ticker === activeTicker);
  const activeSessionAgentIds = activeSession 
    ? Array.from(new Set(activeSession.messages.map((m) => m.agentId)))
    : [];

  return (
    <div className="min-h-screen bg-[#020617] text-slate-300 flex flex-col font-sans">
      
      {/* HEADER */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-3">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-emerald-400 animate-pulse" />
              <span className="text-sm font-bold text-white tracking-wider uppercase font-mono">
                Büyük Yatırım Konseyi
              </span>
            </div>
            <div className="h-4 w-px bg-slate-800" />
            <span className="text-xs text-slate-500 font-mono">BIST-100</span>
            <div className="flex items-center gap-1 text-sm text-emerald-400 font-mono">
              <TrendingUp className="w-4 h-4" />
              <span className="font-bold">+1.38%</span>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono text-slate-500">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              LIVE SYSTEM
            </span>
            <span>{systemTime.toLocaleDateString("tr-TR")}</span>
          </div>
        </div>
      </header>

      {/* INSTRUMENT SELECTION BAND */}
      <div className="border-b border-slate-800 bg-slate-950 p-4 flex gap-3 overflow-x-auto whitespace-nowrap shrink-0 items-center hide-scrollbar">
        <div className="text-xs font-mono text-slate-500 mr-2 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-blue-500" /> ENSTRÜMAN SEÇİMİ:
        </div>
        {stocks.quotes.map((stock) => {
          const isSelected = activeTicker === stock.ticker;
          return (
            <button
              key={stock.ticker}
              onClick={() => setActiveTicker(stock.ticker)}
              className={`flex flex-col border rounded px-4 py-2 cursor-pointer transition-all text-left min-w-[165px]
                ${isSelected 
                  ? 'border-blue-500 bg-blue-950/20 shadow-[0_0_10px_rgba(59,130,246,0.15)]' 
                  : 'border-slate-800 bg-[#090d16] hover:border-slate-600'}`}
            >
              <div className="flex justify-between items-center gap-4 mb-1 w-full">
                <span className="font-bold text-slate-200 text-sm font-mono">{stock.ticker}</span>
                <span className={`text-xs font-mono font-bold ${stock.change >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {stock.change > 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                </span>
              </div>
              <div className="text-xs font-mono text-slate-400">
                {stock.price.toFixed(2)} ₺
              </div>
            </button>
          );
        })}
        {activeTicker && (
          <button 
            onClick={() => setActiveTicker(null)}
            className="text-xs font-mono text-rose-400 hover:text-rose-300 border border-rose-950 bg-rose-950/20 px-3 py-2 rounded hover:border-rose-700 transition-colors"
          >
            TEMİZLE
          </button>
        )}
      </div>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 overflow-y-auto bg-[#040814] relative">
        
        {/* 1. WELCOME DASHBOARD (No stock active) */}
        {!activeStock && (
          <div className="p-6 lg:p-10 flex flex-col space-y-6 fade-in-up max-w-[1600px] mx-auto w-full">
            
            {/* Dashboard Status Bar */}
            <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-5 gap-4">
              <div>
                <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3 font-mono tracking-tight">
                  <Terminal className="w-6 h-6 text-blue-500 animate-pulse" />
                  BÜYÜK YATIRIM KONSEYİ TERMİNALİ v4.2
                </h1>
                <p className="text-xs text-slate-400 font-mono mt-1">
                  Gelişmiş 19 Ajanlı Makro & Temel Değerleme Simülasyon Arayüzü
                </p>
              </div>
              <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
                <div className="bg-[#090d16] border border-slate-800 rounded px-3 py-1.5 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-blue-400" />
                  <span>{systemTime.toLocaleTimeString('tr-TR')}</span>
                </div>
                <div className="bg-[#090d16] border border-slate-800 rounded px-3 py-1.5 flex items-center gap-2">
                  <Server className="w-4 h-4 text-emerald-400 animate-pulse" />
                  <span>API STATUS: READY</span>
                </div>
              </div>
            </div>

            {/* Indices Ticker */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {indices.map((idx, i) => (
                <div key={i} className="bg-[#090d16] border border-slate-800/80 p-3 rounded flex flex-col justify-between">
                  <span className="text-[10px] text-slate-400 font-mono tracking-wider uppercase">{idx.name}</span>
                  <div className="flex items-baseline justify-between mt-1">
                    <span className="text-sm font-bold font-mono text-slate-200">{idx.value}</span>
                    <span className={`text-xs font-mono font-bold ${idx.up ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {idx.change}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Centerpieces Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Left Instructions */}
              <div className="lg:col-span-2 border border-blue-500/20 bg-blue-950/10 p-6 rounded-lg flex flex-col justify-between space-y-4 pulse-border">
                <div>
                  <div className="flex items-center gap-3 mb-3 text-blue-400">
                    <i className="fa-solid fa-bullseye text-xl" />
                    <h3 className="font-bold text-base font-mono">SİMÜLASYON BAŞLATICI</h3>
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed mb-4">
                    Yatırım konseyi <strong>19 seçkin analist</strong>, teorisyen ve piyasa spekülatöründen oluşmaktadır. 
                    Üst panelden değerlendirmek istediğiniz hisseyi seçtiğinizde, sistem bu 19 kişilik havuzdan konuya en uygun **aktif analistleri** toplantıya çağırır.
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono text-slate-400">
                    <div className="flex items-start gap-2 bg-[#090d16]/60 p-2.5 rounded border border-slate-800">
                      <span className="text-emerald-400 mt-0.5">✓</span>
                      <span>Anlık olarak güncel kapanış fiyatları ile analiz hedefleri karşılaştırılır.</span>
                    </div>
                    <div className="flex items-start gap-2 bg-[#090d16]/60 p-2.5 rounded border border-slate-800">
                      <span className="text-emerald-400 mt-0.5">✓</span>
                      <span>Analistler kendi teorilerine ve kitap felsefelerine göre tez üretir.</span>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <span className="text-xs font-mono text-blue-400 animate-pulse flex items-center gap-1.5">
                    <i className="fa-solid fa-circle-play" /> Lütfen yukarıdaki hisselerden birine tıklayarak oturumu başlatın
                  </span>
                  <div className="flex gap-2">
                    <span className="text-[10px] font-mono bg-[#090d16] px-2 py-1 rounded text-slate-400">Targeting BIST 100</span>
                    <span className="text-[10px] font-mono bg-[#090d16] px-2 py-1 rounded text-slate-400">USD Stable</span>
                  </div>
                </div>
              </div>

              {/* Right Stats */}
              <div className="bg-[#090d16] border border-slate-800 p-6 rounded-lg flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-200 font-mono mb-4 flex items-center gap-2">
                    <i className="fa-solid fa-chart-pie text-cyan-400" />
                    KONSEY EKOL DAĞILIMI
                  </h3>
                  <div className="space-y-2.5">
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-400">Temel Analiz & Değerleme</span>
                        <span className="text-slate-200 font-mono">6 Ajan</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-blue-500 h-full rounded-full" style={{ width: '31.5%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-400">Büyüme & İnovasyon</span>
                        <span className="text-slate-200 font-mono">4 Ajan</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-fuchsia-500 h-full rounded-full" style={{ width: '21%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-400">Risk Yönetimi & Makro</span>
                        <span className="text-slate-200 font-mono">4 Ajan</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-cyan-500 h-full rounded-full" style={{ width: '21%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-400">Fiyat Trendi & Spekülasyon</span>
                        <span className="text-slate-200 font-mono">5 Ajan</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-amber-500 h-full rounded-full" style={{ width: '26.5%' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
                <p className="text-[10px] text-slate-500 font-mono mt-4 border-t border-slate-800/80 pt-3">
                  * Tüm analistler eserlerindeki metodolojik parametrelere göre kurgulanmıştır.
                </p>
              </div>

            </div>

            {/* Bottom Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-[#090d16] border border-slate-800 p-4 rounded-lg">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono mb-2.5 flex items-center gap-2">
                  <Newspaper className="w-4 h-4 text-emerald-400" />
                  GÜNLÜK PİYASA AJANDASI
                </h4>
                <ul className="text-xs space-y-2 text-slate-400">
                  <li className="flex justify-between py-1 border-b border-slate-800/40">
                    <span>Enflasyon Odaklı Makro Dengelemeler</span>
                    <span className="text-slate-500 font-mono">TAKİPTE</span>
                  </li>
                  <li className="flex justify-between py-1 border-b border-slate-800/40">
                    <span>BIST 100 Likidite ve Endeks Ağırlıkları</span>
                    <span className="text-slate-500 font-mono">GÜNCEL</span>
                  </li>
                  <li className="flex justify-between py-1">
                    <span>Teknoloji Devlerinde Yeni Hacim Kırılımları</span>
                    <span className="text-slate-500 font-mono">AKTİF</span>
                  </li>
                </ul>
              </div>

              <div className="bg-[#090d16] border border-slate-800 p-4 rounded-lg flex flex-col justify-between">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono mb-2 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-blue-400" />
                  SİMÜLASYON MOTORU BİLGİSİ
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Seçilen hissenin hedef fiyatları ve piyasa çarpanları dinamik analiz odasına beslenerek her analistin kendi felsefesi üzerinden yapay zeka tarafından asenkron olarak tartıştırılır.
                </p>
              </div>
            </div>

          </div>
        )}

        {/* 2. ACTIVE DEBATE SCENARIO */}
        {activeStock && (
          <div className="w-full flex flex-col">
            
            {/* STOCK DETAILS HEADER PANEL */}
            <div className="bg-[#040814]/95 backdrop-blur border-b border-slate-800 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 fade-in-up">
              <div>
                <div className="flex items-baseline gap-3 mb-1">
                  <h1 className="text-3xl font-bold text-white tracking-tight">{activeStock.ticker}</h1>
                  <span className="text-slate-400 text-lg font-medium">{activeStock.name}</span>
                </div>
                <div className="flex items-center gap-4 mt-2">
                  <span className="text-2xl font-mono text-slate-200">
                    {activeStock.price.toFixed(2)} <span className="text-slate-500 text-lg">₺</span>
                  </span>
                  <span className={`px-2 py-1 rounded text-sm font-mono font-medium flex items-center gap-1 ${activeStock.change >= 0 ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'}`}>
                    {activeStock.change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                    {Math.abs(activeStock.changePercent).toFixed(2)}%
                  </span>
                  <span className="text-slate-500 text-sm border-l border-slate-700 pl-4">BIST Sektör Hissesi</span>
                </div>
              </div>
              
              {activeStock.targetPrice && (
                <div className="bg-[#090d16] border border-slate-800 rounded p-4 flex flex-col md:items-end min-w-[200px]">
                  <span className="text-xs text-slate-400 uppercase tracking-wider mb-1 font-mono">Konsensüs Hedef</span>
                  <div className="text-xl font-bold font-mono text-blue-400">
                    {activeStock.targetPrice.toFixed(2)} <span className="text-slate-500 text-base">₺</span>
                  </div>
                  <div className="text-emerald-400 text-sm font-medium mt-1 flex items-center gap-1 font-mono">
                    <i className="fa-solid fa-bullseye text-xs" />
                    Potansiyel: +{(((activeStock.targetPrice - activeStock.price) / activeStock.price) * 100).toFixed(1)}%
                  </div>
                </div>
              )}
            </div>

            {/* BOARDROOM TABLE & TRANSCRIPT PANEL */}
            <div className="flex flex-col xl:flex-row gap-6 p-6 max-w-[1600px] mx-auto w-full">
              
              {/* Left Side: Boardroom Perspective Table */}
              <div className="flex-1 min-w-0 bg-slate-950/40 border border-slate-800/80 rounded-xl p-6 flex flex-col justify-between min-h-[460px]">
                <BoardroomTable 
                  activeStock={activeStock} 
                  currentSpeaker={currentSpeaker} 
                  activeSessionAgentIds={activeSessionAgentIds}
                />
                
                {/* Active Session Members Summary List */}
                <div className="mt-6 flex flex-wrap items-center gap-2 p-3 bg-slate-900/10 border border-slate-800/80 rounded">
                  <span className="text-xs text-slate-500 font-mono mr-2">OTURUM ÜYELERİ:</span>
                  {agents.filter((a) => activeSessionAgentIds.includes(a.id)).map((agent, i) => (
                    <div 
                      key={agent.id} 
                      className={`flex items-center gap-2 border-r border-slate-800 pr-3 last:border-0 fade-in-up`}
                      style={{ animationDelay: `${i * 0.1}s` }}
                    >
                      <div className={`w-6 h-6 rounded flex items-center justify-center border text-[10px] ${agent.color}`}>
                        <i className={`fa-solid ${agent.icon}`} />
                      </div>
                      <span className="text-xs font-semibold text-slate-300 font-mono">{agent.name.split(" ")[0]}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Right Side: Transcript Dialogue Viewer */}
              <div className="w-full xl:w-[500px] shrink-0">
                <TranscriptViewer 
                  messages={streamedMessages} 
                  activeStock={activeStock} 
                  isStreaming={isStreaming} 
                />
              </div>

            </div>

          </div>
        )}

      </main>

      {/* FOOTER */}
      <footer className="border-t border-slate-800 px-6 py-3 bg-slate-950/40">
        <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono max-w-[1600px] mx-auto">
          <span>COUNCIL CHAMBER v4.2 // 19 ANALYSTS IN SESSION</span>
          <span>SYSTEM TIME: {systemTime.toLocaleTimeString('tr-TR')}</span>
        </div>
      </footer>

    </div>
  );
}
