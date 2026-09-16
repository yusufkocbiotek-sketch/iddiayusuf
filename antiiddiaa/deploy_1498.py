import codecs
import re

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1498 = '''
class Rule1498(BaseRule):
    code = "1498"
    name = "Sahte Banko Gol Tuzağı (1.10 Yemi)"
    category = "SKOR"
    description = "Favori olmayan takımın KESİN gol atacakmış gibi 1.10 altı orana sahip olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ev_ust05 = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst", "Ev Sahibi Altı/Üstü 0.5_Üst"])
        
        if ms1 >= 2.00 and ev_ust05 > 0 and ev_ust05 <= 1.12:
            return True, "SAHTE BANKO GOL TUZAĞI: Ev sahibi takım maçın net favorisi değil (MS1 2.00 ve üzeri), ANCAK iddaa Ev Sahibinin gol atma ihtimaline (0.5 Üst) 1.12 ve altı gibi komik derecede 'banko' bir oran açmış. Favori olmayan ve maçı kazanma garantisi bulunmayan bir takımın KESİN gol atacağına piyasayı bu kadar inandırmak devasa bir tuzaktır. Bu oran, herkesi kombinelere 'Ev 0.5 Üst' veya 'KG Var' ekletmek içindir. Sonuç tam bir şok olur: Ev sahibi gol bile atamaz, deplasman takımı maçı rahat kazanır (0-2, 0-4). MS2, X2 veya Karşılıklı Gol Yok oynanmalıdır."
        return False, ""
'''

content = content.replace('def get_all_rules():', rule_1498 + '\ndef get_all_rules():')
content = content.replace('Rule1497, Rule1496', 'Rule1498, Rule1497, Rule1496')

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

story_analyzer_path = 'story_analyzer.py'
with codecs.open(story_analyzer_path, 'r', 'utf-8') as f:
    story_content = f.read()

story_addition = '''
    elif any(r['code'] == '1498' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Sürpriz Deplasman Galibiyeti (Ev Gol Atamaz)")
        output.append(f"- **Kombine Öneri:** MS 2 + Karşılıklı Gol Yok (Sürpriz Skor: 0-3 / 0-4)")
'''

story_content = story_content.replace("    elif any(r['code'] == '1497'", story_addition.strip('\n') + "\n    elif any(r['code'] == '1497'")
with codecs.open(story_analyzer_path, 'w', 'utf-8') as f:
    f.write(story_content)

print("Rule 1498 deployed.")
