import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

rule_1476 = """class Rule1476(BaseRule):
    code = "1476"
    category = "YARI"
    name = "Uyuyan Dev (İkinci Yarı Düello Patlaması)"
    description = "KG Var <= 1.40 + İY 0 <= 2.30 + İY KG Var > 2.60 + 2. Yarı KG Var <= 2.40"
    
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        iy_0 = get_odd(odds, ["1. Yarı Sonucu_0"])
        iy_kg_var = get_odd(odds, ["1. Yarı Karşılıklı Gol_Var"])
        ikinci_yari_kg_var = get_odd(odds, ["2. Yarı Karşılıklı Gol_Var"])
        
        if kg_var <= 1.40 and iy_0 <= 2.30 and iy_kg_var > 2.60 and ikinci_yari_kg_var <= 2.40:
            return True, "İKİNCİ YARI ŞOVU (3.5 ÜST UZANTISI): Maçın ilk yarısının tamamen golsüz veya çok kısır (0-0) geçeceği fiyatlanmış (İY 0 çok düşük, İY KG Var çok yüksek). Ancak maçın genelinde KG Var oranı 1.40 altında ve 2. Yarı KG Var oldukça iddialı. Bu da demek oluyor ki ilk yarı uyuyan takımlar, ikinci yarıda 2-2 veya 3-3'e kadar uzayabilecek devasa bir düelloya girecek. İlk yarı golsüz kilitlenip, ikinci yarı gol yağmuru (3.5 Üst) beklenmelidir."
            
        return False, ""

def get_all_rules():"""

content = content.replace("def get_all_rules():", rule_1476)
content = content.replace("Rule1475", "Rule1475, Rule1476")

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

story = story.replace(
    "elif any(r['code'] == '1475' for r in triggered_rules):",
    "elif any(r['code'] == '1476' for r in triggered_rules):\n        output.append(f\"- **Ana Tahmin:** 2. Yarı Daha Çok Gol Olur veya 3.5 Gol Üst\")\n        output.append(f\"- **Kombine Öneri:** İlk Yarı 1.5 Alt + Maç Sonu Karşılıklı Gol Var (2-2 / 3-3 Beklentisi)\")\n    elif any(r['code'] == '1475' for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("Rule 1476 injected for Second Half Explosions.")
