import json
import sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import get_all_rules, evaluate_synergies

mac_data = {
  "ev_sahibi": "Türkiye",
  "deplasman": "Paraguay",
  "tarih": "2026-06-13",
  "lig": "",
  "oranlar": {
    "Maç Sonucu_1": 2.11,
    "Maç Sonucu_0": 3.05,
    "Maç Sonucu_2": 3.27,
    "Çifte Şans_1 ve 0": 1.25,
    "Çifte Şans_1 ve 2": 1.29,
    "Çifte Şans_0 ve 2": 1.56,
    "Alt/Üst 1.5_Alt": 2.76,
    "Alt/Üst 1.5_Üst": 1.34,
    "Alt/Üst 2.5_Alt": 1.53,
    "Alt/Üst 2.5_Üst": 2.2,
    "Alt/Üst 3.5_Alt": 1.15,
    "Alt/Üst 3.5_Üst": 4.2,
    "Karşılıklı Gol_Var": 1.9,
    "Karşılıklı Gol_Yok": 1.71,
    "İlk Yarı Sonucu_1": 2.84,
    "İlk Yarı Sonucu_0": 1.95,
    "İlk Yarı Sonucu_2": 4.08,
    "İlk Yarı Alt/Üst 0.5_Alt": 2.46,
    "İlk Yarı Alt/Üst 0.5_Üst": 1.43,
    "İlk Yarı Alt/Üst 1.5_Alt": 1.25,
    "İlk Yarı Alt/Üst 1.5_Üst": 3.22,
    "İlk Yarı Karşılıklı Gol_Var": 5.42,
    "İlk Yarı Karşılıklı Gol_Yok": 1.09,
    "İkinci Yarı Karşılıklı Gol_Var": 4.08,
    "İkinci Yarı Karşılıklı Gol_Yok": 1.16,
    "Ev Sahibi Alt/Üst 0.5_Alt": 3.32,
    "Ev Sahibi Alt/Üst 0.5_Üst": 1.24,
    "Ev Sahibi Alt/Üst 1.5_Alt": 1.45,
    "Ev Sahibi Alt/Üst 1.5_Üst": 2.36,
    "Ev Sahibi Alt/Üst 2.5_Alt": 1.07,
    "Ev Sahibi Alt/Üst 2.5_Üst": 5.83,
    "Deplasman Alt/Üst 0.5_Alt": 2.46,
    "Deplasman Alt/Üst 0.5_Üst": 1.43,
    "Deplasman Alt/Üst 1.5_Alt": 1.23,
    "Deplasman Alt/Üst 1.5_Üst": 3.34,
    "Ev Sahibi İlk Yarı Altı/Üstü 0.5_Alt": 1.62,
    "Ev Sahibi İlk Yarı Altı/Üstü 0.5_Üst": 2.04,
    "Deplasman İlk Yarı Altı/Üstü 0.5_Alt": 1.4,
    "Deplasman İlk Yarı Altı/Üstü 0.5_Üst": 2.53,
    "Her İki Yarıda da Alt 1.5_Evet": 1.98,
    "Her İki Yarıda da Alt 1.5_Hayır": 1.66,
    "Her İki Yarıda da Üst 1.5_Evet": 8.05,
    "Hangi Yarıda Daha Fazla Gol Olur_1.": 3.17,
    "Hangi Yarıda Daha Fazla Gol Olur_Eşit": 3.12,
    "Hangi Yarıda Daha Fazla Gol Olur_2.": 2.12,
    "Toplam Gol_0-1 gol": 2.68,
    "Toplam Gol_2-3 gol": 1.88,
    "Toplam Gol_4-5 gol": 4.83,
    "Toplam Gol_6+ gol": 26.0,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Alt": 4.21,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_0 ve Alt": 2.4,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_2 ve Alt": 5.6,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Üst": 7.73,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_0 ve Üst": 8.71,
    "İlk Yarı Sonucu ve Altı/Üstü 1.5_2 ve Üst": 13.05
  }
}

rules = get_all_rules()
odds = mac_data['oranlar']
kural_zinciri = []
mesajlar = []

for R in rules:
    trigger, msg = R.evaluate(odds)
    if trigger:
        kural_zinciri.append(R.code)
        mesajlar.append(f"[{R.code}] {msg}")

synergies = evaluate_synergies(kural_zinciri)

print(f"Maç: {mac_data['ev_sahibi']} vs {mac_data['deplasman']}")
if kural_zinciri:
    print(f"Tetiklenen Kurallar: {' -> '.join(kural_zinciri)}")
    for m in mesajlar:
        print(f"  - {m}")
else:
    print("Tetiklenen Kural: YOK")

for syn in synergies:
    print(f"  {syn}")
