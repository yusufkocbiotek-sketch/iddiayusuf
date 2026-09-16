import json
with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for idx in [-361, -362]:
    m = data['matches'][idx]
    print(f"\n--- Match {idx} ---")
    print(m['ev_sahibi'], '-', m['deplasman'], f"Skor: {m.get('skor_ev')}-{m.get('skor_dep')} (İlk Yarı: {m.get('skor_1y_ev')}-{m.get('skor_1y_dep')})")
    for k, v in m.get('oranlar', {}).items():
        if '1. Yarı' in k or '2. Yarı' in k or 'Alt' in k or 'Üst' in k or 'KG' in k or 'Karşılıklı' in k:
            print(f'{k}: {v}')
