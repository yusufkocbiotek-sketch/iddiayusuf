import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import get_all_rules

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

rules = get_all_rules()

for mac in matches:
    idx = mac.get('index')
    if idx in [23717, 23718]:
        ev = mac.get('ev_sahibi', '?')
        dep = mac.get('deplasman', '?')
        skor = f"{mac.get('skor_ev', '?')}-{mac.get('skor_dep', '?')}"
        odds = mac.get('oranlar', {})
        
        print(f"\n[{idx}] {ev} {skor} {dep}")
        print("Taraf Oranlari:", odds.get('Maç Sonucu_1'), odds.get('Maç Sonucu_0'), odds.get('Maç Sonucu_2'))
        print("Alt/Ust Oranlari (2.5/3.5/4.5 vs):")
        for k, v in odds.items():
            if "Alt/Üst" in k or "Altı/Üstü" in k or "Karşılıklı" in k or "Yarı" in k:
                if v != 99.0 and v is not None:
                    print(f"  {k}: {v}")
                    
        kural_zinciri = []
        for R in rules:
            trigger, msg = R.evaluate(odds)
            if trigger:
                kural_zinciri.append(R.code)
                print(f"  --> RULE {R.code} TRIGGERED: {R.name}")
