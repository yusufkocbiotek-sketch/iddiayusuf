import json
from story_analyzer import generate_story

match_data = {
      "ev_sahibi": "Patronato P",
      "deplasman": "Quilmes Atletico Club",
      "durum": "baslamadi",
      "skor_ev": 0,
      "skor_dep": 0,
      "skor_1y_ev": 0,
      "skor_1y_dep": 0,
      "oranlar": {
        "Maç Sonucu_1": 2.31,
        "Maç Sonucu_0": 2.53,
        "Maç Sonucu_2": 2.73,
        "Handikaplı Maç Sonucu 0:1_1": 5.2,
        "Handikaplı Maç Sonucu 0:1_0": 3.47,
        "Handikaplı Maç Sonucu 0:1_2": 1.3,
        "Çifte Şans_1 ve 0": 1.21,
        "Çifte Şans_1 ve 2": 1.25,
        "Çifte Şans_0 ve 2": 1.3,
        "1. Yarı Sonucu_1": 3.15,
        "1. Yarı Sonucu_0": 1.66,
        "1. Yarı Sonucu_2": 3.63,
        "2. Yarı Sonucu_1": 2.75,
        "2. Yarı Sonucu_0": 1.96,
        "2. Yarı Sonucu_2": 3.12,
        "1. Yarı Karşılıklı Gol_Var": 5.6,
        "1. Yarı Çifte Şans_1 ve 0": 1.1,
        "1. Yarı Çifte Şans_1 ve 2": 1.64,
        "1. Yarı Çifte Şans_0 ve 2": 1.14,
        "1. Yarı Tek/Çift_Tek": 2.04,
        "1. Yarı Tek/Çift_Çift": 1.42,
        "Alt/Üst 1.5_Alt": 2.02,
        "Alt/Üst 1.5_Üst": 1.43,
        "Ev Sahibi Alt/Üst 0.5_Alt": 2.32,
        "Ev Sahibi Alt/Üst 0.5_Üst": 1.31,
        "Deplasman Alt/Üst 0.5_Alt": 2.09,
        "Deplasman Alt/Üst 0.5_Üst": 1.39,
        "1. Yarı Alt/Üst 0.5_Alt": 1.94,
        "1. Yarı Alt/Üst 0.5_Üst": 1.47,
        "Ev Sahibi 1. Yarı Altı/Üstü 0.5_Alt": 1.34,
        "Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst": 2.24,
        "Deplasman 1. Yarı Altı/Üstü 0.5_Alt": 1.28,
        "Deplasman 1. Yarı Altı/Üstü 0.5_Üst": 2.44,
        "Karşılıklı Gol_Var": 2.05,
        "Karşılıklı Gol_Yok": 1.42,
        "Tek / Çift_Tek": 1.77,
        "Tek / Çift_Çift": 1.6,
        "2. Yarı Karşılıklı Gol_Var": 4.35
      }
}

story = generate_story(match_data, verbose=False)
print(story)
