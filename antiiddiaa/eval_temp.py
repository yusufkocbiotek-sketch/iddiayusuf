import json
from rule_engine import get_all_rules, evaluate_synergies, filter_triggered_rules

with open('temp_mac.json', 'r', encoding='utf-8') as f:
    mac = json.load(f)

rules = get_all_rules()
tetiklenen = []
oranlar = mac.get('oranlar', {})

for r in rules:
    hit, msg = r.evaluate(oranlar)
    if hit:
        tetiklenen.append((r.code, msg))

tetiklenen = filter_triggered_rules(tetiklenen)
active_codes = [t[0] for t in tetiklenen]
syn = evaluate_synergies(active_codes)

print('Tetiklenen Kurallar:', active_codes)
for c, m in tetiklenen:
    print(f'- [{c}] {m}')
for s in syn:
    print(f'MEGA SİNERJİ: {s}')
