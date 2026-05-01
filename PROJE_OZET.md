\# İddaa Oran Sitesi - Proje Özeti



\## Proje Sahibi

\- GitHub: yusufkocbiotek-sketch

\- Repo: https://github.com/yusufkocbiotek-sketch/iddiayusuf

\- Site: https://yusufkocbiotek-sketch.github.io/iddiayusuf/

\- Eski Arena: https://019ddb51-14c1-7ab6-8c5b-aeae35b0e8a7.arena.site/



\## Klasör

C:\\Users\\YUSUF\\OneDrive\\Desktop\\iddiayusuf-main



\## Ne Yapıyor?

iddaa.com'dan Selenium ile maç oranlarını çekip, GitHub Pages'da yayınlayan bir iddaa oran analiz sitesi.



\## Dosyalar



\### scraper.py

\- Kaynak: iddaa.com/program/futbol

\- Selenium ile Chrome açar

\- Sadece ÖNE ÇIKAN 5 maçı çeker

\- Detaylı oranları çeker (800+ oran/maç)

\- Maça tıklar → "Tümü" bekler → parse eder

\- Çıktı: public/data/mac.json



\### scraper\_full.py (ANA SCRAPER)

\- Kaynak: iddaa.com/program/futbol

\- URL ile tarih değiştirir: ?date=01.05.2026

\- Tarih dropdown'ından günleri alır (6 gün)

\- Her gün için ayrı sayfa yükler

\- Her maç için: sayfa yükle → takım adına tıkla → "Tümü" bekle → detay parse

\- Detay oranları: MS, İY, Handikap, Alt/Üst, KG, Kombine (800+ oran)

\- Çıktı: public/data/mac.json

\- Süre: \~15 dakika



\### scraper\_gecmis.py

\- Kaynak: spordb.com/iddaa-programi/

\- Hafta dropdown'ından 25 hafta geçmiş çeker

\- Select ile hafta seçer → maçları parse eder

\- Skorlar + İY skorları + 11 oran türü

\- 14,327 maç çekildi

\- Çıktı: public/data/gecmis\_maclar.json

\- Süre: \~48 dakika



\### index.html (SİTE)

\- GitHub Pages'da yayında

\- 2 sekme: Bülten + Oran Analizi

\- Bülten: Tablo görünümü, 13 oran kolonu, detay panel

\- Filtreler: Takım arama, tarih, lig, durum, oran filtresi (çoklu, eşittir)

\- Oran Analizi: 14,000+ geçmiş maç üzerinden analiz

&#x20; - Çoklu filtre (VE koşulu, eşittir)

&#x20; - MS sonucu barı, Alt/Üst barı, KG barı, İY barı

&#x20; - Maç detayları listesi

\- JSON kaynakları:

&#x20; - mac.json: raw.githubusercontent.com/.../public/data/mac.json

&#x20; - gecmis\_maclar.json: raw.githubusercontent.com/.../public/data/gecmis\_maclar.json



\### guncelle.bat

\- Masaüstünde, çift tıkla çalışır

\- scraper\_full.py çalıştırır → git push yapar



\## mac.json Yapısı

```json

{

&#x20; "version": 2,

&#x20; "updated": "2026-04-30T23:40:44",

&#x20; "matches": \[

&#x20;   {

&#x20;     "index": 1,

&#x20;     "mac\_kodu": "841",

&#x20;     "ev\_sahibi": "Braga",

&#x20;     "deplasman": "Freiburg",

&#x20;     "saat": "22:00",

&#x20;     "tarih": "2026-04-30",

&#x20;     "lig": "",

&#x20;     "durum": "baslamadi",

&#x20;     "skor\_ev": 0,

&#x20;     "skor\_dep": 0,

&#x20;     "skor\_1y\_ev": 0,

&#x20;     "skor\_1y\_dep": 0,

&#x20;     "kaynak": "iddaa.com",

&#x20;     "oranlar": {

&#x20;       "Maç Sonucu\_1": 2.05,

&#x20;       "Maç Sonucu\_0": 2.8,

&#x20;       "Maç Sonucu\_2": 3.18,

&#x20;       "Alt/Üst 2.5\_Alt": 1.45,

&#x20;       "Alt/Üst 2.5\_Üst": 2.13,

&#x20;       "Karşılıklı Gol\_Var": 1.82,

&#x20;       "Karşılıklı Gol\_Yok": 1.63,

&#x20;       "İlk Yarı Sonucu\_1": 2.72,

&#x20;       "İlk Yarı Alt/Üst 1.5\_Alt": 1.39,

&#x20;       "İlk Yarı Karşılıklı Gol\_Var": 3.43,

&#x20;       "Her İki Yarıda da Üst 1.5\_Evet": 4.50,

&#x20;       "Maç Sonucu ve Karşılıklı Gol\_1 ve Var": 3.80,

&#x20;       "İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur\_Evet / Evet": 12.50

&#x20;     }

&#x20;   }

&#x20; ]

}


{
  "version": 1,
  "updated": "2026-05-01T07:55:00",
  "kaynak": "spordb.com",
  "toplam_mac": 14327,
  "biten_mac": 14196,
  "matches": [
    {
      "ev_sahibi": "Bolivar",
      "deplasman": "Fluminense",
      "saat": "01:00",
      "tarih": "2026-05-01",
      "lig": "LBRK",
      "durum": "bitti",
      "skor_ev": 2,
      "skor_dep": 0,
      "skor_1y_ev": 1,
      "skor_1y_dep": 0,
      "oranlar": {
        "Maç Sonucu_1": 1.72,
        "Maç Sonucu_0": 2.98,
        "Maç Sonucu_2": 3.50,
        "Alt/Üst 2.5_Alt": 1.47,
        "Alt/Üst 2.5_Üst": 1.91,
        "Karşılıklı Gol_Var": 1.74,
        "Karşılıklı Gol_Yok": 1.59
      }
    }
  ]
}


### skor_guncelle.py
- SporDB'den biten maçların skorlarını çeker
- mac.json'daki "baslamadi" maçları "bitti" olarak günceller
- Detaylı oranlar + skorlar = Analiz çalışır