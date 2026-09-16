import sys
sys.path.append(r"C:\Users\YUSUF\.gemini\antigravity\scratch")
import json
from rule_engine import get_all_rules

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

rules = get_all_rules()

for i in range(-269, -274, -1):
    m = data['matches'][i]
    odds = m.get('oranlar', {})
    print(f"\n--- MATCH {i} : {m.get('ev_sahibi')} vs {m.get('deplasman')} ---")
    print(f"SKOR: {m.get('skor_ev')}-{m.get('skor_dep')} (IY: {m.get('skor_1y_ev')}-{m.get('skor_1y_dep')})")
    
    triggered = []
    for R in rules:
        try:
            is_active, _ = R.evaluate(odds)
            if is_active:
                triggered.append(R.code)
        except Exception:
            pass
            
    print(f"Triggered Rules: {triggered}")
