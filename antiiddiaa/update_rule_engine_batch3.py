import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

# 1. Update MILLI_TAKIMLAR
old_milli = '''MILLI_TAKIMLAR = [
    "Türkiye", "İspanya", "İngiltere", "Almanya", "Fransa", "İtalya", "Hollanda", "Portekiz", "Belçika", "Brezilya", "Arjantin",
    "Senegal", "Irak", "Mısır", "İran", "Yeşil Burun", "Suudi Arabistan", "Uruguay", "Japonya", "Güney Kore", "Fas", "Cezayir",
    "Nijerya", "Fildişi", "Kamerun", "Gana", "ABD", "Meksika", "Kolombiya", "Şili", "Peru", "İsveç", "İsviçre", "Danimarka",
    "Norveç", "Finlandiya", "Rusya", "Sırbistan", "Hırvatistan", "Yunanistan", "Çekya", "Polonya", "Avusturya", "Macaristan"
]'''

new_milli = '''MILLI_TAKIMLAR = [
    "Türkiye", "İspanya", "İngiltere", "Almanya", "Fransa", "İtalya", "Hollanda", "Portekiz", "Belçika", "Brezilya", "Arjantin",
    "Senegal", "Irak", "Mısır", "İran", "Yeşil Burun", "Suudi Arabistan", "Uruguay", "Japonya", "Güney Kore", "Fas", "Cezayir",
    "Nijerya", "Fildişi", "Kamerun", "Gana", "ABD", "Meksika", "Kolombiya", "Şili", "Peru", "İsveç", "İsviçre", "Danimarka",
    "Norveç", "Finlandiya", "Rusya", "Sırbistan", "Hırvatistan", "Yunanistan", "Çekya", "Polonya", "Avusturya", "Macaristan",
    "Demokratik Kongo", "Kongo", "Özbekistan", "Güney Afrika", "Mali", "Gine", "Burkina Faso", "Zambiya", "Kosta Rika",
    "Panama", "Honduras", "Jamaika", "Kanada", "Galler", "İskoçya", "İrlanda", "Kuzey İrlanda", "İzlanda", "Ukrayna",
    "Romanya", "Bulgaristan", "Slovakya", "Slovenya", "Bosna", "Karadağ", "Makedonya", "Arnavutluk", "Kıbrıs", "Ekvador",
    "Paraguay", "Venezuela", "Bolivya", "Avustralya", "Yeni Zelanda", "Katar", "BAE", "Umman", "Bahreyn", "Kuveyt",
    "Suriye", "Ürdün", "Lübnan", "Çin", "Kuzey Kore", "Tayland", "Vietnam", "Endonezya", "Malezya", "Hindistan"
]'''

content = content.replace(old_milli, new_milli)

# 2. Update Rule 1481
old_1481 = '''        if 0 < ms1 < 1.75 and ms2 < 4.00 and kg_var < 1.40:'''
new_1481 = '''        ev_iy_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst"])
        
        # Eğer ev sahibi ilk yarı 0.5 üst oranı çok düşükse (ev sahibi maça hızlı başlayacaksa) bu kural iptal olur.
        if ev_iy_05_ust > 0 and ev_iy_05_ust <= 1.50:
            return False, ""
            
        if 0 < ms1 < 1.75 and ms2 < 4.00 and kg_var < 1.40:'''

content = content.replace(old_1481, new_1481)

# 3. Add new Rule for Swedish Low KG Var Trap
new_rule_1514 = '''class Rule1514(BaseRule):
    code = "1514"
    name = "Aşırı Düşük KG Var Tuzağı (Buzul Sessizliği)"
    category = "SKOR"
    description = "KG Var oranı çok düşük olmasına rağmen ilk yarı 1.5 Üst oranı çok yüksekse maç kısır biter."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        iy_15_ust = get_odd(odds, ["1. Yarı Alt/Üst 1.5_Üst", "İlk Yarı Altı/Üstü 1.5_Üst"])
        
        if 0 < kg_var <= 1.35 and iy_15_ust >= 1.60:
            return True, "AŞIRI DÜŞÜK KG VAR TUZAĞI: Piyasada KG Var oranı 1.35 ve altında açılarak herkese 'Bu maç kesin gollü geçecek, iki takım da atacak' mesajı veriliyor. Ancak İlk Yarı 1.5 Üst oranı (1.60+) bunun tam tersini, yani maçın yavaş ve kilitli başlayacağını söylüyor. Bu muazzam bir alt tuzağıdır. Maç 0-0 veya 1-0 gibi çok kısır bir skorla biter."
        return False, ""
'''

if "Rule1514" not in content:
    content = content.replace('def get_all_rules():', new_rule_1514 + '\ndef get_all_rules():')
    content = content.replace('Rule1513, ', 'Rule1514, Rule1513, ')

# 4. Filter missing odds in Rule2001 and 2002 to avoid default 99.0 false positives
old_2001_eval = '''        is_balanced = min(ms1, ms2) >= 1.90
        is_iy_kisir = (ev_iy_05_ust >= 1.85 and dep_iy_05_ust >= 1.85)
        
        if is_balanced and (kg_var <= 1.85 or is_iy_kisir):'''

new_2001_eval = '''        # Oranların 99.0 (veri yok) olmamasını sağla
        if ms1 == 99.0 or ms2 == 99.0: return False, ""
        
        is_balanced = min(ms1, ms2) >= 1.90
        is_iy_kisir = (ev_iy_05_ust >= 1.85 and dep_iy_05_ust >= 1.85 and ev_iy_05_ust != 99.0)
        
        if is_balanced and (kg_var <= 1.85 or is_iy_kisir):'''
        
content = content.replace(old_2001_eval, new_2001_eval)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)
