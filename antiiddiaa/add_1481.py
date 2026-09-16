import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

rule_1481 = """class Rule1481(BaseRule):
    code = "1481"
    category = "YÖN"
    name = "Aşırı Gollü Sahte Favori Tuzağı (Deplasman Sürprizi)"
    description = "MS1 Favori + KG Var Çok Düşük + 3.5 Üst Çok Düşük = Sürpriz Deplasman (X2)"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        
        if ms1 < ms2 and ms1 <= 1.70 and kg_var <= 1.35 and ust35 <= 1.85 and ust35 != 99.0:
            return True, "AŞIRI GOLLÜ SAHTE FAVORİ TUZAĞI: Ev sahibi 1.6X oranla favori gösterilmiş ve maçın 4+ gol (3.5 Üst) ile KG Var şeklinde biteceği çok bariz bir şekilde (aşırı düşük oranlarla) fiyatlanmış. Bu durum oyuncuları 'Ev sahibi 3-1 veya 4-1 kazanır' (MS1 + Üst) tuzağına çekmek içindir. İddaa böylesine gollü ve net bir favori galibiyetini bu kadar bağırarak vermez. Bu, deplasman takımının sürpriz bir şekilde maçta üstünlük kuracağı (Örn: 1-3, 2-2) devasa bir tuzaktır. MS2 veya X2 denenmelidir."
            
        return False, ""

def get_all_rules():"""

content = content.replace("def get_all_rules():", rule_1481)
content = content.replace("Rule1480", "Rule1480, Rule1481")

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

# Add 1481 to the generic trap list
story = story.replace(
    "if any(r['code'] in ['T32', 'T35', 'T9', '1470', '1478', '1479', '1480'] for r in triggered_rules):",
    "if any(r['code'] in ['T32', 'T35', 'T9', '1470', '1478', '1479', '1480', '1481'] for r in triggered_rules):"
)

# Insert specific branch for 1481
story = story.replace(
    "elif any(r['code'] == '1480' for r in triggered_rules):",
    "elif any(r['code'] == '1481' for r in triggered_rules):\n        output.append(f\"- **Ana Tahmin:** Sürpriz Deplasman Galibiyeti (MS 2) veya 02 Çifte Şans\")\n        output.append(f\"- **Kombine Öneri:** 02 Çifte Şans + 2.5 Gol Üst (Sürpriz Skor: 1-3 / 2-2)\")\n    elif any(r['code'] == '1480' for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("Rule 1481 injected.")
