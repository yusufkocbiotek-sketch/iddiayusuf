import json
with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for m in data['matches']:
    if 'Belgrano' in m.get('ev_sahibi', '') or 'Atlanta' in m.get('deplasman', ''):
        print(f"{m['ev_sahibi']} - {m['deplasman']}")
        for k, v in m['oranlar'].items():
            if 'Maç Sonucu' in k or 'Karşılıklı' in k or 'Alt/Üst 1.5' in k or 'Alt/Üst 0.5' in k:
                print(f"{k}: {v}")
