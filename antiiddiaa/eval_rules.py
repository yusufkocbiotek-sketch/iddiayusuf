import json
from rule_engine import RuleT33, RuleT32, Rule1478, get_odd

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for m in data['matches']:
    if m.get('ev_sahibi') == 'Def. de Belgrano' and m.get('deplasman') == 'Atlanta':
        print('Def. de Belgrano - Atlanta')
        odds = m['oranlar']
        print(f"MS1: {get_odd(odds, ['Maç Sonucu_1'])}")
        print(f"MS2: {get_odd(odds, ['Maç Sonucu_2'])}")
        print(f"Rule T33 triggers: {RuleT33.evaluate(odds)}")
        
    if m.get('ev_sahibi') == 'Wollongong Wolves' and m.get('deplasman') == 'Sydney Olympic FC':
        print('Wollongong Wolves - Sydney Olympic FC')
        odds = m['oranlar']
        print(f"Rule 1478 triggers: {Rule1478.evaluate(odds)}")
