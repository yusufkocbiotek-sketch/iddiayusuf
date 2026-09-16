import sys
sys.path.append(r"C:\Users\YUSUF\.gemini\antigravity\scratch")
import json
from story_analyzer import generate_story
import os

artifact_dir = r"C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651"
artifact_path = os.path.join(artifact_dir, "Analiz_Blok_334_353.md")

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

output_text = "# KAPSAMLI 20 MAÇLIK ANALİZ RAPORU (İndex: -334 / -353)\n\n"
output_text += "Bu rapor makine tarafından oluşturulmuş tam teşekküllü şablonları içerir ve ÖĞRENME MOTORU aktif edilmiştir.\n\n"

for i in range(-334, -354, -1):
    try:
        m = data['matches'][i]
        story = generate_story(m, verbose=False)
        output_text += f"==================================================\n"
        output_text += f"📌 İndex: {i} | {m.get('ev_sahibi')} - {m.get('deplasman')}\n"
        output_text += f"💥 GERÇEK SKOR: {m.get('skor_ev')} - {m.get('skor_dep')} (İlk Yarı: {m.get('skor_1y_ev')} - {m.get('skor_1y_dep')})\n\n"
        output_text += story + "\n"
    except Exception as e:
        output_text += f"Error processing {i}: {e}\n"

with open(artifact_path, "w", encoding="utf-8") as f:
    f.write(output_text)

print(f"Artifact created at {artifact_path}")
