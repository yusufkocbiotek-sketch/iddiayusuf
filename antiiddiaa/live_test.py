import json
import story_analyzer

match_data = {
  "ev_sahibi": "Oakleigh C.",
  "deplasman": "ST Albans Saints SC",
  "tarih": "2026-06-04",
  "lig": "",
  "oranlar": {
    "Maç Sonucu_1": 1.22,
    "Maç Sonucu_0": 4.64,
    "Maç Sonucu_2": 6.15,
    "Alt/Üst 3.5_Alt": 1.51,
    "Alt/Üst 3.5_Üst": 1.89,
    "Karşılıklı Gol_Var": 1.5,
    "Karşılıklı Gol_Yok": 1.89,
    "İlk Yarı Sonucu_1": 1.6,
    "İlk Yarı Sonucu_0": 2.53,
    "İlk Yarı Sonucu_2": 5.78,
    "İlk Yarı Alt/Üst 1.5_Alt": 1.54,
    "İlk Yarı Alt/Üst 1.5_Üst": 1.84,
    "İlk Yarı Karşılıklı Gol_Var": 3.39,
    "İlk Yarı Karşılıklı Gol_Yok": 1.11,
    "İkinci Yarı Karşılıklı Gol_Var": 2.71,
    "İkinci Yarı Karşılıklı Gol_Yok": 1.22,
    "Ev Sahibi Alt/Üst 2.5_Alt": 1.5,
    "Ev Sahibi Alt/Üst 2.5_Üst": 1.89,
    "Deplasman Alt/Üst 0.5_Alt": 2.14,
    "Deplasman Alt/Üst 0.5_Üst": 1.38,
    "Ev Sahibi İlk Yarı Altı/Üstü 0.5_Alt": 2.47,
    "Ev Sahibi İlk Yarı Altı/Üstü 0.5_Üst": 1.27,
    "Deplasman İlk Yarı Altı/Üstü 0.5_Alt": 1.3,
    "Deplasman İlk Yarı Altı/Üstü 0.5_Üst": 2.36
  }
}

story = story_analyzer.generate_story(match_data, verbose=True)
print(story)
