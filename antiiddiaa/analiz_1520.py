import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import Rule1520

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

found = []
for mac in matches:
    odds = mac.get('oranlar', {})
    trigger, _ = Rule1520.evaluate(odds)
    if trigger:
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        if sev >= 0:
            found.append({'skor': f"{sev}-{sdep}", 'toplam_gol': sev+sdep, 'idx': mac.get('index')})

print(f"Toplam 1520 Mac: {len(found)}")
if found:
    ust = [x for x in found if x['toplam_gol'] > 2]
    print(f"Ust Biten (Basarili): {len(ust)} ({(len(ust)/len(found))*100:.1f}%)")
