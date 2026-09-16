import json
import sys
import codecs
from story_analyzer import generate_story
from rule_engine import get_all_rules

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    matches = data['matches']

# Get rules to ensure they are loaded
rules = get_all_rules()

output = []
output.append("# Analiz Bloğu: -898 ile -907 Arası (10 Maç)")
output.append("")
output.append("**YENİ FUZZY MATCHING & SİNERJİ MOTORU İŞ BAŞINDA!**")
output.append("Artık 99.0 hatalarından arındırılmış tam kapasite kural motoruyla sıradaki 10 maçı inceliyoruz.")
output.append("")

for i in range(898, 908):
    m = matches[-i]
    story = generate_story(m)
    output.append(f"## 🎯 Index -{i} ({m.get('ev_sahibi', 'Ev')} - {m.get('deplasman', 'Dep')})")
    output.append(story)
    output.append("---")

out_path = r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Analiz_Blok_898_907.md'

with codecs.open(out_path, 'w', 'utf-8') as f:
    f.write('\n'.join(output))

print("Block 898-907 generated successfully!")
