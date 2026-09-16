import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

for mac in matches:
    if mac.get('index') == 23810:
        od = mac.get('oranlar', {})
        print("23810 Oranlar (ilk 10):", list(od.items())[:10])
