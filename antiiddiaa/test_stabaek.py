import json
import codecs
from story_analyzer import generate_story

match_data = {
  "ev_sahibi": "Stabaek",
  "deplasman": "Hodd IL",
  "saat": "",
  "lig": "Norveç 1. Lig",
  "tarih": "2026-07-26",
  "oranlar": {
    "Maç Sonucu_1": 1.27,
    "Maç Sonucu_0": 4.57,
    "Maç Sonucu_2": 5.3,
    "Handikaplı Maç Sonucu 0:1_1": 1.78,
    "Handikaplı Maç Sonucu 0:1_0": 3.66,
    "Handikaplı Maç Sonucu 0:1_2": 2.41,
    "1. Yarı Sonucu_1": 1.63,
    "1. Yarı Sonucu_0": 2.6,
    "1. Yarı Sonucu_2": 5.05,
    "2. Yarı Sonucu_1": 1.55,
    "2. Yarı Sonucu_0": 2.97,
    "2. Yarı Sonucu_2": 4.66,
    "1. Yarı Karşılıklı Gol_Var": 2.96,
    "1. Yarı Karşılıklı Gol_Yok": 1.17,
    "Alt/Üst 2.5_Alt": 2.72,
    "Alt/Üst 2.5_Üst": 1.21,
    "Alt/Üst 3.5_Alt": 1.67,
    "Alt/Üst 3.5_Üst": 1.69,
    "Alt/Üst 4.5_Alt": 1.22,
    "Alt/Üst 4.5_Üst": 2.64,
    "Ev Sahibi Alt/Üst 1.5_Alt": 2.81,
    "Ev Sahibi Alt/Üst 1.5_Üst": 1.19,
    "Ev Sahibi Alt/Üst 2.5_Alt": 1.56,
    "Ev Sahibi Alt/Üst 2.5_Üst": 1.81,
    "Ev Sahibi Alt/Üst 3.5_Alt": 1.14,
    "Ev Sahibi Alt/Üst 3.5_Üst": 3.19,
    "Deplasman Alt/Üst 0.5_Alt": 2.52,
    "Deplasman Alt/Üst 0.5_Üst": 1.25,
    "Deplasman Alt/Üst 1.5_Alt": 1.24,
    "Deplasman Alt/Üst 1.5_Üst": 2.57,
    "1. Yarı Alt/Üst 0.5_Alt": 3.96,
    "1. Yarı Alt/Üst 0.5_Üst": 1.07,
    "1. Yarı Alt/Üst 1.5_Alt": 1.64,
    "1. Yarı Alt/Üst 1.5_Üst": 1.7,
    "1. Yarı Alt/Üst 2.5_Alt": 1.11,
    "1. Yarı Alt/Üst 2.5_Üst": 3.42,
    "Ev Sahibi 1. Yarı Altı/Üstü 0.5_Alt": 2.55,
    "Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst": 1.25,
    "Deplasman 1. Yarı Altı/Üstü 0.5_Alt": 1.39,
    "Deplasman 1. Yarı Altı/Üstü 0.5_Üst": 2.09,
    "Karşılıklı Gol_Var": 1.36,
    "Karşılıklı Gol_Yok": 2.18,
    "2. Yarı Karşılıklı Gol_Var": 2.35,
    "2. Yarı Karşılıklı Gol_Yok": 1.3
  }
}

story = generate_story(match_data, verbose=False)
print(story)
