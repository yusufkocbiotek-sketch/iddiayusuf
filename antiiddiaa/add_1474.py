import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

rule_1474 = """class Rule1474(BaseRule):
    code = "1474"
    category = "SKOR"
    name = "Enflasyon Tuzağı (Favori ve Beraberlik Eşitliği)"
    description = "Beraberlik Oranı < Ev Oranı (veya çok yakın) + Kısır Maç"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Alt/Üst 2,5_Alt"])
        
        # Beraberlik oranı 2.50 altındaysa ve taraflardan birinin (özellikle favorinin) oranından düşükse
        if ms0 <= 2.50 and (ms0 < ms1 or ms0 < ms2):
            if alt25 <= 1.45 or kg_yok <= 1.50:
                # Ancak burada bir detay var: Eğer MS1 2.41, MS0 2.22, MS2 3.04 ise ve maç 0-1 bitiyorsa
                # Bürolar beraberliği en düşük tutarak ("Kesin 0-0 biter" algısı yaratıp) oyuncuları beraberliğe kilitliyor.
                # Sonra maç tek bir golle deplasman veya ev sahibine kayıyor.
                return True, "SÜPER BERABERLİK TUZAĞI: Bürolar beraberlik oranını (Örn: 2.22) taraf oranlarından bile düşük tutarak 'Bu maç %100 berabere biter' algısı yaratmıştır. Ancak bu kadar bariz bir beraberlik oranı genellikle bir tuzaktır. Maç 0-0 kilitlenecekmiş gibi görünürken tek bir golle zayıf takımın veya oran olarak dezavantajlı olan takımın galibiyetiyle (0-1 / 1-0) sonuçlanır. Beraberlikten ziyade 01 veya 02 Çifte Şans ve 1.5 Alt denenmelidir."
        return False, ""

def get_all_rules():"""

content = content.replace("def get_all_rules():", rule_1474)
content = content.replace(
    "RuleG12, Rule1473",
    "RuleG12, Rule1473, Rule1474"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    story = f.read()

# Add logic for 1474 to output the actual prediction for MS 2 (Deplasman) when it happens
story = story.replace(
    "elif any(r['code'] == '1473' for r in triggered_rules):",
    "elif any(r['code'] == '1474' for r in triggered_rules):\n        output.append(f\"- **Ana Tahmin:** Maç Sonucu 2 veya 02 Çifte Şans (Deplasman Sürprizi)\")\n        output.append(f\"- **Kombine Öneri:** 1.5 Gol Altı + Karşılıklı Gol Yok\")\n    elif any(r['code'] == '1473' for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(story)

print("Rule 1474 created and injected.")
