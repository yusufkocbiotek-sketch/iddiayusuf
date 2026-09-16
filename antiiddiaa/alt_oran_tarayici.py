import json
import os
from collections import defaultdict

def scan_secondary_odds():
    JSON_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json'
    RULES_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\lig_kurallari.json'

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        matches = json.load(f)['matches']

    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        lig_kurallari = json.load(f)

    primary_keys = {
        'Maç Sonucu_1', 'Maç Sonucu_2', 
        'Karşılıklı Gol_Yok', 'Karşılıklı Gol_Var',
        'Alt/Üst 2.5_Alt', 'Alt/Üst 2.5_Üst'
    }

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
        
        return True

    # Kural bazında alt oran istatistiklerini tut
    rule_stats = {}
    
    for kural in lig_kurallari:
        rule_code = kural['kural_kodu']
        rule_stats[rule_code] = defaultdict(list)
        
        # Bu kurala uyan tüm maçları bul
        for m in matches:
            lig = m.get('lig', '').strip()
            o = m.get('oranlar', {})
            if match_rule(o, lig, kural):
                # Eşleşen maçtaki ikincil oranları topla
                for key, val in o.items():
                    if key not in primary_keys:
                        rule_stats[rule_code][key].append(val)

    # Anlamlı İkincil Kilitleri Belirle
    updates = 0
    for kural in lig_kurallari:
        rule_code = kural['kural_kodu']
        stats = rule_stats.get(rule_code, {})
        
        # Her alt oran için
        best_lock_key = None
        best_lock_min = 0
        best_lock_max = 99
        
        # Sadece IY0, IY1.5 Alt, Maç Sonucu_0, Dep 0.5 Alt/Üst gibi kritik anahtarlara odaklanalım
        critical_keys = ['1. Yarı Sonucu_0', 'Maç Sonucu_0', '1. Yarı Alt/Üst 1.5_Alt', 'Deplasman Alt/Üst 0.5_Alt', 'Deplasman Alt/Üst 0.5_Üst', 'Ev Sahibi Alt/Üst 1.5_Üst']
        
        found_locks = {}
        for key in critical_keys:
            if key in stats:
                vals = stats[key]
                # Eğer bu oran, eşleşen maçların en az %80'inde açılmışsa
                if len(vals) >= (kural['toplam_mac'] * 0.8):
                    min_val = min(vals)
                    max_val = max(vals)
                    # Çok geniş bir yelpaze değilse (Örn: Hep 1.80-2.20 arasındaysa, 1.50-4.50 gibi dağınık değilse)
                    if (max_val - min_val) <= 0.60:
                        # Bu anlamlı bir kilit olabilir!
                        # Küçük tolerans payı bırakalım
                        lock_min = round(min_val - 0.05, 2)
                        lock_max = round(max_val + 0.05, 2)
                        found_locks[key] = {"min": lock_min, "max": lock_max}
        
        if found_locks:
            kural['ikincil_kilitler'] = found_locks
            updates += 1
            print(f"Kural {rule_code} için ikincil kilitler bulundu: {found_locks}")

    if updates > 0:
        with open(RULES_PATH, 'w', encoding='utf-8') as f:
            json.dump(lig_kurallari, f, ensure_ascii=False, indent=4)
        print(f"\nToplam {updates} kurala ikincil kilitler entegre edildi ve lig_kurallari.json güncellendi!")
    else:
        print("\nHiçbir kural için stabil bir ikincil kilit bulunamadı. (Oranlar çok dağınık veya veriler eksik)")

if __name__ == "__main__":
    scan_secondary_odds()
