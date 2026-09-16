import json
import sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import get_all_rules, evaluate_synergies

match_data = {
  "ev_sahibi": "Güney Afrika",
  "deplasman": "Güney Kore",
  "tarih": "2026-06-17",
  "lig": "",
  "oranlar": {
    "Maç Sonucu_1": 5.25,
    "Maç Sonucu_0": 3.65,
    "Maç Sonucu_2": 1.46,
    "Çifte Şans_1 ve 0": 2.11,
    "Çifte Şans_1 ve 2": 1.14,
    "Alt/Üst 1.5_Alt": 3.09,
    "Alt/Üst 1.5_Üst": 1.22,
    "Alt/Üst 2.5_Alt": 1.63,
    "Alt/Üst 2.5_Üst": 1.85,
    "Alt/Üst 3.5_Alt": 1.17,
    "Alt/Üst 3.5_Üst": 3.35,
    "Karşılıklı Gol_Var": 1.91,
    "Karşılıklı Gol_Yok": 1.6,
    "İlk Yarı Sonucu_1": 5.71,
    "İlk Yarı Sonucu_0": 2.1,
    "İlk Yarı Sonucu_2": 2.01,
    "İlk Yarı Alt/Üst 0.5_Alt": 2.7,
    "İlk Yarı Alt/Üst 0.5_Üst": 1.29,
    "İlk Yarı Alt/Üst 1.5_Alt": 1.28,
    "İlk Yarı Alt/Üst 1.5_Üst": 2.71,
    "İlk Yarı Karşılıklı Gol_Var": 5.15,
    "İkinci Yarı Karşılıklı Gol_Var": 4.0,
    "İkinci Yarı Karşılıklı Gol_Yok": 1.11,
    "Ev Sahibi Alt/Üst 0.5_Alt": 1.93,
    "Ev Sahibi Alt/Üst 0.5_Üst": 1.59,
    "Ev Sahibi Alt/Üst 1.5_Alt": 1.08,
    "Ev Sahibi Alt/Üst 1.5_Üst": 4.45,
    "Deplasman Alt/Üst 0.5_Alt": 4.78,
    "Deplasman Alt/Üst 0.5_Üst": 1.07,
    "Deplasman Alt/Üst 1.5_Alt": 1.82,
    "Deplasman Alt/Üst 1.5_Üst": 1.67,
    "Ev Sahibi İlk Yarı Altı/Üstü 0.5_Alt": 1.24,
    "Ev Sahibi İlk Yarı Altı/Üstü 0.5_Üst": 2.9,
    "Deplasman İlk Yarı Altı/Üstü 0.5_Alt": 1.92,
    "Deplasman İlk Yarı Altı/Üstü 0.5_Üst": 1.59,
    "Her İki Yarıda da Alt 1.5_Evet": 2.14,
    "Her İki Yarıda da Alt 1.5_Hayır": 1.46,
    "Her İki Yarıda da Üst 1.5_Evet": 6.25,
    "Hangi Yarıda Daha Fazla Gol Olur_1.": 2.88,
    "Hangi Yarıda Daha Fazla Gol Olur_Eşit": 3.21,
    "Hangi Yarıda Daha Fazla Gol Olur_2.": 2.03,
    "Toplam Gol_0-1 gol": 3.0,
    "Toplam Gol_2-3 gol": 1.81,
    "Toplam Gol_4-5 gol": 3.98,
    "Toplam Gol_6+ gol": 17.75,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Alt": 7.47,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_0 ve Alt": 2.64,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_2 ve Alt": 3.33,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Üst": 20.5,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_0 ve Üst": 8.74,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_2 ve Üst": 4.58
  }
}

rules = get_all_rules()
triggered_rules = []
for r in rules:
    triggered, message = r.evaluate(match_data["oranlar"])
    if triggered:
        triggered_rules.append((r.code, message))

print(f"Maç: {match_data['ev_sahibi']} vs {match_data['deplasman']}")
print("-" * 50)
if not triggered_rules:
    print("Hiçbir kural tetiklenmedi (Standart Maç).")
else:
    for code, msg in triggered_rules:
        print(f"[{code}] {msg}")

synergies = evaluate_synergies([code for code, _ in triggered_rules])
if synergies:
    print("-" * 50)
    for sync in synergies:
        print(f"🚨 MEGA SİNERJİ: {sync}")
