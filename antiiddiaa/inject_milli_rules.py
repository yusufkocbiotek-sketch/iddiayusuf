import codecs

# 1. Update rule_engine.py
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

# Add CURRENT_MATCH and is_milli_mac
header_addition = '''
CURRENT_MATCH = {}

MILLI_TAKIMLAR = [
    "Türkiye", "İspanya", "İngiltere", "Almanya", "Fransa", "İtalya", "Hollanda", "Portekiz", "Belçika", "Brezilya", "Arjantin",
    "Senegal", "Irak", "Mısır", "İran", "Yeşil Burun", "Suudi Arabistan", "Uruguay", "Japonya", "Güney Kore", "Fas", "Cezayir",
    "Nijerya", "Fildişi", "Kamerun", "Gana", "ABD", "Meksika", "Kolombiya", "Şili", "Peru", "İsveç", "İsviçre", "Danimarka",
    "Norveç", "Finlandiya", "Rusya", "Sırbistan", "Hırvatistan", "Yunanistan", "Çekya", "Polonya", "Avusturya", "Macaristan"
]

def is_milli_mac(match):
    ev = match.get('ev_sahibi', '').upper()
    dep = match.get('deplasman', '').upper()
    
    # Check for U19, U20, U21 etc.
    if ' U1' in ev or ' U2' in ev or ' U1' in dep or ' U2' in dep:
        return True
    
    # Check for Women (K) or Reserves (B)
    if ev.endswith(' K') or dep.endswith(' K') or ev.endswith(' (K)') or dep.endswith(' (K)'):
        return True
        
    # Check if country name is in the team name
    for ulke in MILLI_TAKIMLAR:
        if ulke.upper() == ev or ulke.upper() == dep:
            return True
            
    return False
'''

if "CURRENT_MATCH =" not in content:
    content = content.replace('import re\n', 'import re\n' + header_addition)

# Add Rule 2001 and 2002 for Milli Matches
milli_rules = '''
class Rule2001(BaseRule):
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
        return False, ""

class Rule2002(BaseRule):
    code = "2002"
    name = "Milli Maç Şovu (Zayıf Halka Ezilir)"
    category = "GOL"
    description = "Milli maçlarda favori takım, zayıf rakibi acımadan ezer."
    @classmethod
    def evaluate(cls, odds):
        if not is_milli_mac(CURRENT_MATCH): return False, ""
        
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if min(ms1, ms2) <= 1.35:
            return True, "MİLLİ MAÇ EZİCİLİĞİ: Milli maçlarda klasman farkı çok derindir. Normal liglerde zayıf takım kapanıp maçı 1-0'da tutabilir, ancak milli takımlarda zayıf halkalar koptuğunda maç 4-0, 5-0 gibi tarihi farklara gider. Burada sürpriz aramak intihardır. MS (Favori) ve 2.5 / 3.5 Üst bankodur."
        return False, ""
'''

if "Rule2001" not in content:
    content = content.replace('def get_all_rules():', milli_rules + '\ndef get_all_rules():')
    content = content.replace('Rule1513, ', 'Rule2001, Rule2002, Rule1513, ')

# Inject İlk Yarı 0.5 Üst optimization into Rule 1512 (Gizli Barem)
old_1512 = '''        if not has_25 and has_35 and 0 < ms1 <= 1.55 and 0 < kg_var <= 1.50 and ust35 > 0:
            if ust35 < 1.80:'''
new_1512 = '''        ev_iy_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst"])
        dep_iy_05_ust = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        
        if not has_25 and has_35 and 0 < ms1 <= 1.55 and 0 < kg_var <= 1.50 and ust35 > 0:
            # Optimizasyon: İlk Yarı 0.5 Üst oranları gol habercisidir
            if ust35 < 1.80 or (ev_iy_05_ust > 0 and ev_iy_05_ust <= 1.50) or (dep_iy_05_ust > 0 and dep_iy_05_ust <= 1.50):'''
content = content.replace(old_1512, new_1512)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)


# 2. Update story_analyzer.py
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()

# Inject CURRENT_MATCH assignment
story_injection = '''    # Set CURRENT_MATCH in rule_engine
    import rule_engine
    rule_engine.CURRENT_MATCH = match
    
    triggered_rules = []'''

if "rule_engine.CURRENT_MATCH = match" not in story:
    story = story.replace('    triggered_rules = []', story_injection)

# Add handling for 2001 and 2002
correct_state = '''    elif any(r['code'] == '2001' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 2.5 Gol Altı (Milli Maç Kısırlığı)")
        output.append(f"- **Kombine Öneri:** 2.5 Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0 / 1-1 / 1-0)")
    elif any(r['code'] == '2002' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1/2 (Milli Maç Fark Patlaması)")
        output.append(f"- **Kombine Öneri:** Favori Kazanır + 3.5 Gol Üst (Sürpriz Skor: 4-0 / 5-0)")
    elif any(r['code'] == '1513' for r in triggered_rules):'''
    
bad_state = '''    elif any(r['code'] == '1513' for r in triggered_rules):'''

if "2001" not in story:
    story = story.replace(bad_state, correct_state)
    
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf-8') as f:
    f.write(story)
