import codecs
import re

# Update rule_engine.py
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf8') as f:
    engine = f.read()

rule_1516 = """
class Rule1516(BaseRule):
    code = "1516"
    name = "Sahte Deplasman Golü Tuzağı (Ev Sahibi Katliamı)"
    category = "GOL"
    description = "Ev Sahibi Ağır Favori + Deplasman Asla Kazanamaz (MS2 >= 4.00) + KG Var Düşük (Yem)"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms1 <= 1.40 and ms2 >= 4.00 and kg_var <= 1.45:
            return True, "SAHTE DEPLASMAN GOLÜ: Ev sahibi takımı rahat kazanacak (1.40 altı). Deplasmana ise kazanması imkansız bir oran (4.00 ve üzeri) açılmış. Buna rağmen KG Var oranı 1.45 gibi çok düşük bir seviyede. Bu, iddaacıların 'Ev sahibi zaten yener, Deplasman da bari 1 gol atar' diye düşünmesini sağlamak için kurulmuş devasa bir yemdir. Deplasman gol atamaz, Ev Sahibi takımı fark atarak (3-0, 4-0, 6-0) kazanır. KG Yok."
        return False, ""
"""

engine = engine.replace('def get_all_rules():', rule_1516 + '\ndef get_all_rules():')
engine = re.sub(r'(anomaly_rules = \[)', r'\1Rule1516, ', engine)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf8') as f:
    f.write(engine)

# Update story_analyzer.py
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf8') as f:
    analyzer = f.read()

new_1516 = "\n        '1516': (\"Sahte Deplasman Golü Tuzağı (Ev Sahibi Katliamı)\", \"MS 1 + Karşılıklı Gol Yok (Sürpriz Skor: 3-0 / 4-0 / 6-0)\"),"
analyzer = analyzer.replace("predictions = {", "predictions = {" + new_1516)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf8') as f:
    f.write(analyzer)

# Update Kurallar_Kitabi.md
rule_md = "\n| **1516** | Sahte Deplasman Golü Tuzağı (Ev Sahibi Katliamı) | GOL | **SAHTE DEPLASMAN GOLÜ:** Ev sahibi takımı rahat kazanacak (1.40 altı). Deplasmana ise kazanması imkansız bir oran (4.00 ve üzeri) açılmış. Buna rağmen KG Var oranı 1.45 gibi çok düşük bir seviyede. Bu, iddaacıların 'Ev sahibi zaten yener, Deplasman da bari 1 gol atar' diye düşünmesini sağlamak için kurulmuş devasa bir yemdir. Deplasman gol atamaz, Ev Sahibi takımı fark atarak (3-0, 4-0, 6-0) kazanır. KG Yok. |\n"
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Kurallar_Kitabi.md', 'a', 'utf8') as f:
    f.write(rule_md)

print("Rule 1516 injected to all files!")
