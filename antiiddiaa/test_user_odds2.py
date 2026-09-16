import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
from story_analyzer import generate_story

odds = {
    "Maç Sonucu_1": 2.44,
    "Maç Sonucu_0": 2.96,
    "Maç Sonucu_2": 2.3,
    "Handikaplı Maç Sonucu 1:0_1": 1.33,
    "Handikaplı Maç Sonucu 1:0_0": 3.76,
    "Handikaplı Maç Sonucu 1:0_2": 4.63,
    "Çifte Şans_1 ve 0": 1.33,
    "Çifte Şans_1 ve 2": 1.19,
    "Çifte Şans_0 ve 2": 1.29,
    "1. Yarı Sonucu_1": 3.11,
    "1. Yarı Sonucu_0": 1.92,
    "1. Yarı Sonucu_2": 2.95,
    "2. Yarı Sonucu_1": 2.76,
    "2. Yarı Sonucu_0": 2.28,
    "2. Yarı Sonucu_2": 2.63,
    "1. Yarı Karşılıklı Gol_Var": 4.15,
    "1. Yarı Karşılıklı Gol_Yok": 1.07,
    "Alt/Üst 1.5_Alt": 2.9,
    "Alt/Üst 1.5_Üst": 1.19,
    "Alt/Üst 2.5_Alt": 1.58,
    "Alt/Üst 2.5_Üst": 1.82,
    "Alt/Üst 3.5_Alt": 1.16,
    "Alt/Üst 3.5_Üst": 3.16,
    "Ev Sahibi Alt/Üst 1.5_Alt": 1.33,
    "Ev Sahibi Alt/Üst 1.5_Üst": 2.34,
    "Deplasman Alt/Üst 1.5_Alt": 1.36,
    "Deplasman Alt/Üst 1.5_Üst": 2.24,
    "1. Yarı Alt/Üst 0.5_Alt": 2.46,
    "1. Yarı Alt/Üst 0.5_Üst": 1.29,
    "Karşılıklı Gol_Var": 1.62,
    "Karşılıklı Gol_Yok": 1.77,
    "Tek / Çift_Tek": 1.75,
    "Tek / Çift_Çift": 1.64
}

match = {
    "ev_sahibi": "Kullanıcı",
    "deplasman": "Analiz",
    "oranlar": odds
}

story = generate_story(match)
print(story)
