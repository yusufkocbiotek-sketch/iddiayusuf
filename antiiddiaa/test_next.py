import json
import codecs
from story_analyzer import generate_story

def run_single(idx, m):
    skor_1y_ev = m.get("skor_1y_ev", "?")
    skor_1y_dep = m.get("skor_1y_dep", "?")
    skor_ev = m.get("skor_ev", "?")
    skor_dep = m.get("skor_dep", "?")
    
    print(f"==================================================")
    print(f"🔍 İNDEX {idx} ANALİZİ BAŞLIYOR...")
    print(f"==================================================")
    
    story = generate_story(m, verbose=False)
    print(story)
    
    print(f"\n==================================================")
    print(f"🏆 GERÇEKLEŞEN SKOR: İlk Yarı {skor_1y_ev}-{skor_1y_dep} | Maç Sonucu {skor_ev}-{skor_dep}")
    print(f"==================================================")

with codecs.open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', 'utf8') as f:
    matches = json.load(f)['matches']

found = 0
for i in range(-459, -500, -1):
    m = matches[i]
    ms1 = m.get('oranlar', {}).get('Maç Sonucu_1')
    if ms1 is not None and str(ms1) != "99.0":
        run_single(i, m)
        found += 1
        if found == 1:
            break
