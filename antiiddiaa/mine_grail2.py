import json

def load_data():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        return json.load(f)['matches']

def get_odd(odds, keys):
    for k in keys:
        if k in odds and odds[k] is not None:
            return float(odds[k])
    return 99.0

def find_holy_grail(matches):
    print("--- HER İKİ YARIDA KG VAR: ELMAS ARAYIŞI ---")
    
    test_toplam = 0
    test_hit = 0
    
    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            ms1 = get_odd(odds, ["Maç Sonucu_1"])
            ms2 = get_odd(odds, ["Maç Sonucu_2"])
            kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
            iy_kg_var = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Var"])
            
            # Filtre 3: Asiri Dusuk IY KG (<= 3.00), Asiri Dusuk KG Var (<= 1.40) ve Denk Guc
            if iy_kg_var <= 3.00 and kg_var <= 1.40 and abs(ms1 - ms2) <= 0.80:
                test_toplam += 1
                
                sev = mac.get('skor_ev', -1)
                sdep = mac.get('skor_dep', -1)
                iy_sev = mac.get('skor_1y_ev', -1)
                iy_sdep = mac.get('skor_1y_dep', -1)
                iy_kg = iy_sev > 0 and iy_sdep > 0
                iy2_kg = (sev - iy_sev) > 0 and (sdep - iy_sdep) > 0
                
                if iy_kg and iy2_kg:
                    test_hit += 1

    if test_toplam > 0:
        print(f"\n[Filtre 3: IY KG <= 3.00 + Fark <= 0.80 + KG Var <= 1.40]")
        print(f"Uygun Maç Sayısı: {test_toplam}")
        print(f"Tam Saha Düello İsabeti: {test_hit} ({(test_hit/test_toplam)*100:.2f}%)")
        print("Gereken Oran (Başabaş için): {:.2f}".format(1/(test_hit/test_toplam)))
        
    test_toplam4 = 0
    test_hit4 = 0
    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            ms1 = get_odd(odds, ["Maç Sonucu_1"])
            ms2 = get_odd(odds, ["Maç Sonucu_2"])
            iy_kg_var = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Var"])
            ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
            
            # Filtre 4: Hollanda, Avustralya vs asiri gollu oranlar
            if iy_kg_var <= 2.80 and ust35 <= 1.80 and abs(ms1 - ms2) <= 1.20:
                test_toplam4 += 1
                
                sev = mac.get('skor_ev', -1)
                sdep = mac.get('skor_dep', -1)
                iy_sev = mac.get('skor_1y_ev', -1)
                iy_sdep = mac.get('skor_1y_dep', -1)
                iy_kg = iy_sev > 0 and iy_sdep > 0
                iy2_kg = (sev - iy_sev) > 0 and (sdep - iy_sdep) > 0
                
                if iy_kg and iy2_kg:
                    test_hit4 += 1

    if test_toplam4 > 0:
        print(f"\n[Filtre 4: IY KG <= 2.80 + 3.5 Ust <= 1.80 + Fark <= 1.20]")
        print(f"Uygun Maç Sayısı: {test_toplam4}")
        print(f"Tam Saha Düello İsabeti: {test_hit4} ({(test_hit4/test_toplam4)*100:.2f}%)")
        print("Gereken Oran (Başabaş için): {:.2f}".format(1/(test_hit4/test_toplam4)))

if __name__ == "__main__":
    matches = load_data()
    find_holy_grail(matches)
