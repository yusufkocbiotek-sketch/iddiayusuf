from pathlib import Path
import shutil

INDEX = Path("index.html")
BACKUP = Path("index_backup_before_compare.html")

if not INDEX.exists():
    raise SystemExit("index.html bulunamadı.")

# Yedek al
shutil.copy2(INDEX, BACKUP)

html = INDEX.read_text(encoding="utf-8")

HELPERS = r"""
/* KARSILASTIRMALI ANALIZ YARDIMCI FONKSIYONLARI - OTOMATIK EKLENDI */
function tekliAnalizSonuc(hepsi, filtre){
  const uygun = hepsi.filter(m=>{
    if(m.durum !== "bitti") return false;
    const v = m.oranlar ? m.oranlar[filtre.tur] : null;
    if(!v || Math.abs(v - filtre.deger) > 0.009) return false;
    return true;
  });

  return uygun;
}

function ikiFiltreKarsilastirma(hepsi, f1, f2){
  const biten = hepsi.filter(m=>m.durum === "bitti");

  let sadece1 = 0;
  let sadece2 = 0;
  let ikisi = 0;
  let hicbiri = 0;

  biten.forEach(m=>{
    const v1 = m.oranlar ? m.oranlar[f1.tur] : null;
    const v2 = m.oranlar ? m.oranlar[f2.tur] : null;

    const a = !!(v1 && Math.abs(v1 - f1.deger) <= 0.009);
    const b = !!(v2 && Math.abs(v2 - f2.deger) <= 0.009);

    if(a && b) ikisi++;
    else if(a && !b) sadece1++;
    else if(!a && b) sadece2++;
    else hicbiri++;
  });

  return {
    toplam: biten.length,
    sadece1,
    sadece2,
    ikisi,
    hicbiri
  };
}

function yuzdeHesapla(sayi, toplam){
  if(!toplam) return 0;
  return Math.round((sayi / toplam) * 100);
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

  // Ana kartlar
  h+='<div class="analiz-grid">';
  h+='<div class="ak"><div class="akb">Maç</div><div class="akd">'+n+'</div></div>';
  h+='<div class="ak"><div class="akb">Ort Gol</div><div class="akd">'+(tg/n).toFixed(1)+'</div></div>';
  h+='<div class="ak"><div class="akb">Üst2.5</div><div class="akd" style="color:#00c853">%'+P(u25)+'</div><div class="aka">'+u25+'/'+n+'</div></div>';
  h+='<div class="ak"><div class="akb">KG Var</div><div class="akd" style="color:#f0b90b">%'+P(kgv)+'</div><div class="aka">'+kgv+'/'+n+'</div></div>';
  h+='<div class="ak"><div class="akb">Ev Kazandı</div><div class="akd" style="color:#00c853">%'+P(ek)+'</div><div class="aka">'+ek+'/'+n+'</div></div>';
  h+='<div class="ak"><div class="akb">Berabere</div><div class="akd" style="color:#f0b90b">%'+P(be)+'</div><div class="aka">'+be+'/'+n+'</div></div>';
  h+='</div>';

  // Eğer tam 2 filtre varsa karşılaştırmalı kartlar ekle
  if(analizFiltreler.length === 2){
    const f1 = analizFiltreler[0];
    const f2 = analizFiltreler[1];

    const tek1 = tekliAnalizSonuc(hepsi, f1);
    const tek2 = tekliAnalizSonuc(hepsi, f2);
    const k = ikiFiltreKarsilastirma(hepsi, f1, f2);

    h+='<div class="analiz-baslik" style="margin-top:10px">⚡ Karşılaştırmalı Kombine Analizi</div>';
    h+='<div class="analiz-grid">';
    h+='<div class="ak"><div class="akb">'+KA(f1.tur)+' = '+f1.deger+'</div><div class="akd">%'+yuzdeHesapla(tek1.length, k.toplam)+'</div><div class="aka">'+tek1.length+'/'+k.toplam+'</div></div>';
    h+='<div class="ak"><div class="akb">'+KA(f2.tur)+' = '+f2.deger+'</div><div class="akd">%'+yuzdeHesapla(tek2.length, k.toplam)+'</div><div class="aka">'+tek2.length+'/'+k.toplam+'</div></div>';
    h+='<div class="ak"><div class="akb">İkisi Birlikte</div><div class="akd" style="color:#00c853">%'+yuzdeHesapla(k.ikisi, k.toplam)+'</div><div class="aka">'+k.ikisi+'/'+k.toplam+'</div></div>';
    h+='<div class="ak"><div class="akb">Sadece 1. Oran</div><div class="akd" style="color:#f0b90b">%'+yuzdeHesapla(k.sadece1, k.toplam)+'</div><div class="aka">'+k.sadece1+'/'+k.toplam+'</div></div>';
    h+='<div class="ak"><div class="akb">Sadece 2. Oran</div><div class="akd" style="color:#f0b90b">%'+yuzdeHesapla(k.sadece2, k.toplam)+'</div><div class="aka">'+k.sadece2+'/'+k.toplam+'</div></div>';
    h+='<div class="ak"><div class="akb">İkisi de Gelmedi</div><div class="akd" style="color:#e74c3c">%'+yuzdeHesapla(k.hicbiri, k.toplam)+'</div><div class="aka">'+k.hicbiri+'/'+k.toplam+'</div></div>';
    h+='</div>';
  }

  h+=bar("Maç Sonucu","Ev%"+P(ek),P(ek),"X%"+P(be),P(be),"Dep%"+P(dk),P(dk));
  h+=bar("Alt/Üst","Alt%"+P(a25),P(a25),"",0,"Üst%"+P(u25),P(u25));
  h+=bar("KG","Var%"+P(kgv),P(kgv),"",0,"Yok%"+P(kgy),P(kgy));
  h+=bar("İY","Ev%"+P(iye),P(iye),"X%"+P(iyb),P(iyb),"Dep%"+P(iyd),P(iyd));

  h+='<div class="analiz-baslik" style="margin-top:12px">📋 Filtreye Uyan Maçlar ve Oranlar</div>';
  h+=analizMacTablosuHtml(bm);

  document.getElementById("analizSonuc").innerHTML=h;
}
"""

# CSS yardımcılarını ekle
if "KARSILASTIRMALI ANALIZ YARDIMCI FONKSIYONLARI - OTOMATIK EKLENDI" not in html:
    idx = html.find("function analizYap(){")
    if idx == -1:
        raise SystemExit("analizYap bulunamadı.")
    html = html[:idx] + HELPERS + "\n" + html[idx:]

# analizYap fonksiyonunu değiştir
start = html.find("function analizYap(){")
if start == -1:
    raise SystemExit("analizYap fonksiyonu bulunamadı.")

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
    raise SystemExit("analizYap sonu bulunamadı.")

html = html[:start] + NEW_ANALIZ + html[end:]

INDEX.write_text(html, encoding="utf-8")
print("✅ Karşılaştırmalı ikili analiz kartları eklendi.")
print("📦 Yedek alındı:", BACKUP.name)