import json
import sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import get_all_rules, evaluate_synergies, filter_triggered_rules

START_INDEX = -737
END_INDEX = -727
OUTPUT_FILE = "block13_output_utf8.txt"

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

rules = get_all_rules()

output = [f"--- MEGA SİNERJİ TESTİ ({START_INDEX} ile {END_INDEX} Arası) ---"]
for mac in matches[START_INDEX:END_INDEX]:
    ev = mac.get('ev_sahibi', '?')
    dep = mac.get('deplasman', '?')
    skor_ev = mac.get('skor_ev', '?')
    skor_dep = mac.get('skor_dep', '?')
    skor_iy_ev = mac.get('skor_1y_ev', '?')
    skor_iy_dep = mac.get('skor_1y_dep', '?')
    
    skor = f"{skor_ev}-{skor_dep} (İY: {skor_iy_ev}-{skor_iy_dep})"
    odds = mac.get('oranlar', {})
    idx = mac.get('index', '?')
    
    raw_triggered = []
    for R in rules:
        trigger, msg = R.evaluate(odds)
        if trigger:
            raw_triggered.append((R.code, msg))
            
    filtered = filter_triggered_rules(raw_triggered)
    kural_zinciri = [t[0] for t in filtered]
    mesajlar = [f"[{t[0]}] {t[1]}" for t in filtered]
            
    synergies = evaluate_synergies(kural_zinciri)
            
    output.append(f"\n[{idx}] {ev} vs {dep}")
    output.append(f"Skor: {skor}")
    if kural_zinciri:
        output.append(f"Tetiklenen Kurallar: {' -> '.join(kural_zinciri)}")
        for m in mesajlar:
            output.append(f"  - {m}")
    else:
        output.append("Tetiklenen Kural: YOK (Standart Maç)")
        
    for syn in synergies:
        output.append(f"  {syn}")

with open(f'C:\\Users\\YUSUF\\.gemini\\antigravity\\scratch\\{OUTPUT_FILE}', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
