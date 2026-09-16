import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

new_rule = '''class Rule1482(BaseRule):
    code = "1482"
    category = "TUZAK"
    name = "Ağır Deplasman Favorisi + Sahte KG Var Tuzağı (KG Yok)"
    description = "MS2 < 1.55 + KG Var < 1.60 = Ev sahibi gol atamaz, KG Yok Biter"
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms2 != 99.0 and ms2 <= 1.55 and kg_var != 99.0 and kg_var <= 1.60:
            return True, "SAHTE KG VAR TUZAĞI: Deplasman takımı maçı kazanmak için çok ağır favori (1.50 altı). Maçın normalde 0-2 veya 0-3 bitmesi beklenir. Ancak İddaa, KG Var oranını 1.60'ın altında açarak 'Ev sahibi de gol bulacak, bu maç karşılıklı golle üst bitecek (Örn: 1-2, 1-3)' izlenimi yaratıyor. Bu tamamen bahisçileri ÜST ve KG VAR bahislerine çekmek için kurulan bir yemdir. Ev sahibi gol bulamaz. Maç KG YOK biter."
            
        return False, ""

'''

# Insert it before Rule1495
import re
content = re.sub(r'(class Rule1495)', new_rule + r'\1', content, count=1)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)
