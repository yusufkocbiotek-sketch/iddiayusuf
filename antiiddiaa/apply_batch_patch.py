import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1468
content = content.replace(
    "if ms1 <= 2.00 and kg_var <= 1.55 and ev_15_alt < ev_15_ust:",
    "if ms1 <= 2.00 and kg_var <= 1.55 and ev_15_alt <= 1.45:"
)
content = content.replace(
    "if ms2 <= 2.00 and kg_var <= 1.55 and dep_15_alt < dep_15_ust:",
    "if ms2 <= 2.00 and kg_var <= 1.55 and dep_15_alt <= 1.45:"
)

# Fix 1474
content = content.replace(
    "if ms0 <= 2.50 and (ms0 < ms1 or ms0 < ms2):",
    "if ms0 <= 2.50 and (ms0 < ms1 - 0.10 or ms0 < ms2 - 0.10):"
)

# Add 1475
rule_1475 = """class Rule1475(BaseRule):
    code = "1475"
    category = "SKOR"
    name = "Yalancı İmparator Tuzağı (1.0X Favori Çöküşü)"
    description = "Favori <= 1.15 + Favori 2.5 Alt < Favori 2.5 Üst"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_25_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Alt"])
        ev_25_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Üst"])
        dep_25_alt = get_odd(odds, ["Deplasman Alt/Üst 2.5_Alt"])
        dep_25_ust = get_odd(odds, ["Deplasman Alt/Üst 2.5_Üst"])
        
        is_trap = False
        if ms1 <= 1.15 and ev_25_alt < ev_25_ust: is_trap = True
        if ms2 <= 1.15 and dep_25_alt < dep_25_ust: is_trap = True
        
        if is_trap:
             return True, "YALANCI İMPARATOR TUZAĞI: Takımlardan birine 1.0X veya 1.1X gibi inanılmaz derecede favori oranı açılmış. Ancak kendi takımlarının 2.5 Alt oranı, Üst oranından daha düşük. Yani bürolar bu kadar kesin favori gösterdikleri takımın 3 gol bile atamayacağını söylüyor! Bu korkunç bir tuzaktır. Favori takım maçı kazanamaz veya büyük ihtimalle kaybeder. Zayıf takımın çifte şansı (1X veya 02) denenebilir."
             
        return False, ""

def get_all_rules():"""

content = content.replace("def get_all_rules():", rule_1475)
content = content.replace("Rule1474", "Rule1474, Rule1475")

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)


with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

# Add logic for 1475 output
story = story.replace(
    "elif any(r['code'] == '1474' for r in triggered_rules):",
    "elif any(r['code'] == '1475' for r in triggered_rules):\n        output.append(f\"- **Ana Tahmin:** Sürpriz Çifte Şans (Favorinin Karşısı: 1X / 02)\")\n        output.append(f\"- **Kombine Öneri:** Sürpriz Çifte Şans + Karşılıklı Gol Var\")\n    elif any(r['code'] == '1474' for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("Patch applied.")
