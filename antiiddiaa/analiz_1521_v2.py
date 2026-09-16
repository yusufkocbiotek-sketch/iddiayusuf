import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

found = []
for mac in matches:
    od = mac.get('oranlar', {})
    alt_25 = od.get('Alt/Üst 2.5_Alt', 99)
    if alt_25 == 99: alt_25 = od.get('Altı/Üstü 2.5_Alt', 99)
    kg_var = od.get('Karşılıklı Gol_Var', 99)
    if kg_var == 99: kg_var = od.get('Karşılıklı Gol Var', 99)
    
    sev = mac.get('skor_ev', -1)
    sdep = mac.get('skor_dep', -1)
    
    if alt_25 == 99.0 and kg_var <= 1.35 and kg_var != 99.0 and sev >= 0:
        toplam_gol = sev + sdep
        kg_yok_geldi = (sev == 0 or sdep == 0)
        found.append({
            'skor': f"{sev}-{sdep}",
            'toplam_gol': toplam_gol,
            'kg_yok_geldi': kg_yok_geldi,
            'idx': mac.get('index', '?')
        })

print(f"Toplam Kapali 2.5 ve KG Var <= 1.35 Mac: {len(found)}")
if found:
    kg_yok = [x for x in found if x['kg_yok_geldi']]
    alt_25_biten = [x for x in found if x['toplam_gol'] <= 2]
    alt_35_biten = [x for x in found if x['toplam_gol'] <= 3]
    print(f"KG Yok (Basari): {len(kg_yok)} ({(len(kg_yok)/len(found))*100:.1f}%)")
    print(f"2.5 Alt (Basari): {len(alt_25_biten)} ({(len(alt_25_biten)/len(found))*100:.1f}%)")
    print(f"3.5 Alt (Basari): {len(alt_35_biten)} ({(len(alt_35_biten)/len(found))*100:.1f}%)")
