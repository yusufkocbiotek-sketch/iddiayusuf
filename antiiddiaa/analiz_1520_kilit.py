import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import Rule1520

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

found = []
for mac in matches:
    odds = mac.get('oranlar', {})
    trigger, _ = Rule1520.evaluate(odds)
    if trigger:
        sev = mac.get('skor_ev', -1)
        sdep = mac.get('skor_dep', -1)
        
        iy_05_ust = odds.get('İlk Yarı Alt/Üst 0.5_Üst', 99)
        if iy_05_ust == 99: iy_05_ust = odds.get('1. Yarı Altı/Üstü 0.5_Üst', 99)
        
        iy_15_alt = odds.get('İlk Yarı Alt/Üst 1.5_Alt', 99)
        if iy_15_alt == 99: iy_15_alt = odds.get('1. Yarı Altı/Üstü 1.5_Alt', 99)
        
        iy_ms_00 = odds.get('İlk Yarı / Maç Sonucu_0/0', 99)
        iy_0 = odds.get('İlk Yarı Sonucu_0', 99)
        
        if sev >= 0:
            found.append({
                'skor': f"{sev}-{sdep}",
                'toplam_gol': sev+sdep,
                'iy_05_ust': iy_05_ust,
                'iy_15_alt': iy_15_alt,
                'iy_ms_00': iy_ms_00,
                'iy_0': iy_0,
                'idx': mac.get('index')
            })

print(f"Toplam 1520 Mac (2.5 Ust <= 1.50 ve Takim 1.5 Altlar Favori): {len(found)}")
alt = [x for x in found if x['toplam_gol'] <= 2]
print(f"Tümünde Alt (Basari): {len(alt)} ({(len(alt)/len(found))*100:.1f}%)")

# Deneme 1: IY 0.5 Ust >= 1.35 (Erken gol beklenmiyorsa)
f_deneme1 = [x for x in found if x['iy_05_ust'] >= 1.35 and x['iy_05_ust'] != 99.0]
alt_deneme1 = [x for x in f_deneme1 if x['toplam_gol'] <= 2]
if f_deneme1:
    print(f"\nFiltre 1 (IY 0.5 Ust >= 1.35) - Toplam: {len(f_deneme1)}")
    print(f"Alt (Basari): {len(alt_deneme1)} ({(len(alt_deneme1)/len(f_deneme1))*100:.1f}%)")

# Deneme 2: IY 1.5 Alt <= 1.35
f_deneme2 = [x for x in found if x['iy_15_alt'] <= 1.35 and x['iy_15_alt'] != 99.0]
alt_deneme2 = [x for x in f_deneme2 if x['toplam_gol'] <= 2]
if f_deneme2:
    print(f"\nFiltre 2 (IY 1.5 Alt <= 1.35) - Toplam: {len(f_deneme2)}")
    print(f"Alt (Basari): {len(alt_deneme2)} ({(len(alt_deneme2)/len(f_deneme2))*100:.1f}%)")

# Deneme 3: Kesin Kilit (IY0 <= 2.20 & IY_MS_00 <= 6.00)
f_deneme3 = [x for x in found if x['iy_0'] <= 2.30 and x['iy_ms_00'] <= 6.50 and x['iy_0'] != 99.0 and x['iy_ms_00'] != 99.0]
alt_deneme3 = [x for x in f_deneme3 if x['toplam_gol'] <= 2]
if f_deneme3:
    print(f"\nFiltre 3 (IY0 <= 2.30 & IY_MS_00 <= 6.50) - Toplam: {len(f_deneme3)}")
    print(f"Alt (Basari): {len(alt_deneme3)} ({(len(alt_deneme3)/len(f_deneme3))*100:.1f}%)")
    
# Deneme 4: IY0 <= 2.10
f_deneme4 = [x for x in found if x['iy_0'] <= 2.10 and x['iy_0'] != 99.0]
alt_deneme4 = [x for x in f_deneme4 if x['toplam_gol'] <= 2]
if f_deneme4:
    print(f"\nFiltre 4 (IY0 <= 2.10) - Toplam: {len(f_deneme4)}")
    print(f"Alt (Basari): {len(alt_deneme4)} ({(len(alt_deneme4)/len(f_deneme4))*100:.1f}%)")
