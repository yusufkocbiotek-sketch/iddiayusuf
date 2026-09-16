import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

rule_1480 = """class Rule1480(BaseRule):
    code = "1480"
    category = "YÖN"
    name = "Tek Skor Darboğazı Tuzağı (Sahte Deplasman Favorisi)"
    description = "MS2 Favori + KG Var Düşük + 2.5 Üst Düşük + Ev 1.5 Alt Düşük = MS1 Tuzağı"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        
        if ms2 < ms1 and ms2 <= 1.95 and kg_var <= 1.50 and ust25 <= 1.60 and ev_15_alt <= 1.35 and ev_15_alt != 99.0:
            return True, "TEK SKOR DARBOĞAZI TUZAĞI: Deplasman favori, KG Var ve 2.5 Üst oranları çok düşük. Normal şartlarda maçın 1-2 veya 1-3 biteceği fiyatlanmış. Ancak Ev sahibinin 1.5 Alt oranı (maksimum 1 gol) da çok düşük. Bu durum maçı tek bir matematiksel senaryoya (1-2 deplasman galibiyetine) sıkıştırır. İddaa büroları asla bu kadar bariz bir 'tek skor' senaryosunu ucuza vermez. Bu devasa bir tuzaktır; maç MS1 veya 1X çifte şans ile ev sahibine gidecek ve maç alt bitecektir (Örn: 2-0, 1-0)."
            
        return False, ""

def get_all_rules():"""

content = content.replace("def get_all_rules():", rule_1480)
content = content.replace("Rule1479", "Rule1479, Rule1480")

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

# Also add 1480 to the generic trap list
story = story.replace(
    "if any(r['code'] in ['T32', 'T35', 'T9', '1470', '1478', '1479'] for r in triggered_rules):",
    "if any(r['code'] in ['T32', 'T35', 'T9', '1470', '1478', '1479', '1480'] for r in triggered_rules):"
)

# Insert specific branch for 1480
story = story.replace(
    "elif any(r['code'] == '1479' for r in triggered_rules):",
    "elif any(r['code'] == '1480' for r in triggered_rules):\n        output.append(f\"- **Ana Tahmin:** Maç Sonucu 1 veya 1X Çifte Şans\")\n        output.append(f\"- **Kombine Öneri:** MS 1 + Karşılıklı Gol Yok / 2.5 Alt\")\n    elif any(r['code'] == '1479' for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("Rule 1480 injected.")
