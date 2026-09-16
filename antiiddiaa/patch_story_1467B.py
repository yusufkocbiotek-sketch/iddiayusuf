import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add 1467B to mappings
old_1467 = """'1467': ("Dengeli Kısır Çelişki (0-0)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 0-0)"),"""
new_1467B = """'1467': ("Dengeli Kısır Çelişki (0-0)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 0-0)"),\n    '1467B': ("Gollü Beraberlik Tuzağı (2-2 / 3-3)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 2-2 veya 3-3)"),"""

content = content.replace(old_1467, new_1467B)

# Add 1467B to score logic
old_score_logic = """    has_g1 = any(r['code'] == 'G1' for r in triggered_rules)
    has_g11 = any(r['code'] == 'G11' for r in triggered_rules)"""
new_score_logic = """    has_g1 = any(r['code'] == 'G1' for r in triggered_rules)
    has_g11 = any(r['code'] == 'G11' for r in triggered_rules)
    has_1467B = any(r['code'] == '1467B' for r in triggered_rules)"""

old_score_if = """    if has_g1:"""
new_score_if = """    if has_1467B:
        skorlar = "2-2 > 3-3 > 1-1"
        kacin = "0-0 / 1-0 / 0-1 gibi kısır skorlar"
    elif has_g1:"""

content = content.replace(old_score_logic, new_score_logic)
content = content.replace(old_score_if, new_score_if)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("story_analyzer.py patched for 1467B!")
