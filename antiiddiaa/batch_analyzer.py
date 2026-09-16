import json
import os
import sys
from super_live_analyzer import analyze_match

DB_PATH = r"C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json"
LIG_PATH = r"C:\Users\YUSUF\.gemini\antigravity\scratch\lig_kurallari.json"
COMBO_PATH = r"C:\Users\YUSUF\.gemini\antigravity\scratch\combo_kurallari.json"

def main():
    if not os.path.exists(DB_PATH):
        print(f"Hata: {DB_PATH} bulunamadı.")
        return
        
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        maclar = data.get('matches', []) if isinstance(data, dict) else data

    lig_rules = []
    if os.path.exists(LIG_PATH):
        with open(LIG_PATH, 'r', encoding='utf-8') as f:
            d2 = json.load(f)
            lig_rules = d2.get('kurallar', []) if isinstance(d2, dict) else d2
            
    combo_rules = []
    if os.path.exists(COMBO_PATH):
        with open(COMBO_PATH, 'r', encoding='utf-8') as f:
            combo_rules = json.load(f)

    # Son 6 maçtan ilk 3'ünü al
    maclar_list = list(maclar.values()) if isinstance(maclar, dict) else maclar
    son_maclar = maclar_list[-6:-3]
    
    print(f"Toplam maç: {len(maclar)}. Son 3 maç analiz ediliyor...\n")
    
    for i, m in enumerate(reversed(son_maclar)):
        print(f"\n================================================================")
        print(f"👉 MAÇ {len(maclar) - i}")
        print(f"Ev Sahibi: {m.get('ev_sahibi', 'Bilinmiyor')} | Deplasman: {m.get('deplasman', 'Bilinmiyor')}")
        
        gercek_skor_ev = m.get('skor_ev', '?')
        gercek_skor_dep = m.get('skor_deplasman', '?')
        print(f"📌 GERÇEK SKOR: {gercek_skor_ev} - {gercek_skor_dep}")
        print(f"================================================================\n")
        
        analiz_sonucu = analyze_match(m, lig_rules, combo_rules, verbose=False)
        print(analiz_sonucu)

if __name__ == "__main__":
    main()
