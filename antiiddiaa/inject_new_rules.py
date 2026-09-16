import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

rule_1469_1470 = """class Rule1469(BaseRule):
    code = "1469"
    category = "SKOR"
    name = "Aşırı Düşük Beraberlik Tuzağı (Kısır Favori)"
    description = "Favori (MS1 <= 2.10) + Beraberlik (<= 3.05) + Ev 1.5 Alt (<= 1.55)"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt"])
        
        if ms1 <= 2.10 and ms0 <= 3.05 and ev_15_alt <= 1.55:
            return True, "GİZLİ BERABERLİK KİLİDİ: Ev sahibi favori gösterilse de (Örn: 1.90), beraberlik oranı anormal derecede düşüktür (3.05 ve altı). Üstelik favorinin 2 gol atması beklenmemektedir (Ev 1.5 Alt <= 1.55). Bu maçta favorinin galibiyet gücü yoktur, maç 0-0 veya 1-1 kilitlenir. MS 0 denenmelidir."
        
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt"])
        if ms2 <= 2.10 and ms0 <= 3.05 and dep_15_alt <= 1.55:
            return True, "GİZLİ BERABERLİK KİLİDİ: Deplasman favori gösterilse de, beraberlik oranı anormal derecede düşüktür. Deplasmanın 2 gol atması beklenmemektedir. Bu maçta maç 0-0 veya 1-1 kilitlenir. MS 0 denenmelidir."
            
        return False, ""

class Rule1470(BaseRule):
    code = "1470"
    category = "GOL"
    name = "KG Var 1.2X Tuzağı (Sahte Açık Futbol)"
    description = "KG Var <= 1.30 + Deplasman 0.5 Üst yüksek"
    
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        dep_05_ust = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Üst", "Deplasman 1. Yarı Alt/Üst 0.5_Üst"])
        
        if kg_var <= 1.35 and ms1 <= 1.65 and dep_05_ust >= 1.65:
            return True, "KUSURSUZ GOL TUZAĞI: Bürolar KG Var oranını 1.30'lara kadar çekerek herkesi gollü bir maça inandırmış. Ancak deplasman takımının ilk yarıda gol atma ihtimali (0.5 Üst) çok zayıf görülüyor. Bu, 'KG Var'ın tamamen sahte bir yem olduğunu, maçın 1-0 veya 2-0 gibi tek taraflı kısır bir skorla biteceğini gösterir. KG Yok oynanmalıdır."
            
        return False, ""

def get_all_rules():"""

content = content.replace("def get_all_rules():", rule_1469_1470)

content = content.replace(
    "Rule999, Rule1462, Rule1463, Rule1464, Rule1465, Rule1466, Rule1467, Rule1468",
    "Rule999, Rule1462, Rule1463, Rule1464, Rule1465, Rule1466, Rule1467, Rule1468, Rule1469, Rule1470"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Rules 1469 and 1470 injected.")

# Now update story_analyzer.py to handle them
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

# Add 1469 to the Upset MS 0 logic (T33, T34, 1467)
story = story.replace(
    "elif any(r['code'] == 'T33' for r in triggered_rules):",
    "elif any(r['code'] in ['T33', '1469'] for r in triggered_rules):"
)

# Add 1470 to the Kısır logic (G10 etc) -> force gol_beklentisi = "DÜŞÜK"
story = story.replace(
    "if any(r['code'] == 'G10' for r in triggered_rules):",
    "if any(r['code'] in ['G10', '1470'] for r in triggered_rules):"
)

# Also explicitly add a Kombine for 1470
story = story.replace(
    "    elif any(r['code'] == 'Y7' for r in triggered_rules):",
    "    elif any(r['code'] == '1470' for r in triggered_rules):\n        output.append(f\"- **Ana Tahmin:** Maç Sonucu 1 (veya 1X)\")\n        output.append(f\"- **Kombine Öneri:** 2.5 Gol Altı + Karşılıklı Gol Yok\")\n    elif any(r['code'] == 'Y7' for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("Rules integrated into story_analyzer.")
