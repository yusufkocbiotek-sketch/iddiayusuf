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
    
    iy_0 = od.get('İlk Yarı Sonucu_0', 99)
    iy_ms_00 = od.get('İlk Yarı / Maç Sonucu_0/0', 99)
    iy_05_ust = od.get('İlk Yarı Alt/Üst 0.5_Üst', 99)
    if iy_05_ust == 99: iy_05_ust = od.get('1. Yarı Altı/Üstü 0.5_Üst', 99)
    
    sev = mac.get('skor_ev', -1)
    sdep = mac.get('skor_dep', -1)
    
    if alt25 <= 1.55 and ms0 <= 2.85 and ms0 != 99.0 and alt25 != 99.0 and sev >= 0:
        # User observation fix: Exclude matches expected to have early goals (IY 0.5 Ust <= 1.35)
        # Require strong 0/0 lock if available, or just a very weak early goal expectation.
        if iy_05_ust >= 1.42 or (iy_ms_00 <= 4.10 and iy_ms_00 != 99.0):
            toplam_gol = sev + sdep
            found.append({
                'skor': f"{sev}-{sdep}",
                'toplam_gol': toplam_gol,
                'idx': mac.get('index', '?')
            })

print(f"Toplam Gelistirilen (Erken Gol Filtreli) 1486 Mac: {len(found)}")
if found:
    alt_bitenler = [x for x in found if x['toplam_gol'] <= 2]
    print(f"Alt Biten (Basarili): {len(alt_bitenler)} ({(len(alt_bitenler)/len(found))*100:.1f}%)")
