import json
import sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import get_all_rules, evaluate_synergies

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

rules = get_all_rules()

print("--- MEGA SİNERJİ TESTİ (-717 ile -707 Arası) ---")
for mac in matches[-717:-707]:
    ev = mac.get('ev_sahibi', '?')
    dep = mac.get('deplasman', '?')
    skor_ev = mac.get('skor_ev', '?')
    skor_dep = mac.get('skor_dep', '?')
    skor_iy_ev = mac.get('skor_1y_ev', '?')
    skor_iy_dep = mac.get('skor_1y_dep', '?')
    
    skor = f"{skor_ev}-{skor_dep} (İY: {skor_iy_ev}-{skor_iy_dep})"
    odds = mac.get('oranlar', {})
    idx = mac.get('index', '?')
    
    # Run rules
    kural_zinciri = []
    mesajlar = []
    for R in rules:
        trigger, msg = R.evaluate(odds)
        if trigger:
            kural_zinciri.append(R.code)
            mesajlar.append(f"[{R.code}] {msg}")
            
    # Check Synergies
    synergies = evaluate_synergies(kural_zinciri)
            
    print(f"\n[{idx}] {ev} vs {dep}")
    print(f"Skor: {skor}")
    if kural_zinciri:
        print(f"Tetiklenen Kurallar: {' -> '.join(kural_zinciri)}")
        for m in mesajlar:
            print(f"  - {m}")
    else:
        print("Tetiklenen Kural: YOK (Standart Maç)")
        
    for syn in synergies:
        print(f"  {syn}")
