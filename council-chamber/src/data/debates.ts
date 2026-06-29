export interface DebateMessage {
  speaker: string;
  message: string;
  emotion: string;
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
      { speaker: "Aswath Damodaran", message: "Ford Otosan'ın geçmiş 10 yıldaki nakit akışı istikrarına bakın. Borç/özsermaye oranı son derece makul. Sektöründe güçlü rekabet avantajına (moat) sahip bu tarz şirketler krizlerde bile uyur.", emotion: "Boğa (Bullish)" },
      { speaker: "Nassim Taleb", message: "Herkes FROTO'ya 'güvenli liman' derken, asıl risk küresel faiz dalgalanmaları ve Avrupa'daki olası bir durgunluk. Otomotiv talebi çok kırılgan ve bu kuyruk riskini modellerinizde fiyatlamıyorsunuz.", emotion: "Ayı (Bearish)" },
      { speaker: "Charlie Munger", message: "Otosan Türkiye'nin en büyük ticari araç üreticisi olarak dürüst ve yetkin bir yönetime sahip. Ancak duran varlık yatırımları ve artan sermaye harcamaları serbest nakit akışı marjını kısa vadede baskılayabilir.", emotion: "Şüpheci" },
      { speaker: "Ben Graham", message: "Şu anki hisse fiyatı bilanço defter değerine göre yüksek bir çarpanla işlem görüyor. Güvenlik marjı (margin of safety) benim kriterlerime göre daralmış durumda. Daha ucuz fiyatları beklemek akıllıca olur.", emotion: "Nötr" },
      { speaker: "Stanley Druckenmiller", message: "Likidite ve makro dinamikleri unutuyorsunuz. Merkez Bankası faiz indirim döngüsüne girdiğinde genişleyen kredi hacmi iç talebi canlandırır. FROTO ise bu ivmeden ilk yararlanacak oyunculardan biri.", emotion: "Boğa (Bullish)" },
      { speaker: "Mohnish Pabrai", message: "Ben bu fiyattan alıcıyım. Düşük risk ile yüksek potansiyeli birleştiren asimetrik bir fırsat var. Tura gelirsek kazanırım, yazı gelirse az kaybederim. Dhandho yatırımcısı için ideal bir senaryo.", emotion: "Boğa (Bullish)" },
    ],
  },
  {
    date: "2026-06-28",
    ticker: "THYAO",
    context: "THY yolcu sayısı Mayıs 2026'da %12 arttı, dış hat kapasite genişlemesi ve yakıt maliyetlerindeki düşüş.",
    messages: [
      { speaker: "Peter Lynch", message: "Çevremdeki herkes yurt dışına seyahat ediyor. THY'nin uçak doluluk oranları rekor kırıyor. Bildiğim bir sektör ve her gün gördüğüm bir büyüme hikayesi — bu benim için yeterli.", emotion: "Boğa (Bullish)" },
      { speaker: "Michael Burry", message: "Herkes havacılığa hücum ederken, bilançodaki yabancı para borç yüküne bakmak gerek. Jet yakıtı hedge'leri ve kur riski derinlemesine incelenmeli. Yüzeysel iyimserlik tehlikelidir.", emotion: "Ayı (Bearish)" },
      { speaker: "Stanley Druckenmiller", message: "Küresel likidite genişlerken ve turizm patlarken, THY gibi bir taşıyıcıdan daha fazlasını beklemek mantıklı. Makro rüzgar arkamızda.", emotion: "Boğa (Bullish)" },
      { speaker: "Morgan Housel", message: "Havacılık yatırımı sabır ve uzun vadeli düşünme gerektirir. Kısa vadeli yakıt ve kur dalgalanmaları sizi korkutmasın. THY'nin hikayesi uzun vadeli düşünenler için.", emotion: "Nötr" },
    ],
  },
  {
    date: "2026-06-28",
    ticker: "PGSUS",
    context: "Pegasus Havayolları dış hat kapasite artışı, turizm sezonu beklentileri ve jet yakıtı maliyetleri.",
    messages: [
      { speaker: "Bill Ackman", message: "Pegasus agresif bir kapasite artışına gidiyor. Operasyonel maliyet yönetimi çok başarılı. Havacılık riskli bir sektör olsa da, bu yönetim kalitesiyle rakiplerinden pazar payı çalmaya devam edecektir.", emotion: "Boğa (Bullish)" },
      { speaker: "Nassim Taleb", message: "Havacılık sektörü antifragile değildir, tam aksine aşırı kırılgandır. Jeopolitik gerilimler veya ani bir salgın hastalık tüm uçuş ağını felç edebilir. Risk yönetimi açısından bu hisse tam bir saatli bomba.", emotion: "Ayı (Bearish)" },
      { speaker: "Michael W. Covel", message: "Temel hikayeleri bir kenara bırakın. Fiyat hareketine bakın. PGSUS hissesi 200 günlük hareketli ortalamasının üzerinde güçlü bir yükseliş trendi sergiliyor. Trend yönündeyiz, alım devam etmeli.", emotion: "Boğa (Bullish)" },
      { speaker: "Nicolas Darvas", message: "Hisse son haftalarda dar bir fiyat kutusunda sıkışmıştı. Bugün yüksek hacimle birlikte bu kutunun üst sınırını yukarı yönlü kırdı. Benim kutu teorime göre bu çok net bir yeni pozisyon açma sinyalidir.", emotion: "Boğa (Bullish)" },
    ],
  },
  {
    date: "2026-06-28",
    ticker: "ANHYT",
    context: "Anadolu Hayat Emeklilik BES fon büyüklüğü artışı ve faiz indirimlerinin portföy getirilerine etkisi.",
    messages: [
      { speaker: "Peter Lynch", message: "BES katılımcı sayısındaki istikrarlı artışı herkes görebilir. Çevremdeki insanların otomatik katılım fonlarını nasıl büyüttüğünü izliyorum. Bu, anlaşılması son derece kolay ve halkın görebileceği harika bir iş.", emotion: "Boğa (Bullish)" },
      { speaker: "Aswath Damodaran", message: "Finansal şirketlerin değerlemesinde büyüme hikayesi ve özsermaye kârlılığı esastır. ANHYT'nin hikayesi güçlü, ancak faiz indirimleri portföy gelir marjlarında daralmaya sebep olabilir. Değerleme bu riski yansıtmalı.", emotion: "Nötr" },
      { speaker: "Morgan Housel", message: "BES yatırımları matematiksel formüllerden çok insanların sabır ve tasarruf davranışlarıyla ilgili. ANHYT gibi düzenli nakit biriktiren sistemler uzun vadede sabırlı yatırımcının en büyük dostudur.", emotion: "Boğa (Bullish)" },
      { speaker: "Michael Burry", message: "Enflasyonist ortamlarda sigortacılık ve emeklilik fonları reel getiri sunmakta zorlanır. Defter değerindeki büyüme illüzyondan ibaret olabilir. Derin kriz durumlarında likidite sıkışıklığı yaşanabilir.", emotion: "Ayı (Bearish)" },
    ],
  },
  {
    date: "2026-06-28",
    ticker: "NFLX",
    context: "Netflix abone büyüme hızı, şifre paylaşım kısıtlamaları sonrası ARPU artışı ve içerik harcamaları.",
    messages: [
      { speaker: "Cathie Wood", message: "Netflix, yapay zeka tabanlı öneri motorları ve bulut tabanlı içerik dağıtımıyla tam bir inovasyon lideri. Küresel pazar payı ve teknolojik üstünlüğü onu geleceğin dijital eğlence tekeli yapıyor.", emotion: "Boğa (Bullish)" },
      { speaker: "Warren Buffett", message: "İçerik üretmek için her yıl milyarlarca dolar harcamak zorundalar. Rekabet avantajını sürdürmek için sürekli sermaye tüketen bu iş modeli benim anladığım anlamda kalıcı bir moat sunmuyor.", emotion: "Nötr" },
      { speaker: "Michael Burry", message: "Abone kısıtlamalarıyla büyüme rakamları geçici olarak şişirildi. Şirket doygunluk noktasına ulaştı ve F/K çarpanı aşırı iyimser beklentileri yansıtıyor. Büyüme yavaşladığında büyük bir satış dalgası kaçınılmaz.", emotion: "Ayı (Bearish)" },
      { speaker: "Phil Fisher", message: "Scuttlebutt yöntemiyle Netflix'in içerik stratejisini incelediğimde, kullanıcı başına izlenme süresinin arttığını görüyorum. Rekabet yoğun ama müşteri bağlılığı yüksek. Detaylarda büyüme sinyalleri var.", emotion: "Boğa (Bullish)" },
      { speaker: "Rakesh Jhunjhunwala", message: "Netflix küresel bir hikaye. Ben her zaman derim: büyük trendlerin önünde durmayın. Streaming devrimi henüz bitmedi. NFLX uzun vadede katlanacak.", emotion: "Boğa (Bullish)" },
    ],
  },
];
