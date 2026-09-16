import json

def mean(lst):
    if not lst: return 0.0
    return sum(lst) / len(lst)

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

alt_odds = {'ms1': [], 'h2': [], 'ev_15_ust': [], 'dep_05_ust': [], 'ust35': [], 'kg_var': []}
ust_odds = {'ms1': [], 'h2': [], 'ev_15_ust': [], 'dep_05_ust': [], 'ust35': [], 'kg_var': []}

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
            
            h2 = odds.get('Handikaplı Maç Sonucu 0:1_2', odds.get('Handikaplı Maç Sonucu 1:0_2', 0))
            ev_15_ust = odds.get('Ev Sahibi Alt/Üst 1.5_Üst', 0)
            dep_05_ust = odds.get('Deplasman Altı/Üstü 0.5_Üst', odds.get('Deplasman 1. Yarı Altı/Üstü 0.5_Üst', 0))
            ust35 = odds.get('Alt/Üst 3.5_Üst', 0)
            
            if toplam <= 2:
                alt_odds['ms1'].append(ms1)
                if h2 > 0: alt_odds['h2'].append(h2)
                if ev_15_ust > 0: alt_odds['ev_15_ust'].append(ev_15_ust)
                if dep_05_ust > 0: alt_odds['dep_05_ust'].append(dep_05_ust)
                if ust35 > 0: alt_odds['ust35'].append(ust35)
                alt_odds['kg_var'].append(kg_var)
                
            elif toplam >= 4:
                ust_odds['ms1'].append(ms1)
                if h2 > 0: ust_odds['h2'].append(h2)
                if ev_15_ust > 0: ust_odds['ev_15_ust'].append(ev_15_ust)
                if dep_05_ust > 0: ust_odds['dep_05_ust'].append(dep_05_ust)
                if ust35 > 0: ust_odds['ust35'].append(ust35)
                ust_odds['kg_var'].append(kg_var)

print("--- 2.5 ALT BİTENLER (133 Maç) ORTALAMA ORANLARI ---")
print(f"MS1: {mean(alt_odds['ms1']):.2f}")
print(f"KG Var: {mean(alt_odds['kg_var']):.2f}")
print(f"3.5 Üst: {mean(alt_odds['ust35']):.2f}")
print(f"Handikap 2: {mean(alt_odds['h2']):.2f}")
print(f"Ev 1.5 Üst: {mean(alt_odds['ev_15_ust']):.2f}")
print(f"Dep 0.5 Üst: {mean(alt_odds['dep_05_ust']):.2f}")

print("\n--- 3.5 ÜST BİTENLER (144 Maç) ORTALAMA ORANLARI ---")
print(f"MS1: {mean(ust_odds['ms1']):.2f}")
print(f"KG Var: {mean(ust_odds['kg_var']):.2f}")
print(f"3.5 Üst: {mean(ust_odds['ust35']):.2f}")
print(f"Handikap 2: {mean(ust_odds['h2']):.2f}")
print(f"Ev 1.5 Üst: {mean(ust_odds['ev_15_ust']):.2f}")
print(f"Dep 0.5 Üst: {mean(ust_odds['dep_05_ust']):.2f}")
