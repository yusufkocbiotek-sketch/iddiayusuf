import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

old_1481 = '''        ev_iy_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst"])
        
        if ev_iy_05_ust != 99.0 and ev_iy_05_ust <= 1.45:
            return False, ""'''

new_1481 = '''        ev_iy_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst"])
        
        if ev_iy_05_ust != 99.0 and ev_iy_05_ust <= 1.45:
            return False, ""'''

if old_1481 in content:
    print("Code is present.")
else:
    print("Code NOT PRESENT! Replacement failed.")
