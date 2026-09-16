import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', encoding='utf-8') as f:
    data = json.load(f)

matches = data['matches']
start_idx = 948
end_idx = 957

output_md = rf'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Analiz_Blok_{start_idx}_{end_idx}.md'
with open(output_md, 'w', encoding='utf-8') as f:
    f.write(f'# KÖR ANALİZ BLOĞU ({start_idx}-{end_idx})\n\n')
    for i in range(start_idx, min(end_idx + 1, len(matches))):
        m = matches[i]
        f.write(f'## Index -{i} ({m.get("ev_sahibi", "?")} - {m.get("deplasman", "?")})\n')
        f.write('### 🧠 Sistemin Kör Tahmini (Skorlar Gizliyken)\n')
        story = generate_story(m)
        f.write(story + '\n')
        f.write('### 🔍 GERÇEK SONUÇ & HESAPLAŞMA\n')
        
        iy = f'{m.get("skor_1y_ev", "?")}-{m.get("skor_1y_dep", "?")}'
        ms = f'{m.get("skor_ev", "?")}-{m.get("skor_dep", "?")}'
        
        f.write(f'> **Gerçekleşen Skor:** İlk Yarı **{iy}** | Maç Sonucu **{ms}**\n\n')
        f.write('---\n\n')
print(f'Blind analysis generated successfully for {start_idx}-{end_idx}!')
