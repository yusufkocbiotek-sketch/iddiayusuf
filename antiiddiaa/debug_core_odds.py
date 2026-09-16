import json, sys
sys.stdout.reconfigure(encoding='utf-8')
f=open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', encoding='utf-8')
d=json.load(f)
keys = ['Maç Sonucu_1', 'Maç Sonucu_0', 'Maç Sonucu_2', 'Alt/Üst 2.5_Alt', 'Alt/Üst 2.5_Üst', 'Karşılıklı Gol_Var', 'Karşılıklı Gol_Yok', 'İlk Yarı Alt/Üst 0.5_Üst', 'Çifte Şans_1X', 'Çifte Şans_12', 'Çifte Şans_X2']
for idx in [749, 754, 757, 748, 753]:
    print(f'\n--- Match {idx} ---')
    o = d['matches'][-idx]['oranlar']
    for k in keys:
        print(f'{k}: {o.get(k)}')
