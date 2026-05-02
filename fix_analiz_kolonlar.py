from pathlib import Path
import re

p = Path("index.html")
html = p.read_text(encoding="utf-8")

NEW_FUNC = r'''
function analizOranKeyleri(maclar){
  const istenen = [
    // Maç Sonucu
    "Maç Sonucu_1",
    "Maç Sonucu_0",
    "Maç Sonucu_2",

    // Alt Üst 2.5
    "Alt/Üst 2.5_Alt",
    "Alt/Üst 2.5_Üst",

    // KG
    "Karşılıklı Gol_Var",
    "Karşılıklı Gol_Yok",

    // İlk Yarı Sonucu
    "İlk Yarı Sonucu_1",
    "İlk Yarı Sonucu_0",
    "İlk Yarı Sonucu_2",

    // İlk Yarı Alt/Üst 1.5
    "İlk Yarı Alt/Üst 1.5_Alt",
    "İlk Yarı Alt/Üst 1.5_Üst",

    // Her iki yarıda Üst 1.5
    "Her İki Yarıda da Üst 1.5_Evet",
    "Her İki Yarıda da Üst 1.5_Hayır",

    // Alt/Üst 3.5
    "Alt/Üst 3.5_Alt",
    "Alt/Üst 3.5_Üst",

    // İlk Yarı ve İkinci Yarıda KG Olur
    "İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur_Evet / Evet",
    "İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur_Evet / Hayır",
    "İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur_Hayır / Evet",
    "İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur_Hayır / Hayır",

    // Ev sahibi her iki yarıda gol atar
    "Ev Sahibi Her İki Yarıda da Gol Atar_Evet",
    "Ev Sahibi Her İki Yarıda da Gol Atar_Hayır",

    // Deplasman her iki yarıda gol atar
    "Deplasman Her İki Yarıda da Gol Atar_Evet",
    "Deplasman Her İki Yarıda da Gol Atar_Hayır",

    // İkinci Yarı KG
    "İkinci Yarı Karşılıklı Gol_Var",
    "İkinci Yarı Karşılıklı Gol_Yok",

    // Altı/Üstü 2.5 ve KG
    "Altı/Üstü 2.5 ve Karşılıklı Gol_Alt ve Var",
    "Altı/Üstü 2.5 ve Karşılıklı Gol_Alt ve Yok",
    "Altı/Üstü 2.5 ve Karşılıklı Gol_Üst ve Var",
    "Altı/Üstü 2.5 ve Karşılıklı Gol_Üst ve Yok",

    // İlk Yarı Sonucu ve İlk Yarı KG
    "İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_1 ve Var",
    "İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_1 ve Yok",
    "İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_0 ve Var",
    "İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_0 ve Yok",
    "İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_2 ve Var",
    "İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_2 ve Yok",

    // İlk Yarı / Maç Sonucu
    "İlk Yarı / Maç Sonucu_1/1",
    "İlk Yarı / Maç Sonucu_1/0",
    "İlk Yarı / Maç Sonucu_1/2",
    "İlk Yarı / Maç Sonucu_0/1",
    "İlk Yarı / Maç Sonucu_0/0",
    "İlk Yarı / Maç Sonucu_0/2",
    "İlk Yarı / Maç Sonucu_2/1",
    "İlk Yarı / Maç Sonucu_2/0",
    "İlk Yarı / Maç Sonucu_2/2",

    // Ev sahibi her iki yarıyı kazanır
    "Ev Sahibi Her İki Yarıyı Kazanır_Evet",
    "Ev Sahibi Her İki Yarıyı Kazanır_Hayır",

    // Deplasman her iki yarıyı kazanır
    "Deplasman Her İki Yarıyı Kazanır_Evet",
    "Deplasman Her İki Yarıyı Kazanır_Hayır"
  ];

  // Sadece eşleşen maçlarda gerçekten bulunan kolonları göster
  const mevcut = new Set();

  maclar.forEach(m=>{
    Object.keys(m.oranlar || {}).forEach(k=>{
      mevcut.add(k);
    });
  });

  return istenen.filter(k=>mevcut.has(k));
}
'''

start = html.find("function analizOranKeyleri(maclar){")
if start == -1:
    raise SystemExit("analizOranKeyleri fonksiyonu bulunamadı. Önce analiz tablo yamasının ekli olması gerekiyor.")

brace = html.find("{", start)
depth = 0
end = None

for i in range(brace, len(html)):
    if html[i] == "{":
        depth += 1
    elif html[i] == "}":
        depth -= 1
        if depth == 0:
            end = i + 1
            break

if end is None:
    raise SystemExit("analizOranKeyleri fonksiyon sonu bulunamadı.")

html = html[:start] + NEW_FUNC + html[end:]

p.write_text(html, encoding="utf-8")
print("✅ Analiz tablosu kolonları istenen oranlarla sınırlandı.")