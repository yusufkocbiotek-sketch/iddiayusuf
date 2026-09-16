import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

# ==========================================================
# SON KRİTİK ANALİZ: Asıl fark nerede?
#
# HATALI (-563, -566): Dep Handikap 0:1 = 1.29 / 1.44
# DOGRU  (-564, -567, -565): 1.33 / 1.42 / 1.43
#
# Yani DEP HANDİKAP çok düşük → iddaa deplasmanın FARK ATACAĞINI söylüyor!
# Eğer dep fark atacaksa VE KG Yok favori → aslında tek taraflı ama GOL OLACAK
#
# AMA: KG Yok = 1.37 → iddaa "karşılıklı gol olmaz" diyor
# VE DEP HANDİKAP = 1.29 → "dep fark atar" diyor
#
# Bu ikisi bir arada = Dep gol atar (ve çok atar), ev gol atmaz
# = Maçta 2-0, 3-0 tipi GOLLÜ ama KG YOK senaryo
# = Bizim sistem KG Yok + kısır dedi YANLIŞ!
# = Doğru: DEP GALİBİYETİ + KG YOK + GOL OLUR (tek taraflı)
#
# Skor 2-1 oldu = KG Var gerçekleşti. Neden?
# Ev 0.5 Üst = 1.34 / 1.26 → ev de gol atar sinyali var!
# Demek ki CS12 + Ev 0.5 Üst birlikte bakılmalı
# ==========================================================

# YENİ KRİTİK FORMÜL:
# KGVar >= 2.0 (KG Var beklenmiyor görünüyor)
# VE KGYok <= 1.42 (yani kısır görünüyor)
# VE 1.5Üst <= 1.55 (ama gol OLACAK)
# VE Dep Handikap 0:1_2 <= 1.35 (dep fark atar)
# VE Ev 0.5 Üst <= 1.38 (ev de en az 1 gol atar!)
# → Bu = SAHTE KG YOK! Maç aslında gollü (2-1, 2-0 gibi)

print('=== FINAL KURAL FORMÜLÜ ===')
print()
print('Aday formül: KGVar>=2.0 + KGYok<=1.42 + 1.5Ust<=1.55 + DepH<=1.35 + Ev0.5Ust<=1.38')
print()

for idx, label in [(563,'HATALI'), (566,'HATALI'), (564,'DOGRU'), (567,'DOGRU'), (565,'BERAB')]:
    m = matches[len(matches)-idx]
    o = m.get('oranlar', {})
    dep_h = o.get('Handikaplı Maç Sonucu 0:1_2', 99)
    ev05 = o.get('Ev Sahibi Alt/Üst 0.5_Üst', 99)
    dep05 = o.get('Deplasman Alt/Üst 0.5_Üst', 99)
    skor = str(m.get('skor_ev'))+'-'+str(m.get('skor_dep'))
    cs12 = o.get('Çifte Şans_12', 99)
    ust15 = o.get('Alt/Üst 1.5_Üst', 99)
    
    # Formul tetikler mi?
    trigger = dep_h <= 1.35 and ev05 <= 1.38 and ev05 != 99
    print(label+' -'+str(idx)+' → '+skor+' | DepH='+str(dep_h)+' Ev0.5Ust='+str(ev05)+' Dep0.5Ust='+str(dep05)+' 1.5Ust='+str(ust15)+' | TETIKLER:'+str(trigger))

print()
# İstatistik
found = []
for m in matches:
    o = m.get('oranlar', {})
    kg_var = o.get('Karşılıklı Gol_Var', 99)
    kg_yok = o.get('Karşılıklı Gol_Yok', 99)
    ust15 = o.get('Alt/Üst 1.5_Üst', 99)
    dep_h = o.get('Handikaplı Maç Sonucu 0:1_2', 99)
    ev05 = o.get('Ev Sahibi Alt/Üst 0.5_Üst', 99)
    sev = m.get('skor_ev', -1)
    sdep = m.get('skor_dep', -1)

    if (kg_var >= 2.0 and kg_yok <= 1.42 and ust15 <= 1.55 and ust15 != 99
            and dep_h <= 1.38 and dep_h != 99 and ev05 <= 1.40 and ev05 != 99 and sev >= 0):
        total = sev + sdep
        found.append({'total': total, 'kg_var': kg_var, 'dep_h': dep_h, 'ev05': ev05,
                      'ev': m.get('ev_sahibi','?'), 'dep': m.get('deplasman','?'), 'idx': m.get('index','?'),
                      'skor': str(sev)+'-'+str(sdep)})

gol2p = [x for x in found if x['total'] >= 2]
kisir = [x for x in found if x['total'] <= 1]
print('KGVar>=2.0 + KGYok<=1.42 + 1.5Ust<=1.55 + DepH<=1.38 + Ev0.5Ust<=1.40')
print('Toplam mac: ' + str(len(found)))
if found:
    print('2+ gol (SAHTE KG YOK → GOL VAR): ' + str(len(gol2p)) + ' (%.1f%%)' % (100*len(gol2p)/len(found)))
    print('0-1 gol (GERCEK KISIR)          : ' + str(len(kisir)) + ' (%.1f%%)' % (100*len(kisir)/len(found)))
    print()
    print('--- ORNEKLER (2+ gol olanlar) ---')
    for x in gol2p[:15]:
        print('  #'+str(x['idx'])+' '+x['ev']+' vs '+x['dep']+' | KGVar='+str(x['kg_var'])+' DepH='+str(x['dep_h'])+' Ev0.5='+str(x['ev05'])+' → '+x['skor'])
