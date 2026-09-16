import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

found = []
for mac in matches:
    od = mac.get('oranlar', {})
    ms0 = od.get('Maç Sonucu_0', 99)
    alt25 = od.get('Alt/Üst 2.5_Alt', 99)
    if alt25 == 99: alt25 = od.get('Altı/Üstü 2.5_Alt', 99)
    
    iy_05_ust = od.get('İlk Yarı Alt/Üst 0.5_Üst', 99)
    if iy_05_ust == 99: iy_05_ust = od.get('1. Yarı Altı/Üstü 0.5_Üst', 99)
    
    kg_var = od.get('Karşılıklı Gol_Var', 99)
    
    sev = mac.get('skor_ev', -1)
    sdep = mac.get('skor_dep', -1)
    
    if alt25 <= 1.55 and ms0 <= 2.85 and ms0 != 99.0 and alt25 != 99.0 and sev >= 0:
        toplam_gol = sev + sdep
        found.append({
            'skor': f"{sev}-{sdep}",
            'toplam_gol': toplam_gol,
            'iy_05_ust': iy_05_ust,
            'kg_var': kg_var,
            'idx': mac.get('index', '?'),
            'ms0': ms0,
            'alt25': alt25
        })

print(f"Toplam 1486 Tetiklenen Mac: {len(found)}")
alt_bitenler = [x for x in found if x['toplam_gol'] <= 2]
ust_bitenler = [x for x in found if x['toplam_gol'] > 2]

print(f"Alt Biten (Basarili): {len(alt_bitenler)} ({(len(alt_bitenler)/len(found))*100:.1f}%)")
print(f"Ust Biten (Basarisiz): {len(ust_bitenler)} ({(len(ust_bitenler)/len(found))*100:.1f}%)")

def avg(lst, key):
    valid = [x[key] for x in lst if x[key] != 99]
    return sum(valid)/len(valid) if valid else 0

print("\nBasarili Maclarin IY 0.5 Ust Ortalamasi:", avg(alt_bitenler, 'iy_05_ust'))
print("Basarisiz Maclarin IY 0.5 Ust Ortalamasi:", avg(ust_bitenler, 'iy_05_ust'))

print("\nBasarili Maclarin KG Var Ortalamasi:", avg(alt_bitenler, 'kg_var'))
print("Basarisiz Maclarin KG Var Ortalamasi:", avg(ust_bitenler, 'kg_var'))
