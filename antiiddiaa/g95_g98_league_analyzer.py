import json
from collections import defaultdict

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

g95_leagues = defaultdict(lambda: {'s':0, 'f':0})
g98_leagues = defaultdict(lambda: {'s':0, 'f':0})

for m in matches:
    o = m.get('oranlar')
    if not o: continue
    ms1 = o.get('Maç Sonucu_1')
    if not ms1: continue
    
    kgyok = o.get('Karşılıklı Gol_Yok', 9)
    kgvar = o.get('Karşılıklı Gol_Var', 0)
    alt = o.get('Alt/Üst 2.5_Alt', 9)
    ust = o.get('Alt/Üst 2.5_Üst', 0)
    
    # İki kuralın da ortak şartı: KG Var favori, Üst favori
    if kgvar < kgyok and ust < alt:
        ev = m.get('skor_ev', 0)
        dep = m.get('skor_dep', 0)
        lig = m.get('lig', '').strip()
        if not lig: lig = 'Bilinmeyen'
        
        # G95: 2.00 - 2.30
        if 2.00 <= ms1 <= 2.30:
            if ev > 0 and dep > 0:
                g95_leagues[lig]['s'] += 1
            else:
                g95_leagues[lig]['f'] += 1
                
        # G98: 1.40 - 1.60
        elif 1.40 <= ms1 <= 1.60:
            if ev > 0 and dep > 0:
                g98_leagues[lig]['s'] += 1
            else:
                g98_leagues[lig]['f'] += 1

def print_top_leagues(leagues_dict, title):
    print(f"\n--- {title} LİG BAZLI İSTİSNA ANALİZİ ---")
    # Sadece en az 10 maç olan ligleri filtrele
    filtered = {k: v for k, v in leagues_dict.items() if (v['s'] + v['f']) >= 10 and k != 'Bilinmeyen'}
    
    # En yüksek başarıya sahip ligler (Güvenli)
    safe_top = sorted(filtered.items(), key=lambda x: x[1]['s']/(x[1]['s']+x[1]['f']), reverse=True)[:5]
    print("\n[+] GUVENLI BOLGELER (KG Var Orani En Yuksek):")
    for k, v in safe_top:
        total = v['s'] + v['f']
        print(f"{k:<15} | Toplam: {total:<3} | Başarı: %{(v['s']/total*100):.1f}")
        
    # En düşük başarıya sahip ligler (Tuzak)
    trap_top = sorted(filtered.items(), key=lambda x: x[1]['s']/(x[1]['s']+x[1]['f']))[:5]
    print("\n[-] TUZAK BOLGELER (KG Var Orani En Dusuk / KG Yok Bitenler):")
    for k, v in trap_top:
        total = v['s'] + v['f']
        print(f"{k:<15} | Toplam: {total:<3} | Başarı: %{(v['s']/total*100):.1f}")

print_top_leagues(g95_leagues, "G95 (Açık Denge)")
print_top_leagues(g98_leagues, "G98 (Sahte Favori KG Tuzağı)")
