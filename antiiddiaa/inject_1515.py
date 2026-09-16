import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf8') as f:
    engine = f.read()

rule_1515 = """
class Rule1515(BaseRule):
    code = "1515"
    name = "Sahte Ev Sahibi Golü Tuzağı (Deplasman Fark Patlaması)"
    category = "GOL"
    description = "Deplasman Ağır Favori + Ev Sahibi Asla Kazanamaz (MS1 >= 4.00) + KG Var Düşük (Yem)"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms2 <= 1.50 and ms1 >= 4.00 and kg_var <= 1.45:
            return True, "SAHTE EV SAHİBİ GOLÜ: Deplasman takımı rahat kazanacak (1.50 altı). Ev sahibine ise kazanması imkansız bir oran (4.00 ve üzeri) açılmış. Buna rağmen KG Var oranı 1.45 gibi çok düşük ve komik bir seviyede. Bu, iddaacıların 'Ev sahibi nasıl olsa evinde 1 gol atar' diye düşünmesini sağlamak için kurulmuş devasa bir yemdir. Ev sahibi gol atamaz, Deplasman takımı fark atarak (0-3, 0-4) kazanır. KG Yok."
        return False, ""
"""

# Insert Rule1515 before "def get_all_rules():"
engine = engine.replace('def get_all_rules():', rule_1515 + '\ndef get_all_rules():')

# Add Rule1515 to anomaly_rules
engine = re.sub(r'(anomaly_rules = \[)', r'\1Rule1515, ', engine)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf8') as f:
    f.write(engine)

print("Rule 1515 injected!")
