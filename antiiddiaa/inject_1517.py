import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf8') as f:
    engine = f.read()

rule_1517 = """
class Rule1517(BaseRule):
    code = "1517"
    name = "Matematiksel KG Var Paradoksu (Sürpriz Deplasman Golü)"
    category = "GOL_VE_YÖN"
    description = "Ev sahibi 3 gol atamazken maçın 3 gollü beklenmesi ama KG Var oranının şişirilmesi."
    
    @classmethod
    def evaluate(cls, odds):
        ev_alt25 = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Alt", "Ev Sahibi Altı/Üstü 2.5_Alt"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ev_alt25 > 0 and ev_alt25 <= 1.45 and ev_alt25 != 99.0 and ust25 <= 1.65 and kg_var >= 1.75 and kg_var != 99.0:
            return True, "MATEMATİKSEL KG VAR PARADOKSU: İddaa 'Ev Sahibi 2.5 Alt' oranını düşük tutarak ev sahibinin tek başına 3 gol atamayacağını söylüyor. Fakat aynı iddaa maçın '2.5 Üst' biteceğini de düşük oranla savunuyor. Ev sahibi 3 gol atamayacaksa, o 3. gol mecburen deplasman takımından gelecektir! Buna rağmen KG Var oranı 1.75'in üzerine çıkarılarak millet KG Yok'a (deplasman gol atamaz) yönlendiriliyor. Bu korkunç bir tuzaktır. Deplasman kesin gol atar ve maç 2.5 Üst (Örn: 2-1) biter."
        return False, ""
"""

# Insert Rule1517 before get_all_rules()
engine = engine.replace('def get_all_rules():', rule_1517 + '\ndef get_all_rules():')
# Add Rule1517 to paradox_rules (Phase 1)
engine = re.sub(r'(paradox_rules = \[)', r'\1Rule1517, ', engine)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf8') as f:
    f.write(engine)

# Update story_analyzer.py
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf8') as f:
    analyzer = f.read()

new_1517 = "\n        '1517': (\"Matematiksel KG Var Paradoksu\", \"Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 2-1)\"),"
analyzer = analyzer.replace("predictions = {", "predictions = {" + new_1517)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf8') as f:
    f.write(analyzer)

# Update Kurallar_Kitabi.md
md_rule = "\n| **1517** | Matematiksel KG Var Paradoksu | GOL_VE_YÖN | **DEPLASMAN GOLÜ:** Ev Sahibi 2.5 Alt oranı düşük (<=1.45) ve Maç 2.5 Üst oranı düşük (<=1.65) olmasına rağmen KG Var oranı çok yüksekse (>=1.75), bu matematiksel olarak eksik golü deplasmanın atacağının kanıtıdır. KG Var ve 2.5 Üst (2-1) aranır. |\n"
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Kurallar_Kitabi.md', 'a', 'utf8') as f:
    f.write(md_rule)

print("Rule 1517 Injected Successfully.")
