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
    print("--- HER İKİ YARIDA KG VAR: KUTSAL KASE ARAYIŞI ---")
    
    test_toplam = 0
    test_hit = 0
    
    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            ms1 = get_odd(odds, ["Maç Sonucu_1"])
            ms2 = get_odd(odds, ["Maç Sonucu_2"])
            kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
            iy_kg_var = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Var"])
            ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
            ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
            
            # Kutsal Kase Arayisi:
            # - Ilk Yari KG Var beklentisi asiri yuksek (<= 3.30)
            # - Genel KG Var beklentisi yuksek (<= 1.40)
            # - Taraf orani dengeli
            if iy_kg_var <= 3.30 and kg_var <= 1.45 and abs(ms1 - ms2) <= 1.00:
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
        print(f"\n[Filtre 1: IY KG <= 3.30 + Dengeli Maç (Fark <= 1.0) + KG Var <= 1.45]")
        print(f"Uygun Maç Sayısı: {test_toplam}")
        print(f"Tam Saha Düello İsabeti: {test_hit} ({(test_hit/test_toplam)*100:.2f}%)")
        print("Gereken Oran (Başabaş için): {:.2f}".format(1/(test_hit/test_toplam)))

    test_toplam2 = 0
    test_hit2 = 0
    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            iy1 = get_odd(odds, ["İlk Yarı Sonucu_1"])
            iy2 = get_odd(odds, ["İlk Yarı Sonucu_2"])
            kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
            iy_kg_var = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Var"])
            ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
            
            # Filtre 2: Asiri Gollu Dengeli (3.5 Ust <= 2.20) + IY0 Cok Yuksek (Kimse berabere beklemiyor)
            iy0 = get_odd(odds, ["İlk Yarı Sonucu_0"])
            if iy0 >= 2.20 and ust35 <= 2.20 and kg_var <= 1.40 and iy_kg_var <= 3.40:
                test_toplam2 += 1
                
                sev = mac.get('skor_ev', -1)
                sdep = mac.get('skor_dep', -1)
                iy_sev = mac.get('skor_1y_ev', -1)
                iy_sdep = mac.get('skor_1y_dep', -1)
                iy_kg = iy_sev > 0 and iy_sdep > 0
                iy2_kg = (sev - iy_sev) > 0 and (sdep - iy_sdep) > 0
                
                if iy_kg and iy2_kg:
                    test_hit2 += 1

    if test_toplam2 > 0:
        print(f"\n[Filtre 2: IY0 >= 2.20 + 3.5 Üst <= 2.20 + IY KG <= 3.40 + KG Var <= 1.40]")
        print(f"Uygun Maç Sayısı: {test_toplam2}")
        print(f"Tam Saha Düello İsabeti: {test_hit2} ({(test_hit2/test_toplam2)*100:.2f}%)")
        print("Gereken Oran (Başabaş için): {:.2f}".format(1/(test_hit2/test_toplam2)))

if __name__ == "__main__":
    matches = load_data()
    find_holy_grail(matches)
