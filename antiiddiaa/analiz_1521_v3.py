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
    ust_35 = od.get('Alt/Üst 3.5_Üst', 99)
    if ust_35 == 99: ust_35 = od.get('Altı/Üstü 3.5_Üst', 99)
    ms1 = od.get('Maç Sonucu_1', 99)
    
    sev = mac.get('skor_ev', -1)
    sdep = mac.get('skor_dep', -1)
    
    if alt_25 == 99.0 and kg_var <= 1.35 and kg_var != 99.0 and sev >= 0:
        if (ust_35 >= 1.85 or ust_35 == 99.0) or (ust_35 >= 1.75 and ms1 >= 2.00):
            toplam_gol = sev + sdep
            kg_yok_geldi = (sev == 0 or sdep == 0)
            found.append({
                'skor': f"{sev}-{sdep}",
                'kg_yok_geldi': kg_yok_geldi,
                'idx': mac.get('index', '?')
            })

print(f"Toplam Filtreli 1521 Mac: {len(found)}")
if found:
    kg_yok = [x for x in found if x['kg_yok_geldi']]
    print(f"KG Yok (Basari): {len(kg_yok)} ({(len(kg_yok)/len(found))*100:.1f}%)")
