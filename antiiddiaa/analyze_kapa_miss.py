import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

# Kapa-KTP profili: MS2=1.47, X2=1.06, IY KG Yok=1.09, 2Y KG Yok=1.19
# Profil: Guclu dep favorisi (MS2 <= 1.55), X2 ultra dusuk (<= 1.10)

found = []
for m in matches:
    odds = m.get('oranlar', {})

    ms2 = 99.0
    for k in ['Maç Sonucu_2', 'Mac Sonucu_2', 'Maç Sonucu 2']:
        if k in odds:
            ms2 = odds[k]
            break

    x2 = 99.0
    for k in ['Çifte Şans_0 ve 2', 'Cifte Sans_0 ve 2', 'Çifte Şans_X2']:
        if k in odds:
            x2 = odds[k]
            break

    kg_var = 99.0
    for k in ['Karşılıklı Gol_Var', 'Karsılikli Gol_Var']:
        if k in odds:
            kg_var = odds[k]
            break

    kg_yok = 99.0
    for k in ['Karşılıklı Gol_Yok', 'Karsılikli Gol_Yok']:
        if k in odds:
            kg_yok = odds[k]
            break

    skor_ev = m.get('skor_ev', -1)
    skor_dep = m.get('skor_dep', -1)

    # Guclu dep favorisi + X2 ultra dusuk + KG Yok favori
    if ms2 <= 1.55 and x2 <= 1.10 and kg_yok > kg_var and skor_ev >= 0:
        total = skor_ev + skor_dep
        ev_gol = skor_ev > 0
        found.append({
            'idx': m.get('index', '?'),
            'ev': m.get('ev_sahibi', '?'),
            'dep': m.get('deplasman', '?'),
            'ms2': ms2, 'x2': x2,
            'kg_var': kg_var, 'kg_yok': kg_yok,
            'skor': str(skor_ev)+'-'+str(skor_dep),
            'total': total, 'ev_gol': ev_gol
        })

print('MS2<=1.55 + X2<=1.10 + KGYok favori profili:', len(found), 'mac')
if found:
    ev_gol_var = [x for x in found if x['ev_gol']]
    ev_gol_yok = [x for x in found if not x['ev_gol']]
    alt25 = [x for x in found if x['total'] <= 2]
    ust25 = [x for x in found if x['total'] > 2]
    print('Ev GOL ATTI (KG Var):', len(ev_gol_var), '(%.1f%%)' % (100*len(ev_gol_var)/len(found)))
    print('Ev GOL ATMADI (KG Yok):', len(ev_gol_yok), '(%.1f%%)' % (100*len(ev_gol_yok)/len(found)))
    print('2.5 ALT:', len(alt25), '(%.1f%%)' % (100*len(alt25)/len(found)))
    print('2.5 UST:', len(ust25), '(%.1f%%)' % (100*len(ust25)/len(found)))
    print()
    print('--- KG YOK (Ev Golsuz) Ornekler ---')
    for x in ev_gol_yok[:15]:
        print('  #'+str(x['idx'])+' | '+x['ev']+' vs '+x['dep']+' | MS2='+str(x['ms2'])+' X2='+str(x['x2'])+' KGVar='+str(x['kg_var'])+' KGYok='+str(x['kg_yok'])+' | Skor='+x['skor'])
    print()
    print('--- KG VAR (Ev de Gol) Ornekler ---')
    for x in ev_gol_var[:10]:
        print('  #'+str(x['idx'])+' | '+x['ev']+' vs '+x['dep']+' | MS2='+str(x['ms2'])+' X2='+str(x['x2'])+' KGVar='+str(x['kg_var'])+' KGYok='+str(x['kg_yok'])+' | Skor='+x['skor'])
