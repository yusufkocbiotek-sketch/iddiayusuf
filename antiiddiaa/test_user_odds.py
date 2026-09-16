import sys
sys.stdout.reconfigure(encoding='utf-8')
from story_analyzer import generate_story

match_data = {
    "Ev Sahibi": "Ev Sahibi",
    "Deplasman": "Deplasman",
    "Lig": "Bilinmiyor",
    "saat": "00:00",
    "oranlar": {
        "Maç Sonucu_1": 3.38,
        "Maç Sonucu_0": 3.09,
        "Maç Sonucu_2": 1.78,
        "Handikaplı Maç Sonucu 1:0_1": 1.59,
        "Handikaplı Maç Sonucu 1:0_0": 3.5,
        "Handikaplı Maç Sonucu 1:0_2": 3.1,
        "Çifte Şans_1 ve 0": 1.58,
        "Çifte Şans_1 ve 2": 1.18,
        "Çifte Şans_0 ve 2": 1.14,
        "1. Yarı Sonucu_1": 3.88,
        "1. Yarı Sonucu_0": 2.05,
        "1. Yarı Sonucu_2": 2.3,
        "Alt/Üst 1.5_Alt": 3.32,
        "Alt/Üst 1.5_Üst": 1.14,
        "Alt/Üst 2.5_Alt": 1.73,
        "Alt/Üst 2.5_Üst": 1.65,
        "Alt/Üst 3.5_Alt": 1.23,
        "Alt/Üst 3.5_Üst": 2.72,
        "1. Yarı Alt/Üst 0.5_Alt": 2.71,
        "1. Yarı Alt/Üst 0.5_Üst": 1.23,
        "Karşılıklı Gol_Var": 1.55,
        "Karşılıklı Gol_Yok": 1.87,
        "Tek / Çift_Tek": 1.77,
        "Tek / Çift_Çift": 1.62
    }
}

print(generate_story(match_data))
