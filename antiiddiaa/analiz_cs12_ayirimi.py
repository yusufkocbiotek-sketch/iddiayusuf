import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

# ==========================================================
# Asıl fark bu değil. Tekrar bak:
# HATALI: 1.5Alt = 1.88 / 2.03 → 1.5 Alt DAHA YÜKSEK (yani 1.5 Üst beklenmiyor görünse de...)
# DOGRU : 1.5Alt = 1.92 / 1.93 → 1.5 Alt biraz daha düşük
#
# HANDİKAP farkı:
# -563: Dep Handi = 1.29 (çok düşük, dep çok favori)
# -566: Dep Handi = 1.44
# -564: Dep Handi = 1.33
# -567: Dep Handi = 1.42
#
# CS12: -563=1.31, -566=1.29 (düşük)
#        -564=1.28, -567=1.26 (daha düşük - herhangi kazanır)
#
# -563'te CS12=1.31 ve Handi_dep=1.29 → dep hem maçı hem 1:0'ı kazanır → DEP GOL ATAR!
# Dep 0.5 Üst = 1.47 (dep kesin gol atar)
# Ev 0.5 Üst = 1.34 (ev de gol atar! 2.23 değil 1.34!)
#
# GERÇEK KRİTİK FARK:
# -563: Ev 0.5 Üst = 1.34  ← EV GOLÜ NEREDEYSE GARANTİ!
# -564: Ev 0.5 Üst = 1.31  ← benzer ama...
# -567: Ev 0.5 Üst = 1.27  ← daha düşük = ev gol atar
#
# Bekle, -567 de ev gol atar sinyali ama 0-0 bitti?
# -567 oranı: Ev 0.5 Üst = 1.27 AMA skor 0-0...
#
# Yeni yaklaşım: CS12 + 1.5Alt kombinasyonu
# CS12 <= 1.30 VE 1.5Alt >= 1.90 → Maç gollü biter!
# ==========================================================

print('=== YENİ AYRIMI DENİYORUZ: CS12 <= 1.30 + 1.5Alt >= 1.90 ===')
print()

for idx, label in [(563,'HATALI'), (566,'HATALI'), (564,'DOGRU'), (567,'DOGRU'), (565,'BERAB')]:
    m = matches[len(matches)-idx]
    o = m.get('oranlar', {})
    cs12 = o.get('Çifte Şans_12', 99)
    alt15 = o.get('Alt/Üst 1.5_Alt', 99)
    dep_h = o.get('Handikaplı Maç Sonucu 0:1_2', 99)
    skor = str(m.get('skor_ev'))+'-'+str(m.get('skor_dep'))
    ev05 = o.get('Ev Sahibi Alt/Üst 0.5_Üst', o.get('Ev Sahibi Alt/Üst 0.5_Üst', 99))
    dep05 = o.get('Deplasman Alt/Üst 0.5_Üst', 99)
    print(label+' -'+str(idx)+' | '+skor+' | CS12='+str(cs12)+' 1.5Alt='+str(alt15)+' DepH='+str(dep_h)+' Ev05Ust='+str(ev05)+' Dep05Ust='+str(dep05))

print()
print('=== İSTATİSTİK: KGVar>=2.0 + KGYok<=1.42 + 1.5Ust<=1.55 + CS12<=1.31 ===')

found = []
for m in matches:
    o = m.get('oranlar', {})
    kg_var = o.get('Karşılıklı Gol_Var', 99)
    kg_yok = o.get('Karşılıklı Gol_Yok', 99)
    ust15 = o.get('Alt/Üst 1.5_Üst', 99)
    alt15 = o.get('Alt/Üst 1.5_Alt', 99)
    cs12 = o.get('Çifte Şans_12', 99)
    sev = m.get('skor_ev', -1)
    sdep = m.get('skor_dep', -1)

    if kg_var >= 2.0 and kg_yok <= 1.42 and ust15 <= 1.55 and ust15 != 99 and cs12 <= 1.32 and cs12 != 99 and sev >= 0:
        total = sev + sdep
        found.append({'total': total, 'kg_var': kg_var, 'kg_yok': kg_yok,
                       'ust15': ust15, 'alt15': alt15, 'cs12': cs12,
                       'sev': sev, 'sdep': sdep,
                       'ev': m.get('ev_sahibi','?'), 'dep': m.get('deplasman','?'),
                       'idx': m.get('index','?')})

gol2p = [x for x in found if x['total'] >= 2]
kisir = [x for x in found if x['total'] <= 1]
print('Toplam mac: ' + str(len(found)))
print('2+ gol GOL OLDU: ' + str(len(gol2p)) + ' (%.1f%%)' % (100*len(gol2p)/len(found) if found else 0))
print('0-1 gol KISIR  : ' + str(len(kisir)) + ' (%.1f%%)' % (100*len(kisir)/len(found) if found else 0))
print()

# Şimdi alt15 ile ayir
print('--- CS12<=1.32 + 1.5ALT >= 1.90 ise GOL MU? ---')
sub_alt = [x for x in found if x['alt15'] >= 1.90]
sub_kisir = [x for x in found if x['alt15'] < 1.90]
gol_alt = [x for x in sub_alt if x['total'] >= 2]
gol_kisir = [x for x in sub_kisir if x['total'] >= 2]
print('1.5Alt >= 1.90 (' + str(len(sub_alt)) + ' mac): ' + str(len(gol_alt)) + ' gol (%.1f%%)' % (100*len(gol_alt)/len(sub_alt) if sub_alt else 0))
print('1.5Alt <  1.90 (' + str(len(sub_kisir)) + ' mac): ' + str(len(gol_kisir)) + ' gol (%.1f%%)' % (100*len(gol_kisir)/len(sub_kisir) if sub_kisir else 0))
print()
print('ORNEKLER (CS12<=1.32 + 1.5Alt>=1.90 + gol olan):')
for x in [y for y in sub_alt if y['total'] >= 2][:10]:
    print('  #'+str(x['idx'])+' '+x['ev']+' vs '+x['dep']+' | KGVar='+str(x['kg_var'])+' KGYok='+str(x['kg_yok'])+' 1.5Ust='+str(x['ust15'])+' 1.5Alt='+str(x['alt15'])+' CS12='+str(x['cs12'])+' → '+str(x['sev'])+'-'+str(x['sdep']))
