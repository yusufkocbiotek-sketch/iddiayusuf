import re

# Fix 1470 in rule_engine.py
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("if kg_var <= 1.35 and ms1 <= 1.65 and dep_05_ust >= 1.65:", "if kg_var <= 1.42 and ms1 <= 1.65 and dep_05_ust >= 1.65:")

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix story_analyzer.py logic
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

story = story.replace(
    "elif any(r['code'] == '1474' for r in triggered_rules):\n        output.append(f\"- **Ana Tahmin:** Maç Sonucu 2 veya 02 Çifte Şans (Deplasman Sürprizi)\")\n        output.append(f\"- **Kombine Öneri:** 1.5 Gol Altı + Karşılıklı Gol Yok\")",
    "elif any(r['code'] == '1474' for r in triggered_rules):\n        output.append(f\"- **Ana Tahmin:** 12 Çifte Şans (Beraberlik Tuzağına Düşmeyin)\")\n        output.append(f\"- **Kombine Öneri:** 12 Çifte Şans + Karşılıklı Gol Yok\")"
)

# Prioritize T27 over 1469
story = story.replace(
    "elif any(r['code'] in ['T33', '1469'] for r in triggered_rules):",
    "elif any(r['code'] in ['T33', '1469'] for r in triggered_rules) and not any(r['code'] == 'T27' for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("Patched 1474 output, prioritized T27, and expanded 1470.")
