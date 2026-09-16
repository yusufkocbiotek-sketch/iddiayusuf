import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

for mac in matches:
    if mac.get('index') == 23800:
        od = mac.get('oranlar', {})
        print("IY_MS_00:", od.get("İlk Yarı / Maç Sonucu_0/0"))
        print("IY_MS_11:", od.get("İlk Yarı / Maç Sonucu_1/1"))
        print("IY_MS_22:", od.get("İlk Yarı / Maç Sonucu_2/2"))
        print("MS1:", od.get("Maç Sonucu_1"))
        print("MS2:", od.get("Maç Sonucu_2"))
