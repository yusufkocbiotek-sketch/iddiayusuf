import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', encoding='utf-8') as f:
    data = json.load(f)

for i in [769, 770, 771, 773]:
    m = data['matches'][i]
    o = m['oranlar']
    print(f'Match {i}: {m["ev_sahibi"]} - {m["deplasman"]}')
    print(f'  MS1: {o.get("Maç Sonucu_1", 99)}, MS0: {o.get("Maç Sonucu_0", 99)}, MS2: {o.get("Maç Sonucu_2", 99)}')
    print(f'  Alt 2.5: {o.get("Alt/Üst 2.5_Alt", o.get("Altı/Üstü 2.5_Alt"))}, Üst 2.5: {o.get("Alt/Üst 2.5_Üst")}')
    print(f'  KG Var: {o.get("Karşılıklı Gol_Var")}, KG Yok: {o.get("Karşılıklı Gol_Yok")}')
    print(f'  Ev 0.5 Üst: {o.get("Ev Sahibi Alt/Üst 0.5_Üst", 99)}, Dep 0.5 Üst: {o.get("Deplasman Alt/Üst 0.5_Üst", 99)}')
    print('-'*40)
