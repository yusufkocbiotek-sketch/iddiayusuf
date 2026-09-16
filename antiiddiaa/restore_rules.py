import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

rules = '''
class Rule1553(BaseRule):
    code = "1553"
    name = "Dengeli KG Patlaması (Sahte Kısır - 3-2/2-2)"
    category = "TUZAK"
    description = "Tam dengeli maçta KG Var bankoyken Alt 2.5'in cazip gösterilmesi."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        
        if ms1 != 99.0 and ms2 != 99.0 and ms1 >= 1.95 and ms2 >= 1.95:
            if kg_var != 99.0 and kg_var <= 1.50 and alt25 != 99.0 and alt25 <= 1.65:
                return True, "DENGELİ KG PATLAMASI (SAHTE KISIR): Maç tamamen dengeli (Taraf yok) ve İddaa her iki takımın da kesinlikle gol atacağını (KG Var < 1.50) itiraf ediyor. Ancak 2.5 Alt oranı (1.65 altı) ile maçı 1-1 bitmeye kilitli gibi gösteriyor. Bu bir tuzaktır! İki takımın da gol atacağı garanti olan bir maçta, beraberlik bozucu bir 3. gol kesinlikle çıkacaktır. Maç 3-2 veya 2-2 gibi bol gollü bir skora patlayacaktır (2.5 Üst bankodur)."
        return False, ""

class Rule1554(BaseRule):
    code = "1554"
    name = "Ağır Favori Oran Çelişkisi (Puan Kaybı Tuzağı - 1-1/0-0)"
    category = "TUZAK"
    description = "1.30 altı favoriye anormal derecede düşük MS0 ve MS2 verilmesi."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if ms1 != 99.0 and ms1 <= 1.30 and ms0 != 99.0 and ms0 <= 4.50 and ms2 != 99.0 and ms2 <= 8.50:
            return True, "AĞIR FAVORİ ORAN ÇELİŞKİSİ (PUAN KAYBI): Ev sahibi 1.30 altı oranla devasa bir favori. Ancak Beraberlik (4.50 altı) ve Deplasman (8.50 altı) oranları, bir ağır favori maçına göre İNANILMAZ DERECEDE DÜŞÜK! İddaa, MS1'i cazip bir banko yemi olarak sunarken aslında içeride konuk ekibin direneceğini çok iyi biliyor. Bu maçta ağır favori kesinlikle puan kaybedecektir (1-1 veya 0-0). MS1 uzak durulması gereken ölümcül bir tuzaktır."
        return False, ""

class Rule1555(BaseRule):
    code = "1555"
    name = "1-1 Sendromu (Yüksek Beraberlik Riski)"
    category = "TUZAK"
    description = "Normal favorili maçta MS0 ve KG Var düşükse 1-1 kilitlenme tuzağı."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        
        if ms1 != 99.0 and 1.30 <= ms1 <= 1.55 and ms0 != 99.0 and ms0 <= 3.40 and kg_var != 99.0 and kg_var <= 1.55:
            if ust25 != 99.0 and ust25 <= 1.50:
                return False, ""
            return True, "1-1 SENDROMU (BERABERLİK TUZAĞI): Ev sahibi normal bir favori (1.30-1.55) ama Beraberlik (3.40 altı) ve KG Var (1.55 altı) oranları şüpheli derecede cazip. Bu maç 1-1 bitmeye programlanmıştır. MS0 veya İlk Yarı Beraberliği değerlendirilebilir."
        return False, ""

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

# Delete the get_all_rules function
content = content.split('def get_all_rules():')[0]

# Append the rules
content += rules

# Recreate get_all_rules
get_all_rules = '''
def get_all_rules():
    trend_rules = [RuleG11, RuleG1, RuleS1, RuleS2, RuleT10, RuleT27, RuleT8, RuleY11]
    anomaly_rules = [Rule1556, Rule1555, Rule1554, Rule1553, Rule1552, Rule1551, Rule1550, Rule1549, Rule1548, Rule1547, Rule1545, Rule1542, Rule1541, Rule1540, Rule1536, Rule1535, Rule1534, Rule1533, Rule1532, Rule1531, Rule1530, Rule1523, Rule1522, Rule1519, Rule1518, Rule1517, RuleT70, Rule1516, Rule1515, Rule999, Rule2003, Rule1513B, Rule2001, Rule2002, Rule1514, Rule1513, Rule1512A, Rule1512B, Rule1511, Rule1510, Rule1509, Rule1508, Rule1507, Rule1506, Rule1505, Rule1504, Rule1503, Rule1502, Rule1501, Rule1500, Rule1499, Rule1498, Rule1497, Rule1496, Rule1494, Rule1493, Rule1492, Rule1491, Rule1490, Rule1489, Rule1488, Rule1487, Rule1486, Rule1485, Rule1484, Rule1483, Rule1481, Rule1480, Rule1479, Rule1478, Rule1477, Rule1476, Rule1475, Rule1474, Rule1473, Rule1472, Rule1470, Rule1469, Rule1468, Rule1467, Rule1466, Rule1465, Rule1464, Rule1463, Rule1462B, Rule1462, Rule1460]
    return anomaly_rules + trend_rules
'''
content += get_all_rules

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Restored deleted rules.")
