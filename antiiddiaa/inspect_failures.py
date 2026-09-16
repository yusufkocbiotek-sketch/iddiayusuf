import json
import codecs

with codecs.open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', 'utf8') as f:
    matches = json.load(f)['matches']

for idx in [-410, -409, -408]:
    m = matches[idx]
    print(f'INDEX {idx}')
    print(f'{m["ev_sahibi"]} vs {m["deplasman"]}')
    print(f'Skor: {m.get("skor_1y_ev")}-{m.get("skor_1y_dep")} / {m.get("skor_ev")}-{m.get("skor_dep")}')
    
    o = m['oranlar']
    keys = ['Maç Sonucu_1', 'Maç Sonucu_0', 'Maç Sonucu_2', 'Alt/Üst 1.5_Alt', 'Alt/Üst 2.5_Alt', 'Alt/Üst 2.5_Üst', 'Karşılıklı Gol_Var', 'Karşılıklı Gol_Yok', 'Çifte Şans_1 ve 0', 'Çifte Şans_0 ve 2', 'Çifte Şans_1 ve 2']
    for k in keys:
        if k in o: 
            print(f'  {k}: {o[k]}')
        
    print('-'*40)
