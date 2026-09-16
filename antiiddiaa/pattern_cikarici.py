import json
import os
from collections import defaultdict, Counter

def extract_sub_patterns():
    JSON_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json'
    RULES_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\lig_kurallari.json'

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        matches = json.load(f)['matches']

    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        lig_kurallari = json.load(f)

    # Kural koşul fonksiyonunu dinamik olarak tanımla (kural_motoru.py ile aynı mantık)
    def match_rule(o, lig, k):
        if lig != k['lig']: return False
        
        ms1 = o.get('Maç Sonucu_1', 99)
        ms2 = o.get('Maç Sonucu_2', 99)
        kgyok = o.get('Karşılıklı Gol_Yok', 99)
        kgvar = o.get('Karşılıklı Gol_Var', 0)
        alt = o.get('Alt/Üst 2.5_Alt', 99)
        ust = o.get('Alt/Üst 2.5_Üst', 0)
        
        if k.get('ms1_min') is not None and not (k['ms1_min'] <= ms1 <= k['ms1_max']): return False
        if k.get('ms2_min') is not None and not (k['ms2_min'] <= ms2 <= k['ms2_max']): return False
        
        if k['kg_fav'] == 'var' and kgvar >= kgyok: return False
        if k['kg_fav'] == 'yok' and kgyok >= kgvar: return False
        
        if k['au_fav'] == 'alt' and alt >= ust: return False
        if k['au_fav'] == 'ust' and ust >= alt: return False
        
        # İkincil Kilit Kontrolü
        ikincil = k.get('ikincil_kilitler', {})
        if ikincil:
            for lock_key, lock_range in ikincil.items():
                val = o.get(lock_key)
                if val is None: return False
                if not (lock_range['min'] <= val <= lock_range['max']): return False
        
        return True

    updates = 0

    for kural in lig_kurallari:
        rule_code = kural['kural_kodu']
        
        scores = []
        iy_results = []
        kg_results = []
        
        # Bu kurala uyan tüm maçları bul
        for m in matches:
            lig = m.get('lig', '').strip()
            o = m.get('oranlar', {})
            if match_rule(o, lig, kural):
                ev = m.get('skor_ev')
                dep = m.get('skor_dep')
                iy_ev = m.get('skor_1y_ev')
                iy_dep = m.get('skor_1y_dep')
                
                if ev is not None and dep is not None:
                    # Skor paterni
                    scores.append(f"{ev}-{dep}")
                    
                    # KG Paterni
                    if ev > 0 and dep > 0:
                        kg_results.append("KG Var")
                    else:
                        kg_results.append("KG Yok")
                        
                    # IY Paterni
                    if iy_ev is not None and iy_dep is not None:
                        if iy_ev > iy_dep: iy_results.append("IY 1")
                        elif iy_ev == iy_dep: iy_results.append("IY 0")
                        else: iy_results.append("IY 2")
        
        total_matches = len(scores)
        if total_matches == 0: continue
        
        patterns = {}
        
        # Dominant Skor
        score_counts = Counter(scores)
        top_score, top_score_count = score_counts.most_common(1)[0]
        if top_score_count / total_matches >= 0.40: # En az %40 ağırlık
            patterns['En Çok Gelen Skor'] = f"{top_score} (%{round(top_score_count / total_matches * 100, 1)})"
            
        # Dominant KG
        kg_counts = Counter(kg_results)
        top_kg, top_kg_count = kg_counts.most_common(1)[0]
        if top_kg_count / total_matches >= 0.75: # En az %75 ağırlık
            patterns['KG Karakteri'] = f"{top_kg} (%{round(top_kg_count / total_matches * 100, 1)})"
            
        # Dominant IY
        iy_counts = Counter(iy_results)
        top_iy, top_iy_count = iy_counts.most_common(1)[0]
        if top_iy_count / total_matches >= 0.60: # En az %60 ağırlık
            patterns['İlk Yarı Sonucu'] = f"{top_iy} (%{round(top_iy_count / total_matches * 100, 1)})"
            
        if patterns:
            kural['alt_patternler'] = patterns
            updates += 1
            print(f"Kural {rule_code} için alt patternler çıkarıldı: {patterns}")

    if updates > 0:
        with open(RULES_PATH, 'w', encoding='utf-8') as f:
            json.dump(lig_kurallari, f, ensure_ascii=False, indent=4)
        print(f"\nToplam {updates} kurala Alt Patternler (DNA) işlendi!")
    else:
        print("\nHiçbir kural için dominant bir alt pattern bulunamadı.")

if __name__ == "__main__":
    extract_sub_patterns()
