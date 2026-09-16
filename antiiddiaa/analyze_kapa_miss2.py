import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

found = []
for m in matches:
    odds = m.get('oranlar', {})
    ms2 = odds.get('Maç Sonucu_2', 99)
    x2 = odds.get('Çifte Şans_0 ve 2', 99)
    kg_var = odds.get('Karşılıklı Gol_Var', 99)
    kg_yok = odds.get('Karşılıklı Gol_Yok', 99)
    ev_05_alt = odds.get('Ev Sahibi Alt/Üst 0.5_Alt', 99)
    skor_ev = m.get('skor_ev', -1)
    skor_dep = m.get('skor_dep', -1)

    if ms2 <= 1.55 and x2 <= 1.10 and kg_var <= 1.55 and ev_05_alt >= 2.10 and skor_ev >= 0:
        total = skor_ev + skor_dep
        ev_gol = skor_ev > 0
        found.append({
            'idx': m.get('index', '?'),
            'ev': m.get('ev_sahibi', '?'),
            'dep': m.get('deplasman', '?'),
            'ms2': ms2, 'x2': x2, 'kg_var': kg_var, 'kg_yok': kg_yok,
            'ev_05_alt': ev_05_alt,
            'skor': str(skor_ev)+'-'+str(skor_dep),
            'ev_gol': ev_gol, 'total': total
        })

print('Profil mac sayisi:', len(found))
if found:
    ev_gol_var = [x for x in found if x['ev_gol']]
    ev_gol_yok = [x for x in found if not x['ev_gol']]
    alt25 = [x for x in found if x['total'] <= 2]
    print('Ev GOL ATTI:', len(ev_gol_var), '(%.1f%%)' % (100*len(ev_gol_var)/len(found)))
    print('Ev GOL ATMADI KG Yok:', len(ev_gol_yok), '(%.1f%%)' % (100*len(ev_gol_yok)/len(found)))
    print('2.5 ALT:', len(alt25), '(%.1f%%)' % (100*len(alt25)/len(found)))
    print()
    print('--- EV GOL ATMADI ---')
    for x in ev_gol_yok[:12]:
        line = '  #' + str(x['idx']) + ' ' + x['ev'] + ' vs ' + x['dep']
        line += ' | X2=' + str(x['x2']) + ' KGVar=' + str(x['kg_var']) + ' KGYok=' + str(x['kg_yok'])
        line += ' | Ev0.5Alt=' + str(x['ev_05_alt']) + ' | ' + x['skor']
        print(line)
    print()
    print('--- EV GOL ATTI ---')
    for x in ev_gol_var[:8]:
        line = '  #' + str(x['idx']) + ' ' + x['ev'] + ' vs ' + x['dep']
        line += ' | X2=' + str(x['x2']) + ' KGVar=' + str(x['kg_var']) + ' KGYok=' + str(x['kg_yok'])
        line += ' | Ev0.5Alt=' + str(x['ev_05_alt']) + ' | ' + x['skor']
        print(line)
