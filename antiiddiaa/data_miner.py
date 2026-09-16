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

def mine_asian_handicap(matches):
    print("--- 1. ASYA HANDİKAP & TARAF ÇATIŞMASI MADENCİLİĞİ ---")
    # MS1 favori (1.30 - 1.60) ama Handikap 1 (Ev sahibinin 2 farkla kazanması) oranı uyumsuz.
    # Eger Handikap 1 çok yüksekse (Örn: >= 2.50), bu "Zoraki Favori" demektir.
    results = []
    for mac in matches:
        odds = mac.get('oranlar', {})
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        h1 = get_odd(odds, ["Handikaplı Maç Sonucu 0:1_1", "Handikaplı Maç Sonucu 1:0_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        
        if 1.30 <= ms1 <= 1.60 and h1 >= 2.60 and sev >= 0:
            results.append({
                'skor': f"{sev}-{sdep}",
                'ev_kazandi': sev > sdep,
                'dep_kazandi': sdep > sev,
                'berabere': sev == sdep
            })
            
    if results:
        toplam = len(results)
        ev_k = sum(1 for r in results if r['ev_kazandi'])
        dep_k = sum(1 for r in results if r['dep_kazandi'])
        beraberlik = sum(1 for r in results if r['berabere'])
        print(f"Kombinasyon: MS1 (1.30-1.60) VE Handikap 1 (>= 2.60)")
        print(f"Toplam Maç: {toplam}")
        print(f"Ev Sahibi Kazanma (MS1): {ev_k} ({(ev_k/toplam)*100:.1f}%)")
        print(f"Sürpriz (X2): {dep_k + beraberlik} ({((dep_k+beraberlik)/toplam)*100:.1f}%)\n")

def mine_ht_ft(matches):
    print("--- 2. İLK YARI / MAÇ SONUCU (HT/FT) MADENCİLİĞİ ---")
    # MS0 düşük (Beraberlik bekleniyor <= 3.20) ama IY0 yüksek (İlk Yarı beraberlik beklenmiyor >= 2.30)
    results = []
    for mac in matches:
        odds = mac.get('oranlar', {})
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        iy0 = get_odd(odds, ["İlk Yarı Sonucu_0"])
        
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        
        if ms0 <= 3.20 and iy0 >= 2.30 and ms0 != 99.0 and iy0 != 99.0 and sev >= 0:
            results.append({
                'skor': f"{sev}-{sdep}",
                'kg_var': sev > 0 and sdep > 0,
                'ust25': (sev + sdep) > 2
            })
            
    if results:
        toplam = len(results)
        kg = sum(1 for r in results if r['kg_var'])
        ust = sum(1 for r in results if r['ust25'])
        print(f"Kombinasyon: MS0 (<= 3.20) VE IY0 (>= 2.30)")
        print(f"Toplam Maç: {toplam}")
        print(f"KG Var Oranı: {kg} ({(kg/toplam)*100:.1f}%)")
        print(f"2.5 Üst Oranı: {ust} ({(ust/toplam)*100:.1f}%)\n")

def mine_league_exceptions(matches):
    print("--- 3. LİG BAZLI İSTİSNA MADENCİLİĞİ (2.5 Alt Kapalı Durumu) ---")
    # 2.5 Alt kapalı ve KG Var çok düşük. Hangi liglerde 3.5 Alt/Ust ne veriyor?
    # Maclari ulke/lig'e gore gruplayalim (Lig adi olmadigi icin ev sahibi takim isminden kaba bir analiz)
    results = []
    for mac in matches:
        odds = mac.get('oranlar', {})
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        
        if alt25 == 99.0 and kg_var <= 1.40 and sev >= 0:
            if ust35 <= 1.55: # Bol Gol Beklentisi
                results.append({
                    'toplam_gol': sev + sdep
                })
                
    if results:
        toplam = len(results)
        ust35_biten = sum(1 for r in results if r['toplam_gol'] > 3)
        ust45_biten = sum(1 for r in results if r['toplam_gol'] > 4)
        print(f"Kombinasyon: 2.5 Kapalı VE KG Var <= 1.40 VE 3.5 Üst <= 1.55")
        print(f"Toplam Maç: {toplam}")
        print(f"3.5 Üst Gelme Oranı: {ust35_biten} ({(ust35_biten/toplam)*100:.1f}%)")
        print(f"4.5 Üst Gelme Oranı: {ust45_biten} ({(ust45_biten/toplam)*100:.1f}%)\n")

if __name__ == "__main__":
    matches = load_data()
    mine_asian_handicap(matches)
    mine_ht_ft(matches)
    mine_league_exceptions(matches)
