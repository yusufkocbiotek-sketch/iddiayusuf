import sys

lines = open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', encoding='utf-8').readlines()
new_lines = []
skip = False
for line in lines:
    if 'class RuleT10(BaseRule):' in line:
        skip = True
        new_lines.append(line)
        continue
    if skip and 'class RuleT11(BaseRule):' in line:
        skip = False
        new_lines.append("""    code = "T10"
    category = "YÖN"
    name = "Tamamen Eşit Oranlı Maç"
    description = "Taraf oranları birbirine çok yakın (fark <= 0.20)."
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        if ms1 >= 90.0 or ms0 >= 90.0 or ms2 >= 90.0:
            return False, ""
        if abs(ms1 - ms0) <= 0.30 and abs(ms0 - ms2) <= 0.30:
            return True, "Taraf seçimi kesinlikle yapılmamalı; sadece 2.5 Alt veya KG Yok'a odaklanılmalı."
        return False, ""

""")
        new_lines.append(line)
        continue
    if not skip:
        new_lines.append(line)
open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8').writelines(new_lines)
print("Done!")
