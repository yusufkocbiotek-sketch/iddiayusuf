import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

indices_to_check = [-383, -385, -389, -390]

for idx in indices_to_check:
    m = data['matches'][idx]
    print(f"\n--- Match {idx} ---")
    print(f"{m['ev_sahibi']} - {m['deplasman']} | Skor: {m.get('skor_ev')}-{m.get('skor_dep')}")
    odds = m.get('oranlar', {})
    for key in ['Maç Sonucu_1', 'Maç Sonucu_0', 'Maç Sonucu_2', 'Karşılıklı Gol_Var', 'Karşılıklı Gol_Yok', 
                'Alt/Üst 2.5_Alt', 'Alt/Üst 2.5_Üst', 'Altı/Üstü 2.5_Alt', 'Altı/Üstü 2.5_Üst',
                'Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst', 'Deplasman 1. Yarı Altı/Üstü 0.5_Üst', 
                '1. Yarı Alt/Üst 1.5_Alt', '1. Yarı Alt/Üst 1.5_Üst', '1. Yarı Karşılıklı Gol_Var', '1. Yarı Karşılıklı Gol_Yok']:
        if key in odds:
            print(f"{key}: {odds[key]}")
