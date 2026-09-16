import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

found_low = []
found_high = []

for mac in matches:
    od = mac.get('oranlar', {})
    ms0 = od.get('Maç Sonucu_0', 99)
    alt25 = od.get('Alt/Üst 2.5_Alt', 99)
    if alt25 == 99: alt25 = od.get('Altı/Üstü 2.5_Alt', 99)
    
    iy_05_ust = od.get('İlk Yarı Alt/Üst 0.5_Üst', 99)
    if iy_05_ust == 99: iy_05_ust = od.get('1. Yarı Altı/Üstü 0.5_Üst', 99)
    
    sev = mac.get('skor_ev', -1)
    sdep = mac.get('skor_dep', -1)
    
    if alt25 <= 1.55 and ms0 <= 2.85 and ms0 != 99.0 and alt25 != 99.0 and sev >= 0:
        toplam_gol = sev + sdep
        data = {'skor': f"{sev}-{sdep}", 'toplam_gol': toplam_gol, 'idx': mac.get('index', '?')}
        if iy_05_ust <= 1.35:
            found_low.append(data)
        elif iy_05_ust >= 1.45 and iy_05_ust != 99:
            found_high.append(data)

print("--- IY 0.5 UST <= 1.35 (Erken Gol Beklentisi) ---")
alt = [x for x in found_low if x['toplam_gol'] <= 2]
print(f"Toplam: {len(found_low)}, Alt (Basari): {len(alt)} ({(len(alt)/max(1,len(found_low)))*100:.1f}%)")

print("\n--- IY 0.5 UST >= 1.45 (Gercek Kisir Beklenti) ---")
alt_high = [x for x in found_high if x['toplam_gol'] <= 2]
print(f"Toplam: {len(found_high)}, Alt (Basari): {len(alt_high)} ({(len(alt_high)/max(1,len(found_high)))*100:.1f}%)")
