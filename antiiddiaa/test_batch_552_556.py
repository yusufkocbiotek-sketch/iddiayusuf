import json
import sys
import codecs
from story_analyzer import generate_story
from rule_engine import get_all_rules

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

# Get rules to ensure they are loaded
rules = get_all_rules()

output = []
for i in range(552, 557):
    m = matches[-i]
    story = generate_story(m)
    output.append(f"## 🔍 İndex -{i} ({m.get('ev_sahibi')} - {m.get('deplasman')})")
    output.append(story)

out_path = r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Analiz_Blok_552_556.md'
with codecs.open(out_path, 'w', 'utf8') as f:
    f.write('\n---\n'.join(output))

print(f"Test tamamlandı, {out_path} oluşturuldu.")
