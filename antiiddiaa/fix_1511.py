import codecs
import re

content = codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf8').read()

new_1511 = '''class Rule1511(BaseRule):
    code = "1511"
    name = "Beraberliksiz Gol Düellosu (12 Çifte Şans İllüzyonu)"
    category = "SKOR"
    description = "MS1 ve MS2 >= 2.20 iken KG Var <= 1.45 ve 12 ÇŞ <= 1.20"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        cs_12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1 ve 2", "Çifte Şans_1-2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms1 != 99.0 and ms2 != 99.0 and 2.20 <= ms1 <= 2.80 and 2.20 <= ms2 <= 2.80:
            if kg_var <= 1.45 and cs_12 <= 1.20 and cs_12 != 99.0:
                return True, "BERABERLİKSİZ GOL DÜELLOSU: Dengeli maçlarda (Taraf oranları 2.20 - 2.80 arası) teorik olarak 12 Çifte Şans oranının 1.25+ olması gerekirken iddaa bunu 1.20'nin altına düşürüp (Beraberlik ihtimalini dışlayıp) KG Var oranını da çok düşük (1.45 altı) açmışsa, maçın bol gollü geçeceğini ancak kesinlikle bir kazanan çıkacağını gösterir. 2-2 veya 3-3 gibi gollü beraberlikler ihtimal dışıdır. Skor 3-1, 1-3, 2-1 gibi gollü galibiyetlere gider. Çifte Şans 12 + 2.5 Üst + KG Var oynanmalıdır."
        return False, ""'''

content = re.sub(r'class Rule1511\(BaseRule\):.*?return False, ""', new_1511, content, flags=re.DOTALL)
codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf8').write(content)
print('Rule 1511 updated successfully.')
