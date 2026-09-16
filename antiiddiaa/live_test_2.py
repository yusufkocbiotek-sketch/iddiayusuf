import json
import story_analyzer

match_data = {
  "ev_sahibi": "Cooks Hill United",
  "deplasman": "Belmont Swansea United FC",
  "tarih": "2026-06-04",
  "lig": "",
  "oranlar": {
    "Maç Sonucu_1": 2.23,
    "Maç Sonucu_0": 3.76,
    "Maç Sonucu_2": 2.09,
    "Çifte Şans_1 ve 0": 1.38,
    "Çifte Şans_1 ve 2": 1.1,
    "Çifte Şans_0 ve 2": 1.33,
    "Alt/Üst 3.5_Alt": 1.77,
    "Alt/Üst 3.5_Üst": 1.59,
    "Karşılıklı Gol_Var": 1.18,
    "Karşılıklı Gol_Yok": 2.89,
    "İlk Yarı Sonucu_1": 2.63,
    "İlk Yarı Sonucu_0": 2.41,
    "İlk Yarı Sonucu_2": 2.49,
    "İlk Yarı Alt/Üst 1.5_Alt": 1.68,
    "İlk Yarı Alt/Üst 1.5_Üst": 1.67,
    "İlk Yarı Karşılıklı Gol_Var": 2.49,
    "İlk Yarı Karşılıklı Gol_Yok": 1.26,
    "İkinci Yarı Karşılıklı Gol_Var": 1.97,
    "İkinci Yarı Karşılıklı Gol_Yok": 1.46,
    "Ev Sahibi Alt/Üst 1.5_Alt": 1.87,
    "Ev Sahibi Alt/Üst 1.5_Üst": 1.52,
    "Deplasman Alt/Üst 1.5_Alt": 1.95,
    "Deplasman Alt/Üst 1.5_Üst": 1.46,
    "Ev Sahibi İlk Yarı Altı/Üstü 0.5_Alt": 1.89,
    "Ev Sahibi İlk Yarı Altı/Üstü 0.5_Üst": 1.5,
    "Deplasman İlk Yarı Altı/Üstü 0.5_Alt": 1.94,
    "Deplasman İlk Yarı Altı/Üstü 0.5_Üst": 1.47
  }
}

story = story_analyzer.generate_story(match_data, verbose=True)
print(story)
