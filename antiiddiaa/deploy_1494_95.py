import codecs
import re

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1494_95 = '''
class Rule1494(BaseRule):
    code = "1494"
    name = "Sahte Kısır Deplasman (Ev Gol Atar Tuzağı)"
    category = "SKOR"
    description = "MS2 favoriyken Alt oranı düşük ama Ev Sahibinin gol atma ihtimali çok yüksek."
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        ev_ust05 = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst", "Ev Sahibi Altı/Üstü 0.5_Üst"])
        
        if ms2 <= 1.65 and alt25 <= 1.65 and ev_ust05 <= 1.45:
            return True, "SAHTE KISIR DEPLASMAN TUZAĞI: Deplasman favori gösterilmiş ve 2.5 Alt oranı çok düşük (1.65 altı). Herkes 0-1 veya 0-2 bekliyor. Ancak Ev Sahibinin gol atma oranı (0.5 Üst) 1.45 ve altında! Ev sahibi kesin gol atacaksa ve deplasman da favoriyse maç nasıl Alt bitecek? Bu büyük bir çelişki ve tuzaktır. Maç kesinlikle karşılıklı gollerle 1-1, 1-2 veya 2-2 gibi gollü skorlara gidecektir. 2.5 Alt büyük bir yemdir. KG Var veya 2.5 Üst oynanmalıdır."
        return False, ""

class Rule1495(BaseRule):
    code = "1495"
    name = "Şüpheli Zayıf Takım Golü (Sürpriz 1-1 Tuzağı)"
    category = "SKOR"
    description = "MS1 banko favori ama zayıf takımın gol atma oranı şüpheli şekilde düşük."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        dep_ust05 = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        
        if ms1 <= 1.45 and alt25 <= 1.65 and dep_ust05 <= 1.60:
            return True, "ŞÜPHELİ ZAYIF TAKIM GOLÜ TUZAĞI: Ev sahibi (1.45 altı) banko favori ve maçın 2.5 Alt (1.65 altı) bitmesi bekleniyor. Klasik 1-0 veya 2-0 banko profili. ANCAK zayıf deplasman takımının 0.5 Üst (gol atar) oranı 1.60 ve altında açılmış! Bu kadar favori bir takımın evinde, zayıf takımın gol atmasına bu kadar yüksek ihtimal verilmesi devasa bir tuzaktır. Deplasman takımı kesin gol bulacak ve maç kilitlenip sürpriz bir şekilde 1-1 bitecektir. Banko MS1 oynamak intihardır, sürpriz beraberlik (MS0 veya X2 Çifte Şans) aranmalıdır."
        return False, ""
'''

content = content.replace('def get_all_rules():', rule_1494_95 + '\ndef get_all_rules():')

# Refactor the get_all_rules array inside the function to include 1494 and 1495
content = content.replace('Rule1493, Rule1492', 'Rule1495, Rule1494, Rule1493, Rule1492')

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

# Update story_analyzer.py
story_analyzer_path = 'story_analyzer.py'
with codecs.open(story_analyzer_path, 'r', 'utf-8') as f:
    story_content = f.read()

story_addition = '''
    elif any(r['code'] == '1494' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Gol Düellosu (Ev Sahibi Sürprizi)")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 1X Çifte Şans)")
    elif any(r['code'] == '1495' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 0 veya X2 (Zayıf Takım Direnişi)")
        output.append(f"- **Kombine Öneri:** X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz: 1-1)")
'''

story_content = story_content.replace("    elif any(r['code'] == '1493'", story_addition.strip('\n') + "\n    elif any(r['code'] == '1493'")
with codecs.open(story_analyzer_path, 'w', 'utf-8') as f:
    f.write(story_content)

print("Rules 1494 and 1495 deployed.")
