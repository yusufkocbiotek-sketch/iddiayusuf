from pathlib import Path

p = Path("index.html")
html = p.read_text(encoding="utf-8")

HELPER = r"""
function ikiFiltreBasariDagilimi(maclar, f1, f2){
  let sadece1 = 0;
  let sadece2 = 0;
  let ikisi = 0;
  let hicbiri = 0;

  maclar.forEach(m=>{
    const a = dogruOranAnaliz(m, f1.tur);
    const b = dogruOranAnaliz(m, f2.tur);

    if(a && b) ikisi++;
    else if(a && !b) sadece1++;
    else if(!a && b) sadece2++;
    else hicbiri++;
  });

  return {
    toplam: maclar.length,
    sadece1,
    sadece2,
    ikisi,
    hicbiri
  };
}
"""

if "function ikiFiltreBasariDagilimi(maclar, f1, f2){" not in html:
    idx = html.find("function analizYap(){")
    if idx == -1:
        raise SystemExit("analizYap bulunamadı.")
    html = html[:idx] + HELPER + "\n" + html[idx:]

old_block = """  if(analizFiltreler.length === 2){
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
  }"""

new_block = """  if(analizFiltreler.length === 2){
    const f1 = analizFiltreler[0];
    const f2 = analizFiltreler[1];

    // Genel evren: tüm bitmiş maçlar içinde bu oranların varlığı
    const tek1 = tekliAnalizSonuc(hepsi, f1);
    const tek2 = tekliAnalizSonuc(hepsi, f2);
    const genel = ikiFiltreKarsilastirma(hepsi, f1, f2);

    // Yerel evren: filtreye uyan maçlar içinde gerçekten gelip gelmediği
    const lokal = ikiFiltreBasariDagilimi(bm, f1, f2);

    const lokal1 = lokal.sadece1 + lokal.ikisi;
    const lokal2 = lokal.sadece2 + lokal.ikisi;

    h+='<div class="analiz-baslik" style="margin-top:10px">⚡ Karşılaştırmalı Kombine Analizi</div>';
    h+='<div class="analiz-grid">';

    h+='<div class="ak"><div class="akb">'+KA(f1.tur)+' = '+f1.deger+' (tek başına)</div><div class="akd">%'+yuzdeHesapla(lokal1, lokal.toplam)+'</div><div class="aka">yerel: '+lokal1+'/'+lokal.toplam+' | genel: '+tek1.length+'/'+genel.toplam+'</div></div>';

    h+='<div class="ak"><div class="akb">'+KA(f2.tur)+' = '+f2.deger+' (tek başına)</div><div class="akd">%'+yuzdeHesapla(lokal2, lokal.toplam)+'</div><div class="aka">yerel: '+lokal2+'/'+lokal.toplam+' | genel: '+tek2.length+'/'+genel.toplam+'</div></div>';

    h+='<div class="ak"><div class="akb">İkisi Birlikte</div><div class="akd" style="color:#00c853">%'+yuzdeHesapla(lokal.ikisi, lokal.toplam)+'</div><div class="aka">yerel: '+lokal.ikisi+'/'+lokal.toplam+' | genel: '+genel.ikisi+'/'+genel.toplam+'</div></div>';

    h+='<div class="ak"><div class="akb">Sadece 1. Oran</div><div class="akd" style="color:#f0b90b">%'+yuzdeHesapla(lokal.sadece1, lokal.toplam)+'</div><div class="aka">yerel: '+lokal.sadece1+'/'+lokal.toplam+' | genel: '+genel.sadece1+'/'+genel.toplam+'</div></div>';

    h+='<div class="ak"><div class="akb">Sadece 2. Oran</div><div class="akd" style="color:#f0b90b">%'+yuzdeHesapla(lokal.sadece2, lokal.toplam)+'</div><div class="aka">yerel: '+lokal.sadece2+'/'+lokal.toplam+' | genel: '+genel.sadece2+'/'+genel.toplam+'</div></div>';

    h+='<div class="ak"><div class="akb">İkisi de Gelmedi</div><div class="akd" style="color:#e74c3c">%'+yuzdeHesapla(lokal.hicbiri, lokal.toplam)+'</div><div class="aka">yerel: '+lokal.hicbiri+'/'+lokal.toplam+' | genel: '+genel.hicbiri+'/'+genel.toplam+'</div></div>';

    h+='</div>';
  }"""

if old_block not in html:
    raise SystemExit("Eski karşılaştırmalı analiz bloğu bulunamadı. Dosyada yapı değişmiş olabilir.")

html = html.replace(old_block, new_block)

p.write_text(html, encoding="utf-8")
print("✅ Yerel + genel yüzde kartları eklendi.")