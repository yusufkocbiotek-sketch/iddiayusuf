import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for idx in range(-377, -381, -1):
    m = data['matches'][idx]
    print(f"\n--- Match {idx} ---")
    print(m['ev_sahibi'], '-', m['deplasman'], f"Skor: {m.get('skor_ev')}-{m.get('skor_dep')}")
    for k, v in m.get('oranlar', {}).items():
        if 'Sonucu_1' in k or 'Sonucu_2' in k or 'Karşılıklı' in k or '2.5' in k or '0.5' in k:
            print(f'{k}: {v}')
