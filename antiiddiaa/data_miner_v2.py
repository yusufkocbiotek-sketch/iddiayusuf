import json

def load_data():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        return json.load(f)['matches']

def get_odd(odds, keys):
    for k in keys:
        if k in odds and odds[k] is not None:
            return float(odds[k])
    return 99.0

def refine_miner(matches):
    print("--- DETAYLI MADENCİLİK (GİZLİ HAZİNELER) ---")
    
    # Kural A: Handikap Şişirmesi (X2 Sürprizi)
    # MS1 = 1.35 - 1.55 (Net Favori) ama Handikap 1 = 2.65 üstü
    kural_a = []
    for mac in matches:
        odds = mac.get('oranlar', {})
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        h1 = get_odd(odds, ["Handikaplı Maç Sonucu 0:1_1", "Handikaplı Maç Sonucu 1:0_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        
        if 1.35 <= ms1 <= 1.55 and h1 >= 2.65 and sev >= 0:
            kural_a.append({
                'skor': f"{sev}-{sdep}",
                'ms1': sev > sdep,
                'x2': sdep >= sev
            })
            
    if kural_a:
        toplam = len(kural_a)
        x2_sayi = sum(1 for x in kural_a if x['x2'])
        print(f"\n[A] KOMBİNASYON: MS1 (1.35-1.55) & Handikap 1 (>= 2.65)")
        print(f"Toplam Maç: {toplam}")
        print(f"Sürpriz X2 Gelme Oranı (Patlama): {x2_sayi} ({(x2_sayi/toplam)*100:.1f}%)")
        print(f"Bürolar MS1'i 1.45 gösterip, X2'ye 2.50 civarı oran veriyor. X2 oynanırsa %{((x2_sayi/toplam)*2.50 - 1)*100:.1f} KÂR MARJI (ROI) var!")

    # Kural B: Sahte 3.5 Şöleni (3.5 Alt Bankosu)
    # 2.5 Alt kapalı, KG Var <= 1.45, ve 3.5 Üst <= 1.60
    kural_b = []
    for mac in matches:
        odds = mac.get('oranlar', {})
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        
        if alt25 == 99.0 and kg_var <= 1.45 and ust35 <= 1.60 and sev >= 0:
            kural_b.append({
                'skor': f"{sev}-{sdep}",
                'alt35': (sev + sdep) <= 3
            })
            
    if kural_b:
        toplam = len(kural_b)
        alt35_sayi = sum(1 for x in kural_b if x['alt35'])
        print(f"\n[B] KOMBİNASYON: 2.5 Kapalı & KG Var (<= 1.45) & 3.5 Üst (<= 1.60)")
        print(f"Toplam Maç: {toplam}")
        print(f"3.5 ALT Gelme Oranı (Tuzak): {alt35_sayi} ({(alt35_sayi/toplam)*100:.1f}%)")
        print(f"Bürolar 3.5 Üst'ü 1.50 gösterip 3.5 Alt'a 2.40 veriyor. 3.5 ALT oynanırsa %{((alt35_sayi/toplam)*2.40 - 1)*100:.1f} KÂR MARJI (ROI) var!")

    # Kural C: İlk Yarı Gol Uyumsuzluğu
    # IY 0.5 Ust çok düşük (<= 1.25) ama MS 2.5 Üst yüksek (>= 1.90)
    kural_c = []
    for mac in matches:
        odds = mac.get('oranlar', {})
        iy05ust = get_odd(odds, ["İlk Yarı Alt/Üst 0.5_Üst", "1. Yarı Altı/Üstü 0.5_Üst"])
        ms25ust = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        
        if iy05ust <= 1.25 and ms25ust >= 1.90 and ms25ust != 99.0 and sev >= 0:
            kural_c.append({
                'skor': f"{sev}-{sdep}",
                'alt25': (sev + sdep) <= 2,
                'iy_gol_oldu': mac.get('skor_iy_ev', -1) + mac.get('skor_iy_dep', -1) > 0 if mac.get('skor_iy_ev', -1) >= 0 else False
            })
            
    if kural_c:
        toplam = len(kural_c)
        alt25 = sum(1 for x in kural_c if x['alt25'])
        print(f"\n[C] KOMBİNASYON: IY 0.5 Üst (<= 1.25) & MS 2.5 Üst (>= 1.90)")
        print(f"Toplam Maç: {toplam}")
        print(f"2.5 ALT Gelme Oranı: {alt25} ({(alt25/toplam)*100:.1f}%)")
        print(f"Bürolar 'İlk yarı kesin gol olur ama maç alt biter' diyor. 2.5 Alt oynanırsa (Oran ~1.85) %{((alt25/toplam)*1.85 - 1)*100:.1f} KÂR MARJI (ROI) var!")

if __name__ == "__main__":
    matches = load_data()
    refine_miner(matches)
