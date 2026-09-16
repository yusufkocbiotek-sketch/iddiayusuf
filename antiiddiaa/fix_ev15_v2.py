import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "kg_var = rule_engine.get_odd(odds, [\"Karşılıklı Gol_Var\"])",
    "kg_var = rule_engine.get_odd(odds, [\"Karşılıklı Gol_Var\"])\n    ev_15_ust = rule_engine.get_odd(odds, [\"Ev Sahibi Alt/Üst 1.5_Üst\"])"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)
