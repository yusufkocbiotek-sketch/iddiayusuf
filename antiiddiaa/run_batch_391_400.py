import json
import codecs
from story_analyzer import generate_story
import rule_engine

def run_batch():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # [-400:-390] gives us 10 matches
    batch = data['matches'][-400:-390]
    
    # We want to reverse them so we present them from -391 down to -400.
    # Wait, -391 is the latest among them. 
    # Let's just process them as they are and number them.
    
    output_lines = []
    output_lines.append("# 📈 ANALİZ BLOK 391-400\n")
    output_lines.append("> [!TIP]\n> **Sistem Notu:** Yeni 5 Fazlı Makine Zekası ve 1483 (Alt/Üst Paradoksu) Kuralı kullanılarak her bir oran derinlemesine taranmıştır.\n\n")
    
    for idx, match in enumerate(reversed(batch), start=391):
        output_lines.append(f"## 🔴 İndex -{idx}")
        try:
            story = generate_story(match, verbose=True)
            output_lines.append(story)
        except Exception as e:
            output_lines.append(f"**Hata oluştu:** {str(e)}")
        output_lines.append("\n---\n")
        
    with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Analiz_Blok_391_400.md', 'w', 'utf-8') as f:
        f.write("\n".join(output_lines))
        
    print("Batch 391-400 completed and saved to artifact.")

if __name__ == '__main__':
    run_batch()
