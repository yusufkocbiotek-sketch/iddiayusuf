import json
with open('single_match.json', encoding='utf-8') as f:
    match_data = json.load(f)
from rule_engine import get_all_rules
rules = get_all_rules()
for r in rules:
    ok, msg = r.evaluate(match_data['oranlar'])
    if ok:
        print(f'[{r.code}] {r.name}')
        print(msg)
        print('---')
