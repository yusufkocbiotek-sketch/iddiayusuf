import codecs
import re

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1496_97 = '''
class Rule1496(BaseRule):
    code = "1496"
    name = "Patlak Tahterevalli Tuzağı (Farklı Galibiyet)"
    category = "YÖN_VE_GOL"
    description = "Taraf oranları eşitken beraberlik oranının anormal yüksek olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if ms1 > 0 and ms2 > 0 and abs(ms1 - ms2) <= 0.30 and ms0 >= 4.00:
            return True, "PATLAK TAHTEREVALLİ TUZAĞI: İki takımın taraf oranları birbirine çok yakın (Örn: 2.16 - 2.07) açılarak maç kağıt üzerinde tamamen ortada (dengeli) gibi gösterilmiş. ANCAK beraberlik oranı inanılmaz derecede yüksek (4.00 ve üzeri)! Eşit güçteki takımların maçında beraberliğin bu kadar imkansız fiyatlanması büyük bir çelişkidir. Bu durum, arka planda takımlardan birinin maça çok eksik veya moralsiz çıktığını ve maçın tarihi bir farka (Örn: 0-4, 3-0) sahne olacağını gösterir. Taraf bahsi yerine Karşılıklı Gol Yok veya 2.5 Üst (Tek taraflı şov) denenmelidir."
        return False, ""

class Rule1497(BaseRule):
    code = "1497"
    name = "Ölümcül Sessizlik Tuzağı (0-0 Yemi)"
    category = "SKOR"
    description = "KG Var oranının aşırı düşük olup maçın 0-0 kilitlenmesi."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        
        if kg_var > 0 and kg_var <= 1.25 and ms0 >= 3.80:
            return True, "ÖLÜMCÜL SESSİZLİK TUZAĞI: Maçta KG Var oranı 1.25'in altına kadar düşürülmüş ve beraberlik oranı 3.80'in üzerine çıkarılmış. Bürolar vitrinde açıkça 'Bu maçta gollü bir düello olacak, taraf seçmeyin Üst ve KG Var oynayın' diye bağırıyor. İddaa hiçbir zaman bu kadar bariz ve risksiz bir gol partisini bedavaya dağıtmaz. Bu, tüm piyasayı gollere yönlendirip maçı 0-0 veya 1-0 gibi inanılmaz kısır bir skorda kilitlemek için kurulan ölümcül bir tuzaktır. Kesinlikle 2.5 Alt veya Karşılıklı Gol Yok oynanmalıdır."
        return False, ""
'''

content = content.replace('def get_all_rules():', rule_1496_97 + '\ndef get_all_rules():')
content = content.replace('Rule1495, Rule1494', 'Rule1497, Rule1496, Rule1495, Rule1494')

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

story_analyzer_path = 'story_analyzer.py'
with codecs.open(story_analyzer_path, 'r', 'utf-8') as f:
    story_content = f.read()

story_addition = '''
    elif any(r['code'] == '1496' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 veya 2 (Beraberlik İmkansız, Tek Taraflı Şov)")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Yok + 2.5 Gol Üst (Sürpriz Skor: 0-3 / 3-0)")
    elif any(r['code'] == '1497' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 0 veya Alt (Ölümcül Sessizlik)")
        output.append(f"- **Kombine Öneri:** 2.5 Gol Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0)")
'''

story_content = story_content.replace("    elif any(r['code'] == '1495'", story_addition.strip('\n') + "\n    elif any(r['code'] == '1495'")
with codecs.open(story_analyzer_path, 'w', 'utf-8') as f:
    f.write(story_content)

print("Rules 1496 and 1497 deployed.")
