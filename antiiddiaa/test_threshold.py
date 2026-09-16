import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

alt_trap_correct = 0
alt_trap_wrong = 0
ust_trap_correct = 0
ust_trap_wrong = 0

for idx, m in enumerate(data['matches']):
    odds = m.get('oranlar', {})
    has_25 = any('2.5' in k for k in odds.keys() if 'Alt/Üst 2.5' in k and not 'Ev Sahibi' in k and not 'Deplasman' in k)
    has_35 = any('3.5' in k for k in odds.keys())
    ms1 = odds.get('Maç Sonucu_1', 0)
    kg_var = odds.get('Karşılıklı Gol_Var', 0)
    
    if not has_25 and has_35 and 0 < ms1 <= 1.55 and 0 < kg_var <= 1.50:
        skor_ev = m.get('skor_ev')
        skor_dep = m.get('skor_dep')
        
        if skor_ev is not None and skor_dep is not None:
            toplam = skor_ev + skor_dep
            ust35 = odds.get('Alt/Üst 3.5_Üst', 0)
            
            if ust35 > 0:
                if ust35 >= 1.80:
                    # We predict ALT
                    if toplam <= 2: alt_trap_correct += 1
                    elif toplam >= 4: alt_trap_wrong += 1
                else:
                    # We predict UST
                    if toplam >= 4: ust_trap_correct += 1
                    elif toplam <= 2: ust_trap_wrong += 1

print(f"When 3.5 Üst >= 1.80 (Predicted ALT): Correct: {alt_trap_correct}, Wrong: {alt_trap_wrong}")
print(f"When 3.5 Üst < 1.80 (Predicted UST): Correct: {ust_trap_correct}, Wrong: {ust_trap_wrong}")
