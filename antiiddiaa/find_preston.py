import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for idx, m in enumerate(data['matches']):
    if "Preston Lions" in m['ev_sahibi'] or "Preston Lions" in m['deplasman']:
        print(f"Match Index: {idx} or {-len(data['matches']) + idx}")
        print(f"{m['ev_sahibi']} - {m['deplasman']} | Skor: {m.get('skor_ev')}-{m.get('skor_dep')} (IY: {m.get('skor_1y_ev')}-{m.get('skor_1y_dep')})")
        print("\n--- Tüm Oranlar ---")
        for k, v in m.get('oranlar', {}).items():
            print(f"{k}: {v}")
        break
