import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

new_1481 = '''class Rule1481(BaseRule):
    code = "1481"
    category = "YÖN"
    name = "Aşırı Gollü Sahte Favori Tuzağı (Deplasman Sürprizi)"
    description = "MS1 Favori + KG Var Çok Düşük + 3.5 Üst Çok Düşük = Sürpriz Deplasman (X2)"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        
        ev_iy_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Alt/Üst 0.5_Üst", "Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst"])
        if ev_iy_05_ust != 99.0 and ev_iy_05_ust <= 1.45:
            return False, ""
        
        if ms1 < ms2 and ms1 <= 1.65 and ms1 >= 1.45 and kg_var <= 1.35 and ust35 <= 1.85 and ust35 != 99.0:
            return True, "AŞIRI GOLLÜ SAHTE FAVORİ TUZAĞI: Ev sahibi 1.6X oranla favori gösterilmiş ve maçın 4+ gol (3.5 Üst) ile KG Var şeklinde biteceği çok bariz bir şekilde (aşırı düşük oranlarla) fiyatlanmış. Bu durum oyuncuları 'Ev sahibi 3-1 veya 4-1 kazanır' (MS1 + Üst) tuzağına çekmek içindir. İddaa böylesine gollü ve net bir favori galibiyetini bu kadar bağırarak vermez. Bu, deplasman takımının sürpriz bir şekilde maçta üstünlük kuracağı (Örn: 1-3, 2-2) devasa bir tuzaktır. MS2 veya X2 denenmelidir."
            
        return False, ""
'''

# Replace the whole class definition
content = re.sub(r'class Rule1481\(BaseRule\):.*?return False, ""\s*', new_1481, content, flags=re.DOTALL)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)
