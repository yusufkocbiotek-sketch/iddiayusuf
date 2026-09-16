import sys
sys.path.append(r"C:\Users\YUSUF\.gemini\antigravity\scratch")

import json
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

matches = data.get('matches', [])

output_text = ""
start_idx = -253
end_idx = -260

for i in range(start_idx, end_idx - 1, -1):
    try:
        m = matches[i]
        story = generate_story(m, verbose=True)
        output_text += f"==================================================\n"
        output_text += f"📌 İndex: {i} | {m.get('ev_sahibi')} - {m.get('deplasman')}\n"
        output_text += f"💥 GERÇEK SKOR: {m.get('skor_ev')} - {m.get('skor_dep')} (İlk Yarı: {m.get('skor_1y_ev')} - {m.get('skor_1y_dep')})\n\n"
        output_text += story + "\n"
    except IndexError:
        break

with open(r"C:\Users\YUSUF\.gemini\antigravity\scratch\batch_253_260.md", "w", encoding="utf-8") as f:
    f.write(output_text)

print("Batch 253-260 processed and saved to batch_253_260.md")
