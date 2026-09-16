import json
import os
from collections import defaultdict

def analyze_leagues():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)['matches']

    templates = []
    
    # --- TEMPLATE GENERATOR ---
    # 1. MS1 Bands
    ms1_bands = [
        (1.10, 1.30), (1.30, 1.50), (1.50, 1.70), (1.70, 2.00), (2.00, 2.30), (2.30, 2.80)
    ]
    # 2. KG Favourites
    kg_favs = ["var", "yok", None]
    # 3. AU Favourites
    au_favs = ["alt", "ust", None]
    
    tid = 1
    for b_min, b_max in ms1_bands:
        for k in kg_favs:
            for a in au_favs:
                # Target: KG Var
                templates.append({"id": f"T{tid}", "ms_min": b_min, "ms_max": b_max, "ms2_min": None, "ms2_max": None, "kg_fav": k, "au_fav": a, "target": "KG Var"})
                tid += 1
                # Target: KG Yok
                templates.append({"id": f"T{tid}", "ms_min": b_min, "ms_max": b_max, "ms2_min": None, "ms2_max": None, "kg_fav": k, "au_fav": a, "target": "KG Yok"})
                tid += 1
                # Target: 2.5 Alt
                templates.append({"id": f"T{tid}", "ms_min": b_min, "ms_max": b_max, "ms2_min": None, "ms2_max": None, "kg_fav": k, "au_fav": a, "target": "2.5 Alt"})
                tid += 1
                # Target: 2.5 Üst
                templates.append({"id": f"T{tid}", "ms_min": b_min, "ms_max": b_max, "ms2_min": None, "ms2_max": None, "kg_fav": k, "au_fav": a, "target": "2.5 Üst"})
                tid += 1
                # Target: MS 1
                templates.append({"id": f"T{tid}", "ms_min": b_min, "ms_max": b_max, "ms2_min": None, "ms2_max": None, "kg_fav": k, "au_fav": a, "target": "MS 1"})
                tid += 1
                # Target: MS 0
                templates.append({"id": f"T{tid}", "ms_min": b_min, "ms_max": b_max, "ms2_min": None, "ms2_max": None, "kg_fav": k, "au_fav": a, "target": "MS 0"})
                tid += 1

    # Add Deplasman Favori (MS2 Bands)
    ms2_bands = [
        (1.30, 1.60), (1.60, 2.00), (2.00, 2.40)
    ]
    for b_min, b_max in ms2_bands:
        for k in kg_favs:
            for a in au_favs:
                templates.append({"id": f"T{tid}", "ms_min": None, "ms_max": None, "ms2_min": b_min, "ms2_max": b_max, "kg_fav": k, "au_fav": a, "target": "MS 2"})
                tid += 1
                templates.append({"id": f"T{tid}", "ms_min": None, "ms_max": None, "ms2_min": b_min, "ms2_max": b_max, "kg_fav": k, "au_fav": a, "target": "2.5 Alt"})
                tid += 1
                templates.append({"id": f"T{tid}", "ms_min": None, "ms_max": None, "ms2_min": b_min, "ms2_max": b_max, "kg_fav": k, "au_fav": a, "target": "2.5 Üst"})
                tid += 1


    results = defaultdict(lambda: defaultdict(lambda: {'s': 0, 'f': 0}))

    for m in matches:
        o = m.get('oranlar')
        if not o: continue
        
        lig = m.get('lig', '').strip()
        if not lig or lig == 'Bilinmeyen': continue
        
        ms1 = o.get('Maç Sonucu_1')
        ms2 = o.get('Maç Sonucu_2')
        kgyok = o.get('Karşılıklı Gol_Yok', 9)
        kgvar = o.get('Karşılıklı Gol_Var', 0)
        alt = o.get('Alt/Üst 2.5_Alt', 9)
        ust = o.get('Alt/Üst 2.5_Üst', 0)
        
        ev = m.get('skor_ev', 0)
        dep = m.get('skor_dep', 0)
        
        for t in templates:
            # Check MS1
            if t['ms_min'] is not None:
                if ms1 is None or not (t['ms_min'] <= ms1 <= t['ms_max']): continue
            # Check MS2
            if t['ms2_min'] is not None:
                if ms2 is None or not (t['ms2_min'] <= ms2 <= t['ms2_max']): continue
                
            # Check KG condition
            kg_match = True
            if t['kg_fav'] == 'var' and kgvar >= kgyok: kg_match = False
            if t['kg_fav'] == 'yok' and kgyok >= kgvar: kg_match = False
            
            # Check Alt/Ust condition
            au_match = True
            if t['au_fav'] == 'alt' and alt >= ust: au_match = False
            if t['au_fav'] == 'ust' and ust >= alt: au_match = False
            
            if kg_match and au_match:
                success = False
                if t['target'] == 'KG Var' and ev > 0 and dep > 0: success = True
                elif t['target'] == 'KG Yok' and (ev == 0 or dep == 0): success = True
                elif t['target'] == '2.5 Alt' and (ev + dep < 3): success = True
                elif t['target'] == '2.5 Üst' and (ev + dep >= 3): success = True
                elif t['target'] == 'MS 1' and ev > dep: success = True
                elif t['target'] == 'MS 0' and ev == dep: success = True
                elif t['target'] == 'MS 2' and dep > ev: success = True
                
                if success:
                    results[lig][t['id']]['s'] += 1
                else:
                    results[lig][t['id']]['f'] += 1

    generated_rules = []
    rule_counter = 1
    
    # Aynı ligde aynı sonucu üreten çok benzer kuralları elemek için
    lig_target_hashes = set()

    for lig, t_results in results.items():
        for t_id, data in t_results.items():
            total = data['s'] + data['f']
            if total >= 10: # En az 10 maç
                win_rate = data['s'] / total * 100
                if win_rate >= 90.0:
                    t_info = next(item for item in templates if item["id"] == t_id)
                    
                    # Aynı lig, aynı hedef, benzer başarı oranındaki dublikatları önle
                    hash_str = f"{lig}_{t_info['target']}_{total}_{win_rate}"
                    if hash_str in lig_target_hashes: continue
                    lig_target_hashes.add(hash_str)
                    
                    rule = {
                        "kural_kodu": f"{lig.replace(' ', '')}-{rule_counter:02d}",
                        "lig": lig,
                        "ms1_min": t_info['ms_min'],
                        "ms1_max": t_info['ms_max'],
                        "ms2_min": t_info['ms2_min'],
                        "ms2_max": t_info['ms2_max'],
                        "kg_fav": t_info['kg_fav'],
                        "au_fav": t_info['au_fav'],
                        "hedef": t_info['target'],
                        "basari_orani": round(win_rate, 2),
                        "toplam_mac": total
                    }
                    generated_rules.append(rule)
                    rule_counter += 1

    import math
    generated_rules.sort(key=lambda x: x['basari_orani'] * math.log(x['toplam_mac']), reverse=True)

    print(f"Toplam {len(generated_rules)} adet LİG BAZLI (%90+ Başarı) kural üretildi!")
    
    output_path = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\lig_kurallari.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(generated_rules, f, ensure_ascii=False, indent=4)
        
    print(f"Kurallar {output_path} adresine kaydedildi.")

if __name__ == "__main__":
    analyze_leagues()
