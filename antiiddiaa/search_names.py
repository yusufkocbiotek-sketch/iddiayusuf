import json
with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for m in data['matches']:
    if 'Diriangen' in m.get('ev_sahibi', '') or 'Numancia' in m.get('deplasman', ''):
        print('='*40)
        print(f"{m.get('ev_sahibi')} - {m.get('deplasman')}")
        print(f"Skor: {m.get('skor_ev')}-{m.get('skor_dep')} (IY: {m.get('skor_1y_ev')}-{m.get('skor_1y_dep')})")
        for k, v in m.get('oranlar', {}).items():
            if 'Sonucu' in k or 'Alt' in k or 'Üst' in k or 'Karşılıklı' in k or 'Çifte' in k:
                print(f"{k}: {v}")
