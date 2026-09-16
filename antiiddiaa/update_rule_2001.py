import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

old_rule = '''class Rule2001(BaseRule):
    code = "2001"
    name = "Milli Maç Sendromu (Kısır Turnuva)"
    category = "GOL"
    description = "Milli maçlarda (veya U20) piyasa Asya tuzağı koksa da maç alt biter."
    @classmethod
    def evaluate(cls, odds):
        if not is_milli_mac(CURRENT_MATCH): return False, ""
        
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        
        if min(ms1, ms2) >= 1.90 and kg_var <= 1.65:
            return True, "MİLLİ MAÇ KISIRLIĞI: Normal bir lig maçında bu oranlar 'Asya Tuzağı' veya 'Gol Düellosu' alarmı verirdi. Ancak bu bir Milli Maç (veya Gençler turnuvası). Milli maçlarda takımlar temkinli oynar, beraberlik (0-0, 1-1) çok yaygındır. KG Var veya Üst bahisleri büyük bir tuzaktır. 2.5 Alt en güvenli limandır."
        return False, ""'''

new_rule = '''class Rule2001(BaseRule):
    code = "2001"
    name = "Milli Maç Sendromu (Kısır Turnuva)"
    category = "GOL"
    description = "Milli maçlarda (veya U20) piyasa Asya tuzağı koksa da maç alt biter."
    @classmethod
    def evaluate(cls, odds):
        if not is_milli_mac(CURRENT_MATCH): return False, ""
        
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ev_iy_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst"])
        dep_iy_05_ust = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Üst"])
        
        # Eğer taraf denkliği varsa (min(ms1, ms2) >= 1.90) 
        # ve iki takımın da ilk yarı bireysel gol atma oranları çok yüksekse (2.00 üzeri)
        # VEYA KG Var oranı Asya baremindeyse (1.50 - 1.90 arası)
        
        is_balanced = min(ms1, ms2) >= 1.90
        is_iy_kisir = (ev_iy_05_ust >= 1.85 and dep_iy_05_ust >= 1.85)
        
        if is_balanced and (kg_var <= 1.85 or is_iy_kisir):
            return True, "MİLLİ MAÇ KISIRLIĞI: Normal bir lig maçında dengeli takımlar 'Asya Tuzağı' veya 'Gol Düellosu' alarmı verirdi. Ancak bu bir Milli Maç. İlk Yarı 0.5 Üst bireysel takım oranları (2.00 civarı) bize kimsenin erken gol bulamayacağını söylüyor. Milli maçlarda takımlar temkinli oynar, beraberlik (0-0, 1-1) çok yaygındır. KG Var veya Üst bahisleri büyük bir tuzaktır. 2.5 Alt bankodur."
        return False, ""'''

content = content.replace(old_rule, new_rule)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)
