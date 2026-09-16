import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.strip().startswith('class Rule1530(BaseRule):'):
        # We will manually inject the whole Rule1530
        skip = True
        new_rule = '''class Rule1530(BaseRule):
    code = "1530"
    name = "İlk Yarı Şifresi (Kısır Maç, Hızlı Gol)"
    category = "ZAMANLAMA"
    description = "Piyasa Kısır Beklerken (Alt), İlk Yarı 0.5 Üst aşırı düşük."
    
    @classmethod
    def evaluate(cls, odds):
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        iy_05_ust = get_odd(odds, ["İlk Yarı Alt/Üst 0.5_Üst", "1. Yarı Altı/Üstü 0.5_Üst"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        
        # Eğer MS0 <= 2.90 ise, beraberlik ihtimali çok yüksektir ve bu gerçek bir kısır kilitlenme (0-0/1-1) maçıdır. 1530 tuzağı değildir.
        if alt25 <= 1.60 and iy_05_ust <= 1.30 and iy_05_ust != 99.0 and ms1 >= 1.60 and ms2 >= 1.60 and ms1 != 99.0 and ms2 != 99.0 and ms0 > 2.90:
            return True, "İLK YARI ŞİFRESİ (ERKEN GOL PATLAMASI): Piyasa 2.5 Alt (1.60 altı) göstererek maçı kısır bir 0-0 veya 1-0 maçına kilitliyor. FAKAT dengeli bir maç (taraf oranları yüksek) olmasına rağmen mikro baremlere baktığımızda, İlk Yarı 0.5 Üst (1.30 altı) adeta banko gösterilmiş! İddaa ilk yarıdan kesinlikle en az bir gol geleceğini biliyor. Genel kısır algısının aksine, bu maç ilk yarıdan çözülecek ve büyük ihtimalle 2.5 Üst'e de taşınacaktır. 0-0 kilitlenmesi bekleyenler büyük hüsrana uğrayacaktır. İlk yarı golü değerlendirilmelidir."
        return False, ""
'''
        new_lines.append(new_rule)
        continue
    
    if skip:
        if line.strip().startswith('class Rule1523(BaseRule):'):
            skip = False
            new_lines.append(line)
        continue
    
    if not skip:
        new_lines.append(line)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write("".join(new_lines))

print("Fixed Rule 1530 completely.")
