import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()

correct_state = '''    if any(r['code'] == '2001' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 2.5 Gol Altı (Milli Maç Kısırlığı)")
        output.append(f"- **Kombine Öneri:** 2.5 Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0 / 1-1 / 1-0)")
    elif any(r['code'] == '2002' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1/2 (Milli Maç Fark Patlaması)")
        output.append(f"- **Kombine Öneri:** Favori Kazanır + 3.5 Gol Üst (Sürpriz Skor: 4-0 / 5-0)")
    elif any(r['code'] == '1512' and 'ŞOV PATLAMASI' in r['insight'] for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 3.5 Gol Üstü (Gizli Barem Patlaması)")
        output.append(f"- **Kombine Öneri:** MS 1 + 3.5 Gol Üst (Sürpriz Skor: 4-1 / 3-2)")'''

bad_state_1 = '''    if any(r['code'] == '2001' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 2.5 Gol Altı (Milli Maç Kısırlığı)")
        output.append(f"- **Kombine Öneri:** 2.5 Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0 / 1-1 / 1-0)")
    elif any(r['code'] == '2002' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1/2 (Milli Maç Fark Patlaması)")
        output.append(f"- **Kombine Öneri:** Favori Kazanır + 3.5 Gol Üst (Sürpriz Skor: 4-0 / 5-0)")
    elif any(r['code'] == '1512' and 'ŞOV PATLAMASI' in r['insight'] for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 3.5 Gol Üstü (Gizli Barem Patlaması)")
        output.append(f"- **Kombine Öneri:** MS 1 + 3.5 Gol Üst (Sürpriz Skor: 4-1 / 3-2)")'''

bad_state_2 = '''    if any(r['code'] == '1512' and 'ŞOV PATLAMASI' in r['insight'] for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 3.5 Gol Üstü (Gizli Barem Patlaması)")
        output.append(f"- **Kombine Öneri:** MS 1 + 3.5 Gol Üst (Sürpriz Skor: 4-1 / 3-2)")'''

# Clean up any leftover 2001 or 2002 down in the file
import re
story = re.sub(r"    elif any\(r\['code'\] == '2001' for r in triggered_rules\):\n.*\n.*\n", "", story)
story = re.sub(r"    elif any\(r\['code'\] == '2002' for r in triggered_rules\):\n.*\n.*\n", "", story)

if bad_state_1 in story:
    pass # already fixed
elif bad_state_2 in story:
    story = story.replace(bad_state_2, correct_state)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf-8') as f:
    f.write(story)
