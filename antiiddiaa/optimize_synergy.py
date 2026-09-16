import json
import sys
from collections import defaultdict
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import get_all_rules

def load_data():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        return json.load(f)['matches']

def get_odd(odds, keys):
    for k in keys:
        if k in odds and odds[k] is not None:
            try:
                return float(odds[k])
            except:
                pass
    return None

def analyze_odds(title, hits, misses):
    print(f"\n{'='*50}\n{title} OPTİMİZASYON ANALİZİ\n{'='*50}")
    print(f"Toplam Tetiklenme: {len(hits) + len(misses)}")
    print(f"Başarılı (HIT): {len(hits)} | Başarısız (MISS): {len(misses)}")
    if len(hits) + len(misses) > 0:
        print(f"Mevcut İsabet Oranı: {(len(hits)/(len(hits)+len(misses)))*100:.1f}%\n")
    
    # Analyze key odds
    keys_to_analyze = [
        ("İlk Yarı Beraberlik Oranı", ["İlk Yarı Sonucu_0"]),
        ("Maç Sonu Beraberlik Oranı", ["Maç Sonucu_0"]),
        ("2.5 Alt Oranı", ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"]),
        ("2.5 Üst Oranı", ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"]),
        ("KG Var Oranı", ["Karşılıklı Gol_Var"]),
        ("Ev Sahibi Galibiyeti", ["Maç Sonucu_1"]),
        ("Deplasman Galibiyeti", ["Maç Sonucu_2"])
    ]
    
    for label, keys in keys_to_analyze:
        hit_odds = [get_odd(m['oranlar'], keys) for m in hits]
        hit_odds = sorted([o for o in hit_odds if o is not None])
        
        miss_odds = [get_odd(m['oranlar'], keys) for m in misses]
        miss_odds = sorted([o for o in miss_odds if o is not None])
        
        if len(hit_odds) > 5 and len(miss_odds) > 5:
            hit_mean = sum(hit_odds) / len(hit_odds)
            miss_mean = sum(miss_odds) / len(miss_odds)
            hit_min, hit_max = hit_odds[0], hit_odds[-1]
            
            # Percentiles calculation
            def get_percentile(data, p):
                idx = int((len(data) - 1) * p)
                return data[idx]
                
            p25 = get_percentile(hit_odds, 0.25)
            p75 = get_percentile(hit_odds, 0.75)
            
            # How many hits/misses fall in this sweet spot?
            filtered_hits = [o for o in hit_odds if p25 <= o <= p75]
            filtered_misses = [o for o in miss_odds if p25 <= o <= p75]
            
            total_filtered = len(filtered_hits) + len(filtered_misses)
            new_hit_rate = (len(filtered_hits) / total_filtered) * 100 if total_filtered > 0 else 0
            
            print(f"--- {label} ---")
            print(f"  Hit Ortalaması: {hit_mean:.2f} (Aralık: {hit_min:.2f} - {hit_max:.2f})")
            print(f"  Miss Ortalaması: {miss_mean:.2f}")
            print(f"  * Tatlı Nokta (Sweet Spot): {p25:.2f} - {p75:.2f} arası")
            if total_filtered > 15: # Sadece anlamlı sayıda maç varsa göster
                print(f"  * Bu aralığı filtrelersek İsabet Oranı: {new_hit_rate:.1f}% ({len(filtered_hits)} Hit / {total_filtered} Toplam)")

def optimize_synergy(matches):
    rules = get_all_rules()
    
    # 0/2 Sinerjisi (Y11 + MS2)
    s02_hits = []
    s02_misses = []
    
    # 0/1 Sinerjisi (Y11 + MS1)
    s01_hits = []
    s01_misses = []

    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            
            y11_triggered = False
            ms2_triggered = False
            ms1_triggered = False
            
            for R in rules:
                trigger, msg = R.evaluate(odds)
                if trigger:
                    if R.code == "Y11":
                        y11_triggered = True
                    if R.code in ["1503", "1535"]:
                        ms2_triggered = True
                    if R.code in ["1516", "T8"]:
                        ms1_triggered = True
            
            sev = mac.get('skor_ev', -1)
            sdep = mac.get('skor_dep', -1)
            iy_sev = mac.get('skor_1y_ev', -1)
            iy_sdep = mac.get('skor_1y_dep', -1)
            
            is_iy0 = (iy_sev == iy_sdep)
            is_ms2 = (sdep > sev)
            is_ms1 = (sev > sdep)
            
            if y11_triggered and ms2_triggered:
                if is_iy0 and is_ms2:
                    s02_hits.append(mac)
                else:
                    s02_misses.append(mac)
                    
            if y11_triggered and ms1_triggered:
                if is_iy0 and is_ms1:
                    s01_hits.append(mac)
                else:
                    s01_misses.append(mac)

    analyze_odds("0/2 SİNERJİSİ", s02_hits, s02_misses)
    analyze_odds("0/1 SİNERJİSİ", s01_hits, s01_misses)

if __name__ == "__main__":
    matches = load_data()
    optimize_synergy(matches)
