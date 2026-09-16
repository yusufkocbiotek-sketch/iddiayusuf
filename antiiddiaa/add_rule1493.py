import codecs
import re

content = codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf8').read()

new_rule = '''
class Rule1493(BaseRule):
    code = "1493"
    name = "Sahte Deplasman Favorisi (Handikap 1 Gizli Bankosu)"
    category = "YÖN"
    description = "Deplasman favori (1.85-2.15) ama H1 <= 1.45 ve KG Var <= 1.50"
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        h1 = get_odd(odds, ["Handikaplı Maç Sonucu 0:1_1", "Handikaplı Maç Sonucu 1:0_1", "Handikap 1:0_1"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if 1.85 <= ms2 <= 2.15 and h1 <= 1.45 and h1 != 99.0 and kg_var <= 1.50:
            return True, "SAHTE DEPLASMAN FAVORİSİ: Deplasman takımı 1.85-2.15 arası oranla 'hafif favori' gibi sunulur ve KG Var (1.50 altı) ile maçın gollü geçeceği algısı yaratılır. Herkes Deplasman galibiyetine veya gollere yönelirken, iddaa arka planda 'Handikap 1' (Ev sahibinin yenilmeyeceği) oranını 1.45'in altına çekerek maçı Ev sahibine bağlamıştır. Deplasman favorisi tamamen sahtedir, maçı Ev sahibi sürpriz bir şekilde (2-0, 2-1) kazanır. Doğrudan MS1, 1X veya Handikap 1 oynanmalıdır."
        return False, ""
'''

# Insert after Rule1492
pos = content.find('class Rule1492')
if pos != -1:
    end_pos = content.find('class Rule', pos + 10)
    if end_pos != -1:
        content = content[:end_pos] + new_rule + content[end_pos:]
    else:
        content += new_rule
    codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf8').write(content)
    print("Rule1493 added.")
else:
    print("Rule1492 not found.")
