import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import Rule1520

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

ust_odds = []
for mac in matches:
    odds = mac.get('oranlar', {})
    trigger, _ = Rule1520.evaluate(odds)
    if trigger:
        ust25 = odds.get('Alt/Üst 2.5_Üst', 99)
        if ust25 == 99: ust25 = odds.get('Altı/Üstü 2.5_Üst', 99)
        if ust25 != 99:
            ust_odds.append(ust25)

if ust_odds:
    print(f"1520 İcin Ortalama 2.5 Ust Orani: {sum(ust_odds)/len(ust_odds):.2f}")
    print(f"Min: {min(ust_odds)}, Max: {max(ust_odds)}")
