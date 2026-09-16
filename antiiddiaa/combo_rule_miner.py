import json
from collections import defaultdict

def mine_combo_rules():
    JSON_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json'
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        matches = json.load(f)['matches']
        
    lig_maclari = defaultdict(list)
    for m in matches:
        lig = m.get('lig', '').strip()
        if lig: lig_maclari[lig].append(m)
        
    combo_rules = []
    
    # Hedefler
    def check_hedef(m, hedef):
        ev = m.get('skor_ev', 0)
        dep = m.get('skor_dep', 0)
        if hedef == 'MS 1': return ev > dep
        if hedef == 'MS 2': return ev < dep
        if hedef == 'MS 0': return ev == dep
        if hedef == 'ALT': return (ev + dep) < 3
        if hedef == 'UST': return (ev + dep) >= 3
        if hedef == 'KG VAR': return ev > 0 and dep > 0
        if hedef == 'KG YOK': return ev == 0 or dep == 0
        return False

    # Filtreler (Multi-Factor)
    # Temel Filtre: MS1 veya MS2 bandı
    base_bands = [
        {'isim': 'MS1 Çok Ağır Fav (1.10-1.30)', 'cond': lambda o: 1.10 <= o.get('Maç Sonucu_1', 99) <= 1.30},
        {'isim': 'MS1 Ağır Fav (1.30-1.50)', 'cond': lambda o: 1.30 <= o.get('Maç Sonucu_1', 99) <= 1.50},
        {'isim': 'MS1 Fav (1.50-1.80)', 'cond': lambda o: 1.50 <= o.get('Maç Sonucu_1', 99) <= 1.80},
        {'isim': 'MS2 Çok Ağır Fav (1.10-1.30)', 'cond': lambda o: 1.10 <= o.get('Maç Sonucu_2', 99) <= 1.30},
        {'isim': 'MS2 Ağır Fav (1.30-1.50)', 'cond': lambda o: 1.30 <= o.get('Maç Sonucu_2', 99) <= 1.50},
        {'isim': 'MS2 Fav (1.50-1.80)', 'cond': lambda o: 1.50 <= o.get('Maç Sonucu_2', 99) <= 1.80},
    ]
    
    # İnce Filtreler (Tuzak Kırıcılar)
    fine_filters = [
        {'isim': '+ KG VAR Favori', 'cond': lambda o: o.get('Karşılıklı Gol_Var', 99) < o.get('Karşılıklı Gol_Yok', 99)},
        {'isim': '+ KG YOK Favori', 'cond': lambda o: o.get('Karşılıklı Gol_Yok', 99) < o.get('Karşılıklı Gol_Var', 99)},
        {'isim': '+ ÜST Favori', 'cond': lambda o: o.get('Alt/Üst 2.5_Üst', 99) < o.get('Alt/Üst 2.5_Alt', 99)},
        {'isim': '+ ALT Favori', 'cond': lambda o: o.get('Alt/Üst 2.5_Alt', 99) < o.get('Alt/Üst 2.5_Üst', 99)},
        {'isim': '+ İY 0 Tuzağı (İY 0 Çok Düşük < 2.10)', 'cond': lambda o: o.get('1. Yarı Sonucu_0', 99) < 2.10},
        {'isim': '+ İY 1 Kesin (İY1 < İY2 ve İY1 < İY0)', 'cond': lambda o: o.get('1. Yarı Sonucu_1', 99) < o.get('1. Yarı Sonucu_0', 99) and o.get('1. Yarı Sonucu_1', 99) < o.get('1. Yarı Sonucu_2', 99)},
        {'isim': '+ İY 2 Kesin (İY2 < İY1 ve İY2 < İY0)', 'cond': lambda o: o.get('1. Yarı Sonucu_2', 99) < o.get('1. Yarı Sonucu_0', 99) and o.get('1. Yarı Sonucu_2', 99) < o.get('1. Yarı Sonucu_1', 99)},
    ]
    
    targets = ['MS 1', 'MS 2', 'ALT', 'UST', 'KG VAR', 'KG YOK']
    
    rule_id_counter = 1
    
    for lig, maclar in lig_maclari.items():
        if len(maclar) < 50: continue # Ligi geç
        
        for base in base_bands:
            base_matches = [m for m in maclar if base['cond'](m.get('oranlar', {}))]
            if len(base_matches) < 10: continue
            
            for target in targets:
                # Önce sadece base ile başarıya bakalım
                success = sum(1 for m in base_matches if check_hedef(m, target))
                rate = success / len(base_matches)
                
                if rate >= 0.90 and len(base_matches) >= 10:
                    # Zaten çok iyi bir kural (Base Rule)
                    combo_rules.append({
                        'kural_kodu': f"COMBO-{rule_id_counter}",
                        'lig': lig,
                        'hedef': target,
                        'filtre_kombinasyonu': base['isim'],
                        'mac_sayisi': len(base_matches),
                        'basari_orani': round(rate * 100, 1)
                    })
                    rule_id_counter += 1
                
                elif 0.60 <= rate < 0.90:
                    # Yetersiz başarı. Şimdi KARAR AĞACI devreye giriyor (İnce Filtre ekle)
                    for f1 in fine_filters:
                        f1_matches = [m for m in base_matches if f1['cond'](m.get('oranlar', {}))]
                        if len(f1_matches) < 10: continue
                        
                        success_f1 = sum(1 for m in f1_matches if check_hedef(m, target))
                        rate_f1 = success_f1 / len(f1_matches)
                        
                        if rate_f1 >= 0.90:
                            combo_rules.append({
                                'kural_kodu': f"COMBO-{rule_id_counter}",
                                'lig': lig,
                                'hedef': target,
                                'filtre_kombinasyonu': f"{base['isim']} {f1['isim']}",
                                'mac_sayisi': len(f1_matches),
                                'basari_orani': round(rate_f1 * 100, 1)
                            })
                            rule_id_counter += 1
                        
                        elif 0.70 <= rate_f1 < 0.90:
                            # Hala yetmedi, BİR FİLTRE DAHA EKLE (Deep Combo)
                            for f2 in fine_filters:
                                if f1 == f2: continue
                                f2_matches = [m for m in f1_matches if f2['cond'](m.get('oranlar', {}))]
                                if len(f2_matches) < 10: continue
                                
                                success_f2 = sum(1 for m in f2_matches if check_hedef(m, target))
                                rate_f2 = success_f2 / len(f2_matches)
                                
                                if rate_f2 >= 0.90:
                                    combo_rules.append({
                                        'kural_kodu': f"COMBO-{rule_id_counter}",
                                        'lig': lig,
                                        'hedef': target,
                                        'filtre_kombinasyonu': f"{base['isim']} {f1['isim']} {f2['isim']}",
                                        'mac_sayisi': len(f2_matches),
                                        'basari_orani': round(rate_f2 * 100, 1)
                                    })
                                    rule_id_counter += 1
                                    
    # Raporlama
    # Aynı lig/hedef için benzer kuralları elemeye çalışalım (basitçe sıralayalım)
    combo_rules = sorted(combo_rules, key=lambda x: x['basari_orani'], reverse=True)
    
    with open('combo_kurallari.json', 'w', encoding='utf-8') as f:
        json.dump(combo_rules, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Sistem başarıyla Multi-Factor (Çoklu Filtre) taraması yaptı.")
    print(f"✅ Tam {len(combo_rules)} adet yeni KOMBO ŞABLONU bulundu ve combo_kurallari.json dosyasına kaydedildi.")
    
    # En iyi 5 kuralı ekrana bas
    print("\n🏆 EN İYİ 5 KOMBO ŞABLONU:")
    for r in combo_rules[:5]:
        print(f"[{r['kural_kodu']}] LİG: {r['lig']} | Şablon: {r['filtre_kombinasyonu']} -> HEDEF: {r['hedef']} (Başarı: %{r['basari_orani']}, Maç: {r['mac_sayisi']})")

if __name__ == "__main__":
    mine_combo_rules()
