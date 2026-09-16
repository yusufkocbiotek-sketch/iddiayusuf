import json
import codecs
import sys
from story_analyzer import generate_story

def main():
    with codecs.open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', 'utf8') as f:
        matches = json.load(f)['matches']
        
    out_file = r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Analiz_Blok_526_530.md'
    
    indices = [-526, -527, -528, -529, -530]
    
    with codecs.open(out_file, 'w', 'utf8') as out:
        out.write("# Kör Test Sonuçları (İndex -526 ile -530 Arası)\n\n")
        
        for idx in indices:
            try:
                m = matches[idx]
            except IndexError:
                out.write(f"## 🔍 İndex {idx} (BULUNAMADI)\n\n---\n\n")
                continue
            
            oranlar = m.get('oranlar', {})
            ms1 = oranlar.get('Maç Sonucu_1')
            
            skor_1y_ev = m.get("skor_1y_ev", "?")
            skor_1y_dep = m.get("skor_1y_dep", "?")
            skor_ev = m.get("skor_ev", "?")
            skor_dep = m.get("skor_dep", "?")
            takimlar = m.get('ev_sahibi', '?') + ' - ' + m.get('deplasman', '?')
            
            temp_m = m.copy()
            for k in ['skor_1y_ev', 'skor_1y_dep', 'skor_ev', 'skor_dep']:
                if k in temp_m: del temp_m[k]

            story = generate_story(temp_m, verbose=False)
            lines = story.split('\n')
            filtered_lines = [l for l in lines if 'GERÇEKLEŞEN SKOR' not in l]
            
            out.write(f"## 🔍 İndex {idx} ({takimlar})\n")
            out.write('\n'.join(filtered_lines) + "\n")
            out.write(f"\n**🏆 GERÇEKLEŞEN SKOR: İlk Yarı {skor_1y_ev}-{skor_1y_dep} | Maç Sonucu {skor_ev}-{skor_dep}**\n\n---\n\n")
            
    print(f"Test tamamlandı, {out_file} oluşturuldu.")

if __name__ == '__main__':
    main()
