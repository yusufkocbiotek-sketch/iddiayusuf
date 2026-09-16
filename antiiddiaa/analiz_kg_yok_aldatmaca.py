import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

total = len(matches)

# =====================================================================
# KRİTİK PATTERN TESPİTİ:
#
# HATALI MACLAR (-563, -566):
#   KG Yok = 1.37 / 1.40 → "kısır maç" dedi sistem
#   AMA: Tek/Çift_Çift = 1.54 (Çift gol sayısı = 0,2,4... favori!)
#         Handikap 0:1_2 = 1.29 / 1.44 → Dep Handikap favori
#         1.5 Üst = 1.51 / 1.43 → 2+ gol bekleniyor!
#
# DOĞRU MAÇLAR (-564 Mouloudia 0-0, -567 Moghreb 0-0):
#   Çift = 1.54 (aynı) AMA Tek/Çift_Tek farklı mı?
#
# Ayrım: KG Yok ağırlıklı ama 1.5 Üst < 1.55 = GOL OLMALI!
# Eğer 1.5 Üst <= 1.55 → piyasa 2+ gol bekliyor → KG Yok = YANILTICI
#
# KURAL: KG Yok favori (>= 1.35) IKEN 1.5 Üst <= 1.55 ise
#        Bu "KG Yok" SAHTE → Maç gollü ama tek taraflı biter
# =====================================================================

print('=== KARŞILAŞTIRMALI ORAN ANALİZİ ===')
print()

# Hatali (gol oldu)
hatali = [563, 566]
# Dogru (kisir kaldi)
dogru = [564, 567, 565]

for grp, idxler in [('HATALI (Gol Oldu)', hatali), ('DOGRU (Kisir Kaldi)', dogru)]:
    print('--- ' + grp + ' ---')
    for idx in idxler:
        m = matches[total - idx]
        odds = m.get('oranlar', {})
        ms1 = odds.get('Maç Sonucu_1', 99)
        ms0 = odds.get('Maç Sonucu_0', 99)
        ms2 = odds.get('Maç Sonucu_2', 99)
        kg_var = odds.get('Karşılıklı Gol_Var', 99)
        kg_yok = odds.get('Karşılıklı Gol_Yok', 99)
        alt15 = odds.get('Alt/Üst 1.5_Alt', 99)
        ust15 = odds.get('Alt/Üst 1.5_Üst', 99)
        tek = odds.get('Tek / Çift_Tek', 99)
        cift = odds.get('Tek / Çift_Çift', 99)
        h2 = odds.get('Handikaplı Maç Sonucu 0:1_2', 99)
        cs12 = odds.get('Çifte Şans_12', 99)
        dep_05 = odds.get('Deplasman Alt/Üst 0.5_Üst', 99)
        ev_05 = odds.get('Ev Sahibi Alt/Üst 0.5_Üst', 99)
        skor = str(m.get('skor_ev', '?')) + '-' + str(m.get('skor_dep', '?'))
        
        print('  -' + str(idx) + ' ' + m.get('ev_sahibi', '?') + ' vs ' + m.get('deplasman', '?') + ' → ' + skor)
        print('    KGVar=' + str(kg_var) + '  KGYok=' + str(kg_yok))
        print('    1.5Alt=' + str(alt15) + '  1.5Ust=' + str(ust15) + '  ← KRİTİK!')
        print('    Tek=' + str(tek) + '  Cift=' + str(cift))
        print('    Handikap_Dep=' + str(h2) + '  CS12=' + str(cs12))
        print('    EvGol0.5Ust=' + str(ev_05) + '  DepGol0.5Ust=' + str(dep_05))
        print()

# Şimdi istatistiksel doğrula:
# Profil: KGVar > 2.0 + KGYok < 1.42 + 1.5Üst < 1.55
# Bu profilde sonuç ne?
print()
print('=== İSTATİSTİKSEL DOĞRULAMA ===')
print('Profil: KGVar >= 2.0, KGYok <= 1.42, 1.5Üst <= 1.55')
print()

found = []
for m in matches:
    odds = m.get('oranlar', {})
    kg_var = odds.get('Karşılıklı Gol_Var', 99)
    kg_yok = odds.get('Karşılıklı Gol_Yok', 99)
    ust15 = odds.get('Alt/Üst 1.5_Üst', 99)
    skor_ev = m.get('skor_ev', -1)
    skor_dep = m.get('skor_dep', -1)
    
    if kg_var >= 2.0 and kg_yok <= 1.42 and ust15 <= 1.55 and ust15 != 99 and skor_ev >= 0:
        total_gol = skor_ev + skor_dep
        found.append({
            'idx': m.get('index', '?'),
            'ev': m.get('ev_sahibi', '?'),
            'dep': m.get('deplasman', '?'),
            'kg_var': kg_var, 'kg_yok': kg_yok, 'ust15': ust15,
            'skor': str(skor_ev)+'-'+str(skor_dep),
            'total': total_gol,
            'iy_ev': m.get('skor_1y_ev', '?'),
            'iy_dep': m.get('skor_1y_dep', '?')
        })

gol_oldu = [x for x in found if x['total'] >= 2]
kisir = [x for x in found if x['total'] <= 1]
print('Toplam mac:', len(found))
print('2+ gol (GOL OLDU):', len(gol_oldu), '(%.1f%%)' % (100*len(gol_oldu)/len(found) if found else 0))
print('0-1 gol (KISIR):', len(kisir), '(%.1f%%)' % (100*len(kisir)/len(found) if found else 0))
print()
print('--- GOL OLAN ornekler ---')
for x in gol_oldu[:12]:
    print('  #' + str(x['idx']) + ' ' + x['ev'] + ' vs ' + x['dep'] +
          ' | KGVar=' + str(x['kg_var']) + ' KGYok=' + str(x['kg_yok']) +
          ' 1.5Ust=' + str(x['ust15']) +
          ' | IY:' + str(x['iy_ev']) + '-' + str(x['iy_dep']) + ' MS:' + x['skor'])
print()
print('--- KISIR KALAN ornekler ---')
for x in kisir[:8]:
    print('  #' + str(x['idx']) + ' ' + x['ev'] + ' vs ' + x['dep'] +
          ' | KGVar=' + str(x['kg_var']) + ' KGYok=' + str(x['kg_yok']) +
          ' 1.5Ust=' + str(x['ust15']) +
          ' | IY:' + str(x['iy_ev']) + '-' + str(x['iy_dep']) + ' MS:' + x['skor'])
