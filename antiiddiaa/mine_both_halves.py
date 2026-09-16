import json
from collections import defaultdict

def load_data():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        return json.load(f)['matches']

def get_odd(odds, keys):
    for k in keys:
        if k in odds and odds[k] is not None:
            return float(odds[k])
    return 99.0

def mine_both_halves_kg(matches):
    print("--- HER İKİ YARIDA KG VAR (TAM SAHA DÜELLO) MADENCİLİĞİ ---")
    
    hits = []
    
    for mac in matches:
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        iy_sev = mac.get('skor_1y_ev', -1)
        iy_sdep = mac.get('skor_1y_dep', -1)
        
        # Sadece gecerli skorlari olan maclari alalim
        if sev >= 0 and sdep >= 0 and iy_sev >= 0 and iy_sdep >= 0:
            iy_kg_var = iy_sev > 0 and iy_sdep > 0
            iy2_sev = sev - iy_sev
            iy2_sdep = sdep - iy_sdep
            iy2_kg_var = iy2_sev > 0 and iy2_sdep > 0
            
            her_iki_yari_kg = iy_kg_var and iy2_kg_var
            
            odds = mac.get('oranlar', {})
            ms1 = get_odd(odds, ["Maç Sonucu_1"])
            ms2 = get_odd(odds, ["Maç Sonucu_2"])
            kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
            ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
            
            mac['her_iki_yari_kg'] = her_iki_yari_kg
            if her_iki_yari_kg:
                hits.append(mac)
                
    total_valid = sum(1 for m in matches if m.get('skor_ev', -1) >= 0 and m.get('skor_1y_ev', -1) >= 0)
    print(f"Toplam Geçerli Maç: {total_valid}")
    print(f"Her İki Yarı KG Olan Maç: {len(hits)} ({(len(hits)/total_valid)*100:.2f}%)")
    
    # Kural H: Favorisi Olmayan KG Şöleni
    # MS1 ve MS2 birbirine cok yakin (Dengeli mac) ve 3.5 Ust orani cok dusuk degil
    test_kural_toplam = 0
    test_kural_hit = 0
    
    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            ms1 = get_odd(odds, ["Maç Sonucu_1"])
            ms2 = get_odd(odds, ["Maç Sonucu_2"])
            kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
            iy_kg_var = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Var"])
            ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
            ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
            
            # Pattern Arayisi: 
            # 1. Dengeli bir mac mi? (Kimse agır favori degil)
            # 2. Ilk Yari KG Var orani cok yuksek olmamali (<= 4.50)
            # 3. 3.5 Ust kapali olmamali
            if 2.10 <= ms1 <= 2.90 and 2.10 <= ms2 <= 2.90 and kg_var <= 1.55 and iy_kg_var <= 4.00 and iy_kg_var != 99.0:
                test_kural_toplam += 1
                if mac.get('her_iki_yari_kg', False):
                    test_kural_hit += 1
                    
    if test_kural_toplam > 0:
        print(f"\n[Test] Dengeli Maçlar + KG Var (<=1.55) + IY KG (<=4.00)")
        print(f"Uygun Maç Sayısı: {test_kural_toplam}")
        print(f"Tam Saha Düello İsabeti: {test_kural_hit} ({(test_kural_hit/test_kural_toplam)*100:.2f}%)")
        print("Not: Bu bahsin oranı genelde 8.00 ile 12.00 arasındadır. Eger %10'un uzerinde tutarsa cok karli!")

    # Pattern B: 2.5 Kapali Ligi (Az Once Buldugumuz)
    test2_toplam = 0
    test2_hit = 0
    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
            
            if alt25 == 99.0: # Gollu oldugu belli
                test2_toplam += 1
                if mac.get('her_iki_yari_kg', False):
                    test2_hit += 1
                    
    if test2_toplam > 0:
        print(f"\n[Test 2] 2.5 Alt/Ust Kapali Maçlar (Zaten Bol Gollu Beklenenler)")
        print(f"Uygun Maç Sayısı: {test2_toplam}")
        print(f"Tam Saha Düello İsabeti: {test2_hit} ({(test2_hit/test2_toplam)*100:.2f}%)")
        
if __name__ == "__main__":
    matches = load_data()
    mine_both_halves_kg(matches)
