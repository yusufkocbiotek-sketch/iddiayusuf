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
    iy_ms1 = od.get('İlk Yarı Sonucu_1', 99)
    iy_05_alt = od.get('İlk Yarı Alt/Üst 0.5_Alt', 99)
    kg_var = od.get('Karşılıklı Gol_Var', 99)
    
    sev = mac.get('skor_ev', -1)
    sdep = mac.get('skor_dep', -1)
    
    if alt25 <= 1.70 and alt25 < ust25 and ms2_ust < ms2_alt and ms2_ust != 99 and ms2 <= 1.70 and sev >= 0:
        data = {
            'ms1': ms1, 'ms2': ms2, 'iy_ms1': iy_ms1,
            'fark_ms1': iy_ms1 - ms1 if iy_ms1 != 99 and ms1 != 99 else 99,
            'iy_05_alt': iy_05_alt, 'kg_var': kg_var,
            'idx': mac.get('index', '?'), 'skor': f"{sev}-{sdep}"
        }
        if sev >= sdep:
            ev_beraberlik_maclari.append(data)
        else:
            dep_kazanan_maclar.append(data)

print("=== 1X BITEN (SURPRIZ) MACLARIN OZELLIKLERI ===")
for k in ev_beraberlik_maclari:
    print(f"IDX:{k['idx']} Skor:{k['skor']} MS1:{k['ms1']:.2f} IY_MS1:{k['iy_ms1']:.2f} (Fark:{k['fark_ms1']:.2f}) IY0.5Alt:{k['iy_05_alt']} KGVar:{k['kg_var']}")

print("\n=== MS2 BITEN (NORMAL) MACLARIN OZELLIKLERI ===")
for k in dep_kazanan_maclar[:15]:
    print(f"IDX:{k['idx']} Skor:{k['skor']} MS1:{k['ms1']:.2f} IY_MS1:{k['iy_ms1']:.2f} (Fark:{k['fark_ms1']:.2f}) IY0.5Alt:{k['iy_05_alt']} KGVar:{k['kg_var']}")

def avg(lst, key):
    valid = [x[key] for x in lst if x[key] != 99]
    if not valid: return 0
    return sum(valid)/len(valid)

print("\n--- ORTALAMALAR ---")
print("1X Fark MS1 (IY MS1 - MS1):", round(avg(ev_beraberlik_maclari, 'fark_ms1'), 3))
print("MS2 Fark MS1 (IY MS1 - MS1):", round(avg(dep_kazanan_maclar, 'fark_ms1'), 3))
print("1X IY 0.5 Alt:", round(avg(ev_beraberlik_maclari, 'iy_05_alt'), 3))
print("MS2 IY 0.5 Alt:", round(avg(dep_kazanan_maclar, 'iy_05_alt'), 3))
print("1X KG Var:", round(avg(ev_beraberlik_maclari, 'kg_var'), 3))
print("MS2 KG Var:", round(avg(dep_kazanan_maclar, 'kg_var'), 3))
