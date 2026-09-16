import codecs

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

# 1. Replace Rule1489 completely
rule_1489_old = '''
class Rule1489(BaseRule):
    code = "1489"
    name = "Aşırı Düşük KG Var Tuzağı (Gel Gel Tuzağı)"
    category = "GOL"
    description = "KG Var oranı 1.24 ve altındaysa bu devasa bir tuzaktır."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if kg_var <= 1.24:
            return True, "AŞIRI DÜŞÜK KG VAR TUZAĞI: Bürolar KG Var oranını mantık dışı bir seviyeye (1.24 ve altı) çekerek herkese bedava para dağıtıyormuş gibi 'kesin karşılıklı gol olur' yemi atıyor! Bahis şirketleri asla bedava para dağıtmaz. Bu kadar bariz bir 'gel gel' tuzağı, maçın kısır geçeceğinin (0-0, 1-0) veya en azından bir takımın gol atamayacağının en büyük kanıtıdır. Taraf bahsine veya gollere (KG Var, Üst) asla bulaşılmamalı, doğrudan Karşılıklı Gol Yok veya Alt oynanmalıdır."
        return False, ""
'''

rule_1489_new = '''
class Rule1489(BaseRule):
    code = "1489"
    name = "Aşırı Düşük KG Var Tuzağı (Gel Gel Tuzağı)"
    category = "GOL"
    description = "Favorili maçlarda KG Var oranı 1.25 ve altındaysa bu devasa bir tuzaktır."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if kg_var <= 1.25 and (ms1 <= 1.50 or ms2 <= 1.50):
            return True, "AŞIRI DÜŞÜK KG VAR TUZAĞI (Favorili Maç): Maçta çok net bir favori (1.50 altı) varken, KG Var oranı mantık dışı bir seviyeye (1.25 ve altı) çekilmiş. Bu, herkese bedava para dağıtıyormuş gibi 'zayıf takım da kesin gol atar' yemi atılmasıdır! Bahis şirketleri asla bedava para dağıtmaz. Bu kadar bariz bir 'gel gel' tuzağı, favorinin maçı gol yemeden (1-0, 2-0) kazanacağının veya maçın tamamen kilitleneceğinin (0-0) kanıtıdır. Doğrudan Karşılıklı Gol Yok veya Alt oynanmalıdır."
        return False, ""

class Rule1490(BaseRule):
    code = "1490"
    name = "Devasa Favori Çöküşü (Garanti KG Var)"
    category = "SKOR"
    description = "MS1 <= 1.18 ama KG Var <= 1.35 ise deplasman patlaması yaşanır."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        
        if ms1 <= 1.18 and kg_var <= 1.35:
            return True, "DEVASA FAVORİ ÇÖKÜŞÜ: Ev sahibi (1.18 altı) devasa favori olmasına rağmen KG Var oranı (1.35 altı) inanılmaz düşük! Bu ne demek? Deplasmanın KESİNLİKLE gol atacağı biliniyor. Ev sahibinin maçı kazanabilmesi için en az 2-3 gol atması lazım, ancak bu bir patlama maçıdır. Deplasman takımı maçı 1-2 gibi bir skorla kazanabilir veya sürpriz bir beraberlik (1-1, 2-2) koparabilir. Taraf bahsinden (Banko MS1'den) uzak durulup, doğrudan KG Var, 2.5 Üst veya Sürpriz X2 Çifte Şans oynanmalıdır."
        return False, ""

class Rule1491(BaseRule):
    code = "1491"
    name = "Dengeli Maçlarda Gerçek Düello (1.25 Altı KG Var)"
    category = "GOL"
    description = "Tarafı belli olmayan dengeli maçta KG Var <= 1.25 ise kesin Üst biter."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if kg_var <= 1.25 and ms1 > 1.80 and ms2 > 1.80:
            return True, "GERÇEK DÜELLO TESPİTİ: Dengeli bir maçta (MS1 ve MS2 1.80 üzeri) KG Var oranı aşırı düşük (1.25 altı) açılmışsa, bu bir tuzak DEĞİLDİR! Takımların ofansif güçleri çok yüksektir ve maç gerçek bir düellodur (2-1, 2-2 vb.). Kesinlikle Karşılıklı Gol Var ve 2.5 Gol Üstü biter."
        return False, ""
'''

if 'class Rule1489' in content:
    # use a regex to replace the old Rule1489 class completely
    import re
    content = re.sub(r'class Rule1489.*?return False, ""\n', rule_1489_new, content, flags=re.DOTALL)
else:
    content = content.replace('def get_all_rules():', rule_1489_new + '\ndef get_all_rules():')

# Also update story_analyzer.py
story_analyzer_path = 'story_analyzer.py'
with codecs.open(story_analyzer_path, 'r', 'utf-8') as f:
    story_content = f.read()

story_addition = '''
    elif any(r['code'] == '1489' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Kısır Maç (Favori Yem Tuzağı)")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Yok + 2.5 Gol Altı")
    elif any(r['code'] == '1490' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Sürpriz Deplasman Puanı (Favori Çöküşü)")
        output.append(f"- **Kombine Öneri:** X2 Çifte Şans + Karşılıklı Gol Var (veya Üst)")
    elif any(r['code'] == '1491' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Gol Düellosu (Gerçek Yüksek Skor)")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst")
'''

# Find where 1489 is handled currently and replace it, or append it
if "'1489' for r in triggered_rules" in story_content:
    story_content = re.sub(r'    elif any\(r\[\'code\'\] == \'1489\'.*?\(veya 2\.5 Alt\)"\)', story_addition.strip(), story_content, flags=re.DOTALL)
else:
    # just insert before 'T35'
    story_content = story_content.replace("    elif any(r['code'] == 'T35'", story_addition + "\n    elif any(r['code'] == 'T35'")

with codecs.open(story_analyzer_path, 'w', 'utf-8') as f:
    f.write(story_content)

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

# We also need to fix get_all_rules in rule_engine.py again to include 1490 and 1491
with codecs.open('fix_rules.py', 'r', 'utf-8') as f:
    fix_rules_script = f.read()
exec(fix_rules_script)
