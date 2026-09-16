import json
import codecs
from rule_engine import get_all_rules

with codecs.open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', 'utf8') as f:
    matches = json.load(f)['matches']

m = matches[-501]
oranlar = m.get('oranlar', {})

rules = get_all_rules()
for rule in rules:
    active, msg = rule.evaluate(oranlar)
    if active:
        print(f"[{rule.code}] {rule.name}: {msg}")
