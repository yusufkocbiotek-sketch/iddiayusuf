import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf8') as f:
    text = f.read()

# I will replace the broken T11 + T27 combo with the proper T11, T27, T28
target = """class RuleT11(BaseRule):
    code = "T11"
    category = "YÖN"
    name = "En Düşük Favori Tuzağı"
    description = "MS1 <= 1.10 + KG Var <= 1.55 + IY 1.5 Üst <= 1.65"
    name = "Az Gollü Temiz Favori"
    description = "MS1 < 1.75 + KG Yok < 1.55 + 2.5 Alt < 1.60"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kgyok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        alt_25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        if 1.0 < ms1 < 1.75 and kgyok < 1.55 and alt_25 < 1.60:
            return True, "Ev sahibi maçı alır ancak skor tek taraflı ve az gollü (1-0, 2-0) olur."
        return False, ""
"""

replacement = """class RuleT11(BaseRule):
    code = "T11"
    category = "YÖN"
    name = "En Düşük Favori Tuzağı"
    description = "MS1 <= 1.10 + KG Var <= 1.55 + IY 1.5 Üst <= 1.65"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kgvar = get_odd(odds, ["Karşılıklı Gol_Var"])
        iy_15_ust = get_odd(odds, ["1. Yarı Alt/Üst 1.5_Üst", "1. Yarı Altı/Üstü 1.5_Üst"])
        if ms1 <= 1.15 and kgvar <= 1.55 and iy_15_ust <= 1.65:
            return True, "Ev sahibi kazanamaz; deplasman galibiyeti çok yüksek ihtimal."
        return False, ""

class RuleT27(BaseRule):
    code = "T27"
    category = "YÖN"
    name = "Az Gollü Temiz Favori"
    description = "MS1 < 1.75 + KG Yok < 1.55 + 2.5 Alt < 1.60"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kgyok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        alt_25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        if 1.0 < ms1 < 1.75 and kgyok < 1.55 and alt_25 < 1.60:
            return True, "Ev sahibi maçı alır ancak skor tek taraflı ve az gollü (1-0, 2-0) olur."
        return False, ""

class RuleT28(BaseRule):
    code = "T28"
    category = "YÖN"
    name = "Az Gollü Temiz Favori (Deplasman)"
    description = "MS2 < 1.75 + KG Yok < 1.55 + 2.5 Alt < 1.60"
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kgyok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        alt_25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        if 1.0 < ms2 < 1.75 and kgyok < 1.55 and alt_25 < 1.60:
            return True, "Deplasman maçı alır ancak skor tek taraflı ve az gollü (0-1, 0-2) olur."
        return False, ""
"""

# Handle potential \r\n differences
target_normalized = target.replace('\r\n', '\n').strip()
text_normalized = text.replace('\r\n', '\n')

if target_normalized in text_normalized:
    text_normalized = text_normalized.replace(target_normalized, replacement.replace('\r\n', '\n').strip())
    with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf8') as f:
        f.write(text_normalized)
    print("SUCCESS")
else:
    print("FAILED TO FIND TARGET")
