import json
from story_analyzer import generate_story
import rule_engine

match_data = {
    "lig": "STANDART",
    "ev_sahibi": "Caroline Springs George Cross FC",
    "deplasman": "Preston Lions FC",
    "oranlar": {
        "Maç Sonucu_1": 4.14,
        "Maç Sonucu_0": 3.51,
        "Maç Sonucu_2": 1.49,
        "Çifte Şans_1X": 1.83,
        "Çifte Şans_12": 1.11,
        "Çifte Şans_X2": 1.07,
        "İlk Yarı Sonucu_1": 4.52,
        "İlk Yarı Sonucu_0": 2.14,
        "İlk Yarı Sonucu_2": 1.98,
        "Alt/Üst 2.5_Alt": 1.85,
        "Alt/Üst 2.5_Üst": 1.54,
        "Karşılıklı Gol_Var": 1.55,
        "Karşılıklı Gol_Yok": 1.82,
        "Tek / Çift_Tek": 1.70,
        "Tek / Çift_Çift": 1.64
    }
}

rule_engine.CURRENT_MATCH = match_data
story = generate_story(match_data, verbose=True)
print(story)
