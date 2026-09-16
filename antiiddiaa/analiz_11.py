import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

ev_beraberlik_maclari = []
dep_kazanan_maclar = []

for mac in matches:
    od = mac.get('oranlar', {})
    alt25 = od.get('Alt/Üst 2.5_Alt', 99)
    ust25 = od.get('Alt/Üst 2.5_Üst', 99)
    ms2_alt = od.get('Maç Sonucu ve Alt/Üst 2.5_2 ve Alt', 99)
    ms2_ust = od.get('Maç Sonucu ve Alt/Üst 2.5_2 ve Üst', 99)
    ms2 = od.get('Maç Sonucu_2', 99)
    ms1 = od.get('Maç Sonucu_1', 99)
    
    iy_ms_11 = od.get('İlk Yarı / Maç Sonucu_1/1', 99)
    iy_ms_22 = od.get('İlk Yarı / Maç Sonucu_2/2', 99)
    
    sev = mac.get('skor_ev', -1)
    sdep = mac.get('skor_dep', -1)
    
    if alt25 <= 1.70 and alt25 < ust25 and ms2_ust < ms2_alt and ms2_ust != 99 and ms2 <= 1.70 and sev >= 0:
        data = {
            'ms1': ms1, 'ms2': ms2, 'iy_ms_11': iy_ms_11, 'iy_ms_22': iy_ms_22,
            'idx': mac.get('index', '?'), 'skor': f"{sev}-{sdep}"
        }
        if sev >= sdep:
            ev_beraberlik_maclari.append(data)
        else:
            dep_kazanan_maclar.append(data)

def avg(lst, key):
    valid = [x[key] for x in lst if x[key] != 99]
    if not valid: return 0
    return sum(valid)/len(valid)

print("1X 1/1 Ortalamasi:", round(avg(ev_beraberlik_maclari, 'iy_ms_11'), 3))
print("MS2 1/1 Ortalamasi:", round(avg(dep_kazanan_maclar, 'iy_ms_11'), 3))

print("\n1X Ornekler (1/1):")
for x in ev_beraberlik_maclari[:10]: print(f"MS1: {x['ms1']}, 1/1: {x['iy_ms_11']}")
print("\nMS2 Ornekler (1/1):")
for x in dep_kazanan_maclar[:10]: print(f"MS1: {x['ms1']}, 1/1: {x['iy_ms_11']}")
