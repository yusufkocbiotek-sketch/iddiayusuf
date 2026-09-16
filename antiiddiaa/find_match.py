import json
with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    matches = data['matches']
    for i, m in enumerate(matches):
        o = m.get('oranlar', {})
        if o.get('Maç Sonucu_1') == 2.54 and o.get('Alt/Üst 1.5_Üst') == 1.24:
            print("Match index:", i - len(matches))
            print("Match:", m.get('ev_sahibi'), "-", m.get('deplasman'))
            print("Score:", m.get('skor_ev'), "-", m.get('skor_dep'))
            break
