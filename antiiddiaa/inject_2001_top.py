import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()

correct_state = '''    if any(r['code'] == '2001' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 2.5 Gol Altı (Milli Maç Kısırlığı)")
        output.append(f"- **Kombine Öneri:** 2.5 Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0 / 1-1 / 1-0)")
    elif any(r['code'] == '2002' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1/2 (Milli Maç Fark Patlaması)")
        output.append(f"- **Kombine Öneri:** Favori Kazanır + 3.5 Gol Üst (Sürpriz Skor: 4-0 / 5-0)")
    elif any(r['code'] == '1486' for r in triggered_rules):'''

if "1486" in story and "2001" not in story:
    story = story.replace("    if any(r['code'] == '1486' for r in triggered_rules):", correct_state)
    with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf-8') as f:
        f.write(story)
        print("Injected successfully!")
else:
    print("Failed to inject.")
