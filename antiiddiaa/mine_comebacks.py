import json
import sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import get_all_rules

def load_data():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        return json.load(f)['matches']

def mine_comebacks(matches):
    rules = get_all_rules()
    
    print("--- GERİ DÖNÜŞ (1/2 ve 2/1) SİNERJİ MADENCİLİĞİ ---")
    
    # 1. Senaryo: 1/2 (İlk Yarı 1, Maç Sonu 2)
    # Hangi kurallar 1/2'yi tetikler?
    # Fikir: 1503 (Deplasman Sürprizi) + Y8/Y9 (Bol Gol/Düello)
    s12_toplam = 0
    s12_hit = 0
    
    s21_toplam = 0
    s21_hit = 0
    
    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            
            rule_1503 = False
            rule_y89 = False
            
            for R in rules:
                trigger, msg = R.evaluate(odds)
                if trigger:
                    if R.code in ["1503", "1535"]:
                        rule_1503 = True
                    if R.code in ["Y8", "Y9", "Y10"]:
                        rule_y89 = True
                        
            sev = mac.get('skor_ev', -1)
            sdep = mac.get('skor_dep', -1)
            iy_sev = mac.get('skor_1y_ev', -1)
            iy_sdep = mac.get('skor_1y_dep', -1)
            
            is_iy1 = (iy_sev > iy_sdep)
            is_ms2 = (sdep > sev)
            
            if rule_1503 and rule_y89:
                s12_toplam += 1
                if is_iy1 and is_ms2:
                    s12_hit += 1

    print(f"\n[Sinerji 1/2] 1503/1535 (Deplasman Sürprizi) + Y8/Y9/Y10 (Düello)")
    if s12_toplam > 0:
        print(f"Toplam Sinerji: {s12_toplam}")
        print(f"Gerçekleşen 1/2 Sayısı: {s12_hit} ({(s12_hit/s12_toplam)*100:.2f}%)")
        print(f"Not: 1/2 Oranı genelde 25.00 - 40.00 arasıdır.")

if __name__ == "__main__":
    matches = load_data()
    mine_comebacks(matches)
