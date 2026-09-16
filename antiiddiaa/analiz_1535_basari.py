import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

found = []
for mac in matches:
    od = mac.get('oranlar', {})
    alt25 = od.get('Alt/Üst 2.5_Alt', 99)
    ust25 = od.get('Alt/Üst 2.5_Üst', 99)
    ms2_alt = od.get('Maç Sonucu ve Alt/Üst 2.5_2 ve Alt', 99)
    ms2_ust = od.get('Maç Sonucu ve Alt/Üst 2.5_2 ve Üst', 99)
    ms2 = od.get('Maç Sonucu_2', 99)
    ms1 = od.get('Maç Sonucu_1', 99)
    iy_ms1 = od.get('İlk Yarı Sonucu_1', 99)
    
    sev = mac.get('skor_ev', -1)
    sdep = mac.get('skor_dep', -1)
    
    if alt25 <= 1.70 and alt25 < ust25 and ms2_ust < ms2_alt and ms2_ust != 99.0 and ms2 <= 1.70:
        if ms1 >= 4.50 and iy_ms1 != 99.0 and (iy_ms1 - ms1) <= 0.65 and sev >= 0:
            found.append({
                'skor': f"{sev}-{sdep}",
                'ms2_kazandi': sdep > sev,
                'idx': mac.get('index', '?')
            })

ev_kazanan = [x for x in found if not x['ms2_kazandi']]
print(f"Toplam Match: {len(found)}")
print(f"1X Cifte Sans Tutan: {len(ev_kazanan)} ({(len(ev_kazanan)/max(1, len(found)))*100:.1f}%)")
print(f"MS2 (Rule Failed): {len(found) - len(ev_kazanan)} ({(1 - len(ev_kazanan)/max(1, len(found)))*100:.1f}%)")
