import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

count = 0
for i, m in enumerate(matches):
    odds = m.get('oranlar', {})
    ms0 = odds.get('Maç Sonucu_0')
    if ms0 and ms0 <= 2.65:
        ms1 = odds.get('Maç Sonucu_1')
        ms2 = odds.get('Maç Sonucu_2')
        kgy = odds.get('Karşılıklı Gol_Yok')
        kgv = odds.get('Karşılıklı Gol_Var')
        alt_25 = odds.get('Alt/Üst 2.5_Alt', odds.get('Altı/Üstü 2.5_Alt', 99.0))
        score = f"{m.get('skor_ev')}-{m.get('skor_dep')}"
        idx = -len(matches) + i
        print(f"Match {idx}: MS1={ms1}, MS0={ms0}, MS2={ms2}, KGVar={kgv}, KGYok={kgy}, 2.5Alt={alt_25} -> SCORE: {score}")
        count += 1
print(f"Total: {count}")
