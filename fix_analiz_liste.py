from pathlib import Path

p = Path("index.html")
html = p.read_text(encoding="utf-8")

CSS = r"""
/* ANALIZ MAC TABLOSU - OTOMATIK EKLENDI */
.analiz-table-wrap{
  width:100%;
  overflow-x:auto;
  overflow-y:visible;
  border:1px solid #21262d;
  border-radius:8px;
  margin-top:14px;
  background:#0d1117;
}

.analiz-table{
  border-collapse:collapse;
  min-width:1400px;
  width:max-content;
  font-size:11px;
}

.analiz-table th{
  position:sticky;
  top:0;
  background:#161b22;
  color:#00c853;
  border:1px solid #21262d;
  padding:6px 8px;
  white-space:nowrap;
  z-index:2;
}

.analiz-table td{
  border:1px solid #21262d;
  padding:5px 7px;
  white-space:nowrap;
  background:#0d1117;
}

.analiz-table tr:nth-child(even) td{
  background:#111821;
}

.analiz-table .mac-col{
  min-width:240px;
  max-width:360px;
  white-space:normal;
  color:#e6e6e6;
  font-weight:600;
}

.analiz-table .skor-col{
  text-align:center;
  color:#f0b90b;
  font-weight:700;
}

.analiz-table .oran-cell{
  text-align:center;
  min-width:58px;
}

.analiz-table .oran-cell .oran-v{
  color:#f0b90b;
  font-weight:700;
}

.analiz-table .oran-cell .oran-p{
  color:#00c853;
  font-size:9px;
}

.analiz-table .oran-cell.dogru{
  background:#063b22!important;
  border-color:#00c853!important;
  box-shadow:inset 0 0 0 1px rgba(0,200,83,.45);
}

.analiz-table .oran-cell.dogru .oran-v{
  color:#00ff88!important;
}

.analiz-table .oran-cell.dogru .oran-p{
  color:#b6ffd6!important;
}

.analiz-table .bos-oran{
  color:#333;
}

.analiz-table-info{
  color:#888;
  font-size:12px;
  margin:8px 0;
}
"""

