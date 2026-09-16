import sys
sys.path.append(r"C:\Users\YUSUF\.gemini\antigravity\scratch")
import json
from rule_engine import get_all_rules

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

m = data['matches'][-370]
rules = get_all_rules()
for rule in rules:
    res, msg = rule.evaluate(m['oranlar'])
    if res:
        print(rule.code, rule.name)
