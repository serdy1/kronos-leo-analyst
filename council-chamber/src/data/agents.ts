export interface Analyst {
  id: number;
  name: string;
  title: string;
  philosophy: string;
  color: string;
  avatar: string;
  icon: string;
}

export const agents: Analyst[] = [
  { id: 1, name: "Aswath Damodaran", title: "Değerleme Dekanı", philosophy: "Hikaye ile rakamları birleştirir. Şirketin büyüme hikayesi finansal tablolarla uyuşuyor mu ona bakar.", color: "text-blue-400 bg-blue-950/60 border-blue-800 shadow-blue-950", avatar: "AD", icon: "fa-calculator" },
  { id: 2, name: "Ben Graham", title: "Değer Yatırımının Babası", philosophy: "Güvenlik marjına bakar. Hisse net aktif değerinin altındaysa ve ucuzsa heyecanlanır.", color: "text-stone-400 bg-stone-900 border-stone-700 shadow-stone-900", avatar: "BG", icon: "fa-shield-halved" },
  { id: 3, name: "Bill Ackman", title: "Aktivist Yatırımcı", philosophy: "Yönetimde agresif değişimler, radikal kararlar ve büyük hamleler arar. Cesurdur.", color: "text-red-400 bg-red-950 border-red-800 shadow-red-950", avatar: "BA", icon: "fa-bullhorn" },
  { id: 4, name: "Cathie Wood", title: "İnovasyon Kraliçesi", philosophy: "Yapay zeka, genomik gibi yıkıcı teknolojilere ve geleceğin 10 kat büyüyecek şirketlerine odaklanır.", color: "text-fuchsia-400 bg-fuchsia-950 border-fuchsia-800 shadow-fuchsia-950", avatar: "CW", icon: "fa-rocket" },
  { id: 5, name: "Charlie Munger", title: "Rasyonelliğin Kalesi", philosophy: "Harika bir şirketi makul bir fiyata almayı tercih eder. Dürüstlük, yönetim kalitesi ve 'Moat' arar.", color: "text-amber-500 bg-amber-950 border-amber-900 shadow-amber-950", avatar: "CM", icon: "fa-chess-rook" },
  { id: 6, name: "Michael Burry", title: "The Big Short", philosophy: "Herkesin atladığı krizleri veya derin değerleri bulur. Kontrariandır (herkese ters hareket eder).", color: "text-indigo-400 bg-indigo-950 border-indigo-800 shadow-indigo-950", avatar: "MB", icon: "fa-eye-low-vision" },
  { id: 7, name: "Mohnish Pabrai", title: "Dhandho Yatırımcısı", philosophy: "Tura gelirsek kazanırım, yazı gelirse az kaybederim. Düşük riskli asimetrik getiri potansiyeline bakar.", color: "text-emerald-400 bg-emerald-950 border-emerald-800 shadow-emerald-950", avatar: "MP", icon: "fa-coins" },
  { id: 8, name: "Nassim Taleb", title: "Kara Kuğu Analisti", philosophy: "Antifragile yapıları sever. Kuyruk risklerine, sistemin çökme ihtimallerine odaklanır. Serttir.", color: "text-slate-300 bg-slate-800 border-slate-600 shadow-slate-800", avatar: "NT", icon: "fa-crow" },
  { id: 9, name: "Peter Lynch", title: "Halkın Yatırımcısı", philosophy: "Bildiğin işe yatırım yap. Günlük hayatta gördüğün, büyüyen pratik şirketleri seçer.", color: "text-green-400 bg-green-950 border-green-800 shadow-green-950", avatar: "PL", icon: "fa-store" },
  { id: 10, name: "Phil Fisher", title: "Scuttlebutt Üstadı", philosophy: "Şirketin müşterileriyle, çalışanlarıyla konuşur gibi derinlemesine büyüme analizi yapar.", color: "text-teal-400 bg-teal-950 border-teal-800 shadow-teal-950", avatar: "PF", icon: "fa-magnifying-glass-chart" },
  { id: 11, name: "Rakesh Jhunjhunwala", title: "Büyük Boğa", philosophy: "Agresif, büyüme odaklı ve her zaman iyimser (boğa) perspektiften bakar.", color: "text-orange-400 bg-orange-950 border-orange-800 shadow-orange-950", avatar: "RJ", icon: "fa-arrow-trend-up" },
  { id: 12, name: "Stanley Druckenmiller", title: "Makro Efsane", philosophy: "Likidite, merkez bankası politikaları ve büyük trendleri izler. Asimetrik durumlarda büyük oynar.", color: "text-cyan-400 bg-cyan-950 border-cyan-800 shadow-cyan-950", avatar: "SD", icon: "fa-globe" },
  { id: 13, name: "Warren Buffett", title: "Omaha Kahini", philosophy: "Anlaşılması kolay, güçlü nakit akışı olan, rekabet avantajı yüksek şirketleri adil fiyata alır.", color: "text-yellow-500 bg-yellow-950 border-yellow-900 shadow-yellow-950", avatar: "WB", icon: "fa-landmark" },
  { id: 14, name: "Edwin Lefèvre", title: "Spekülasyon Üstadı", philosophy: "Piyasa psikolojisi, fiyat hareketleri ve trendlerin insan doğasıyla ilişkisine odaklanır. (Borsa Spekülatörünün Anıları)", color: "text-rose-400 bg-rose-950 border-rose-800 shadow-rose-950", avatar: "EL", icon: "fa-user-secret" },
  { id: 15, name: "Jack D. Schwager", title: "Piyasa Sihirbazı", philosophy: "Başarılı trader'ların ortak özelliklerini, disiplin ve risk yönetimi stratejilerini arar. (Borsa Sihirbazları)", color: "text-violet-400 bg-violet-950 border-violet-800 shadow-violet-950", avatar: "JS", icon: "fa-wand-magic-sparkles" },
  { id: 16, name: "Michele Cagan", title: "Yatırım 101 Rehberi", philosophy: "Temel finansal okuryazarlık, bilanço sağlığı ve yatırıma yeni başlayanların gözünden temelleri inceler. (Yatırım 101)", color: "text-sky-400 bg-sky-950 border-sky-800 shadow-sky-950", avatar: "MC", icon: "fa-book-open" },
  { id: 17, name: "Morgan Housel", title: "Paranın Psikoloğu", philosophy: "Matematikten ziyade yatırımcı davranışlarına, beklenti yönetimine ve sabrın gücüne odaklanır. (Paranın Psikolojisi)", color: "text-lime-400 bg-lime-950 border-lime-800 shadow-lime-950", avatar: "MH", icon: "fa-brain" },
  { id: 18, name: "Michael W. Covel", title: "Trend Takipçisi", philosophy: "Temel analizi boşverip tamamen fiyat trendlerine ve momentum stratejilerine odaklanır. (Trend Takipçisi)", color: "text-blue-300 bg-blue-900 border-blue-700 shadow-blue-900", avatar: "MC", icon: "fa-chart-line" },
  { id: 19, name: "Nicolas Darvas", title: "Kutu Teorisyeni", philosophy: "Fiyat ve hacim hareketlerini kutular (darvas box) içinde analiz edip kırılımlara oynar. (Borsada 1 Milyon Doları Nasıl Kazandım?)", color: "text-pink-400 bg-pink-950 border-pink-800 shadow-pink-950", avatar: "ND", icon: "fa-box" },
];
