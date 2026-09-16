import json

def load_data():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        return json.load(f)['matches']

def get_odd(odds, keys):
    for k in keys:
        if k in odds and odds[k] is not None:
            return float(odds[k])
    return 99.0

def mine_more_anomalies(matches):
    # Kural G: İlk Yarı Asla Gol Olmaz Algısı
    # Ilk Yari KG Yok cok dusuk (<= 1.10) ama Mac Sonu KG Var da cok dusuk (<= 1.60)
    kural_g = []
    for mac in matches:
        odds = mac.get('oranlar', {})
        iy_kg_yok = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Yok"])
        ms_kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ms_ust_15 = get_odd(odds, ["Alt/Üst 1.5_Üst", "Altı/Üstü 1.5_Üst"])
        
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        iy_sev = mac.get('skor_1y_ev', -1)
        iy_sdep = mac.get('skor_1y_dep', -1)
        
        if iy_kg_yok <= 1.10 and ms_kg_var <= 1.60 and sev >= 0:
            kural_g.append({
                'skor': f"{sev}-{sdep}",
                'iy_skor': f"{iy_sev}-{iy_sdep}",
                'iy_kg_var': iy_sev > 0 and iy_sdep > 0,
                'ms_kg_var': sev > 0 and sdep > 0
            })
            
    if kural_g:
        toplam = len(kural_g)
        iy_kg_hit = sum(1 for x in kural_g if x['iy_kg_var'])
        ms_kg_hit = sum(1 for x in kural_g if x['ms_kg_var'])
        print(f"\n[G] KOMBİNASYON: IY KG Yok (<= 1.10) & MS KG Var (<= 1.60)")
        print(f"Toplam Maç: {toplam}")
        print(f"İlk Yarı KG Var Biten: {iy_kg_hit} ({(iy_kg_hit/toplam)*100:.1f}%)")
        print(f"Maç Sonu KG Var Biten: {ms_kg_hit} ({(ms_kg_hit/toplam)*100:.1f}%)")

if __name__ == "__main__":
    matches = load_data()
    mine_more_anomalies(matches)
