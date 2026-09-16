import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

old_1481 = '''    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        
        if ms1 < ms2 and ms1 <= 1.65 and ms1 >= 1.45 and kg_var <= 1.35 and ust35 <= 1.85 and ust35 != 99.0:'''

new_1481 = '''    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        ev_iy_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst"])
        
        if ev_iy_05_ust != 99.0 and ev_iy_05_ust <= 1.45:
            return False, ""
            
        if ms1 < ms2 and ms1 <= 1.65 and ms1 >= 1.45 and kg_var <= 1.35 and ust35 <= 1.85 and ust35 != 99.0:'''

content = content.replace(old_1481, new_1481)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)
