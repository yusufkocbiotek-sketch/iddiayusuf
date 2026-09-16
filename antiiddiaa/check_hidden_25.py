import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for idx, m in enumerate(data['matches']):
    odds = m.get('oranlar', {})
    has_25 = any('2.5' in k for k in odds.keys() if 'Alt/Üst 2.5' in k and not 'Ev Sahibi' in k and not 'Deplasman' in k)
    has_35 = any('3.5' in k for k in odds.keys())
    ms1 = odds.get('Maç Sonucu_1', 0)
    kg_var = odds.get('Karşılıklı Gol_Var', 0)
    
    if not has_25 and has_35 and ms1 > 0 and ms1 <= 1.55 and kg_var > 0 and kg_var <= 1.50:
        skor_ev = m.get('skor_ev')
        skor_dep = m.get('skor_dep')
        print(f"Match {idx} | {m['ev_sahibi']} - {m['deplasman']} | MS1: {ms1} | KG: {kg_var} | SKOR: {skor_ev}-{skor_dep}")
