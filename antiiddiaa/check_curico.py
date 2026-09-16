import json
from rule_engine import get_all_rules

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

mac = None
for m in matches:
    if m.get('ev_sahibi') == 'Curico Unido' and m.get('deplasman') == 'Nublense':
        mac = m
        break

if mac:
    odds = mac.get('oranlar', {})
    print('Curico Unido vs Nublense Oranlar:')
    print(f'MS1: {odds.get("Maç Sonucu_1", 99)}')
    print(f'MS2: {odds.get("Maç Sonucu_2", 99)}')
    print(f'MS0: {odds.get("Maç Sonucu_0", 99)}')
    print(f'Ev 1.5 Ust: {odds.get("Ev Sahibi Alt/Üst 1.5_Üst", 99)}')
    print(f'Alt 2.5: {odds.get("Alt/Üst 2.5_Alt", 99)}')
    print(f'Ust 2.5: {odds.get("Alt/Üst 2.5_Üst", 99)}')
    
    rules = get_all_rules()
    for R in rules:
        if R.code in ['1503', '1516', 'T8']:
            t, msg = R.evaluate(odds)
            print(f'{R.code} triggered? {t}')
