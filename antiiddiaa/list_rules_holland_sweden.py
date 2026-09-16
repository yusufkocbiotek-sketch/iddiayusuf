import sys, json
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
import rule_engine

match = {
    "ev_sahibi": "Hollanda",
    "deplasman": "İsveç",
    "tarih": "2026-06-03",
    "lig": "",
    "oranlar": {
        "Maç Sonucu_1": 1.48,
        "Maç Sonucu_0": 3.63,
        "Maç Sonucu_2": 4.74,
        "Çifte Şans_1 ve 0": 1.07,
        "Çifte Şans_1 ve 2": 1.14,
        "Çifte Şans_0 ve 2": 2.01,
        "Alt/Üst 1.5_Alt": 3.2,
        "Alt/Üst 1.5_Üst": 1.18,
        "Alt/Üst 2.5_Alt": 1.69,
        "Alt/Üst 2.5_Üst": 1.76,
        "Alt/Üst 3.5_Alt": 1.2,
        "Alt/Üst 3.5_Üst": 3.09,
        "Karşılıklı Gol_Var": 1.79,
        "Karşılıklı Gol_Yok": 1.66,
        "İlk Yarı Sonucu_1": 2.02,
        "İlk Yarı Sonucu_0": 2.1,
        "İlk Yarı Sonucu_2": 5.23,
        "İlk Yarı Alt/Üst 0.5_Alt": 2.73,
        "İlk Yarı Alt/Üst 0.5_Üst": 1.26,
        "İlk Yarı Alt/Üst 1.5_Alt": 1.3,
        "İlk Yarı Alt/Üst 1.5_Üst": 2.57,
        "İlk Yarı Karşılıklı Gol_Var": 4.68,
        "İlk Yarı Karşılıklı Gol_Yok": 1.06,
        "İkinci Yarı Karşılıklı Gol_Var": 3.65,
        "İkinci Yarı Karşılıklı Gol_Yok": 1.13,
        "Ev Sahibi Alt/Üst 0.5_Alt": 4.73,
        "Ev Sahibi Alt/Üst 0.5_Üst": 1.06,
        "Ev Sahibi Alt/Üst 1.5_Alt": 1.82,
        "Ev Sahibi Alt/Üst 1.5_Üst": 1.64,
        "Ev Sahibi Alt/Üst 2.5_Alt": 1.18,
        "Ev Sahibi Alt/Üst 2.5_Üst": 3.21,
        "Deplasman Alt/Üst 0.5_Alt": 2.03,
        "Deplasman Alt/Üst 0.5_Üst": 1.5,
        "Deplasman Alt/Üst 1.5_Alt": 1.11,
        "Deplasman Alt/Üst 1.5_Üst": 3.86,
        "Ev Sahibi İlk Yarı Altı/Üstü 0.5_Alt": 1.91,
        "Ev Sahibi İlk Yarı Altı/Üstü 0.5_Üst": 1.57,
        "Deplasman İlk Yarı Altı/Üstü 0.5_Alt": 1.27,
        "Deplasman İlk Yarı Altı/Üstü 0.5_Üst": 2.68,
        "Her İki Yarıda da Alt 1.5_Evet": 2.22,
        "Her İki Yarıda da Alt 1.5_Hayır": 1.41,
        "Her İki Yarıda da Üst 1.5_Evet": 5.61,
        "Hangi Yarıda Daha Fazla Gol Olur_1.": 2.86,
        "Hangi Yarıda Daha Fazla Gol Olur_Eşit": 3.26,
        "Hangi Yarıda Daha Fazla Gol Olur_2.": 1.99,
        "Toplam Gol_0-1 gol": 3.14,
        "Toplam Gol_2-3 gol": 1.8,
        "Toplam Gol_4-5 gol": 3.72,
        "Toplam Gol_6+ gol": 15.5,
        "İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Alt": 3.4,
        "İlk Yarı Sonucu ve Altı/Üstü 1.5_0 ve Alt": 2.71,
        "İlk Yarı Sonucu ve Altı/Üstü 1.5_2 ve Alt": 7.06,
        "İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Üst": 4.54,
        "İlk Yarı Sonucu ve Altı/Üstü 1.5_0 ve Üst": 8.16,
        "İlk Yarı Sonucu ve Altı/Üstü 1.5_2 ve Üst": 17.55
    }
}

odds = match['oranlar']
rule_engine.CURRENT_MATCH = match
rules = rule_engine.get_all_rules()
triggered = []
for R in rules:
    ok, insight = R.evaluate(odds)
    if ok:
        triggered.append((R.code, R.name, R.category, insight))

print('Triggered rules:')
for code, name, cat, insight in triggered:
    print(f"{code}\t{name}\t{cat}\t{insight}")

print('\nAll codes:', ','.join([c for c,_,_,_ in triggered]))
