import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix G12 and Add 1473
g12_old = """class RuleG12(BaseRule):
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
"""

g12_new = """class RuleG12(BaseRule):
    code = "G12"
    category = "GOL"
    name = "Katliam Senaryosu (Ağır Favori Düellosu)"
    description = "Favori <= 1.30 + KG Var <= 1.65 + 3.5 Üst <= 1.80 + Favori 2.5 Üst < 1.60"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Alt/Üst 3,5_Üst"])
        ev_25_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Üst"])
        dep_25_ust = get_odd(odds, ["Deplasman Alt/Üst 2.5_Üst"])
        
        is_fav_strong = False
        if ms1 <= 1.30 and ev_25_ust < 1.60: is_fav_strong = True
        if ms2 <= 1.30 and dep_25_ust < 1.60: is_fav_strong = True
        # if missing, assume strong for G12 fallback
        if ms1 <= 1.30 and ev_25_ust == 99.0: is_fav_strong = True
        if ms2 <= 1.30 and dep_25_ust == 99.0: is_fav_strong = True

        if (ms1 <= 1.30 or ms2 <= 1.30) and kg_var <= 1.65 and ust35 <= 1.80 and is_fav_strong:
            return True, "KATLİAM SENARYOSU: Ağır bir favori var ve maçın 4 gol veya üzerine çıkacağı (3.5 Üst) net bir şekilde fiyatlanmış. Favorinin 3+ gol atması yüksek ihtimal (Fav 2.5 Üst düşük). Bu bir kilitlenme veya sürpriz maçı değil; favorinin 3-1, 4-1, 5-2 gibi skorlarla şov yapacağı bir düellodur. Gollere yönelinmelidir."
        return False, ""

class Rule1473(BaseRule):
    code = "1473"
    category = "SKOR"
    name = "Çapraz Sürpriz Düellosu (2-2 Tuzağı)"
    description = "Favori <= 1.30 + 3.5 Üst <= 1.65 + Favori 2.5 Üst >= 1.60"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Alt/Üst 3,5_Üst"])
        ev_25_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Üst"])
        dep_25_ust = get_odd(odds, ["Deplasman Alt/Üst 2.5_Üst"])
        
        is_trap = False
        if ms1 <= 1.30 and ev_25_ust >= 1.60 and ev_25_ust != 99.0: is_trap = True
        if ms2 <= 1.30 and dep_25_ust >= 1.60 and dep_25_ust != 99.0: is_trap = True
        
        if (ms1 <= 1.30 or ms2 <= 1.30) and ust35 <= 1.70 and is_trap:
            return True, "BÜYÜK SÜRPRİZ DÜELLOSU: Maçta 3.5 Üst beklentisi çok yüksek, ancak favori takımın 3 gol atma ihtimali zayıf (Fav 2.5 Üst yüksek). Bu çelişki, yüksek gol beklentisinin zayıf takımın atacağı gollerden kaynaklandığını kanıtlar. Favori maçı kazanamaz. Maç 1-1, 2-2 gibi gollü beraberliklerle veya şok bir mağlubiyetle biter. Çifte Şans veya Sürpriz 0 aranmalıdır."
        return False, ""
"""

content = content.replace(g12_old, g12_new)

content = content.replace(
    "RuleG12",
    "RuleG12, Rule1473"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Update story_analyzer.py to handle 1473
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

story = story.replace(
    "elif any(r['code'] in ['T33', '1469'] for r in triggered_rules):",
    "elif any(r['code'] in ['T33', '1469', '1473'] for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("Rule 1473 injected and G12 patched.")
