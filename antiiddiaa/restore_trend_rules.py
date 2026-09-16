import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

trend_rules_code = '''
class RuleG1(BaseRule):
    code = "G1"
    name = "Kesin 2 Gol Sinyali"
    category = "GOL"
    @classmethod
    def evaluate(cls, odds):
        alt15 = get_odd(odds, ["Alt/Üst 1.5_Alt", "Altı/Üstü 1.5_Alt"])
        if alt15 >= 2.50 and alt15 != 99.0:
            return True, "Maçta en az 2 gol kesin çıkar."
        return False, ""

class RuleG11(BaseRule):
    code = "G11"
    name = "Gollü KG Var"
    category = "GOL"
    @classmethod
    def evaluate(cls, odds):
        kg = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        if kg <= 1.50 and ust25 <= 1.60 and kg != 99.0:
            return True, "KG Var ve 2.5 Üst beklentisi."
        return False, ""

class RuleS1(BaseRule):
    code = "S1"
    name = "Standart Kısır Favori (Tuzak Yok)"
    category = "BİLGİ"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        if (ms1 <= 1.80 or ms2 <= 1.80) and alt25 <= 1.70 and alt25 != 99.0:
            return True, "STANDART PİYASA (KISIR FAVORİ): Bu maçta herhangi bir anomali veya tuzak tespit edilemedi. İddaa oranları favorinin düşük gollü (1-0, 2-0) bir galibiyet alacağını net bir şekilde gösteriyor. Maçın genel gidişatına güvenilebilir, sürpriz aranmamalıdır."
        return False, ""

class RuleS2(BaseRule):
    code = "S2"
    name = "Standart Gollü Favori (Tuzak Yok)"
    category = "BİLGİ"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        if (ms1 <= 1.80 or ms2 <= 1.80) and ust25 <= 1.70 and ust25 != 99.0:
            return True, "STANDART PİYASA (GOLLÜ FAVORİ): Bu maçta herhangi bir anomali veya tuzak tespit edilemedi. İddaa oranları favorinin gollü (2-1, 3-0, 3-1 vb.) bir galibiyet alacağını gösteriyor. Gollere veya favoriye yönelmek piyasanın doğal akışıdır."
        return False, ""

class RuleT10(BaseRule):
    code = "T10"
    name = "Dengeli Kısır İç Saha"
    category = "YÖN"
    @classmethod
    def evaluate(cls, odds):
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        if ms0 <= 2.90 and alt25 <= 1.60 and ms0 != 99.0:
            return True, "Beraberlik oranı çok düşük, maç kısır geçer."
        return False, ""

class RuleT27(BaseRule):
    code = "T27"
    name = "Az Gollü Temiz Favori"
    category = "YÖN"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        if ms1 <= 1.50 and alt25 <= 1.70 and ms1 != 99.0:
            return True, "Ev sahibi maçı alır ancak skor tek taraflı ve az gollü (1-0, 2-0) olur."
        return False, ""

class RuleT8(BaseRule):
    code = "T8"
    name = "Dengeli Ters Favori İç Saha"
    category = "YÖN"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        if ms1 <= 2.20 and ms2 <= 3.20 and ms1 != 99.0:
            return True, "Dengeli maçta beraberlik dışlanmış, ev sahibi kazanır."
        return False, ""

class RuleY11(BaseRule):
    code = "Y11"
    name = "Psikolojik 12 Tuzağı (İlk Yarı 0 Bankosu)"
    category = "YARI"
    @classmethod
    def evaluate(cls, odds):
        cs_12 = get_odd(odds, ["Çifte Şans_1 ve 2", "Çifte Şans_12"])
        if cs_12 <= 1.20 and cs_12 != 99.0:
            return True, "İLK YARI 0 BANKOSU (PSİKOLOJİK TUZAK): İddaa dengeli bir maçta Çifte Şans 12'ye çok düşük oran (<= 1.20) vererek 'Bu maç asla berabere bitmez, kesin biri yener' algısı yaratıyor. Üstüne KG Var oranını da düşük tutarak maçın çok tempolu başlayacağı illüzyonunu kuruyor. Oysa istatistiklere göre bu maçların yarısından fazlası (%53.6) ilk yarıda tamamen kilitlenir. Büroların bu algı operasyonu yüzünden İlk Yarı 0'a verdikleri devasa 2.15+ oranlar sayesinde bu bahis uzun vadede %16.5 net kâr (ROI) bırakır!"
        return False, ""
'''

# Delete get_all_rules again
content = content.split('def get_all_rules():')[0]

# Add trend rules and get_all_rules back
content += trend_rules_code

get_all_rules_code = '''
def get_all_rules():
    trend_rules = [RuleG11, RuleG1, RuleS1, RuleS2, RuleT10, RuleT27, RuleT8, RuleY11]
    anomaly_rules = [Rule1556, Rule1555, Rule1554, Rule1553, Rule1552, Rule1551, Rule1550, Rule1549, Rule1548, Rule1547, Rule1545, Rule1542, Rule1541, Rule1540, Rule1536, Rule1535, Rule1534, Rule1533, Rule1532, Rule1531, Rule1530, Rule1523, Rule1522, Rule1519, Rule1518, Rule1517, RuleT70, Rule1516, Rule1515, Rule999, Rule2003, Rule1513B, Rule2001, Rule2002, Rule1514, Rule1513, Rule1512A, Rule1512B, Rule1511, Rule1510, Rule1509, Rule1508, Rule1507, Rule1506, Rule1505, Rule1504, Rule1503, Rule1502, Rule1501, Rule1500, Rule1499, Rule1498, Rule1497, Rule1496, Rule1494, Rule1493, Rule1492, Rule1491, Rule1490, Rule1489, Rule1488, Rule1487, Rule1486, Rule1485, Rule1484, Rule1483, Rule1481, Rule1480, Rule1479, Rule1478, Rule1477, Rule1476, Rule1475, Rule1474, Rule1473, Rule1472, Rule1470, Rule1469, Rule1468, Rule1467, Rule1466, Rule1465, Rule1464, Rule1463, Rule1462B, Rule1462, Rule1460]
    return anomaly_rules + trend_rules
'''

content += get_all_rules_code

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Trend rules restored.")
