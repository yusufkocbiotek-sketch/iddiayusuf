import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_rule = '''
class Rule1556(BaseRule):
    code = "1556"
    name = "Kısır Favori Kilitlenmesi (0-0/1-1 Tuzağı)"
    category = "TUZAK"
    description = "MS1 favori iken MS0 ve Alt25 oranlarının anormal düşük olması."

    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        
        if ms1 != 99.0 and 1.30 <= ms1 <= 1.55 and ms0 != 99.0 and ms0 <= 3.20 and alt25 != 99.0 and alt25 <= 1.50:
            return True, "KISIR FAVORİ KİLİTLENMESİ (1-1/0-0): Ev sahibi favori (1.30-1.55) olmasına rağmen, Beraberlik oranı (3.20 altı) bir favori maçına göre İNANILMAZ DERECEDE DÜŞÜK. Üstelik 2.5 Alt (1.50 altı) çok cazip. İddaa ev sahibinin gol yollarında tıkanacağını ve konuk ekibin puan alacağını bas bas bağırıyor. Bu maç 1-1 veya 0-0 kilitlenecektir. Çifte Şans X2 veya MS0 harika bir tercihtir."
        return False, ""
'''

if 'class Rule1556' not in content:
    content = content.replace('class Rule1523(BaseRule):', new_rule + '\nclass Rule1523(BaseRule):')
    content = content.replace('[Rule1555, Rule1554,', '[Rule1556, Rule1555, Rule1554,')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Kurallar_Kitabi.md', 'a', encoding='utf-8') as f:
    f.write('\n### 🚨 Rule 1556: Kısır Favori Kilitlenmesi (0-0/1-1 Tuzağı)\n')
    f.write('**Koşul:** `1.30 <= MS1 <= 1.55` VE `MS0 <= 3.20` VE `Alt 2.5 <= 1.50`\n')
    f.write('**Hikaye:** Ev sahibi favori ama beraberlik oranı (3.20 altı) aşırı şüpheli düşük, Alt ise banko gibi (1.50 altı). İddaa favorinin gol atamayarak maçı 0-0 ya da 1-1 de kilitleyeceğini gösteriyor.\n')

print("Rule 1556 added successfully.")
