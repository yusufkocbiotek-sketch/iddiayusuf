import json
from collections import defaultdict

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

leagues = defaultdict(lambda: {'s':0, 'f':0})

for m in matches:
    o = m.get('oranlar')
    if not o: continue
    ms1 = o.get('Maç Sonucu_1')
    if not ms1 or not (2.30 <= ms1 <= 2.70): continue
    
    kgyok = o.get('Karşılıklı Gol_Yok', 9)
    kgvar = o.get('Karşılıklı Gol_Var', 0)
    alt = o.get('Alt/Üst 2.5_Alt', 9)
    ust = o.get('Alt/Üst 2.5_Üst', 0)
    
    if kgyok < kgvar and alt < ust:
        ev = m.get('skor_ev', 0)
        dep = m.get('skor_dep', 0)
        lig = m.get('lig', '').strip()
        if not lig: lig = 'Bilinmeyen (Uluslararası/Eksik)'
        
        if ev + dep < 3:
            leagues[lig]['s'] += 1
        else:
            leagues[lig]['f'] += 1

top = sorted(leagues.items(), key=lambda x: x[1]['s']+x[1]['f'], reverse=True)[:25]
print("--- G90 LİG BAZLI İSTİSNA ANALİZİ ---\n")
for k, v in top:
    total = v['s'] + v['f']
    win_rate = v['s'] / total * 100
    print(f"{k:<35} | Toplam: {total:<3} | Başarı: %{win_rate:.1f} | Alt: {v['s']} | Üst: {v['f']}")
