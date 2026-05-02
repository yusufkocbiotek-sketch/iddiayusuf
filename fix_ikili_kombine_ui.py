from pathlib import Path

p = Path("index.html")
html = p.read_text(encoding="utf-8")

CSS = r"""
/* IKILI KOMBINE ANALIZ - OTOMATIK EKLENDI */
.k2-panel{
  margin: 10px 0 14px 0;
  padding: 12px;
  border:1px solid #21262d;
  background:#0d1117;
  border-radius:8px;
}

.k2-baslik{
  color:#00c853;
  font-weight:700;
  font-size:14px;
  margin-bottom:8px;
}

.k2-aciklama{
  color:#888;
  font-size:11px;
  margin-bottom:10px;
}

.k2-row{
  display:flex;
  gap:8px;
  flex-wrap:wrap;
  align-items:center;
  margin-bottom:8px;
}

.k2-row select,
.k2-row input{
  background:#0d1117;
  color:#e6e6e6;
  border:1px solid #30363d;
  padding:7px 10px;
  border-radius:5px;
  font-size:12px;
  outline:none;
}

.k2-row input[type=number]{
  width:90px;
}

.k2-row select{
  min-width:200px;
}

.k2-badge{
  display:inline-block;
  padding:4px 8px;
  border-radius:5px;
  background:#161b22;
  color:#00c853;
  border:1px solid #21262d;
  font-size:11px;
  margin-top:4px;
}
"""

HTML_BLOCK = r"""
<div class="k2-panel" id="ikili-kombine-panel">
  <div class="k2-baslik">⚡ İkili Kombine Analizi</div>
  <div class="k2-aciklama">
    İki oran seçin. Sistem bu iki oranın aynı maçta birlikte gelme oranını hesaplasın.
    Özellikle istediğiniz marketler: İlk Yarı KG, Her İki Yarıda da KG, Her İki Yarıda da Üst 1.5 vb.
  </div>

  <div class="k2-row">
    <select id="kombineOran1"></select>
    <span>=</span>
    <input type="number" id="kombineDeger1" step="0.01" placeholder="örn 1.68">

    <select id="kombineOran2"></select>
    <span>=</span>
    <input type="number" id="kombineDeger2" step="0.01" placeholder="örn 1.80">

    <button class="btn-a" onclick="kombine2AnalizYap()">🔍 İkili Analiz</button>
    <button class="btn-r" onclick="kombine2Temizle()">Temizle</button>
  </div>

  <div class="k2-badge">
    Not: Bu bölüm mevcut analiz motorunu kullanır. İki filtreyi birlikte uygular.
  </div>
</div>
"""

JS_BLOCK = r"""
/* IKILI KOMBINE ANALIZ - OTOMATIK EKLENDI */
function kombine2InitSecenekler(){
  const kaynak = document.getElementById("analizOranTuru");
  const s1 = document.getElementById("kombineOran1");
  const s2 = document.getElementById("kombineOran2");

  if(!kaynak || !s1 || !s2) return;

  if(s1.options.length === 0){
    s1.innerHTML = kaynak.innerHTML;
  }
  if(s2.options.length === 0){
    s2.innerHTML = kaynak.innerHTML;
  }

  // İstenen marketleri varsayılan dolduralım
  if(!s1.value) s1.value = "İlk Yarı Karşılıklı Gol_Var";
  if(!s2.value) s2.value = "İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur_Evet / Evet";
}

function kombine2Temizle(){
  const d1 = document.getElementById("kombineDeger1");
  const d2 = document.getElementById("kombineDeger2");
  if(d1) d1.value = "";
  if(d2) d2.value = "";
  analizFiltreler = [];
  if(typeof afGoster === "function") afGoster();
  document.getElementById("analizSonuc").innerHTML = '<div class="analiz-yok">👆 Filtre ekleyin ve analiz başlatın</div>';
}

function kombine2AnalizYap(){
  const t1 = document.getElementById("kombineOran1")?.value;
  const t2 = document.getElementById("kombineOran2")?.value;
  const d1 = parseFloat(document.getElementById("kombineDeger1")?.value);
  const d2 = parseFloat(document.getElementById("kombineDeger2")?.value);

  if(!t1 || isNaN(d1) || !t2 || isNaN(d2)){
    document.getElementById("analizSonuc").innerHTML = '<div class="analiz-yok">⚠️ Lütfen iki oranı da seçin ve değer girin.</div>';
    return;
  }

  analizFiltreler = [];
  analizFiltreler.push({tur:t1, deger:d1});

  // Aynı market + aynı değer ise iki kez eklemeyelim
  if(!(t1 === t2 && Math.abs(d1 - d2) <= 0.009)){
    analizFiltreler.push({tur:t2, deger:d2});
  }

  if(typeof afGoster === "function") afGoster();
  if(typeof analizYap === "function") analizYap();
}
"""

# 1) CSS ekle
if "IKILI KOMBINE ANALIZ - OTOMATIK EKLENDI" not in html:
    html = html.replace("</style>", CSS + "\n</style>")

# 2) HTML panel ekle
if 'id="ikili-kombine-panel"' not in html:
    hedef = '<div id="analizSonuc">'
    idx = html.find(hedef)
    if idx == -1:
        raise SystemExit("analizSonuc bloğu bulunamadı.")
    html = html[:idx] + HTML_BLOCK + "\n" + html[idx:]

# 3) JS fonksiyonlarını ekle
if "function kombine2AnalizYap()" not in html:
    idx = html.rfind("yukle();")
    if idx == -1:
        raise SystemExit("yukle(); bulunamadı.")
    html = html[:idx] + JS_BLOCK + "\n" + html[idx:]

# 4) yukle sonrası init çağrısı ekle
if "setTimeout(kombine2InitSecenekler,1000);" not in html:
    html = html.replace("yukle();", "yukle();\nsetTimeout(kombine2InitSecenekler,1000);", 1)

p.write_text(html, encoding="utf-8")
print("✅ index.html içine İkili Kombine Analizi arayüzü eklendi.")