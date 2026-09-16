import json
with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for i, m in enumerate(data['matches']):
    if 'Atlanta' in m.get('deplasman', ''):
        print(f"Index {i}: {m.get('ev_sahibi')} - {m.get('deplasman')}")
