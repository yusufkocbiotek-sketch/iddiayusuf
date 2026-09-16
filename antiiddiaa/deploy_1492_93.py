import codecs
import re

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1492_93 = '''
class Rule1492(BaseRule):
    code = "1492"
    name = "Sahte KG Var Tuzağı (Favori Yemlemesi)"
    category = "SKOR"
    description = "Favori takımın olduğu maçta KG Var oranının aşırı düşürülmesi."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        # Sadece MS1 favoriyse
        if ms1 <= 1.70 and ms2 >= 3.00 and kg_var <= 1.35 and kg_yok >= 2.10:
            return True, "SAHTE KG VAR TUZAĞI: Ev sahibi net bir favori (1.70 altı) olmasına rağmen, KG Var oranı şüpheli bir şekilde (1.35 altı) düşük tutularak 'deplasman takımı kesin gol atacak' algısı yaratılmış. Bu klasik bir iddaa yemi ve tuzağıdır. Gerçekte deplasman gol bulamaz ve Ev sahibi maçı gol yemeden (2-0, 3-0) rahat kazanır. MS 1 ve Karşılıklı Gol Yok oynanmalıdır."
        return False, ""

class Rule1493(BaseRule):
    code = "1493"
    name = "Çıplak Kral Tuzağı (1.10 Altı Patlama)"
    category = "SKOR"
    description = "1.10 ve altı orana sahip takımın maçı kazanamaması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if (ms1 <= 1.10 and ms1 > 0) or (ms2 <= 1.10 and ms2 > 0):
            return True, "ÇIPLAK KRAL TUZAĞI (1.10 ALTI): Takımlardan birine 1.10 veya daha düşük komik bir favori oranı açılmış. İstatistiksel olarak bu oran grubunda hiç beklenmedik anlarda inanılmaz bir patlama (sürpriz) yaşanır. Kasanın parasını 1.05 gibi değersiz bir orana yatırmak yerine, devasa bir sürpriz (Çifte Şans 1X veya X2) kovalamak veya hiç bulaşmamak en mantıklısıdır. Favorinin çöküş ihtimali masadadır."
        return False, ""
'''

# Update Rule 1482 logic
new_1482_eval = '''
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ust = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        kgy = get_odd(odds, ["Karşılıklı Gol_Yok"])
        
        if ms1 <= 2.20 and ms2 >= 2.80 and ust <= 1.50 and kgy >= 2.00:
            return True, "SAHTE DÜELLO TUZAĞI: Maçın gollü geçeceği ve iki takımın da gol atacağı aşırı bariz (KG Yok 2.00+ ve Üst 1.50-). Ancak Ev sahibi çok güçlü bir favori değil (2.10 civarı). Bu durum herkesi gollere iterken, Ev sahibi maçı beklenmedik bir şekilde kilitler ve 1-0 veya 2-0 gibi skorlarla kazanır. Taraf bahislerinde MS1 veya 1X, gol bahislerinde 2.5 Alt denenmelidir."
        return False, ""
'''

content = re.sub(r'@classmethod\s*def evaluate\(cls, odds\):.*?return False, ""', new_1482_eval.strip(), content, count=1, flags=re.DOTALL)
content = content.replace('def get_all_rules():', rule_1492_93 + '\ndef get_all_rules():')

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

# Refactor the get_all_rules arrays inside the function to include 1492 and 1493
with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()
content = content.replace('Rule1491, Rule1490', 'Rule1493, Rule1492, Rule1491, Rule1490')
with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

# Update story_analyzer.py
story_analyzer_path = 'story_analyzer.py'
with codecs.open(story_analyzer_path, 'r', 'utf-8') as f:
    story_content = f.read()

story_addition = '''
    elif any(r['code'] == '1492' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (KG Yok)")
        output.append(f"- **Kombine Öneri:** MS 1 + Karşılıklı Gol Yok")
    elif any(r['code'] == '1493' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Sürpriz Patlama (Favori Kazanamaz)")
        output.append(f"- **Kombine Öneri:** Sürpriz Çifte Şans (Favorinin Karşısı)")
'''
story_content = story_content.replace("    elif any(r['code'] == '1491'", story_addition.strip('\n') + "\n    elif any(r['code'] == '1491'")
with codecs.open(story_analyzer_path, 'w', 'utf-8') as f:
    f.write(story_content)

print("Rules updated.")
