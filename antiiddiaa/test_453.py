import json
import codecs
from story_analyzer import generate_story

def run_single(idx):
    with codecs.open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', 'utf8') as f:
        matches = json.load(f)['matches']
        
    m = matches[idx]
    
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
    
    print("\nRAW ODDS:")
    for k, v in m.get("oranlar", {}).items():
        if v is not None and str(v) != "99.0":
            print(f"  {k}: {v}")

if __name__ == '__main__':
    run_single(-453)
