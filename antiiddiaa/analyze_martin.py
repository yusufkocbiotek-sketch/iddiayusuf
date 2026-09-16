import json
from story_analyzer import generate_story

match_data = {
      "ev_sahibi": "S Martin SJ",
      "deplasman": "Atletico De Rafaela",
      "durum": "baslamadi",
      "skor_ev": 0,
      "skor_dep": 0,
      "skor_1y_ev": 0,
      "skor_1y_dep": 0,
      "oranlar": {
        "Maç Sonucu_1": 1.53,
        "Maç Sonucu_0": 2.85,
        "Maç Sonucu_2": 5.34,
        "Handikaplı Maç Sonucu 0:1_1": 2.91,
        "Handikaplı Maç Sonucu 0:1_0": 2.78,
        "Handikaplı Maç Sonucu 0:1_2": 1.83,
        "-_1 ve 2": 1.6,
        "-_0 ve 2": 1.32,
        "1. Yarı Sonucu_1": 2.21,
        "1. Yarı Sonucu_0": 1.7,
        "1. Yarı Sonucu_2": 6.49,
        "2. Yarı Sonucu_1": 2.01,
        "2. Yarı Sonucu_0": 1.95,
        "2. Yarı Sonucu_2": 5.46,
        "1. Yarı Karşılıklı Gol_Var": 6.79,
        "1. Yarı Tek/Çift_Tek": 2.03,
        "1. Yarı Tek/Çift_Çift": 1.42,
        "Alt/Üst 1.5_Alt": 1.88,
        "Alt/Üst 1.5_Üst": 1.51,
        "Ev Sahibi Alt/Üst 1.5_Alt": 1.37,
        "Ev Sahibi Alt/Üst 1.5_Üst": 2.16,
        "Deplasman Alt/Üst 0.5_Alt": 1.46,
        "Deplasman Alt/Üst 0.5_Üst": 1.96,
        "1. Yarı Alt/Üst 0.5_Alt": 1.92,
        "1. Yarı Alt/Üst 0.5_Üst": 1.48,
        "Ev Sahibi 1. Yarı Altı/Üstü 0.5_Alt": 1.54,
        "Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst": 1.85,
        "Deplasman 1. Yarı Altı/Üstü 0.5_Alt": 1.09,
        "Deplasman 1. Yarı Altı/Üstü 0.5_Üst": 3.62,
        "Karşılıklı Gol_Var": 2.59,
        "Karşılıklı Gol_Yok": 1.23,
        "Tek / Çift_Tek": 1.72,
        "Tek / Çift_Çift": 1.62,
        "2. Yarı Karşılıklı Gol_Var": 5.56
      }
}

story = generate_story(match_data, verbose=False)
print(story)