HELPERS = r"""
/* ANALIZ TABLOSU YARDIMCI FONKSIYONLARI - OTOMATIK EKLENDI */
function dogruOranAnaliz(m,key){
  if(!m || m.durum !== "bitti") return false;
  if(!key) return false;

  const se = Number(m.skor_ev || 0);
  const sd = Number(m.skor_dep || 0);
  const iySe = Number(m.skor_1y_ev || 0);
  const iySd = Number(m.skor_1y_dep || 0);

  const toplamGol = se + sd;
  const iyGol = iySe + iySd;
  const ikinciSe = se - iySe;
  const ikinciSd = sd - iySd;
  const ikinciGol = ikinciSe + ikinciSd;

  const kgVar = se > 0 && sd > 0;
  const iyKgVar = iySe > 0 && iySd > 0;
  const ikinciKgVar = ikinciSe > 0 && ikinciSd > 0;

  const ms = se > sd ? "1" : (se === sd ? "0" : "2");
  const iy = iySe > iySd ? "1" : (iySe === iySd ? "0" : "2");
  const ikinci = ikinciSe > ikinciSd ? "1" : (ikinciSe === ikinciSd ? "0" : "2");

  // Maç sonucu
  if(key === "Maç Sonucu_1") return ms === "1";
  if(key === "Maç Sonucu_0") return ms === "0";
  if(key === "Maç Sonucu_2") return ms === "2";

  // İlk yarı sonucu
  if(key === "İlk Yarı Sonucu_1") return iy === "1";
  if(key === "İlk Yarı Sonucu_0") return iy === "0";
  if(key === "İlk Yarı Sonucu_2") return iy === "2";

  // İkinci yarı sonucu
  if(key === "İkinci Yarı Sonucu_1") return ikinci === "1";
  if(key === "İkinci Yarı Sonucu_0") return ikinci === "0";
  if(key === "İkinci Yarı Sonucu_2") return ikinci === "2";

  // İlk yarı alt/üst önce kontrol edilmeli
  if(key.includes("İlk Yarı Alt/Üst 0.5_Alt")) return iyGol < 0.5;
  if(key.includes("İlk Yarı Alt/Üst 0.5_Üst")) return iyGol > 0.5;
  if(key.includes("İlk Yarı Alt/Üst 1.5_Alt")) return iyGol < 1.5;
  if(key.includes("İlk Yarı Alt/Üst 1.5_Üst")) return iyGol > 1.5;
  if(key.includes("İlk Yarı Alt/Üst 2.5_Alt")) return iyGol < 2.5;
  if(key.includes("İlk Yarı Alt/Üst 2.5_Üst")) return iyGol > 2.5;

  // Maç alt/üst
  if(key.includes("Alt/Üst 0.5_Alt")) return toplamGol < 0.5;
  if(key.includes("Alt/Üst 0.5_Üst")) return toplamGol > 0.5;
  if(key.includes("Alt/Üst 1.5_Alt")) return toplamGol < 1.5;
  if(key.includes("Alt/Üst 1.5_Üst")) return toplamGol > 1.5;
  if(key.includes("Alt/Üst 2.5_Alt")) return toplamGol < 2.5;
  if(key.includes("Alt/Üst 2.5_Üst")) return toplamGol > 2.5;
  if(key.includes("Alt/Üst 3.5_Alt")) return toplamGol < 3.5;
  if(key.includes("Alt/Üst 3.5_Üst")) return toplamGol > 3.5;
  if(key.includes("Altı/Üstü 2.5") && key.includes("_Alt")) return toplamGol < 2.5;
  if(key.includes("Altı/Üstü 2.5") && key.includes("_Üst")) return toplamGol > 2.5;

  // Karşılıklı gol
  if(key === "Karşılıklı Gol_Var") return kgVar;
  if(key === "Karşılıklı Gol_Yok") return !kgVar;
  if(key === "İlk Yarı Karşılıklı Gol_Var") return iyKgVar;
  if(key === "İlk Yarı Karşılıklı Gol_Yok") return !iyKgVar;
  if(key === "İkinci Yarı Karşılıklı Gol_Var") return ikinciKgVar;
  if(key === "İkinci Yarı Karşılıklı Gol_Yok") return !ikinciKgVar;

  // Maç sonucu + KG
  if(key.startsWith("Maç Sonucu ve Karşılıklı Gol_")){
    const secim = key.split("_")[1];
    if(!secim) return false;
    const parca = secim.split(" ve ");
    const msSecim = parca[0];
    const kgSecim = parca[1];
    return msSecim === ms && (kgSecim === "Var" ? kgVar : !kgVar);
  }

  // İlk yarı / maç sonucu
  if(key.startsWith("İlk Yarı / Maç Sonucu_")){
    const secim = key.split("_")[1];
    return secim === (iy + "/" + ms);
  }

  // İlk yarı sonucu + İY KG
  if(key.startsWith("İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_")){
    const secim = key.split("_")[1];
    if(!secim) return false;
    const parca = secim.split(" ve ");
    return parca[0] === iy && (parca[1] === "Var" ? iyKgVar : !iyKgVar);
  }

  // İlk yarı sonucu + İY Alt/Üst 1.5
  if(key.startsWith("İlk Yarı Sonucu ve Altı/Üstü 1.5_")){
    const secim = key.split("_")[1];
    if(!secim) return false;
    const parca = secim.split(" ve ");
    return parca[0] === iy && (parca[1] === "Üst" ? iyGol > 1.5 : iyGol < 1.5);
  }

  // Her iki yarıda üst/alt 1.5
  if(key === "Her İki Yarıda da Üst 1.5_Evet") return iyGol > 1.5 && ikinciGol > 1.5;
  if(key === "Her İki Yarıda da Üst 1.5_Hayır") return !(iyGol > 1.5 && ikinciGol > 1.5);
  if(key === "Her İki Yarıda da Alt 1.5_Evet") return iyGol < 1.5 && ikinciGol < 1.5;
  if(key === "Her İki Yarıda da Alt 1.5_Hayır") return !(iyGol < 1.5 && ikinciGol < 1.5);

  // İlk yarı ve ikinci yarıda KG olur
  if(key.startsWith("İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur_")){
    const secim = key.split("_")[1];
    if(!secim) return false;
    const parca = secim.split(" / ");
    const ilkDogru = parca[0] === "Evet" ? iyKgVar : !iyKgVar;
    const ikinciDogru = parca[1] === "Evet" ? ikinciKgVar : !ikinciKgVar;
    return ilkDogru && ikinciDogru;
  }

  // Tek / çift
  if(key === "Tek/Çift_Tek") return toplamGol % 2 === 1;
  if(key === "Tek/Çift_Çift") return toplamGol % 2 === 0;
  if(key === "İlk Yarı Tek/Çift_Tek") return iyGol % 2 === 1;
  if(key === "İlk Yarı Tek/Çift_Çift") return iyGol % 2 === 0;

  return false;
}

function analizKisaBaslik(key){
  if(typeof KA === "function") return KA(key);
  return key;
}

function analizOranKeyleri(maclar){
  const set = new Set();

  maclar.forEach(m=>{
    Object.keys(m.oranlar || {}).forEach(k=>set.add(k));
  });

  const oncelik = [
    "Maç Sonucu_1",
    "Maç Sonucu_0",
    "Maç Sonucu_2",
    "Alt/Üst 2.5_Alt",
    "Alt/Üst 2.5_Üst",
    "Karşılıklı Gol_Var",
    "Karşılıklı Gol_Yok",
    "İlk Yarı Sonucu_1",
    "İlk Yarı Sonucu_0",
    "İlk Yarı Sonucu_2",
    "İlk Yarı Alt/Üst 1.5_Alt",
    "İlk Yarı Alt/Üst 1.5_Üst",
    "İlk Yarı Karşılıklı Gol_Var",
    "İkinci Yarı Karşılıklı Gol_Var",
    "Her İki Yarıda da Üst 1.5_Evet",
    "Maç Sonucu ve Karşılıklı Gol_1 ve Var",
    "Maç Sonucu ve Karşılıklı Gol_0 ve Var",
    "Maç Sonucu ve Karşılıklı Gol_2 ve Var",
    "İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur_Evet / Evet"
  ];

  const arr = Array.from(set);

  arr.sort((a,b)=>{
    const ia = oncelik.indexOf(a);
    const ib = oncelik.indexOf(b);

    if(ia !== -1 && ib !== -1) return ia - ib;
    if(ia !== -1) return -1;
    if(ib !== -1) return 1;

    return a.localeCompare(b, "tr");
  });

  return arr;
}

function analizMacTablosuHtml(maclar){
  if(!maclar.length) return "";

  const keys = analizOranKeyleri(maclar);

  let h = "";
  h += '<div class="analiz-table-info">';
  h += 'Eşleşen maçlar alt alta listelenir. Oran sütunları sağa doğru kaydırılabilir. Yeşil hücreler o maç sonucuna göre doğru gelen oranlardır.';
  h += '</div>';

  h += '<div class="analiz-table-wrap">';
  h += '<table class="analiz-table">';
  h += '<thead><tr>';
  h += '<th>Tarih</th>';
  h += '<th>Saat</th>';
  h += '<th>Maç</th>';
  h += '<th>İY</th>';
  h += '<th>MS</th>';

  keys.forEach(k=>{
    h += '<th title="'+k.replaceAll('"','&quot;')+'">'+analizKisaBaslik(k)+'</th>';
  });

  h += '</tr></thead><tbody>';

  maclar.forEach(m=>{
    h += '<tr>';
    h += '<td>'+m.tarih+'</td>';
    h += '<td>'+(m.saat || "")+'</td>';
    h += '<td class="mac-col">'+m.ev_sahibi+' - '+m.deplasman+'</td>';
    h += '<td class="skor-col">'+(m.skor_1y_ev ?? 0)+'-'+(m.skor_1y_dep ?? 0)+'</td>';
    h += '<td class="skor-col">'+(m.skor_ev ?? 0)+'-'+(m.skor_dep ?? 0)+'</td>';

    keys.forEach(k=>{
      const v = m.oranlar ? m.oranlar[k] : null;

      if(v){
        const dogru = dogruOranAnaliz(m,k);
        h += '<td class="oran-cell'+(dogru ? ' dogru' : '')+'" title="'+k.replaceAll('"','&quot;')+'">';
        h += '<div class="oran-v">'+v+'</div>';
        h += '<div class="oran-p">%'+pct(v)+'</div>';
        h += '</td>';
      }else{
        h += '<td class="oran-cell"><span class="bos-oran">-</span></td>';
      }
    });

    h += '</tr>';
  });

  h += '</tbody></table></div>';
  return h;
}
"""

