import sys
sys.path.append(r"C:\Users\YUSUF\.gemini\antigravity\scratch")
import json
from rule_engine import Rule1511

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for idx in [-369, -370]:
    m = data['matches'][idx]
    res, msg = Rule1511.evaluate(m['oranlar'])
    print(f"Match {idx} -> Rule 1511: {res}")
