import json
import sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import get_all_rules

def load_data():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        return json.load(f)['matches']

def test_synergy(matches):
    rules = get_all_rules()
    
    print("--- MEGA SİNERJİ TESTİ: Y11 (İY0) + MS Yönlendirmeleri ---")
    
    synergy_0_1_toplam = 0
    synergy_0_1_hit = 0
    
    synergy_0_2_toplam = 0
    synergy_0_2_hit = 0

    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            
            y11_triggered = False
            ms1_triggered = False
            ms2_triggered = False
            
            for R in rules:
                trigger, msg = R.evaluate(odds)
                if trigger:
                    if R.code == "Y11":
                        y11_triggered = True
                    # Hangi kurallar MS2 ongorur? (Örn: 1503, 1535)
                    if R.code in ["1503", "1535", "1493", "1515"]:
                        ms2_triggered = True
                    # Hangi kurallar MS1 ongorur? (Örn: 1516, T8, 1492)
                    if R.code in ["1516", "T8", "1492"]:
                        ms1_triggered = True
            
            sev = mac.get('skor_ev', -1)
            sdep = mac.get('skor_dep', -1)
            iy_sev = mac.get('skor_1y_ev', -1)
            iy_sdep = mac.get('skor_1y_dep', -1)
            
            is_iy0 = (iy_sev == iy_sdep)
            is_ms1 = (sev > sdep)
            is_ms2 = (sdep > sev)
            
            if y11_triggered and ms1_triggered:
                synergy_0_1_toplam += 1
                if is_iy0 and is_ms1:
                    synergy_0_1_hit += 1
                    
            if y11_triggered and ms2_triggered:
                synergy_0_2_toplam += 1
                if is_iy0 and is_ms2:
                    synergy_0_2_hit += 1

    print(f"\n[Sinerji 0/1] Y11 (İY 0) + (1516, T8, 1492 vb.)")
    if synergy_0_1_toplam > 0:
        print(f"Toplam Sinerji: {synergy_0_1_toplam}")
        print(f"Gerçekleşen 0/1 Sayısı: {synergy_0_1_hit} ({(synergy_0_1_hit/synergy_0_1_toplam)*100:.1f}%)")
        print(f"Not: 0/1 Oranı genelde 4.50 - 6.00 arasıdır.")
        
    print(f"\n[Sinerji 0/2] Y11 (İY 0) + (1503, 1535, 1515 vb.)")
    if synergy_0_2_toplam > 0:
        print(f"Toplam Sinerji: {synergy_0_2_toplam}")
        print(f"Gerçekleşen 0/2 Sayısı: {synergy_0_2_hit} ({(synergy_0_2_hit/synergy_0_2_toplam)*100:.1f}%)")
        print(f"Not: 0/2 Oranı (Deplasman Sürprizi) genelde 8.00 - 15.00 arasıdır.")

if __name__ == "__main__":
    matches = load_data()
    test_synergy(matches)
