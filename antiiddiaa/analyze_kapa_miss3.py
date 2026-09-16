import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

# Guclu dep favorisi: MS2 <= 1.55 + X2 (hem eski '-_0 ve 2' hem yeni 'Çifte Şans_0 ve 2') <= 1.10
# + KG Var < KG Yok (piyasa aslinda KG Var dusuk bekliyor ama KG Var favori)

found = []
for m in matches:
    odds = m.get('oranlar', {})
    ms2 = odds.get('Maç Sonucu_2', 99)
    
    # X2 anahtarini bul
    x2 = odds.get('Çifte Şans_0 ve 2', odds.get('-_0 ve 2', 99))
    
    kg_var = odds.get('Karşılıklı Gol_Var', 99)
    kg_yok = odds.get('Karşılıklı Gol_Yok', 99)
    
    skor_ev = m.get('skor_ev', -1)
    skor_dep = m.get('skor_dep', -1)

    # Profil: Guclu dep + X2 cok dusuk + KG Var < KG Yok (suni KG Var aldatmacasi)
    if ms2 <= 1.55 and x2 <= 1.10 and kg_var < kg_yok and skor_ev >= 0:
        total = skor_ev + skor_dep
        ev_gol = skor_ev > 0
        found.append({
            'idx': m.get('index', '?'),
            'ev': m.get('ev_sahibi', '?'),
            'dep': m.get('deplasman', '?'),
            'ms2': ms2, 'x2': x2, 'kg_var': kg_var, 'kg_yok': kg_yok,
            'skor': str(skor_ev)+'-'+str(skor_dep),
            'ev_gol': ev_gol, 'total': total
        })

print('MS2<=1.55 + X2<=1.10 + KGVar<KGYok (suni KG Var):', len(found), 'mac')
if found:
    ev_gol_var = [x for x in found if x['ev_gol']]
    ev_gol_yok = [x for x in found if not x['ev_gol']]
    alt25 = [x for x in found if x['total'] <= 2]
    ust25 = [x for x in found if x['total'] > 2]
    print('Ev GOL ATTI (1513 diyordu):', len(ev_gol_var), '(%.1f%%)' % (100*len(ev_gol_var)/len(found)))
    print('Ev GOL ATMADI (Gercek KG Yok):', len(ev_gol_yok), '(%.1f%%)' % (100*len(ev_gol_yok)/len(found)))
    print('2.5 ALT:', len(alt25), '(%.1f%%)' % (100*len(alt25)/len(found)))
    print('2.5 UST:', len(ust25), '(%.1f%%)' % (100*len(ust25)/len(found)))
    print()
    print('--- EV GOL ATMADI ornekler ---')
    for x in ev_gol_yok[:15]:
        line = '  #' + str(x['idx']) + ' ' + x['ev'] + ' vs ' + x['dep']
        line += ' | MS2=' + str(x['ms2']) + ' X2=' + str(x['x2'])
        line += ' | KGVar=' + str(x['kg_var']) + ' KGYok=' + str(x['kg_yok'])
        line += ' | Skor=' + x['skor']
        print(line)
    print()
    print('--- EV GOL ATTI ornekler ---')
    for x in ev_gol_var[:10]:
        line = '  #' + str(x['idx']) + ' ' + x['ev'] + ' vs ' + x['dep']
        line += ' | MS2=' + str(x['ms2']) + ' X2=' + str(x['x2'])
        line += ' | KGVar=' + str(x['kg_var']) + ' KGYok=' + str(x['kg_yok'])
        line += ' | Skor=' + x['skor']
        print(line)
