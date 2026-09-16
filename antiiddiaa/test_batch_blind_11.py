import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
from story_analyzer import generate_story

def analyze_batch():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    start_idx = 1008
    end_idx = 1017
    batch = data['matches'][start_idx:end_idx+1]
    
    report_lines = []
    report_lines.append(f"# BLİND TEST RAPORU: BLOK {start_idx}-{end_idx}")
    report_lines.append(f"*(Modelin skor ve sonuçları bilmeden yaptığı kör nokta analizi)*\n")
    
    for match in batch:
        idx = data['matches'].index(match)
        ev = match.get('ev_sahibi', 'Bilinmiyor')
        dep = match.get('deplasman', 'Bilinmiyor')
        report_lines.append(f"## Index -{idx} ({ev} - {dep})")
        
        # Orijinal sonuçları sakla
        gercek_iy = f"{match.get('skor_1y_ev', '?')}-{match.get('skor_1y_dep', '?')}"
        gercek_ms = f"{match.get('skor_ev', '?')}-{match.get('skor_dep', '?')}"
        
        # Test için sonuçları sil
        match_copy = match.copy()
        if 'skor_1y_ev' in match_copy: match_copy['skor_1y_ev'] = "?"
        if 'skor_1y_dep' in match_copy: match_copy['skor_1y_dep'] = "?"
        if 'skor_ev' in match_copy: match_copy['skor_ev'] = "?"
        if 'skor_dep' in match_copy: match_copy['skor_dep'] = "?"
        
        # Analizi çalıştır
        story = generate_story(match_copy)
        
        # Hikayeden sadece önemli kısımları alalım
        lines = story.split('\n')
        kural_sirasi = ""
        genel_profil = ""
        
        for line in lines:
            if "**Kural Sırası:**" in line:
                kural_sirasi = line.strip()
            if "**Genel Profil:**" in line:
                genel_profil = line.strip()
                
        report_lines.append(f"{kural_sirasi}")
        report_lines.append(f"{genel_profil}")
        report_lines.append(f"> **Gerçekleşen Skor:** İlk Yarı **{gercek_iy}** | Maç Sonucu **{gercek_ms}**\n")
        
    with open(fr'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Analiz_Blok_{start_idx}_{end_idx}.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
        
    print(f"Blind analysis generated successfully for {start_idx}-{end_idx}!")

if __name__ == "__main__":
    analyze_batch()
