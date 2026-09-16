import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

rule_1479 = """class Rule1479(BaseRule):
    code = "1479"
    category = "YÖN"
    name = "Favori Gol Kısırlığı Tuzağı (Deplasman Galibiyeti)"
    description = "MS1 Favori + Ev 1.5 Alt Düşük + KG Var Düşük = Matematiksel MS2 Sinyali"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms1 < ms2 and ev_15_alt <= 1.55 and kg_var <= 1.55 and ev_15_alt != 99.0:
            return True, "FAVORİ GOL KISIRLIĞI TUZAĞI: Maçın favorisi Ev Sahibi gösterilmiş (MS1). Ancak Ev sahibinin 1.5 Alt oranı (maksimum 1 gol atar beklentisi) ve KG Var oranı çok düşük açılmış. Ev sahibi maksimum 1 gol atacaksa ve deplasman kesin gol bulacaksa, ev sahibinin maçı kazanma şansı matematiksel olarak yoktur! Bu durum MS1 oranının tamamen tuzak olduğunu kanıtlar. Deplasman takımı maçı kazanmaya veya puan almaya çok yakındır (X2 / MS2)."
            
        return False, ""

def get_all_rules():"""

content = content.replace("def get_all_rules():", rule_1479)
content = content.replace("Rule1478", "Rule1478, Rule1479")

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

story = story.replace(
    "elif any(r['code'] == '1478' for r in triggered_rules):",
    "elif any(r['code'] == '1479' for r in triggered_rules):\n        output.append(f\"- **Ana Tahmin:** Maç Sonucu 2 (Deplasman Kazanır) veya 02 Çifte Şans\")\n        output.append(f\"- **Kombine Öneri:** 02 Çifte Şans + Karşılıklı Gol Yok / 2.5 Alt\")\n    elif any(r['code'] == '1478' for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("Rule 1479 injected.")
