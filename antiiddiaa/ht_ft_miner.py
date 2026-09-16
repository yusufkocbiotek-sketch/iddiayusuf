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

def mine_ht_ft_anomalies(matches):
    print("--- HT/FT (İLK YARI / MAÇ SONUCU) MADENCİLİĞİ ---")
    
    # Kural D: İlk Yarı Favorisi, Maç Sonu Sürprizi (1/0 veya 1/2 Tuzağı)
    # Ev sahibi MS1 favori (<=1.55), IY1 çok favori (<= 2.00) ama MS0 oranı aşırı düşük (<= 3.50)
    kural_d = []
    for mac in matches:
        odds = mac.get('oranlar', {})
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        iy1 = get_odd(odds, ["İlk Yarı Sonucu_1"])
        
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        
        if ms1 <= 1.55 and iy1 <= 2.10 and ms0 <= 3.60 and ms1 != 99.0 and ms0 != 99.0 and iy1 != 99.0 and sev >= 0:
            kural_d.append({
                'skor': f"{sev}-{sdep}",
                'berabere': sev == sdep,
                'dep_kazandi': sdep > sev,
                'x2': sdep >= sev
            })
            
    if kural_d:
        toplam = len(kural_d)
        x2 = sum(1 for x in kural_d if x['x2'])
        print(f"\n[D] KOMBİNASYON: MS1 Favori (<= 1.55) & IY1 Banko (<= 2.10) AMA Beraberlik Oranı Düşük (<= 3.60)")
        print(f"Toplam Maç: {toplam}")
        print(f"Sürpriz (X2) Gelme Oranı: {x2} ({(x2/toplam)*100:.1f}%)")

    # Kural E: İlk Yarı 0/Maç Sonucu 0 Kilitlenmesi
    # IY0 çok düşük (<= 2.00) ve MS0 favori (<= 2.90). Herkes 0/0 bekliyor.
    kural_e = []
    for mac in matches:
        odds = mac.get('oranlar', {})
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        iy0 = get_odd(odds, ["İlk Yarı Sonucu_0"])
        
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        
        if ms0 <= 2.90 and iy0 <= 1.95 and ms0 != 99.0 and iy0 != 99.0 and sev >= 0:
            kural_e.append({
                'skor': f"{sev}-{sdep}",
                'ms1': sev > sdep,
                'ms2': sdep > sev,
                'ms0': sev == sdep
            })
            
    if kural_e:
        toplam = len(kural_e)
        ms0 = sum(1 for x in kural_e if x['ms0'])
        print(f"\n[E] KOMBİNASYON: MS0 (<= 2.90) & IY0 (<= 1.95)")
        print(f"Toplam Maç: {toplam}")
        print(f"Beraberlik (0) Gelme Oranı: {ms0} ({(ms0/toplam)*100:.1f}%)")

    # Kural F: Çifte Şans 12 ve IY0 Çatışması
    # 12 ÇŞ çok düşük (<= 1.25) yani "kesin biri yener" diyor. Ama İlk Yarı 0 oranı da aşırı düşük (<= 1.95)
    kural_f = []
    for mac in matches:
        odds = mac.get('oranlar', {})
        cs12 = get_odd(odds, ["Çifte Şans_12"])
        iy0 = get_odd(odds, ["İlk Yarı Sonucu_0"])
        
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        
        if cs12 <= 1.25 and iy0 <= 1.95 and cs12 != 99.0 and iy0 != 99.0 and sev >= 0:
            kural_f.append({
                'skor': f"{sev}-{sdep}",
                'berabere': sev == sdep,
                'iy_berabere': mac.get('skor_1y_ev', -1) == mac.get('skor_1y_dep', -1) if mac.get('skor_1y_ev', -1) >= 0 else False
            })
            
    if kural_f:
        toplam = len(kural_f)
        ms0 = sum(1 for x in kural_f if x['berabere'])
        iy0_hit = sum(1 for x in kural_f if x['iy_berabere'])
        print(f"\n[F] KOMBİNASYON: 12 Çifte Şans (<= 1.25) & IY0 (<= 1.95)")
        print(f"Toplam Maç: {toplam}")
        print(f"Beraberlik Biten Maç: {ms0} ({(ms0/toplam)*100:.1f}%)")
        print(f"İlk Yarı 0 Biten Maç: {iy0_hit} ({(iy0_hit/toplam)*100:.1f}%)")

if __name__ == "__main__":
    matches = load_data()
    mine_ht_ft_anomalies(matches)
