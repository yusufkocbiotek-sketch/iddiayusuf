with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I need to insert `ev_15_ust` near `ust25` in story_analyzer.py
content = content.replace(
    "ust25 = rule_engine.get_odd(odds, [\"Alt/Üst 2.5_Üst\", \"Alt/Üst 2,5_Üst\"])",
    "ust25 = rule_engine.get_odd(odds, [\"Alt/Üst 2.5_Üst\", \"Alt/Üst 2,5_Üst\"])\n    ev_15_ust = rule_engine.get_odd(odds, [\"Ev Sahibi Alt/Üst 1.5_Üst\"])"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)
