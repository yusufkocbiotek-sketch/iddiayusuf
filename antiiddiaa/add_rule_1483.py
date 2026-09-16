import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

new_rule = '''class Rule1483(BaseRule):
    code = "1483"
    category = "GOL"
    name = "Kısır Maç Görünümlü Düello (Alt/Üst Paradoksu)"
    description = "2.5 Alt < 1.65 iken, Üst ve Var < 2.35 ise maçta gizli bir gol düellosu vardır."
    
    @classmethod
    def evaluate(cls, odds):
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        ust_ve_var = get_odd(odds, ["Altı/Üstü 2.5 ve Karşılıklı Gol_Üst ve Var"])
        
        if alt25 != 99.0 and alt25 < 1.65 and ust_ve_var != 99.0 and ust_ve_var <= 2.35:
            return True, "PARADOKS - GİZLİ DÜELLO: İddaa 2.5 Alt oranını düşük (1.65 altı) tutarak piyasayı 'Bu maç kısır geçecek' yalanına inandırıyor. Ancak '2.5 Üst ve KG Var' kombine oranı (2.35 altı) matematiksel olarak imkansız derecede düşük açılmış! Bu, maçın aslında 1-2, 2-1 veya 2-2 gibi gollü bir düelloya sahne olacağının en büyük kanıtıdır. Alt ve KG Yok bahisleri tamamen tuzaktır."
            
        return False, ""

'''

import re
content = re.sub(r'(class Rule1495)', new_rule + r'\1', content, count=1)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)
