import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

old_1514 = '''class Rule1514(BaseRule):
    code = "1514"
    name = "Aşırı Düşük KG Var Tuzağı (Buzul Sessizliği)"
    category = "SKOR"
    description = "KG Var oranı çok düşük olmasına rağmen ilk yarı 1.5 Üst oranı çok yüksekse maç kısır biter."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        iy_15_ust = get_odd(odds, ["1. Yarı Alt/Üst 1.5_Üst", "İlk Yarı Altı/Üstü 1.5_Üst"])
        
        if 0 < kg_var <= 1.35 and iy_15_ust >= 1.60:'''

new_1514 = '''class Rule1514(BaseRule):
    code = "1514"
    name = "Aşırı Düşük KG Var Tuzağı (Buzul Sessizliği)"
    category = "SKOR"
    description = "KG Var oranı çok düşük olmasına rağmen ilk yarı 1.5 Üst oranı çok yüksekse maç kısır biter."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        iy_15_ust = get_odd(odds, ["1. Yarı Alt/Üst 1.5_Üst", "İlk Yarı Altı/Üstü 1.5_Üst"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        is_balanced = ms1 != 99.0 and ms2 != 99.0 and min(ms1, ms2) >= 1.85
        
        if 0 < kg_var <= 1.35 and iy_15_ust >= 1.60 and is_balanced:'''

content = content.replace(old_1514, new_1514)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)
