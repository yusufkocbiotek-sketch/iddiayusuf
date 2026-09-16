import json
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

start_idx = -501
end_idx = -505

for i in range(start_idx, end_idx - 1, -1):
    try:
        match = matches[i]
        ev = match.get('ev_sahibi', 'Bilinmeyen')
        dep = match.get('deplasman', 'Bilinmeyen')
        skor_ev = match.get('skor_ev', '?')
        skor_dep = match.get('skor_dep', '?')
        skor_1y_ev = match.get('skor_1y_ev', '?')
        skor_1y_dep = match.get('skor_1y_dep', '?')
        
        story = generate_story(match, verbose=False)
        
        print(f"\n[{i}] {ev} - {dep}")
        print(f"Gerçek Skor: İY {skor_1y_ev}-{skor_1y_dep} / MS {skor_ev}-{skor_dep}")
        
        # Sadece kural sırası ve genel profili ve tahmini yazdır
        lines = story.split('\n')
        for line in lines:
            if "Kural Sırası:" in line or "Genel Profil:" in line or "Ana Tahmin:" in line or "Kombine Öneri:" in line:
                print(line.strip())
                
    except IndexError:
        print(f"Index {i} out of range.")
        break
