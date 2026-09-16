import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

rule_1477 = """class Rule1477(BaseRule):
    code = "1477"
    category = "SKOR"
    name = "Sahte Fark İllüzyonu (1.2X Banko Patlaması)"
    description = "MS1 <= 1.30 + Ev 2.5 Alt <= 1.55 + Dep 0.5 Üst <= 1.50"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        ev_25_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Alt"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst"])
        
        dep_25_alt = get_odd(odds, ["Deplasman Alt/Üst 2.5_Alt"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst"])
        
        is_trap = False
        trap_team = ""
        
        if ms1 <= 1.30 and ev_25_alt <= 1.55 and dep_05_ust <= 1.50:
            is_trap = True
            trap_team = "Ev Sahibi"
            
        if ms2 <= 1.30 and dep_25_alt <= 1.55 and ev_05_ust <= 1.50:
            is_trap = True
            trap_team = "Deplasman"
            
        if is_trap:
            return True, f"BÜYÜK MATEMATİKSEL PARADOKS: {trap_team} 1.20'lerde bir oranla banko favori gösterilmiş. Ancak maçın detaylarına inildiğinde favori takımın 3 gol atamayacağı (2.5 Altı) kesin gibi fiyatlanmış. İşin daha da tuhafı, zayıf takımın kesinlikle 1 gol atacağı (0.5 Üstü 1.50 altı) bekleniyor! Zayıf takım gol atarsa, favorinin maçı kazanması için 2 gol atması gerekir. Ancak favori zaten maksimum 1-2 gol civarında kısıtlanmış durumda. Bu denklemde favorinin fark atma veya rahat kazanma ihtimali SIFIRDIR. Maç büyük ihtimalle 1-1, 2-1 (baskıyla) veya 1-2 (sürpriz) bitecektir. Taraf bahsinden (Banko'dan) kesinlikle kaçınılmalı, KG Var veya Sürpriz Çifte Şans denenmelidir."
            
        return False, ""

def get_all_rules():"""

content = content.replace("def get_all_rules():", rule_1477)
content = content.replace("Rule1476", "Rule1476, Rule1477")

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

story = story.replace(
    "elif any(r['code'] == '1476' for r in triggered_rules):",
    "elif any(r['code'] == '1477' for r in triggered_rules):\n        output.append(f\"- **Ana Tahmin:** Sürpriz Çifte Şans (Bankonun Karşısı) veya Karşılıklı Gol Var\")\n        output.append(f\"- **Kombine Öneri:** Çifte Şans + Karşılıklı Gol Var (Sürpriz Beklentisi)\")\n    elif any(r['code'] == '1476' for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("Rule 1477 injected.")
