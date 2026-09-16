import sys
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'a', encoding='utf-8') as f:
    f.write('''
class RuleS1(BaseRule):
    code = "S1"
    name = "Standart Kısır Favori (Tuzak Yok)"
    category = "BİLGİ"
    @classmethod
    def evaluate(cls, odds):
        return True, "STANDART PİYASA (KISIR FAVORİ): Bu maçta herhangi bir anomali veya tuzak tespit edilemedi. İddaa oranları favorinin düşük gollü (1-0, 2-0) bir galibiyet alacağını net bir şekilde gösteriyor. Maçın genel gidişatına güvenilebilir, sürpriz aranmamalıdır."

class RuleS2(BaseRule):
    code = "S2"
    name = "Standart Gollü Favori (Tuzak Yok)"
    category = "BİLGİ"
    @classmethod
    def evaluate(cls, odds):
        return True, "STANDART PİYASA (GOLLÜ FAVORİ): Bu maçta herhangi bir anomali veya tuzak tespit edilemedi. İddaa oranları favorinin gollü (2-1, 3-0, 3-1 vb.) bir galibiyet alacağını gösteriyor. Gollere veya favoriye yönelmek piyasanın doğal akışıdır."
''')
