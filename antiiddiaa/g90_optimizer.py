import json
import statistics
from collections import defaultdict

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

success = []
fail = []

for m in matches:
    o = m.get('oranlar', {})
    if not o: continue
    
    ms1 = o.get('Maç Sonucu_1')
    kgvar = o.get('Karşılıklı Gol_Var')
    kgyok = o.get('Karşılıklı Gol_Yok')
    alt = o.get('Alt/Üst 2.5_Alt')
    ust = o.get('Alt/Üst 2.5_Üst')
    
    if not all([ms1, kgvar, kgyok, alt, ust]): continue
    
    if (2.30 <= ms1 <= 2.70) and (kgyok < kgvar) and (alt < ust):
        ev = m.get('skor_ev', 0)
        dep = m.get('skor_dep', 0)
        
        if ev + dep < 3:
            success.append(o)
        else:
            fail.append(o)

def get_avg(group, key):
    vals = [x[key] for x in group if key in x and x[key] is not None]
    if not vals: return 0
    return sum(vals) / len(vals)

keys_to_compare = [
    '1. Yarı Sonucu_0',
    'Ev Sahibi Alt/Üst 1.5_Üst',
    'Deplasman Alt/Üst 1.5_Üst',
    'Handikaplı Maç Sonucu 0:1_1',
    'Alt/Üst 1.5_Üst',
    'Karşılıklı Gol_Yok'
]

print(f"Toplam G90 Maçı: {len(success) + len(fail)}")
print(f"Başarılı (2.5 Alt): {len(success)}")
print(f"Patlayan (2.5 Üst): {len(fail)}\n")

print(f"{'Oran Türü':<35} | {'Başarılı Ort.':<15} | {'Patlayan Ort.':<15} | {'Fark'}")
print("-" * 80)

for k in keys_to_compare:
    succ_avg = get_avg(success, k)
    fail_avg = get_avg(fail, k)
    diff = fail_avg - succ_avg
    print(f"{k:<35} | {succ_avg:<15.2f} | {fail_avg:<15.2f} | {diff:+.2f}")

# Detaylı İnceleme İçin Birkaç Patlayan Maç
print("\n--- Patlayan Maçların Bazılarında Oran Dağılımı ---")
for i, o in enumerate(fail[:15]): # İlk 15 patlayan
    iy0 = o.get('1. Yarı Sonucu_0', 0)
    ev15 = o.get('Ev Sahibi Alt/Üst 1.5_Üst', 0)
    dep15 = o.get('Deplasman Alt/Üst 1.5_Üst', 0)
    ust15 = o.get('Alt/Üst 1.5_Üst', 0)
    print(f"Patlayan {i+1} | İY0: {iy0} | Ev1.5Üst: {ev15} | Dep1.5Üst: {dep15} | 1.5Üst: {ust15}")
