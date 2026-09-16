import json
from collections import defaultdict

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

alt_25_count = 0
tam_3_gol_count = 0
ust_35_count = 0
total = 0

for idx, m in enumerate(data['matches']):
    odds = m.get('oranlar', {})
    
    # Is 2.5 missing but 3.5 present?
    has_25 = any('2.5' in k for k in odds.keys() if 'Alt/Üst 2.5' in k and not 'Ev Sahibi' in k and not 'Deplasman' in k)
    has_35 = any('3.5' in k for k in odds.keys())
    
    if not has_25 and has_35:
        skor_ev = m.get('skor_ev')
        skor_dep = m.get('skor_dep')
        
        # Sadece skorları olan maçlar
        if skor_ev is not None and skor_dep is not None:
            toplam_gol = skor_ev + skor_dep
            
            if toplam_gol <= 2:
                alt_25_count += 1
            elif toplam_gol == 3:
                tam_3_gol_count += 1
            else:
                ust_35_count += 1
            
            total += 1

print(f"Toplam Gizli 2.5 Maçı: {total}")
print(f"2.5 Alt (0, 1, 2 gol): {alt_25_count} (%{alt_25_count/total*100:.1f})")
print(f"Tam 3 Gol (2-1, 3-0): {tam_3_gol_count} (%{tam_3_gol_count/total*100:.1f})")
print(f"3.5 Üst (4+ gol): {ust_35_count} (%{ust_35_count/total*100:.1f})")
