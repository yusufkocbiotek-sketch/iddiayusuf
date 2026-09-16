import sys
sys.path.append(r"C:\Users\YUSUF\.gemini\antigravity\scratch")
import json
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

output_text = ""
for i in range(-264, -269, -1):
    try:
        m = data['matches'][i]
        story = generate_story(m, verbose=False)
        output_text += f"==================================================\n"
        output_text += f"📌 İndex: {i} | {m.get('ev_sahibi')} - {m.get('deplasman')}\n"
        output_text += f"💥 GERÇEK SKOR: {m.get('skor_ev')} - {m.get('skor_dep')} (İlk Yarı: {m.get('skor_1y_ev')} - {m.get('skor_1y_dep')})\n\n"
        output_text += story + "\n"
    except Exception as e:
        output_text += f"Error processing {i}: {e}\n"

with open(r"C:\Users\YUSUF\.gemini\antigravity\scratch\batch_264_268.md", "w", encoding="utf-8") as f:
    f.write(output_text)

print("Batch 264-268 generated.")
