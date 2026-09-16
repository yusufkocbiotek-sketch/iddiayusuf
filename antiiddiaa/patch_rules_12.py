import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix S1
old_s1 = '''class RuleS1(BaseRule):
    code = "S1"
    name = "Standart Kısır Favori (Tuzak Yok)"
    category = "BİLGİ"
    @classmethod
    def evaluate(cls, odds):
        return True, "STANDART PİYASA (KISIR FAVORİ): Bu maçta herhangi bir anomali veya tuzak tespit edilemedi. İddaa oranları favorinin düşük gollü (1-0, 2-0) bir galibiyet alacağını net bir şekilde gösteriyor. Maçın genel gidişatına güvenilebilir, sürpriz aranmamalıdır."'''

new_s1 = '''class RuleS1(BaseRule):
    code = "S1"
    name = "Standart Kısır (Tuzak Yok)"
    category = "BİLGİ"
    @classmethod
    def evaluate(cls, odds):
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        if alt25 != 99.0 and ust25 != 99.0 and alt25 < ust25:
            return True, "STANDART PİYASA (KISIR MAÇ): İddaa oranları maçın 2.5 Alt barajında kalacağını gösteriyor. Herhangi bir anomali tespit edilemedi."
        return False, ""'''
content = content.replace(old_s1, new_s1)

# Fix S2
old_s2 = '''class RuleS2(BaseRule):
    code = "S2"
    name = "Standart Gollü Favori (Tuzak Yok)"
    category = "BİLGİ"
    @classmethod
    def evaluate(cls, odds):
        return True, "STANDART PİYASA (GOLLÜ FAVORİ): Bu maçta herhangi bir anomali veya tuzak tespit edilemedi. İddaa oranları favorinin gollü (2-1, 3-0, 3-1 vb.) bir galibiyet alacağını gösteriyor. Gollere veya favoriye yönelmek piyasanın doğal akışıdır."'''

new_s2 = '''class RuleS2(BaseRule):
    code = "S2"
    name = "Standart Gollü (Tuzak Yok)"
    category = "BİLGİ"
    @classmethod
    def evaluate(cls, odds):
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        if alt25 != 99.0 and ust25 != 99.0 and ust25 <= alt25:
            return True, "STANDART PİYASA (GOLLÜ MAÇ): İddaa oranları maçın 2.5 Üst barajını aşacağını gösteriyor. Herhangi bir anomali tespit edilemedi."
        return False, ""'''
content = content.replace(old_s2, new_s2)

# Fix T70
old_t70 = '''if ms1 <= 1.55 and ms0 <= 3.30 and ms1 != 99.0 and ms0 != 99.0:'''
new_t70 = '''if ms1 <= 1.45 and ms0 <= 3.20 and ms1 != 99.0 and ms0 != 99.0:'''
content = content.replace(old_t70, new_t70)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Add new Rule1487 (Fake Under Trap)
new_rule = '''
class Rule1487(BaseRule):
    code = "1487"
    category = "TUZAK"
    name = "Sahte Kısır Ağır Favori (Gol Patlaması Tuzağı)"
    description = "MS favorisi <= 1.50 iken 2.5 Alt <= 1.55 ise, bu maç 2.5 Üst veya Üst patlaması yapar."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1", "1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2", "2"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        
        # Biri ağır favoriyse
        if (ms1 <= 1.50 or ms2 <= 1.50) and alt25 <= 1.55 and alt25 != 99.0:
            return True, "SAHTE KISIR (GOL PATLAMASI): İddaa bir tarafa 1.50 altı favori açmış, ancak 2.5 Alt oranını da 1.55'in altına çekerek sanki maçta en fazla 1 veya 2 gol olacak algısı yaratmış. Bu, bahisçileri Alt oynamaya yönlendiren klasik bir tuzaktır. Ağır favorinin olduğu bu maçta büyük ihtimalle 3+ gol çıkacak ve sistem patlayacaktır (Örn: 2-5, 3-0, 1-3). 2.5 Üst gizli bir bankodur!"
        return False, ""
'''
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'a', encoding='utf-8') as f:
    f.write(new_rule)

print("Rules S1, S2, T70 fixed. Rule 1487 added!")
