import json
import os
import story_analyzer
import rule_engine

def patch_rule_1478():
    with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patch 1478 to ms2 >= 1.95
    content = content.replace(
        "if ms2 <= 2.20 and kg_var <= 1.50 and ev_1y_05_ust >= 1.75 and ev_1y_05_ust < 99.0 and ev_15_alt <= 1.38:",
        "if 1.95 <= ms2 <= 2.20 and kg_var <= 1.50 and ev_1y_05_ust >= 1.75 and ev_1y_05_ust < 99.0 and ev_15_alt <= 1.38:"
    )
    with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Patched 1478")

def generate_report():
    output_path = r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Toplu_Analiz_195_300.md'
    
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write("# 🏆 GEÇMİŞ MAÇLAR BÜYÜK ANALİZ RAPORU (İndex -195'ten -300'e)\n\n")
        out.write("Patron, sen evden çıkarken sistemi hiç durdurmadan -195'ten -300'e kadar tam **105 maçı** tek tek incelemeye aldım. Tüm güncel kurallarımızı ve yeni eklediğimiz keskin sınırları (1.35, 1.28, 1478 vb.) bu maçlara uyguladım.\n\n")
        out.write("---\n\n")
        
        for i in range(-195, -300, -1):
            try:
                match = data['matches'][i]
                ev_skor = match.get('skor_ev')
                dep_skor = match.get('skor_dep')
                
                # Sadece skoru olan (oynanmış) maçları alalım
                if ev_skor is None or dep_skor is None:
                    continue
                    
                story = story_analyzer.generate_story(match, verbose=True)
                
                out.write(f"### 📌 İndex: {i} | {match.get('ev_sahibi')} - {match.get('deplasman')}\n")
                out.write(f"**GERÇEK SKOR:** {ev_skor} - {dep_skor}\n\n")
                out.write(story)
                out.write("\n\n---\n\n")
                
            except Exception as e:
                out.write(f"HATA OLUŞTU (İndex {i}): {str(e)}\n\n---\n\n")
                
    print(f"Report generated at {output_path}")

if __name__ == "__main__":
    patch_rule_1478()
    generate_report()
