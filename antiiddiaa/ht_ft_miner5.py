import json

def load_data():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        return json.load(f)['matches']

def get_odd(odds, keys):
    for k in keys:
        if k in odds and odds[k] is not None:
            return float(odds[k])
    return 99.0

def deep_dive_12_trap(matches):
    print("--- 12 ÇİFTE ŞANS TUZAĞI DERİN ANALİZİ ---")
    
    # Segmentler:
    # 1. 2.5 Alt Oranı (Favori vs Sürpriz)
    # 2. KG Var Oranı (Favori vs Sürpriz)
    # 3. IY 1.5 Alt Oranı
    
    seg_alt25_dusuk = {'toplam': 0, 'iy0': 0, 'iy0_oranlar': []}
    seg_alt25_yuksek = {'toplam': 0, 'iy0': 0, 'iy0_oranlar': []}
    
    seg_kgvar_dusuk = {'toplam': 0, 'iy0': 0, 'iy0_oranlar': []}
    seg_kgvar_yuksek = {'toplam': 0, 'iy0': 0, 'iy0_oranlar': []}
    
    seg_iy15alt_cok_dusuk = {'toplam': 0, 'iy0': 0, 'iy0_oranlar': []} # Kısır beklenen ilk yarılar
    
    # Efsanevi Kombinasyon (Kesişim)
    seg_efsane = {'toplam': 0, 'iy0': 0, 'iy0_oranlar': []}
    
    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            cs12 = get_odd(odds, ["Çifte Şans_12"])
            iy0 = get_odd(odds, ["İlk Yarı Sonucu_0"])
            alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
            kg_var = get_odd(odds, ["Karşılıklı Gol_Var", "Karşılıklı Gol Var"])
            iy_15_alt = get_odd(odds, ["İlk Yarı Alt/Üst 1.5_Alt", "1. Yarı Altı/Üstü 1.5_Alt"])
            
            if cs12 <= 1.20 and cs12 != 99.0 and iy0 != 99.0:
                iy_sev = mac.get('skor_1y_ev')
                iy_sdep = mac.get('skor_1y_dep')
                is_iy0 = (iy_sev == iy_sdep)
                
                # 2.5 Alt Segmenti
                if alt25 != 99.0:
                    if alt25 <= 1.85: # Alt Favori
                        seg_alt25_dusuk['toplam'] += 1
                        if is_iy0: seg_alt25_dusuk['iy0'] += 1
                        seg_alt25_dusuk['iy0_oranlar'].append(iy0)
                    else: # Ust Favori
                        seg_alt25_yuksek['toplam'] += 1
                        if is_iy0: seg_alt25_yuksek['iy0'] += 1
                        seg_alt25_yuksek['iy0_oranlar'].append(iy0)
                        
                # KG Var Segmenti
                if kg_var != 99.0:
                    if kg_var <= 1.65: # KG Var Favori
                        seg_kgvar_dusuk['toplam'] += 1
                        if is_iy0: seg_kgvar_dusuk['iy0'] += 1
                        seg_kgvar_dusuk['iy0_oranlar'].append(iy0)
                    else: # KG Yok Favori
                        seg_kgvar_yuksek['toplam'] += 1
                        if is_iy0: seg_kgvar_yuksek['iy0'] += 1
                        seg_kgvar_yuksek['iy0_oranlar'].append(iy0)
                        
                # IY 1.5 Alt Segmenti
                if iy_15_alt <= 1.35 and iy_15_alt != 99.0:
                    seg_iy15alt_cok_dusuk['toplam'] += 1
                    if is_iy0: seg_iy15alt_cok_dusuk['iy0'] += 1
                    seg_iy15alt_cok_dusuk['iy0_oranlar'].append(iy0)
                    
                # Efsane Kombinasyon: 12 CS <= 1.20 VE 2.5 Alt Favori (<= 1.85) VE KG Yok Favori (> 1.65)
                if alt25 <= 1.85 and kg_var > 1.65 and kg_var != 99.0:
                    seg_efsane['toplam'] += 1
                    if is_iy0: seg_efsane['iy0'] += 1
                    seg_efsane['iy0_oranlar'].append(iy0)

    def print_segment(name, seg):
        if seg['toplam'] > 0:
            hit_rate = seg['iy0'] / seg['toplam']
            avg_odds = sum(seg['iy0_oranlar']) / len(seg['iy0_oranlar'])
            roi = (hit_rate * avg_odds - 1) * 100
            print(f"\n[Filtre] {name}")
            print(f"Maç Sayısı: {seg['toplam']} | IY0 Biten: {seg['iy0']} ({hit_rate*100:.1f}%)")
            print(f"Ortalama IY0 Oranı: {avg_odds:.2f} | Beklenen ROI (Kâr): %{roi:.1f}")

    print_segment("2.5 ALT Favori (<= 1.85)", seg_alt25_dusuk)
    print_segment("2.5 ÜST Favori (> 1.85)", seg_alt25_yuksek)
    print_segment("KG VAR Favori (<= 1.65)", seg_kgvar_dusuk)
    print_segment("KG YOK Favori (> 1.65)", seg_kgvar_yuksek)
    print_segment("IY 1.5 ALT Çok Düşük (<= 1.35)", seg_iy15alt_cok_dusuk)
    print("\n👑 ALTIN VURUŞ (KOMBİNASYON) 👑")
    print_segment("ÇŞ 12 (<=1.20) + 2.5 ALT (<=1.85) + KG YOK (>1.65)", seg_efsane)

if __name__ == "__main__":
    matches = load_data()
    deep_dive_12_trap(matches)
