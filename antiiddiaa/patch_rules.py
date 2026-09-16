import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('iy_05_ust <= 1.35', 'iy_05_ust <= 1.25')
content = content.replace('İlk Yarı 0.5 Üst (1.35 altı)', 'İlk Yarı 0.5 Üst (1.25 altı)')

new_rule = '''
class Rule1552(BaseRule):
    code = "1552"
    name = "Sahte Kısır Favori Tuzağı (Farklı Galibiyet Yemi)"
    category = "TUZAK"
    description = "MS1 favoriyken 2.5 Alt'ın 1.45 altı açılması (Sahte Alt Tuzağı)."

    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        if ms1 != 99.0 and ms1 <= 1.75 and alt25 != 99.0 and alt25 <= 1.45 and kg_yok != 99.0 and kg_yok <= 1.60:
            return True, "SAHTE KISIR FAVORİ TUZAĞI (ÜST PATLAMASI): Ev sahibi favori (1.75 altı) olmasına rağmen, 2.5 Alt oranı anormal derecede düşük (1.45 altı) açılmış. Bu, maçı 'garanti 1-0 veya 2-0' gösterebilmek için kurulan devasa bir 'Sahte Alt' tuzağıdır. İddaa ev sahibinin 3 veya 4 gol atabileceğini çok iyi biliyor ancak piyasayı Alt'a yönlendiriyor. Gerçekte ev sahibi takımın hücum gücü gizlenmektedir. Bu maç 3-0 veya 4-0 gibi farklı bir ev sahibi galibiyetine ve dolayısıyla 2.5 Üst'e patlayacaktır! Alt tuzağına düşmeyin."
        return False, ""
'''

if 'class Rule1552' not in content:
    content = content.replace('class Rule1523(BaseRule):', new_rule + '\nclass Rule1523(BaseRule):')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patch successful.')
