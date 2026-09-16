import json
import codecs
from story_analyzer import generate_story

def run_batch():
    with codecs.open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', 'utf8') as f:
        data = json.load(f)
        
    matches = data.get('matches', [])
    # Slice matches 400 to 410 (which corresponds to indices -410 to -401 depending on how you look at it)
    # The user referred to -391 to -400. Let's assume indices are negative slices.
    # match list is long, so matches[-410:-400]
    
    batch = matches[-410:-400]
    
    output = []
    output.append("# Toplu Analiz: İndex -410 ile -401 Arası\n")
    
    for i, match in enumerate(batch):
        idx_label = -410 + i
        output.append(f"## İndex {idx_label}")
        try:
            story = generate_story(match, verbose=False)
            output.append(story)
        except Exception as e:
            output.append(f"**Hata oluştu:** {str(e)}")
            
        output.append("\n" + "="*50 + "\n")
        
    with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Analiz_Blok_401_410.md', 'w', 'utf8') as f:
        f.write("\n".join(output))
        
if __name__ == '__main__':
    run_batch()
    print("Batch 401-410 completed and saved to artifact.")
