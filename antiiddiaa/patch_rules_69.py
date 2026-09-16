import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Y7
y7_old = """    @classmethod
    def evaluate(cls, odds):
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        iy_ev_15_alt = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 1.5_Alt", "Ev Sahibi 1. Yarı Alt/Üst 1.5_Alt"])
        iy_dep_05_alt = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Alt", "Deplasman 1. Yarı Alt/Üst 0.5_Alt"])
        
        if ust35 <= 1.75 and kg_var <= 1.55 and iy_ev_15_alt <= 1.45 and iy_dep_05_alt <= 1.45:
            return True, "Bahis şirketleri 3.5 Üst ve KG Var oranlarını çok düşük açarak herkesi gollü bir maça inandırmış. Ancak ilk yarı alt oranlarının aşırı düşüklüğü, bu maçın tamamen bir illüzyon olduğunu gösteriyor. Maç 0-0 veya en fazla 1-0 gibi kısır bir skorla biter, Üst oynayan herkes kaybeder!"
        return False, ""
"""

y7_new = """    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        iy_ev_15_alt = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 1.5_Alt", "Ev Sahibi 1. Yarı Alt/Üst 1.5_Alt"])
        iy_dep_05_alt = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Alt", "Deplasman 1. Yarı Alt/Üst 0.5_Alt"])
        
        fav = min(ms1, ms2) if ms1 < 99.0 and ms2 < 99.0 else (ms1 if ms1 < 99.0 else ms2)
        
        if fav > 1.50 and ust35 <= 1.75 and kg_var <= 1.55 and iy_ev_15_alt <= 1.45 and iy_dep_05_alt <= 1.45:
            return True, "Bahis şirketleri 3.5 Üst ve KG Var oranlarını çok düşük açarak herkesi gollü bir maça inandırmış. Ancak ağır favori olmamasına rağmen ilk yarı alt oranlarının aşırı düşüklüğü, bu maçın tamamen bir illüzyon olduğunu gösteriyor. Maç 0-0 veya en fazla 1-0 gibi kısır bir skorla biter, Üst oynayan herkes kaybeder!"
        return False, ""
"""
content = content.replace(y7_old, y7_new)

# Add 1467
r1467_code = """class Rule1467(BaseRule):
    code = "1467"
    category = "SKOR"
    name = "Dengeli Kısır Çelişki (0-0)"
    description = "Tamamen denk takımlar (MS 2.20-2.60) + Beraberlik < 3.20 + Üst >= 1.60"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Alt/Üst 2,5_Üst"])
        
        if 2.20 <= ms1 <= 2.65 and 2.20 <= ms2 <= 2.65 and ms0 <= 3.20 and ust25 >= 1.60:
            return True, "Her iki takımın oranları birbirine çok yakın (tamamen dengeli), beraberlik oranı normalden düşük (<=3.20) ve maçın gollü geçme ihtimali düşük (Üst >= 1.60). Bu tam bir kilitlenme senaryosudur. İki takım da risk almaz, maç 0-0 biter."
        return False, ""

def get_all_rules():"""

content = content.replace("def get_all_rules():", r1467_code)

content = content.replace(
    "Rule999, Rule1462, Rule1463, Rule1464, Rule1465, Rule1466",
    "Rule999, Rule1462, Rule1463, Rule1464, Rule1465, Rule1466, Rule1467"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Rule Y7 fixed, Rule 1467 added.")
