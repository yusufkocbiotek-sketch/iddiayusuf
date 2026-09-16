import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf8') as f:
    engine = f.read()

rule_t70 = """
class RuleT70(BaseRule):
    code = "T70"
    name = "Süper Kısır Çift Tuzağı (0-0 / 1-1 İllüzyonu)"
    category = "SKOR"
    description = "Üst ve KG Var favori gösterilmesine rağmen Tek oranının çok yüksek, Çift oranının düşük kalması."
    
    @classmethod
    def evaluate(cls, odds):
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        tek = get_odd(odds, ["Tek/Çift_Tek"])
        cift = get_odd(odds, ["Tek/Çift_Çift"])
        
        if ust25 <= 1.65 and kg_var <= 1.65 and tek >= 1.75 and tek != 99.0 and cift <= 1.70:
            return True, "SÜPER KISIR ÇİFT TUZAĞI (0-0 / 1-1): Piyasa KG Var ve Üst oranlarını çok düşük tutarak herkesi gollü bir maça (özellikle 2-1 gibi Tek skorlara) yönlendiriyor. Ancak Tek oranı anormal derecede yüksek (1.75+) ve Çift oranı çok düşük (1.70 altı). Bu devasa çelişki, İddaa'nın maçın gollü (2-1 vb.) geçmeyeceğini, tam tersine 0-0 veya 1-1 gibi Kısır-Çift bir skorla kilitleneceğini bildiğini gösterir. Kesinlikle Alt ve Beraberlik aranmalıdır."
        return False, ""
"""

engine = engine.replace('def get_all_rules():', rule_t70 + '\ndef get_all_rules():')
engine = re.sub(r'(anomaly_rules = \[)', r'\1RuleT70, ', engine)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf8') as f:
    f.write(engine)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf8') as f:
    analyzer = f.read()

new_t70 = "\n        'T70': (\"Süper Kısır Çift Tuzağı (0-0 / 1-1)\", \"Beraberlik (0) + 2.5 Alt (Sürpriz Skor: 0-0 / 1-1)\"),"
analyzer = analyzer.replace("predictions = {", "predictions = {" + new_t70)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf8') as f:
    f.write(analyzer)

md_rule = "\n| **T70** | Süper Kısır Çift Tuzağı (0-0 / 1-1 İllüzyonu) | SKOR | **KISIR ÇİFT:** 2.5 Üst ve KG Var 1.65'in altında olmasına rağmen Tek oranı 1.75 ve üzerindeyse, Çift ise 1.70'in altındaysa bu bir tuzaktır. Gollü (2-1) beklenirken maç 0-0 veya 1-1 kilitlenir. |\n"
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Kurallar_Kitabi.md', 'a', 'utf8') as f:
    f.write(md_rule)

print("T70 Injected.")
