with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "        elif any(r['code'] in ['T36', '1465', '1466', '1468'] for r in triggered_rules):",
    "    elif any(r['code'] in ['T36', '1465', '1466', '1468'] for r in triggered_rules):"
)
content = content.replace(
    "        output.append(f\"- **Ana Tahmin:** Maç Sonucu 2 veya 02 Çifte Şans (Deplasman Sürprizi)\")",
    "        output.append(f\"- **Ana Tahmin:** Maç Sonucu 2 veya 02 Çifte Şans (Deplasman Sürprizi)\")"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)
