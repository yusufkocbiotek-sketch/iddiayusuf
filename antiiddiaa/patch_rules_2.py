import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1530
content = content.replace('iy_05_ust <= 1.25', 'iy_05_ust <= 1.30')
content = content.replace('İlk Yarı 0.5 Üst (1.25 altı)', 'İlk Yarı 0.5 Üst (1.30 altı)')

# Fix 1555
old_1555 = 'if ms1 != 99.0 and 1.30 <= ms1 <= 1.55 and ms0 != 99.0 and ms0 <= 3.40 and kg_var != 99.0 and kg_var <= 1.55:'
new_1555 = '''ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        if ms1 != 99.0 and 1.30 <= ms1 <= 1.55 and ms0 != 99.0 and ms0 <= 3.40 and kg_var != 99.0 and kg_var <= 1.55 and (ust25 == 99.0 or ust25 >= 1.55):'''
content = content.replace(old_1555, new_1555)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied for 1530 and 1555.")
