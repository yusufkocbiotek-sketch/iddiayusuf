import json
import math
from collections import Counter

def format_perc(val, total):
    if total == 0: return 0.0
    return round((val / total) * 100, 1)

def main():
    JSON_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json'
    LIVE_PATH = r'C:\Users\YUSUF\.gemini\antigravity\scratch\live_match.json'

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)['matches']
        
    with open(LIVE_PATH, 'r', encoding='utf-8') as f:
        live = json.load(f)
        
    lig = live['lig']
    o_live = live['oranlar']
    
    ms1_live = o_live.get('Maç Sonucu_1', 99)
    ms2_live = o_live.get('Maç Sonucu_2', 99)
    kgy_live = o_live.get('Karşılıklı Gol_Yok', 99)
    kgv_live = o_live.get('Karşılıklı Gol_Var', 0)
    alt_live = o_live.get('Alt/Üst 2.5_Alt', 99)
    ust_live = o_live.get('Alt/Üst 2.5_Üst', 0)
    
    kg_fav_live = 'Yok' if kgy_live <= kgv_live else 'Var'
    au_fav_live = 'Alt' if alt_live <= ust_live else 'Üst'
    
    print(f"==================================================")
    print(f"🔍 DİNAMİK KURAL ÜRETİCİ (LIVE ANALYZER)")
    print(f"Maç: {lig} | MS1: {ms1_live} | MS2: {ms2_live} | KG Fav: {kg_fav_live} | A/Ü Fav: {au_fav_live}")
    print(f"==================================================\n")
    
    def find_matches(db_matches, require_league=False):
        found = []
        for m in db_matches:
            if require_league and m.get('lig', '').strip() != lig:
                continue
                
            o = m.get('oranlar', {})
            ms1 = o.get('Maç Sonucu_1', 99)
            ms2 = o.get('Maç Sonucu_2', 99)
            kgy = o.get('Karşılıklı Gol_Yok', 99)
            kgv = o.get('Karşılıklı Gol_Var', 0)
            alt = o.get('Alt/Üst 2.5_Alt', 99)
            ust = o.get('Alt/Üst 2.5_Üst', 0)
            
            kg_fav = 'Yok' if kgy <= kgv else 'Var'
            au_fav = 'Alt' if alt <= ust else 'Üst'
            
            # Dinamik Benzerlik Filtresi (+- 0.15 oran toleransı)
            if not (ms1_live - 0.15 <= ms1 <= ms1_live + 0.15): continue
            if not (ms2_live - 0.15 <= ms2 <= ms2_live + 0.15): continue
            if kg_fav != kg_fav_live: continue
            if au_fav != au_fav_live: continue
            
            found.append(m)
        return found
        
    # Önce SADECE KENDİ LİGİNDE ara
    matches = find_matches(db, require_league=True)
    scope = f"{lig} LİGİNDE"
    
    # Eğer liginde 10 maçtan az varsa (Veri yetersizse), TÜM DÜNYAYA açıl
    if len(matches) < 10:
        matches = find_matches(db, require_league=False)
        scope = "TÜM DÜNYA LİGLERİNDE (Küresel İkizler)"
        
    if not matches:
        print("Sistemde bu oran yapısına (Tolerans dahilinde) benzeyen hiçbir geçmiş maç bulunamadı!")
        return
        
    print(f"✅ {scope} tam {len(matches)} adet 'Genetik İkiz (Benzer Oranlı)' maç bulundu!\n")
    
    # Analiz
    ms1_count, ms0_count, ms2_count = 0, 0, 0
    ust_count, alt_count = 0, 0
    kg_var_count, kg_yok_count = 0, 0
    iy1, iy0, iy2 = 0, 0, 0
    scores = []
    
    for m in matches:
        ev = m.get('skor_ev', 0)
        dep = m.get('skor_dep', 0)
        iev = m.get('skor_1y_ev', 0)
        idep = m.get('skor_1y_dep', 0)
        
        if ev > dep: ms1_count += 1
        elif ev == dep: ms0_count += 1
        else: ms2_count += 1
        
        if ev + dep > 2: ust_count += 1
        else: alt_count += 1
        
        if ev > 0 and dep > 0: kg_var_count += 1
        else: kg_yok_count += 1
        
        if iev > idep: iy1 += 1
        elif iev == idep: iy0 += 1
        else: iy2 += 1
        
        scores.append(f"{ev}-{dep}")
        
    tot = len(matches)
    
    print(f"📊 DİNAMİK PATTERN (KURAL) SONUÇLARI:")
    print(f"--------------------------------------------------")
    print(f"📌 MAÇ SONUCU:")
    print(f"   MS 1: %{format_perc(ms1_count, tot)} | MS 0: %{format_perc(ms0_count, tot)} | MS 2: %{format_perc(ms2_count, tot)}")
    print(f"📌 ALT / ÜST:")
    print(f"   2.5 ALT: %{format_perc(alt_count, tot)} | 2.5 ÜST: %{format_perc(ust_count, tot)}")
    print(f"📌 KARŞILIKLI GOL:")
    print(f"   KG VAR: %{format_perc(kg_var_count, tot)} | KG YOK: %{format_perc(kg_yok_count, tot)}")
    print(f"📌 İLK YARI (DNA):")
    print(f"   İY 1: %{format_perc(iy1, tot)} | İY 0: %{format_perc(iy0, tot)} | İY 2: %{format_perc(iy2, tot)}")
    
    top_scores = Counter(scores).most_common(3)
    print(f"📌 EN ÇOK GELEN SKORLAR:")
    for s, c in top_scores:
        print(f"   Skor {s}: %{format_perc(c, tot)}")
    
    print(f"--------------------------------------------------")
    
    # En dominant patterni bul ve yorumla
    max_ms = max([("MS 1", ms1_count), ("MS 0", ms0_count), ("MS 2", ms2_count)], key=lambda x: x[1])
    max_au = max([("2.5 ÜST", ust_count), ("2.5 ALT", alt_count)], key=lambda x: x[1])
    max_kg = max([("KG VAR", kg_var_count), ("KG YOK", kg_yok_count)], key=lambda x: x[1])
    
    print(f"💡 YAPAY ZEKA YORUMU:")
    print(f"Bu oran yapısı oynandığında, geçmişteki veriler bize maçın ağırlıklı olarak {max_ms[0]} biteceğini (%{format_perc(max_ms[1], tot)}) gösteriyor.")
    print(f"Gol açısından ise en baskın karakterin {max_au[0]} (%{format_perc(max_au[1], tot)}) ve {max_kg[0]} (%{format_perc(max_kg[1], tot)}) olduğu net.")
    print(f"Tahmin üretilecekse ana yönelim {max_ms[0]} ve {max_au[0]} etrafında şekillenmeli.")
    
if __name__ == "__main__":
    main()
