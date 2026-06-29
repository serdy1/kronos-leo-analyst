export interface DebateMessage {
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

export const debates: DebateSession[] = [
  {
    date: "2026-06-28",
    ticker: "FROTO",
    context: "Ford Otosan Q1 2026 bilançosu, yeni E-Transit lansmanı ve Romanya ihracat genişlemesi.",
    messages: [
      {
        agentId: 13,
        agentName: "Warren Buffett",
        message: "Ford Otosan'ın geçmiş 10 yıldaki nakit akışı istikrarına bakın. Borç/özsermaye oranı son derece makul. Sektöründe güçlü rekabet avantajına (moat) sahip bu tarz şirketler krizlerde bile uyur.",
        timestamp: "2026-06-28T10:00:00Z",
        stance: "bullish",
      },
      {
        agentId: 8,
        agentName: "Nassim Taleb",
        message: "Herkes FROTO'ya 'güvenli liman' derken, asıl risk küresel faiz dalgalanmaları ve Avrupa'daki olası bir durgunluk. Otomotiv talebi çok kırılgan ve bu kuyruk riskini modellerinizde fiyatlamıyorsunuz.",
        timestamp: "2026-06-28T10:01:00Z",
        stance: "bearish",
      },
      {
        agentId: 5,
        agentName: "Charlie Munger",
        message: "Otosan Türkiye'nin en büyük ticari araç üreticisi olarak dürüst ve yetkin bir yönetime sahip. Ancak duran varlık yatırımları ve artan sermaye harcamaları serbest nakit akışı marjını kısa vadede baskılayabilir.",
        timestamp: "2026-06-28T10:02:00Z",
        stance: "neutral",
      },
      {
        agentId: 2,
        agentName: "Ben Graham",
        message: "Şu anki hisse fiyatı bilanço defter değerine göre yüksek bir çarpanla işlem görüyor. Güvenlik marjı (margin of safety) benim kriterlerime göre daralmış durumda. Daha ucuz fiyatları beklemek akıllıca olur.",
        timestamp: "2026-06-28T10:03:00Z",
        stance: "neutral",
      },
      {
        agentId: 12,
        agentName: "Stanley Druckenmiller",
        message: "Likidite ve makro dinamikleri unutuyorsunuz. Merkez Bankası faiz indirim döngüsüne girdiğinde genişleyen kredi hacmi iç talebi canlandırır. FROTO ise bu ivmeden ilk yararlanacak oyunculardan biri.",
        timestamp: "2026-06-28T10:04:00Z",
        stance: "bullish",
      },
    ],
  },
  {
    date: "2026-06-28",
    ticker: "ANHYT",
    context: "Anadolu Hayat Emeklilik BES fon büyüklüğü artışı ve faiz indirimlerinin portföy getirilerine etkisi.",
    messages: [
      {
        agentId: 9,
        agentName: "Peter Lynch",
        message: "BES katılımcı sayısındaki istikrarlı artışı herkes görebilir. Çevremdeki insanların otomatik katılım fonlarını nasıl büyüttüğünü izliyorum. Bu, anlaşılması son derece kolay ve halkın görebileceği harika bir iş.",
        timestamp: "2026-06-28T10:10:00Z",
        stance: "bullish",
      },
      {
        agentId: 1,
        agentName: "Aswath Damodaran",
        message: "Finansal şirketlerin değerlemesinde büyüme hikayesi ve özsermaye kârlılığı esastır. ANHYT'nin hikayesi güçlü, ancak faiz indirimleri portföy gelir marjlarında daralmaya sebep olabilir. Değerleme bu riski yansıtmalı.",
        timestamp: "2026-06-28T10:11:00Z",
        stance: "neutral",
      },
      {
        agentId: 17,
        agentName: "Morgan Housel",
        message: "BES yatırımları matematiksel formüllerden çok insanların sabır ve tasarruf davranışlarıyla ilgili. ANHYT gibi düzenli nakit biriktiren sistemler uzun vadede sabırlı yatırımcının en büyük dostudur.",
        timestamp: "2026-06-28T10:12:00Z",
        stance: "bullish",
      },
      {
        agentId: 6,
        agentName: "Michael Burry",
        message: "Enflasyonist ortamlarda sigortacılık ve emeklilik fonları reel getiri sunmakta zorlanır. Defter değerindeki büyüme illüzyondan ibaret olabilir. Derin kriz durumlarında likidite sıkışıklığı yaşanabilir.",
        timestamp: "2026-06-28T10:13:00Z",
        stance: "bearish",
      },
    ],
  },
  {
    date: "2026-06-28",
    ticker: "PGSUS",
    context: "Pegasus Havayolları dış hat kapasite artışı, turizm sezonu beklentileri ve jet yakıtı maliyetleri.",
    messages: [
      {
        agentId: 3,
        agentName: "Bill Ackman",
        message: "Pegasus agresif bir kapasite artışına gidiyor. Operasyonel maliyet yönetimi çok başarılı. Havacılık riskli bir sektör olsa da, bu yönetim kalitesiyle rakiplerinden pazar payı çalmaya devam edecektir.",
        timestamp: "2026-06-28T10:20:00Z",
        stance: "bullish",
      },
      {
        agentId: 8,
        agentName: "Nassim Taleb",
        message: "Havacılık sektörü antifragile değildir, tam aksine aşırı kırılgandır. Jeopolitik gerilimler veya ani bir salgın hastalık tüm uçuş ağını felç edebilir. Risk yönetimi açısından bu hisse tam bir saatli bomba.",
        timestamp: "2026-06-28T10:21:00Z",
        stance: "bearish",
      },
      {
        agentId: 18,
        agentName: "Michael W. Covel",
        message: "Temel hikayeleri bir kenara bırakın. Fiyat hareketine bakın. PGSUS hissesi 200 günlük hareketli ortalamasının üzerinde güçlü bir yükseliş trendi sergiliyor. Trend yönündeyiz, alım devam etmeli.",
        timestamp: "2026-06-28T10:22:00Z",
        stance: "bullish",
      },
      {
        agentId: 19,
        agentName: "Nicolas Darvas",
        message: "Hisse son haftalarda dar bir fiyat kutusunda sıkışmıştı. Bugün yüksek hacimle birlikte bu kutunun üst sınırını yukarı yönlü kırdı. Benim kutu teorime göre bu çok net bir yeni pozisyon açma sinyalidir.",
        timestamp: "2026-06-28T10:23:00Z",
        stance: "bullish",
      },
    ],
  },
  {
    date: "2026-06-28",
    ticker: "NFLX",
    context: "Netflix abone büyüme hızı, şifre paylaşım kısıtlamaları sonrası ARPU artışı ve içerik harcamaları.",
    messages: [
      {
        agentId: 4,
        agentName: "Cathie Wood",
        message: "Netflix, yapay zeka tabanlı öneri motorları ve bulut tabanlı içerik dağıtımıyla tam bir inovasyon lideri. Küresel pazar payı ve teknolojik üstünlüğü onu geleceğin dijital eğlence tekeli yapıyor.",
        timestamp: "2026-06-28T10:30:00Z",
        stance: "bullish",
      },
      {
        agentId: 13,
        agentName: "Warren Buffett",
        message: "İçerik üretmek için her yıl milyarlarca dolar harcamak zorundalar. Rekabet avantajını sürdürmek için sürekli sermaye tüketen bu iş modeli benim anladığım anlamda kalıcı bir moat sunmuyor.",
        timestamp: "2026-06-28T10:31:00Z",
        stance: "neutral",
      },
      {
        agentId: 6,
        agentName: "Michael Burry",
        message: "Abone kısıtlamalarıyla büyüme rakamları geçici olarak şişirildi. Şirket doygunluk noktasına ulaştı ve F/K çarpanı aşırı iyimser beklentileri yansıtıyor. Büyüme yavaşladığında büyük bir satış dalgası kaçınılmaz.",
        timestamp: "2026-06-28T10:32:00Z",
        stance: "bearish",
      },
    ],
  },
];
