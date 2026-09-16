import json

def load_data():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        return json.load(f)['matches']

def get_odd(odds, keys):
    for k in keys:
        if k in odds and odds[k] is not None:
            return float(odds[k])
    return 99.0

def deep_ht_ft_miner(matches):
    print("--- HT/FT (İLK YARI / MAÇ SONUCU) DERİN KAZI ---")
    
    # 1. 0/1 veya 0/2 Tuzağı (İlk yarı kesin berabere biter, 2. yarı maç kopar algısı)
    # IY0 çok favori (<= 1.85) ama MS0 çok sürpriz (>= 3.30). Yani "maç kopacak ama 2. yarıda" algısı.
    test_1_toplam = 0
    test_1_ms1 = 0
    test_1_ms2 = 0
    test_1_ms0 = 0
    
    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            iy0 = get_odd(odds, ["İlk Yarı Sonucu_0"])
            ms0 = get_odd(odds, ["Maç Sonucu_0"])
            
            if iy0 <= 1.90 and ms0 >= 3.20 and iy0 != 99.0 and ms0 != 99.0:
                test_1_toplam += 1
                sev = mac.get('skor_ev')
                sdep = mac.get('skor_dep')
                if sev > sdep: test_1_ms1 += 1
                elif sdep > sev: test_1_ms2 += 1
                else: test_1_ms0 += 1
                
    if test_1_toplam > 0:
        print(f"\n[Filtre 1: IY0 (<= 1.90) VE MS0 (>= 3.20)] (İlk yarı kilitlenip 2. yarı açılacak denen maçlar)")
        print(f"Toplam Maç: {test_1_toplam}")
        print(f"Ev Sahibi (MS1): {test_1_ms1} ({(test_1_ms1/test_1_toplam)*100:.1f}%)")
        print(f"Deplasman (MS2): {test_1_ms2} ({(test_1_ms2/test_1_toplam)*100:.1f}%)")
        print(f"Beraberlik (MS0): {test_1_ms0} ({(test_1_ms0/test_1_toplam)*100:.1f}%) -> Bürolar patladı!")

    # 2. Asla Berabere Bitmez (1/2 veya 2/1) Tuzağı
    # 12 ÇŞ aşırı düşük (<= 1.20) yani "Kesin biri kazanacak" deniyor. Peki İlk Yarı 0 veya MS 0 geliyor mu?
    test_2_toplam = 0
    test_2_ms0 = 0
    test_2_iy0 = 0
    
    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            cs12 = get_odd(odds, ["Çifte Şans_12"])
            iy0 = get_odd(odds, ["İlk Yarı Sonucu_0"])
            
            if cs12 <= 1.20 and cs12 != 99.0:
                test_2_toplam += 1
                sev = mac.get('skor_ev')
                sdep = mac.get('skor_dep')
                iy_sev = mac.get('skor_1y_ev')
                iy_sdep = mac.get('skor_1y_dep')
                
                if sev == sdep: test_2_ms0 += 1
                if iy_sev == iy_sdep: test_2_iy0 += 1

    if test_2_toplam > 0:
        print(f"\n[Filtre 2: Çifte Şans 12 (<= 1.20)] (Kesin biri kazanır tuzağı)")
        print(f"Toplam Maç: {test_2_toplam}")
        print(f"Maç Sonu Berabere (MS0) Biten: {test_2_ms0} ({(test_2_ms0/test_2_toplam)*100:.1f}%)")
        print(f"İlk Yarı Berabere (IY0) Biten: {test_2_iy0} ({(test_2_iy0/test_2_toplam)*100:.1f}%)")
        print("Not: Çifte Şans 12'ye oynayanlar %10 kâr için %30 riske giriyor!")
        
    # 3. IY 1/0 ve IY 2/0 Sırrı
    # İlk Yari Ev Favori (<= 1.95) ama MS0 dusuk (<= 3.10)
    test_3_toplam = 0
    test_3_x2 = 0
    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            iy1 = get_odd(odds, ["İlk Yarı Sonucu_1"])
            ms0 = get_odd(odds, ["Maç Sonucu_0"])
            
            if iy1 <= 1.95 and ms0 <= 3.20 and iy1 != 99.0 and ms0 != 99.0:
                test_3_toplam += 1
                sev = mac.get('skor_ev')
                sdep = mac.get('skor_dep')
                if sdep >= sev: test_3_x2 += 1

    if test_3_toplam > 0:
        print(f"\n[Filtre 3: IY1 (<= 1.95) VE MS0 (<= 3.20)]")
        print(f"Toplam Maç: {test_3_toplam}")
        print(f"X2 (Sürpriz) İsabeti: {test_3_x2} ({(test_3_x2/test_3_toplam)*100:.1f}%)")

if __name__ == "__main__":
    matches = load_data()
    deep_ht_ft_miner(matches)
