import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from story_analyzer import generate_story

match = {
    "ev_sahibi": "Hollanda",
    "deplasman": "İsveç",
    "tarih": "2026-06-03",
    "lig": "",
    "oranlar": {
        "Maç Sonucu_1": 1.48,
        "Maç Sonucu_0": 3.63,
        "Maç Sonucu_2": 4.74,
        "Çifte Şans_1 ve 0": 1.07,
        "Çifte Şans_1 ve 2": 1.14,
        "Çifte Şans_0 ve 2": 2.01,
        "Alt/Üst 1.5_Alt": 3.2,
        "Alt/Üst 1.5_Üst": 1.18,
        "Alt/Üst 2.5_Alt": 1.69,
        "Alt/Üst 2.5_Üst": 1.76,
        "Alt/Üst 3.5_Alt": 1.2,
        "Alt/Üst 3.5_Üst": 3.09,
        "Karşılıklı Gol_Var": 1.79,
        "Karşılıklı Gol_Yok": 1.66,
        "İlk Yarı Sonucu_1": 2.02,
        "İlk Yarı Sonucu_0": 2.1,
        "İlk Yarı Sonucu_2": 5.23,
        "İlk Yarı Alt/Üst 0.5_Alt": 2.73,
        "İlk Yarı Alt/Üst 0.5_Üst": 1.26,
        "İlk Yarı Alt/Üst 1.5_Alt": 1.3,
        "İlk Yarı Alt/Üst 1.5_Üst": 2.57,
        "İlk Yarı Karşılıklı Gol_Var": 4.68,
        "İlk Yarı Karşılıklı Gol_Yok": 1.06,
        "İkinci Yarı Karşılıklı Gol_Var": 3.65,
        "İkinci Yarı Karşılıklı Gol_Yok": 1.45,
        "İlk Yarı Alt/Üst 2.5_Alt": 1.8,
        "İlk Yarı Alt/Üst 2.5_Üst": 2.2,
        "İkinci Yarı Alt/Üst 2.5_Alt": 1.85,
        "İkinci Yarı Alt/Üst 2.5_Üst": 2.15,
        "İlk Yarı Alt/Üst 3.5_Alt": 1.9,
        "İlk Yarı Alt/Üst 3.5_Üst": 3.1,
        "İkinci Yarı Alt/Üst 3.5_Alt": 1.95,
        "İkinci Yarı Alt/Üst 3.5_Üst": 3.05
    }
}

print(generate_story(match))
