import json

# Canlı Maç Verisi
live_match = {
    "lig": "ŞMP", # Şampiyonlar Ligi
    "oranlar": {
        "Maç Sonucu_1": 6.24,
        "Maç Sonucu_0": 4.2,
        "Maç Sonucu_2": 1.31,
        "Çifte Şans_1 ve 0": 2.42,
        "Çifte Şans_1 ve 2": 1.09,
        "1. Yarı Sonucu_1": 6.27,
        "1. Yarı Sonucu_0": 2.28,
        "1. Yarı Sonucu_2": 1.78,
        "2. Yarı Sonucu_1": 5.56,
        "2. Yarı Sonucu_0": 2.64,
        "2. Yarı Sonucu_2": 1.66,
        "1. Yarı Karşılıklı Gol_Var": 4.62,
        "1. Yarı Karşılıklı Gol_Yok": 1.06,
        "1. Yarı Çifte Şans_1 ve 0": 1.65,
        "1. Yarı Çifte Şans_1 ve 2": 1.38,
        "Karşılıklı Gol_Var": 1.82,
        "Karşılıklı Gol_Yok": 1.64,
        "2. Yarı Karşılıklı Gol_Var": 3.64,
        "2. Yarı Karşılıklı Gol_Yok": 1.13,
        "Alt/Üst 0.5_Alt": 11.25,
        "Alt/Üst 1.5_Alt": 3.62,
        "Alt/Üst 1.5_Üst": 1.13,
        "Alt/Üst 2.5_Alt": 1.85,
        "Alt/Üst 2.5_Üst": 1.62,
        "Alt/Üst 3.5_Alt": 1.26,
        "Alt/Üst 3.5_Üst": 2.72,
        "Ev Sahibi Alt/Üst 0.5_Alt": 1.88,
        "Ev Sahibi Alt/Üst 0.5_Üst": 1.59,
        "Ev Sahibi Alt/Üst 1.5_Alt": 1.07,
        "Ev Sahibi Alt/Üst 1.5_Üst": 4.39,
        "Deplasman Alt/Üst 0.5_Alt": 5.96,
        "Deplasman Alt/Üst 1.5_Alt": 2.14,
        "Deplasman Alt/Üst 1.5_Üst": 1.44,
        "Deplasman Alt/Üst 2.5_Alt": 1.3,
        "Deplasman Alt/Üst 2.5_Üst": 2.56,
        "1. Yarı Alt/Üst 0.5_Alt": 3.02,
        "1. Yarı Alt/Üst 0.5_Üst": 1.21,
        "1. Yarı Alt/Üst 1.5_Alt": 1.36,
        "1. Yarı Alt/Üst 1.5_Üst": 2.35,
        "Ev Sahibi 1. Yarı Altı/Üstü 0.5_Alt": 1.23,
        "Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst": 2.88,
        "Deplasman 1. Yarı Altı/Üstü 0.5_Alt": 2.16,
        "Deplasman 1. Yarı Altı/Üstü 0.5_Üst": 1.44
    }
}

# 1. EVRENSEL KURALLAR
def check_universal(o):
    ms1 = o.get('Maç Sonucu_1', 99)
    ms2 = o.get('Maç Sonucu_2', 99)
    kgyok = o.get('Karşılıklı Gol_Yok', 99)
    kgvar = o.get('Karşılıklı Gol_Var', 0)
    alt = o.get('Alt/Üst 2.5_Alt', 99)
    ust = o.get('Alt/Üst 2.5_Üst', 0)
    
    hits = []
    
    if 1.30 <= ms1 <= 1.45 and alt < ust:
        hits.append("T70: Ev 1.30-1.45 favori ve Alt favori -> MS1 ve 2.5 ALT beklenir.")
    if 1.30 <= ms2 <= 1.45 and alt < ust:
        hits.append("T68: Dep 1.30-1.45 favori ve Alt favori -> MS2 ve 2.5 ALT beklenir.")
    if 2.30 <= ms1 <= 2.70 and kgyok < kgvar:
        hits.append("G90: Kısır Denge (Alt Makrosu) -> 2.5 ALT beklenir.")
    if 1.70 <= ms1 <= 2.00 and kgyok < kgvar and alt < ust:
        hits.append("G80: Dengeli Favori (MS1 ve 2.5 ALT) beklenir.")
        
    return hits

# 2. LİG BAZLI KESKİN NİŞANCI KURALLARI (İkincil Kilit + DNA dahil)
def check_league_rules(match):
    RULES_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\lig_kurallari.json'
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        kurallar = json.load(f)
        
    o = match['oranlar']
    ms1 = o.get('Maç Sonucu_1', 99)
    ms2 = o.get('Maç Sonucu_2', 99)
    kgyok = o.get('Karşılıklı Gol_Yok', 99)
    kgvar = o.get('Karşılıklı Gol_Var', 0)
    alt = o.get('Alt/Üst 2.5_Alt', 99)
    ust = o.get('Alt/Üst 2.5_Üst', 0)
    
    hits = []
    
    for k in kurallar:
        # Maçın ligi bizim kurallardaki liglerden biriyle örtüşüyor mu diye sadece "ŞMP" yerine, kural ligine uydurmadan oran bazında da bakabiliriz.
        # Ama önce sıkı lig filtresi uygulayalım (Şampiyonlar ligi için 'ŞMP')
        if "ŞMP" not in k['lig']:
            continue
            
        is_match = True
        
        if k.get('ms1_min') is not None and not (k['ms1_min'] <= ms1 <= k['ms1_max']): is_match = False
        if k.get('ms2_min') is not None and not (k['ms2_min'] <= ms2 <= k['ms2_max']): is_match = False
        if k['kg_fav'] == 'var' and kgvar >= kgyok: is_match = False
        if k['kg_fav'] == 'yok' and kgyok >= kgvar: is_match = False
        if k['au_fav'] == 'alt' and alt >= ust: is_match = False
        if k['au_fav'] == 'ust' and ust >= alt: is_match = False
        
        # İkincil Kilit
        ikincil = k.get('ikincil_kilitler', {})
        if ikincil:
            for lk, lval in ikincil.items():
                v = o.get(lk)
                if v is None or not (lval['min'] <= v <= lval['max']):
                    is_match = False
                    
        if is_match:
            hits.append(k)
            
    return hits

print("---- EVRENSEL KURALLAR TESTİ ----")
u_hits = check_universal(live_match['oranlar'])
for h in u_hits: print(h)
if not u_hits: print("Hiçbir Evrensel Kural (T70, vb.) bu maça uymadı.")

print("\n---- LİG KESKİN NİŞANCI TESTİ ----")
l_hits = check_league_rules(live_match)
for h in l_hits:
    print(f"KURAL: {h['kural_kodu']} | Lig: {h['lig']}")
    print(f"Beklenen Sonuç: {h['hedef']}")
    if h.get('alt_patternler'):
        print(f"DNA Patternleri: {h['alt_patternler']}")
if not l_hits: print("Şampiyonlar Ligi (ŞMP) için bu oran bantlarına sahip %90 başarı üstünde bir kural bulunamadı.")
