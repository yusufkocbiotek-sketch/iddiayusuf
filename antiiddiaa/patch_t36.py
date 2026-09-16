import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update T36 in rule_engine.py
t36_old = """class RuleT36(BaseRule):
    code = "T36"
    category = "YÖN"
    name = "Gizli Deplasman Golü (Çelişki Tuzağı)"
    description = "Ev favori + KG Yok düşük + Dep 0.5 Üst çok düşük"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        dep_05_ust = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Üst", "Deplasman 1. Yarı Alt/Üst 0.5_Üst", "Deplasman Alt/Üst 0.5_Üst"])
        
        if ms1 <= 1.65 and kg_yok < kg_var and dep_05_ust <= 1.40:
            return True, "Ev sahibi favori gösterilmesine ve maçın 'KG Yok' (Biri gol atamaz) beklenmesine rağmen, Deplasmanın gol atma oranı çok düşük açılmış. Bu büyük bir çelişkidir! Bürolar deplasmanın gol atacağını, ev sahibinin ise tıkanacağını biliyor. Deplasman yenilmez (X2) veya Sürpriz MS 2 denenebilir."
        return False, ""
"""

t36_new = """class RuleT36(BaseRule):
    code = "T36"
    category = "YÖN"
    name = "Gizli Deplasman Golü (Çelişki Tuzağı)"
    description = "Ev favori + KG Yok düşük + Dep 0.5 Üst çok düşük"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst"])
        if dep_05_ust == 99.0:
            dep_05_ust = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Üst", "Deplasman 1. Yarı Alt/Üst 0.5_Üst"])
        
        ev_15_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Üst"])
        
        if ms1 <= 1.65 and kg_yok < kg_var and dep_05_ust <= 1.40:
            if ev_15_ust >= 1.85:
                return True, "Ev sahibi favori gösterilmesine ve maçın 'KG Yok' beklenmesine rağmen, Deplasmanın gol atma oranı çok düşük açılmış. Ev sahibinin 2 gol atması da beklenmiyor (1.5 Üst yüksek). Bürolar deplasmanın gol atacağını, ev sahibinin ise tıkanacağını biliyor. Deplasman yenilmez (X2) veya Sürpriz MS 2 denenebilir."
            else:
                return True, "Ev sahibi favori gösterilip 'KG Yok' beklenmesine rağmen Deplasmanın gol atma ihtimali yüksek. Ancak Ev sahibinin hücum gücü yüksek (1.5 Üst düşük). Bu çelişki maçın KG Var (Örn: 2-1, 3-1) biteceğini işaret eder."
        return False, ""
"""

content = content.replace(t36_old, t36_new)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Update story_analyzer.py to separate T36 upset behavior
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

story = story.replace(
    "    elif any(r['code'] in ['T36', '1465', '1466', '1468'] for r in triggered_rules):",
    "    elif any(r['code'] in ['1465', '1466', '1468'] for r in triggered_rules) or (any(r['code'] == 'T36' for r in triggered_rules) and ev_15_ust >= 1.85):"
)

# And add the alternate KG Var logic for T36 if Ev_15_ust < 1.85
alternate_t36 = """    elif any(r['code'] == 'T36' for r in triggered_rules) and ev_15_ust < 1.85:
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (Ev Sahibi Kazanır)")
        output.append(f"- **Kombine Öneri:** MS 1 + Karşılıklı Gol Var (2-1, 3-1 Beklentisi)")
    elif any(r['code'] in ['1465', '1466', '1468'] for r in triggered_rules)"""

story = story.replace(
    "    elif any(r['code'] in ['1465', '1466', '1468'] for r in triggered_rules) or (any(r['code'] == 'T36' for r in triggered_rules) and ev_15_ust >= 1.85):",
    alternate_t36 + " or (any(r['code'] == 'T36' for r in triggered_rules) and ev_15_ust >= 1.85):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("T36 updated.")
