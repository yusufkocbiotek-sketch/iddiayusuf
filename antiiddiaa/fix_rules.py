import sys

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start = -1
end = -1
for i, l in enumerate(lines):
    if 'class Rule1467B' in l:
        start = i
    elif start != -1 and l.startswith('class '):
        end = i
        break

new_code = '''class Rule1467B(BaseRule):
    code = "1467B"
    category = "SKOR"
    name = "Gollü Beraberlik Tuzağı (2-2 / 3-3)"
    description = "MS0 > 2.85 + Alt25 <= 1.60 + Denk Takımlar (MS1 ve MS2 >= 2.00)"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1", "1", "Maç Sonucu_Ev"])
        ms0 = get_odd(odds, ["Maç Sonucu_0", "0", "Beraberlik", "Maç Sonucu_X", "X"])
        ms2 = get_odd(odds, ["Maç Sonucu_2", "2", "Maç Sonucu_Deplasman"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt", "Alt/Üst 2,5_Alt"])
        
        if ms1 >= 2.00 and ms2 >= 2.00 and ms0 > 2.85 and ms0 != 99.0 and alt25 <= 1.60 and alt25 != 99.0:
            return True, "GOLLÜ BERABERLİK TUZAĞI (1467B): Taraf oranları birbirine bu kadar yakınken (Dengeli Maç), beraberlik oranının (MS 0) 2.85'in üzerinde tutulması ve Alt oranının (1.60 ve altı) favori gösterilmesi adeta 0-0'a işaret ediyor. Herkes '0 ve Alt' kovalarken bu maç akılalmaz bir gol düellosuna döner. Maç berabere bitse bile 2-2 veya 3-3 gibi astronomik skorlarla biter. 2.5 Üst ve KG Var bankodur!"
        return False, ""

class Rule1530B(BaseRule):
    code = "1530B"
    category = "SKOR"
    name = "1530 Çifte Tuzağı (Ölümcül Kısır Döngü 0-0)"
    description = "Beraberlik Oranı (MS 0) 2.85 ve altındaysa bu bir ÇİFTE TUZAKTIR, gol çıkmaz."
    
    @classmethod
    def evaluate(cls, odds):
        ms0 = get_odd(odds, ["Maç Sonucu_0", "0", "Beraberlik", "Maç Sonucu_X", "X"])
        ms1 = get_odd(odds, ["Maç Sonucu_1", "1", "Maç Sonucu_Ev"])
        ms2 = get_odd(odds, ["Maç Sonucu_2", "2", "Maç Sonucu_Deplasman"])
        
        if ms0 <= 2.85 and ms0 != 99.0 and ms1 >= 2.00 and ms2 >= 2.00 and ms1 != 99.0 and ms2 != 99.0:
            return True, "1530 ÇİFTE TUZAĞI (ÖLÜMCÜL KISIR 0-0): Eğer Beraberlik Oranı (MS 0) 2.85 ve altındaysa bu İddaa'nın en tehlikeli çifte tuzağıdır! Sistem sizi gol beklentisine veya taraf bahsine sokmaya çalışır ama bu maçta gol falan çıkmaz. Maç doğrudan 0-0 kilitlenmeye veya en fazla 1-0/0-1 bitmeye programlıdır. Kesin 2.5 Alt ve İlk Yarı 0/Maç Sonucu 0 denenir!"
        return False, ""

'''

lines = lines[:start] + [new_code] + lines[end:]

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
