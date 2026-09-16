import json
import os
import story_analyzer

DB_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json'

def run_batch(num_matches=5, start_index=-10):
    print("Otonom Analiz Motoru Başlatılıyor...\n")
    if not os.path.exists(DB_PATH):
        print(f"HATA: Veritabanı bulunamadı -> {DB_PATH}")
        return
        
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        maclar = data.get('matches', []) if isinstance(data, dict) else data

    maclar_list = list(maclar.values()) if isinstance(maclar, dict) else maclar
    
    # İstenen aralığı hesapla
    end_index = start_index + num_matches
    if end_index >= 0:
        end_index = None # sona kadar
    
    test_maclar = maclar_list[start_index:end_index] if end_index else maclar_list[start_index:]
    
    print(f"Toplam maç: {len(maclar)}. Son {len(test_maclar)} maç otonom hikaye motoruyla analiz ediliyor...\n")
    
    for i, match in enumerate(test_maclar):
        ev = match.get('ev_sahibi', 'Bilinmeyen Ev')
        dep = match.get('deplasman', 'Bilinmeyen Dep')
        skor_ev = match.get('skor_ev', '?')
        skor_dep = match.get('skor_dep', '?')
        skor_1y_ev = match.get('skor_1y_ev', '?')
        skor_1y_dep = match.get('skor_1y_dep', '?')
        
        print("="*64)
        print(f"👉 MAÇ {i+1} / İndex: {start_index+i}")
        print(f"📌 GERÇEK SKOR: {skor_ev} - {skor_dep} (İY: {skor_1y_ev}-{skor_1y_dep})")
        print("="*64)
        
        # Otonom Hikaye Motorunu Çalıştır
        report = story_analyzer.generate_story(match, verbose=False)
        print(report)
        print("\n")

if __name__ == "__main__":
    # Son 5 maçı analiz et (-5'ten başlayıp sona kadar)
    run_batch(num_matches=5, start_index=-5)
