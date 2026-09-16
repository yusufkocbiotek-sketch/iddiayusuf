import codecs
import re

content = codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf8').read()

new_rule = '''
class Rule1495(BaseRule):
    code = "1495"
    name = "Görünür Kısır Maç, Gizli Deplasman Şovu (0.5 Üst Çelişkisi)"
    category = "GOL_VE_YÖN"
    description = "MS0 <= 2.85, 2.5 Alt <= 1.55 AMA Deplasman (Sürpriz) 0.5 Üst <= 1.30"
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst"])
        
        if ms0 <= 2.85 and alt25 <= 1.55 and ms2 >= 2.50 and dep_05_ust <= 1.30 and dep_05_ust != 99.0:
            return True, "GİZLİ DEPLASMAN ŞOVU: Piyasa MS0 ve 2.5 Alt oranlarını dibe çekerek (1486 Kısır Maç Tuzağı) herkesi 0-0 veya 1-1 skoruna kilitliyor. ANCAK 2.50+ oranlı sürpriz Deplasman takımının gol atma ihtimali (0.5 Üst) 1.30'un altına indirilmiş! İddaa deplasmanın kesin gol atacağını biliyor ve kısır maç algısıyla bunu gizliyor. Bu maç kilitlenmez, Deplasman takımı şov yapar (0-2, 0-3, 1-3). MS 2 ve 2.5 Üst denenmelidir."
        return False, ""
'''

# Insert Rule 1495
pos = content.find('class Rule1492')
if pos != -1:
    end_pos = content.find('class Rule', pos + 10)
    if end_pos != -1:
        content = content[:end_pos] + new_rule + content[end_pos:]
    else:
        content += new_rule

# Modify 1486 to yield to 1495 (actually 1495 will just override if it's evaluated first, but let's just make 1486 return False if dep_05_ust <= 1.30)
# But wait, rule evaluation order in `get_all_rules` is based on definition order. If we put 1495 before 1486?
# Or just let them both trigger and let the analyzer pick the first one. Let's make sure 1495 is listed in the outputs.
codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf8').write(content)
print("Rule1495 added.")
