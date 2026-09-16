import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix G5
content = content.replace(
    "if ust25 <= 1.55 and kg_yok <= 1.95:",
    "if ust25 <= 1.55 and kg_yok <= 1.75:"
)

rule_1478 = """class Rule1478(BaseRule):
    code = "1478"
    category = "SKOR"
    name = "Deplasman Baskını (Ev Sahibi Tıkanması)"
    description = "MS2 <= 2.20 + KG Var <= 1.50 + Ev 1.Yarı 0.5 Üst >= 1.75"
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ev_1y_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst", "Ev Sahibi 1. Yarı Alt/Üst 0.5_Üst"])
        
        if ms2 <= 2.20 and kg_var <= 1.50 and ev_1y_05_ust >= 1.75 and ev_1y_05_ust < 99.0:
            return True, "DEPLASMAN BASKINI: Maçta Deplasman takımı favori (2.00-2.20 arası) ve KG Var (1.45 civarı) oldukça olası gösterilmiş. Ancak Ev sahibinin ilk yarıda gol atma ihtimali (1.Yarı 0.5 Üst) 1.80'lere kadar çıkarak neredeyse sıfırlanmış. Bu durumda ev sahibi kilitlenir, deplasman erken golle kilidi açar ve maç 0-2, 0-3 veya 0-4 gibi tek taraflı bir deplasman şovuna dönüşür. KG Yok ve MS 2 oynanmalıdır."
            
        return False, ""

def get_all_rules():"""

content = content.replace("def get_all_rules():", rule_1478)
content = content.replace("Rule1477", "Rule1477, Rule1478")

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

story = story.replace(
    "elif any(r['code'] == '1477' for r in triggered_rules):",
    "elif any(r['code'] == '1478' for r in triggered_rules):\n        output.append(f\"- **Ana Tahmin:** Maç Sonucu 2 (Deplasman Kazanır) ve KG Yok\")\n        output.append(f\"- **Kombine Öneri:** MS 2 + Karşılıklı Gol Yok (veya 0-3, 0-4 Skor)\")\n    elif any(r['code'] == '1477' for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("Rule 1478 injected and G5 patched.")
