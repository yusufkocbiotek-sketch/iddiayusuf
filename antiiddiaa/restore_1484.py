import codecs

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1484 = '''
class Rule1484(BaseRule):
    code = "1484"
    category = "SKOR"
    name = "Aşırı Şişirilmiş Favori Alt Tuzağı"
    description = "MS1 <= 1.25 + 2.5 Üst <= 1.30 + Ev 1.5 Alt >= 2.50 = 1-0 / 2-0 Alt"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        
        if ms1 <= 1.25 and ust25 <= 1.30 and ev_15_alt >= 2.50:
            return True, "AŞIRI ŞİŞİRİLMİŞ FAVORİ ALT TUZAĞI: Ev sahibi (1.20) banko favori. Maçın Üst biteceği ve Ev sahibinin en az 2-3 gol atacağı oranlara (Ev 1.5 Alt 3.00 vs) yansımış. MS1 oranı para kazandırmadığı için iddaa oyuncuları 'Ev Sahibi 2.5 Üst' veya '1 ve Üst' bahislerine yönlendiriliyor. Bu devasa bir tuzaktır. Maçta favori kazanır ama şova izin verilmez, rölantide 1-0 veya 2-0 biter. 2.5 Alt ve 3.5 Alt bahisleri gizli hazinedir."
        return False, ""

'''
if 'class Rule1484' not in content:
    content = content.replace('def get_all_rules():', rule_1484 + 'def get_all_rules():')
    with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
        f.write(content)
