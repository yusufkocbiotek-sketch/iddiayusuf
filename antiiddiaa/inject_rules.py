import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_rules = """
# ==========================================
# KULLANICI ÖZEL SERİ KURALLARI (999 & 1460 Serisi)
# ==========================================

class Rule999(BaseRule):
    code = "999"
    category = "İSTİSNA"
    name = "Yanıltıcı Üretkenlik & Golsüz İstisnası"
    description = "MS Favori <= 1.40 + KG Var <= 1.25 + Üst 2.5 <= 1.55"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Alt/Üst 2,5_Üst"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Alt/Üst 3,5_Üst"])
        
        fav_odd = min(ms1, ms2) if ms1 < 99.0 and ms2 < 99.0 else (ms1 if ms1 < 99.0 else ms2)
        ust_val = min(ust25, ust35) if ust25 < 99.0 and ust35 < 99.0 else (ust25 if ust25 < 99.0 else ust35)
        
        if fav_odd <= 1.40 and kg_var <= 1.25 and ust_val <= 1.55:
            return True, "BU MAÇ KESİN GOLLÜDÜR! Ancak çok nadir de olsa 0-0 istisnası görülebilir. Oranlar ne kadar kesin görünürse görünsün, oran verilerinin hesap dışı bıraktığı anlık şans ve form eksiklikleriyle bu %5-6'lık 0-0 riski her zaman sistemde tutulmalıdır."
        return False, ""

class Rule1462(BaseRule):
    code = "1462"
    category = "SKOR"
    name = "Belirgin Ev Üstünlüğü (İlk Yarı Kapalı, 1-0)"
    description = "MS1 1.93-2.02 + Beraberlik 2.48-2.58"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        if 1.93 <= ms1 <= 2.02 and 2.48 <= ms0 <= 2.58:
            return True, "Belirgin Ev Üstünlüğü, İlk Yarı Tamamen Kapalı, Tek Taraflı 1-0. İlk yarı 0-0 kilitlenir, maç ev sahibinin tek golüyle 1-0 biter."
        return False, ""

class Rule1463(BaseRule):
    code = "1463"
    category = "SKOR"
    name = "Tamamen Dengeli Beraberlik (0-0)"
    description = "MS1 2.25-2.35 + Beraberlik en düşük"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        if 2.25 <= ms1 <= 2.35 and ms0 <= ms1 and ms0 <= ms2:
            return True, "Tamamen Dengeli. Beraberlik En Güçlü. Tamamen Kapalı 0-0. İlk yarı 0-0 başlar, 0-0 biter."
        return False, ""

class Rule1464(BaseRule):
    code = "1464"
    category = "SKOR"
    name = "Hafif Ev Üstünlüğü (Gollü, 3-1)"
    description = "MS1 2.15-2.25 + Beraberlik 2.35-2.45"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        if 2.15 <= ms1 <= 2.25 and 2.35 <= ms0 <= 2.45:
            return True, "Hafif Ev Üstünlüğü. İlk Yarı Karşılıklı. İkinci Yarı Ev Üstünlüğü. İlk Yarı 1-1 geçer, maç sonu 3-1 ev sahibi lehine biter."
        return False, ""

class Rule1465(BaseRule):
    code = "1465"
    category = "SKOR"
    name = "Uluslararası: Ev Favorisi Görünümlü Konuk Galibiyeti (0-1)"
    description = "MS1 1.82-1.90 + MS2 >= 3.75 + Beraberlik 2.45-2.58"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        if 1.82 <= ms1 <= 1.90 and ms2 >= 3.75 and 2.45 <= ms0 <= 2.58 and ev_15_alt <= 1.28 and kg_yok <= 1.35:
            return True, "Belirgin Ev Favorisi Görünümlü İlk Yarı Tamamen Kapalı Tek Taraflı 0-1 Konuk Galibiyeti. Ev belirgin favori olarak başlar, ilk yarı 0-0 biter; ikinci yarı konukun tek golüyle maç 0-1 konuk galibiyetiyle sonuçlanır."
        return False, ""

def get_all_rules():
"""

content = content.replace("def get_all_rules():\n", new_rules)

array_old = """RuleT35, RuleT36, RuleT68,
        RuleY1, RuleY2, RuleY3, RuleY4, RuleY5, RuleY6, RuleY7
    ]"""
array_new = """RuleT35, RuleT36, RuleT68,
        RuleY1, RuleY2, RuleY3, RuleY4, RuleY5, RuleY6, RuleY7,
        Rule999, Rule1462, Rule1463, Rule1464, Rule1465
    ]"""
content = content.replace(array_old, array_new)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Rule 999 and 1460 Series injected.')
