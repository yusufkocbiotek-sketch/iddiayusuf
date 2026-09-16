import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import get_all_rules

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

rules = get_all_rules()

print("--- ANALIZ BLOK (-647 to -637) ---")
for mac in matches[-647:-637]:
    ev = mac.get('ev_sahibi', '?')
    dep = mac.get('deplasman', '?')
    skor = f"{mac.get('skor_ev', '?')}-{mac.get('skor_dep', '?')}"
    odds = mac.get('oranlar', {})
    
    # Run rules
    kural_zinciri = []
    for R in rules:
        trigger, msg = R.evaluate(odds)
        if trigger:
            kural_zinciri.append(R.code)
            
    print(f"{mac.get('index', '?')} {ev} vs {dep} | Zincir: {'->'.join(kural_zinciri)} | Skor: {skor}")
