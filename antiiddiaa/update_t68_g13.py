import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf8') as f:
    engine = f.read()

# REWRITE T68
t68_pattern = r'class RuleT68\(BaseRule\):.*?return False, ""'
t68_new = """class RuleT68(BaseRule):
    code = "T68"
    category = "YÖN"
    name = "Görünür Favori Tuzağı (Gerçekte Değil)"
    description = "Piyasanın favori gösterdiği takımın aslında kazanamayacağı tuzak."
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        cs_02 = get_odd(odds, ["Çifte Şans_0 ve 2", "Çifte Şans_02"])
        cs_10 = get_odd(odds, ["Çifte Şans_1 ve 0", "Çifte Şans_1X"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt", "Deplasman Altı/Üstü 1.5_Alt"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        
        # 1. Deplasman Görünür Favori Tuzağı
        if ((1.65 <= ms2 <= 1.75) or (2.00 <= ms2 <= 2.10)) and cs_02 <= 1.25 and dep_15_alt <= 1.55:
            return True, "DEPLASMAN GÖRÜNÜR FAVORİ TUZAĞI: Deplasman takımı favori gibi gösterilse de (MS2 1.65-2.10 arası) Çifte Şans 02 ve Deplasman 1.5 Alt oranları bu durumu yalanlıyor. Deplasman kazanamaz, hatta gol bile atamaz. En yüksek ihtimal beraberlik veya ev sahibi sürpriz galibiyetidir."
            
        # 2. Ev Sahibi Görünür Favori Tuzağı
        if (1.65 <= ms1 <= 1.70) and cs_10 <= 1.10 and ev_15_alt <= 1.50:
            return True, "EV SAHİBİ GÖRÜNÜR FAVORİ TUZAĞI: Ev sahibi favori gibi gösterilse de, Ev Sahibi 1.5 Alt oranının 1.50 altında olması tuzağı ele veriyor. Ev sahibi kazanamaz, genellikle gol bile atamaz. En yüksek ihtimal golsüz beraberlik veya az gollü deplasman galibiyetidir."
            
        return False, "" """
engine = re.sub(t68_pattern, t68_new, engine, flags=re.DOTALL)


# ADD G13
g13_new = """
class RuleG13(BaseRule):
    code = "G13"
    category = "GOL"
    name = "Her İki Yarıda Da Karşılıklı Gol (İYKG)"
    description = "Tüm gol baremlerinin ve yarı oranlarının inanılmaz gollü bir senaryoyu desteklemesi."
    
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst"])
        iy_kg_var = get_odd(odds, ["1. Yarı Karşılıklı Gol_Var"])
        iy2_kg_var = get_odd(odds, ["2. Yarı Karşılıklı Gol_Var"])
        
        if (1.35 <= kg_var <= 1.75) and ust25 <= 1.65 and ev_05_ust <= 1.60 and dep_05_ust <= 1.60 and iy_kg_var <= 3.40 and iy2_kg_var <= 2.99:
            return True, "HER İKİ YARIDA KARŞILIKLI GOL (İYKG): Gol beklentisi o kadar yüksek ki, hem ilk yarı hem de ikinci yarıda her iki takımın da gol bulması matematiksel olarak destekleniyor. Çılgın bir düello bekleniyor."
        return False, ""
"""
engine = engine.replace('def get_all_rules():', g13_new + '\ndef get_all_rules():')
engine = re.sub(r'(gol_rules = \[)', r'\1RuleG13, ', engine)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf8') as f:
    f.write(engine)

# Update story_analyzer.py
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf8') as f:
    analyzer = f.read()

analyzer = analyzer.replace(
    "'T68': (\"Beraberlik İptali (Sürpriz Taraf Kazanır)\", \"Çifte Şans 12 + 1.5 Gol Üstü (Sürpriz Skor: 1-2 / 2-1)\"),",
    "'T68': (\"Görünür Favori Tuzağı\", \"Favorinin Karşısındaki Taraf Kaybetmez + 2.5 Alt\"),"
)

new_g13 = "\n        'G13': (\"Her İki Yarıda Da Karşılıklı Gol (İYKG)\", \"1. Yarı KG Var & 2. Yarı KG Var (Sürpriz Skor: 2-2 / 3-3)\"),"
analyzer = analyzer.replace("predictions = {", "predictions = {" + new_g13)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf8') as f:
    f.write(analyzer)

# Update Kurallar_Kitabi.md
md_rule = "\n| **G13** | Her İki Yarıda Da Karşılıklı Gol (İYKG) | GOL | **İYKG:** KG Var=1,35–1,75, 2,5 Üst <=1,65, Ev/Dep 0.5 Üst <=1,60, İlk Yarı KG Var <=3,40, İkinci Yarı KG Var <=2.99. Bu koşullar sağlandığında maç muazzam gollü bir düelloya dönüşür. |\n"
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Kurallar_Kitabi.md', 'a', 'utf8') as f:
    f.write(md_rule)

print("T68 rewritten and G13 added!")
