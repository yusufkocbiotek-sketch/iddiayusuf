import json
import sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import get_all_rules, evaluate_synergies

match_data = {
  "ev_sahibi": "Al Fehaheel",
  "deplasman": "Kazma SC",
  "tarih": "2026-06-18",
  "lig": "",
  "oranlar": {
    "Maç Sonucu_1": 3.59,
    "Maç Sonucu_0": 3.28,
    "Maç Sonucu_2": 1.63,
    "Çifte Şans_1 ve 0": 1.67,
    "Çifte Şans_1 ve 2": 1.14,
    "Çifte Şans_0 ve 2": 1.1,
    "Alt/Üst 1.5_Alt": 3.51,
    "Alt/Üst 1.5_Üst": 1.1,
    "Alt/Üst 2.5_Alt": 1.81,
    "Alt/Üst 2.5_Üst": 1.55,
    "Alt/Üst 3.5_Alt": 1.26,
    "Alt/Üst 3.5_Üst": 2.5,
    "Karşılıklı Gol_Var": 1.51,
    "Karşılıklı Gol_Yok": 1.88,
    "İlk Yarı Sonucu_1": 4.04,
    "İlk Yarı Sonucu_0": 2.09,
    "İlk Yarı Sonucu_2": 2.13,
    "İlk Yarı Alt/Üst 0.5_Alt": 2.81,
    "İlk Yarı Alt/Üst 0.5_Üst": 1.19,
    "İlk Yarı Alt/Üst 1.5_Alt": 1.33,
    "İlk Yarı Alt/Üst 1.5_Üst": 2.25,
    "İlk Yarı Karşılıklı Gol_Var": 3.67,
    "İlk Yarı Karşılıklı Gol_Yok": 1.08,
    "İkinci Yarı Karşılıklı Gol_Var": 2.87,
    "İkinci Yarı Karşılıklı Gol_Yok": 1.18,
    "Ev Sahibi Alt/Üst 0.5_Alt": 2.45,
    "Ev Sahibi Alt/Üst 0.5_Üst": 1.27,
    "Ev Sahibi Alt/Üst 1.5_Alt": 1.22,
    "Ev Sahibi Alt/Üst 1.5_Üst": 2.68,
    "Deplasman Alt/Üst 0.5_Alt": 4.32,
    "Deplasman Alt/Üst 1.5_Alt": 1.75,
    "Deplasman Alt/Üst 1.5_Üst": 1.61,
    "Ev Sahibi İlk Yarı Altı/Üstü 0.5_Alt": 1.37,
    "Ev Sahibi İlk Yarı Altı/Üstü 0.5_Üst": 2.16,
    "Deplasman İlk Yarı Altı/Üstü 0.5_Alt": 1.83,
    "Deplasman İlk Yarı Altı/Üstü 0.5_Üst": 1.54,
    "Her İki Yarıda da Alt 1.5_Evet": 2.41,
    "Her İki Yarıda da Alt 1.5_Hayır": 1.29,
    "Her İki Yarıda da Üst 1.5_Evet": 4.3,
    "Hangi Yarıda Daha Fazla Gol Olur_1.": 2.79,
    "Hangi Yarıda Daha Fazla Gol Olur_Eşit": 3.24,
    "Hangi Yarıda Daha Fazla Gol Olur_2.": 1.9,
    "Toplam Gol_0-1 gol": 3.64,
    "Toplam Gol_2-3 gol": 1.82,
    "Toplam Gol_4-5 gol": 3.2,
    "Toplam Gol_6+ gol": 11.0,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Alt": 5.96,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_0 ve Alt": 2.84,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_2 ve Alt": 3.67,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Üst": 11.05,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_0 ve Üst": 6.75,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_2 ve Üst": 4.54
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
