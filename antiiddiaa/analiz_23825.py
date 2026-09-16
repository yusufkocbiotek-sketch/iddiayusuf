import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import Rule1535

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

for mac in matches:
    if mac.get('index') == 23825:
        od = mac.get('oranlar', {})
        print("Mısır Maci Oranlari:")
        print("MS1:", od.get("Maç Sonucu_1"))
        print("MS2:", od.get("Maç Sonucu_2"))
        print("IY MS1:", od.get("İlk Yarı Sonucu_1"))
        print("2.5 Alt:", od.get("Alt/Üst 2.5_Alt"))
        print("2.5 Ust:", od.get("Alt/Üst 2.5_Üst"))
        print("MS2 + Alt:", od.get("Maç Sonucu ve Alt/Üst 2.5_2 ve Alt"))
        print("MS2 + Ust:", od.get("Maç Sonucu ve Alt/Üst 2.5_2 ve Üst"))
        print(Rule1535.evaluate(od))
