import json
import sys

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

target_indices = [24408, 24225, 24101, 24252, 24265, 24266, 24268]
keys = ['Maç Sonucu_1', 'Maç Sonucu_0', 'Maç Sonucu_2', '1. Yarı Sonucu_0', '1. Yarı Sonucu_1', '1. Yarı Sonucu_2', 'Karşılıklı Gol_Var', 'Karşılıklı Gol_Yok', 'Alt/Üst 2.5_Alt', 'Alt/Üst 2.5_Üst', '1. Yarı Alt/Üst 1.5_Alt', '1. Yarı Alt/Üst 0.5_Alt', 'Deplasman Alt/Üst 0.5_Alt', 'Ev Sahibi Alt/Üst 1.5_Alt']

for idx in target_indices:
    m = next((x for x in matches if x.get('index') == idx), None)
    if not m: continue
    o = m.get('oranlar', {})
    print(f"\n--- MATCH {idx} ({m.get('ev_sahibi')} - {m.get('deplasman')}) | SKOR: {m.get('skor_1y_ev')}-{m.get('skor_1y_dep')} / {m.get('skor_ev')}-{m.get('skor_dep')} ---")
    for k in keys:
        if k in o:
            print(f"{k}: {o[k]}")
