import json
with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for idx in [-274, -278]:
    m = data['matches'][idx]
    print(f'\n--- Match {idx} ---')
    print(m['ev_sahibi'], '-', m['deplasman'], f"Skor: {m.get('skor_ev')}-{m.get('skor_dep')}")
    for k, v in m.get('oranlar', {}).items():
        if 'Alt' in k or 'Üst' in k or 'Sonucu' in k or 'Karşılıklı' in k or 'Çifte' in k:
            print(f'{k}: {v}')
