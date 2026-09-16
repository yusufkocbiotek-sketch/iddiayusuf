import sys
sys.path.append(r"C:\Users\YUSUF\.gemini\antigravity\scratch")
import json
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

idx = -364
m = data['matches'][idx]
story = generate_story(m, verbose=False)
print(f"==================================================\n")
print(f"📌 İndex: {idx} | {m.get('ev_sahibi')} - {m.get('deplasman')}")
print(f"💥 GERÇEK SKOR: {m.get('skor_ev')} - {m.get('skor_dep')} (İlk Yarı: {m.get('skor_1y_ev')} - {m.get('skor_1y_dep')})\n")
print(story)
