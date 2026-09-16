import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', encoding='utf-8') as f:
    data = json.load(f)

matches = data['matches']
start_idx = 758
end_idx = 767

output_md = r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\KOR_Analiz_758_767.md'
with open(output_md, 'w', encoding='utf-8') as f:
    f.write(f'# KÖR ANALİZ BLOĞU ({start_idx}-{end_idx})\n\n')
    for i in range(start_idx, min(end_idx + 1, len(matches))):
        m = matches[i]
        f.write(f'## Index -{i} ({m["ev_sahibi"]} - {m["deplasman"]})\n')
        f.write('### 🧠 Sistemin Kör Tahmini (Skorlar Gizliyken)\n')
        story = generate_story(m)
        f.write(story + '\n')
        f.write('### 🔍 GERÇEK SONUÇ & HESAPLAŞMA\n')
        f.write(f'> **Gerçekleşen Skor:** İlk Yarı **{m.get("skor_ilk_yari", "?")}** | Maç Sonucu **{m.get("skor_mac_sonucu", "?")}**\n\n')
        f.write('---\n\n')
print('Blind analysis generated successfully!')
