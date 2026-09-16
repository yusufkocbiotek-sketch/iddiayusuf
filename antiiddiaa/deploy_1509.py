import codecs

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1509 = '''
class Rule1509(BaseRule):
    code = "1509"
    name = "KG Var Paradoksu (Sürpriz MS2)"
    category = "YÖN_VE_GOL"
    description = "KG Var bankoyken MS1+KG Yok oranının MS1+KG Var oranından düşük olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms1_kg_yok = get_odd(odds, ["Maç Sonucu ve Karşılıklı Gol_1 ve Yok"])
        ms1_kg_var = get_odd(odds, ["Maç Sonucu ve Karşılıklı Gol_1 ve Var"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if (ms1 > 0 and ms1_kg_yok > 0 and ms1_kg_var > 0 and kg_var > 0):
            if kg_var <= 1.55 and ms1 <= 2.00 and ms1_kg_yok < ms1_kg_var:
                return True, "KG VAR PARADOKSU: İddaa, KG Var oranını 1.55 ve altında tutarak maçta iki takımın da gol atacağını çok güçlü fiyatlamış. ANCAK favori takımın (MS1) kombine oranlarına baktığımızda, 'MS1 ve KG Yok' oranı, 'MS1 ve KG Var' oranından daha düşük! Bu imkansızdır. Madem maçta karşılıklı gol kesin gibi, neden favorinin gol yemeden kazanma oranı daha düşük? Çünkü Ev Sahibinin kazanması tamamen YALANDIR. İddaa KG Var olacağını biliyor ama ev sahibinin kazanamayacağını da biliyor. Maçta sürpriz bir şekilde Deplasman takımı gol atarak öne geçer veya kilitler (1-2, 1-3, 1-1). X2 Çifte Şans ve Deplasman galibiyeti çok değerlidir."
        return False, ""
'''

content = content.replace('def get_all_rules():', rule_1509 + '\ndef get_all_rules():')
content = content.replace('Rule1508, Rule1507', 'Rule1509, Rule1508, Rule1507')

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

story_analyzer_path = 'story_analyzer.py'
with codecs.open(story_analyzer_path, 'r', 'utf-8') as f:
    story_content = f.read()

story_addition = '''
    elif any(r['code'] == '1509' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Deplasman Çifte Şans (02) veya Beraberlik")
        output.append(f"- **Kombine Öneri:** 02 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2 / 1-3)")
'''

story_content = story_content.replace("    elif any(r['code'] == '1508'", story_addition.strip('\n') + "\n    elif any(r['code'] == '1508'")
with codecs.open(story_analyzer_path, 'w', 'utf-8') as f:
    f.write(story_content)

print("Rule 1509 deployed.")
