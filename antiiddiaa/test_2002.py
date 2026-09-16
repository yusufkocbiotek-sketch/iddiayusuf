import json
import rule_engine

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

m = data['matches'][-380] # Senegal
rule_engine.CURRENT_MATCH = m
odds = m.get('oranlar', {})

print("Evaluating Rule2002 manually...")
print(rule_engine.Rule2002.evaluate(odds))

print("Is Milli Mac?", rule_engine.is_milli_mac(m))