NEW_ANALIZ = r"""
function analizYap(){
  if(!analizFiltreler.length){
    document.getElementById("analizSonuc").innerHTML='<div class="analiz-yok">Filtre ekleyin</div>';
    return;
  }

  const hepsi = tumMaclar.concat(gecmisMaclar);

  const bm = hepsi.filter(m=>{
    if(m.durum !== "bitti") return false;

    for(const f of analizFiltreler){
      const v = m.oranlar ? m.oranlar[f.tur] : null;
      if(!v || Math.abs(v - f.deger) > 0.009) return false;
    }

    return true;
  });

  if(!bm.length){
    document.getElementById("analizSonuc").innerHTML='<div class="analiz-yok">Eşleşen bitmiş maç yok ('+hepsi.length+' maç tarandı)</div>';
    return;
  }

  let ek=0,be=0,dk=0,u25=0,a25=0,kgv=0,kgy=0,iye=0,iyb=0,iyd=0,tg=0;

  bm.forEach(m=>{
    const se=Number(m.skor_ev||0);
    const sd=Number(m.skor_dep||0);
    const t=se+sd;
    tg+=t;

    if(se>sd) ek++;
    else if(se===sd) be++;
    else dk++;

    if(t>2.5) u25++;
    else a25++;

    if(se>0&&sd>0) kgv++;
    else kgy++;

    const ise=Number(m.skor_1y_ev||0);
    const isd=Number(m.skor_1y_dep||0);

    if(ise>isd) iye++;
    else if(ise===isd) iyb++;
    else iyd++;
  });

  const n=bm.length;
  const P=v=>Math.round(v/n*100);
  const fs=analizFiltreler.map(f=>KA(f.tur)+"="+f.deger).join(" & ");

  let h='';
  h+='<div class="analiz-baslik">'+fs+' — '+n+' Maç ('+hepsi.length+' tarandı)</div>';

  h+='<div class="analiz-grid">';
  h+='<div class="ak"><div class="akb">Maç</div><div class="akd">'+n+'</div></div>';
  h+='<div class="ak"><div class="akb">Ort Gol</div><div class="akd">'+(tg/n).toFixed(1)+'</div></div>';
  h+='<div class="ak"><div class="akb">Üst2.5</div><div class="akd" style="color:#00c853">%'+P(u25)+'</div><div class="aka">'+u25+'/'+n+'</div></div>';
  h+='<div class="ak"><div class="akb">KG Var</div><div class="akd" style="color:#f0b90b">%'+P(kgv)+'</div><div class="aka">'+kgv+'/'+n+'</div></div>';
  h+='<div class="ak"><div class="akb">Ev Kazandı</div><div class="akd" style="color:#00c853">%'+P(ek)+'</div><div class="aka">'+ek+'/'+n+'</div></div>';
  h+='<div class="ak"><div class="akb">Berabere</div><div class="akd" style="color:#f0b90b">%'+P(be)+'</div><div class="aka">'+be+'/'+n+'</div></div>';
  h+='</div>';

  h+=bar("Maç Sonucu","Ev%"+P(ek),P(ek),"X%"+P(be),P(be),"Dep%"+P(dk),P(dk));
  h+=bar("Alt/Üst","Alt%"+P(a25),P(a25),"",0,"Üst%"+P(u25),P(u25));
  h+=bar("KG","Var%"+P(kgv),P(kgv),"",0,"Yok%"+P(kgy),P(kgy));
  h+=bar("İY","Ev%"+P(iye),P(iye),"X%"+P(iyb),P(iyb),"Dep%"+P(iyd),P(iyd));

  h+='<div class="analiz-baslik" style="margin-top:12px">📋 Filtreye Uyan Maçlar ve Oranlar</div>';
  h+=analizMacTablosuHtml(bm);

  document.getElementById("analizSonuc").innerHTML=h;
}
"""

# CSS ekle
if "ANALIZ MAC TABLOSU - OTOMATIK EKLENDI" not in html:
    html = html.replace("</style>", CSS + "\n</style>")

# Helper ekle
if "ANALIZ TABLOSU YARDIMCI FONKSIYONLARI - OTOMATIK EKLENDI" not in html:
    idx = html.find("function analizYap(){")
    if idx == -1:
        raise SystemExit("function analizYap bulunamadi")
    html = html[:idx] + HELPERS + "\n" + html[idx:]

# analizYap fonksiyonunu değiştir
start = html.find("function analizYap(){")
if start == -1:
    raise SystemExit("function analizYap bulunamadi")

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
    raise SystemExit("analizYap sonu bulunamadi")

html = html[:start] + NEW_ANALIZ + html[end:]

p.write_text(html, encoding="utf-8")
print("✅ index.html analiz listeleme ve yeşil doğru oran yaması uygulandı.")