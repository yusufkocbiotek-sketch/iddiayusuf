import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

rule_g12 = """class RuleG12(BaseRule):
    code = "G12"
    category = "GOL"
    name = "Katliam Senaryosu (Ağır Favori Düellosu)"
    description = "Favori <= 1.30 + KG Var <= 1.65 + 3.5 Üst <= 1.80"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Alt/Üst 3,5_Üst"])
        
        if (ms1 <= 1.30 or ms2 <= 1.30) and kg_var <= 1.65 and ust35 <= 1.80:
            return True, "KATLİAM SENARYOSU: Ağır bir favori var ve maçın 4 gol veya üzerine çıkacağı (3.5 Üst) net bir şekilde fiyatlanmış. Zayıf takımın da gol atması bekleniyor. Bu bir kilitlenme veya sürpriz maçı değil; favorinin 3-1, 4-1, 5-2 gibi skorlarla şov yapacağı bir düellodur. Gollere yönelinmelidir."
        return False, ""

def get_all_rules():"""

content = content.replace("def get_all_rules():", rule_g12)

content = content.replace(
    "Rule999, Rule1462, Rule1463, Rule1464, Rule1465, Rule1466, Rule1467, Rule1468, Rule1469, Rule1470",
    "Rule999, Rule1462, Rule1463, Rule1464, Rule1465, Rule1466, Rule1467, Rule1468, Rule1469, Rule1470, RuleG12"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)


with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

# Update gol_beklentisi logic to include ust35 and G11, G12
old_gol_beklentisi = 'gol_beklentisi = "YÜKSEK" if any(r[\'code\'] in [\'G1\', \'G8\', \'T27\', \'1468\'] for r in triggered_rules) or ust25 < 1.60 else "DÜŞÜK"'

new_gol_beklentisi = """ust35 = rule_engine.get_odd(odds, ["Alt/Üst 3.5_Üst", "Alt/Üst 3,5_Üst"])
    gol_beklentisi = "YÜKSEK" if any(r['code'] in ['G1', 'G8', 'G11', 'G12', 'T27', '1468'] for r in triggered_rules) or ust25 < 1.60 or ust35 < 1.90 else "DÜŞÜK" """

story = story.replace(old_gol_beklentisi, new_gol_beklentisi)

# Also add G12 explicit handling in story_analyzer.py
story = story.replace(
    "    elif any(r['code'] == 'G3' for r in triggered_rules):",
    "    elif any(r['code'] == 'G12' for r in triggered_rules):\n        output.append(f\"- **Ana Tahmin:** Maç Sonucu {'1' if ms1 < ms2 else '2'} + Karşılıklı Gol Var\")\n        output.append(f\"- **Kombine Öneri:** 3.5 Gol Üst\")\n    elif any(r['code'] == 'G3' for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("G12 and gol_beklentisi fixed.")
