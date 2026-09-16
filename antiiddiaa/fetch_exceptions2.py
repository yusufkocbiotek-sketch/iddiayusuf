import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

g20_indices = [23357, 23452, 23529, 23996]
t70_indices = [23110, 23327, 23345, 23445, 23518]

print("--- G20 EXCEPTIONS ---")
for idx in g20_indices:
    m = next((x for x in matches if x.get('index') == idx), None)
    if m:
        o = m.get('oranlar', {})
        print(f"\n[{idx}] {m.get('ev_sahibi')} - {m.get('deplasman')} | İY: {m.get('skor_1y_ev')}-{m.get('skor_1y_dep')} MS: {m.get('skor_ev')}-{m.get('skor_dep')}")
        keys_to_print = ['Maç Sonucu_1', 'Maç Sonucu_0', 'Maç Sonucu_2', 'Karşılıklı Gol_Var', 'Karşılıklı Gol_Yok', 'Alt/Üst 2.5_Alt', 'Alt/Üst 2.5_Üst', '1. Yarı Sonucu_0', 'Alt/Üst 1.5_Üst', 'Alt/Üst 3.5_Üst']
        for k in keys_to_print:
            if k in o: print(f"{k}: {o[k]}")

print("\n--- T70 EXCEPTIONS ---")
for idx in t70_indices:
    m = next((x for x in matches if x.get('index') == idx), None)
    if m:
        o = m.get('oranlar', {})
        print(f"\n[{idx}] {m.get('ev_sahibi')} - {m.get('deplasman')} | İY: {m.get('skor_1y_ev')}-{m.get('skor_1y_dep')} MS: {m.get('skor_ev')}-{m.get('skor_dep')}")
        keys_to_print = ['Maç Sonucu_1', 'Maç Sonucu_0', 'Maç Sonucu_2', 'Karşılıklı Gol_Var', 'Karşılıklı Gol_Yok', 'Alt/Üst 2.5_Alt', 'Alt/Üst 2.5_Üst', '1. Yarı Sonucu_0', 'Handikaplı Maç Sonucu 0:1_1', 'Handikaplı Maç Sonucu 0:2_1', 'Ev Sahibi Alt/Üst 1.5_Üst', 'Deplasman Alt/Üst 1.5_Üst', 'Ev Sahibi Alt/Üst 2.5_Üst', '1. Yarı 1.5_Üst']
        for k in keys_to_print:
            if k in o: print(f"{k}: {o[k]}")
