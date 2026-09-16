import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()

rule_1514_block = '''    elif any(r['code'] == '1514' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Kısır Maç (Buzul Sessizliği Tuzağı)")
        output.append(f"- **Kombine Öneri:** 2.5 Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0 / 1-0)")
'''

if "1514" not in story:
    # insert it right before 1481
    story = story.replace("    elif any(r['code'] == '1481' for r in triggered_rules):", rule_1514_block + "    elif any(r['code'] == '1481' for r in triggered_rules):")
    
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf-8') as f:
    f.write(story)
