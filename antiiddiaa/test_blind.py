import json
import codecs
from story_analyzer import generate_story

def run_blind(idx):
    with codecs.open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', 'utf8') as f:
        matches = json.load(f)['matches']
        
    m = matches[idx]
    
    # 1. Gerçek skorları yedekleyelim
    skor_1y_ev = m.get("skor_1y_ev", "?")
    skor_1y_dep = m.get("skor_1y_dep", "?")
    skor_ev = m.get("skor_ev", "?")
    skor_dep = m.get("skor_dep", "?")
    
    # 2. Skorları maç verisinden TAMAMEN SİLELİM (Makinenin görmesi imkansızlaşsın)
    temp_m = m.copy()
    if 'skor_1y_ev' in temp_m: del temp_m['skor_1y_ev']
    if 'skor_1y_dep' in temp_m: del temp_m['skor_1y_dep']
    if 'skor_ev' in temp_m: del temp_m['skor_ev']
    if 'skor_dep' in temp_m: del temp_m['skor_dep']

    print(f"==================================================")
    print(f"🔍 İNDEX {idx} KÖR (BLIND) ANALİZ BAŞLIYOR...")
    print(f"Makinenin skor verisine erişimi TAMAMEN KESİLDİ.")
    print(f"==================================================")
    
    # 3. Sadece oranları vererek hikayeyi oluşturalım
    story = generate_story(temp_m, verbose=False)
    
    # İçinde skor geçen satırları göstermeyelim (bizim şablonumuzda "GERÇEKLEŞEN SKOR" yazıyor)
    lines = story.split('\n')
    filtered_lines = [l for l in lines if 'GERÇEKLEŞEN SKOR' not in l]
    print('\n'.join(filtered_lines))
    
    # 4. En sonda gerçeği açıklayalım
    print(f"\n==================================================")
    print(f"🏆 SIRRIMIZ AÇIĞA ÇIKIYOR... GERÇEKLEŞEN SKOR: İlk Yarı {skor_1y_ev}-{skor_1y_dep} | Maç Sonucu {skor_ev}-{skor_dep}")
    print(f"==================================================")

if __name__ == '__main__':
    run_blind(-460)
