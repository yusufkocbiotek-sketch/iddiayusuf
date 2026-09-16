import sys
sys.path.append(r"C:\Users\YUSUF\.gemini\antigravity\scratch")
import json
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for idx in range(-371, -376, -1):
    m = data['matches'][idx]
    story = generate_story(m, verbose=False)
    
    print(f"\n==================================================")
    print(f"📌 İndex: {idx} | {m.get('ev_sahibi')} - {m.get('deplasman')}")
    print(f"💥 GERÇEK SKOR: {m.get('skor_ev')} - {m.get('skor_dep')} (İlk Yarı: {m.get('skor_1y_ev')} - {m.get('skor_1y_dep')})")
    
    lines = story.split('\n')
    kombine_idx = -1
    for i, line in enumerate(lines):
        if "Kombine Öneri" in line:
            kombine_idx = i
        if "ÖĞRENME MOTORU GERİ BİLDİRİMİ" in line:
            if kombine_idx != -1:
                print(lines[kombine_idx-1]) # Ana Tahmin
                print(lines[kombine_idx])
            print("\n".join(lines[i:i+6]))
            break
