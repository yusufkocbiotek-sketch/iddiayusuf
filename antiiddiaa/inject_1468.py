import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

rule_1468 = """class Rule1468(BaseRule):
    code = "1468"
    category = "SKOR"
    name = "Matematiksel Paradoks (Sahte Favori Çöküşü 1-2/1-3)"
    description = "Favori (MS1 <= 2.00) + KG Var (<= 1.55) + Ev 1.5 Alt < Ev 1.5 Üst"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt"])
        ev_15_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Üst"])
        
        if ms1 <= 2.00 and kg_var <= 1.55 and ev_15_alt < ev_15_ust:
            return True, "BÜYÜK ÇELİŞKİ: Ev sahibi favori (1.89) gösterilmiş, KG Var (1.46) bekleniyor ancak Ev Sahibinin 1.5 Alt oranı (1.60), 1.5 Üst oranından (1.76) düşük! Bu matematiksel bir paradokstur. Ev sahibi en fazla 1 gol atabilecekse ve maç KG Var bitecekse, ev sahibinin maçı kazanma şansı MATEMATİKSEL OLARAK YOKTUR (Skor en iyi ihtimalle 1-1, veya 1-2, 1-3 olur). MS 1 tamamen bir tuzaktır. Deplasman kaybetmez (X2) ve Deplasman galibiyeti çok yüksek ihtimaldir."
        
        # Deplasman favorisi için aynı paradoks
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt"])
        dep_15_ust = get_odd(odds, ["Deplasman Alt/Üst 1.5_Üst"])
        
        if ms2 <= 2.00 and kg_var <= 1.55 and dep_15_alt < dep_15_ust:
             return True, "BÜYÜK ÇELİŞKİ: Deplasman favori gösterilmiş, KG Var bekleniyor ancak Deplasmanın 1.5 Alt oranı, Üst oranından düşük. Deplasman en fazla 1 gol atabilecekse ve maç KG Var olacaksa deplasman kazanamaz (En iyi ihtimal 1-1 veya 2-1). MS 2 tamamen bir tuzaktır. Ev sahibi kaybetmez (1X)."
             
        return False, ""

def get_all_rules():"""

content = content.replace("def get_all_rules():", rule_1468)

content = content.replace(
    "Rule999, Rule1462, Rule1463, Rule1464, Rule1465, Rule1466, Rule1467",
    "Rule999, Rule1462, Rule1463, Rule1464, Rule1465, Rule1466, Rule1467, Rule1468"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Rule 1468 Paradoks injected.")
