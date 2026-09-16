import codecs

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

new_rules = '''
class RuleLIG_ASYA(BaseRule):
    code = "LIG_ASYA"
    name = "Asya Kısırlaştırma İllüzyonu"
    category = "LİG_ÖZEL"
    description = "Asya liglerinde KG Yok oranı düşük tutularak Alt tuzağı kurulması."
    @classmethod
    def evaluate(cls, odds):
        lig_tipi = odds.get('__LIG_TIPI__', 'STANDART')
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        
        if lig_tipi == 'ASYA' and kg_yok <= 1.70:
            return True, "ASYA LİGİ ÖZELLİĞİ: Asya takımları (Japonya, Kore vb.) genellikle hücum futbolu oynar. Bürolar KG Yok oranını çok düşük tutarak 'bu maçta sadece bir takım atar' algısı yaratır. Ancak bu tam bir Asya Tuzağıdır! Maçta iki takımın da gol atma ihtimali çok yüksektir. Direkt KG Var denenmeli."
        return False, ""

class RuleLIG_LATAM(BaseRule):
    code = "LIG_LATAM"
    name = "Güney Amerika Sertlik Tuzağı (Sahte Üst)"
    category = "LİG_ÖZEL"
    description = "Güney Amerika'da 2.5 Üst veya KG Var oranının cazip açılması."
    @classmethod
    def evaluate(cls, odds):
        lig_tipi = odds.get('__LIG_TIPI__', 'STANDART')
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if lig_tipi == 'GÜNEY_AMERİKA' and ust25 <= 1.85 and kg_var <= 1.75:
            return True, "GÜNEY AMERİKA LİGİ ÖZELLİĞİ: Latin Amerika futbolu son derece sert ve defansiftir. Bürolar 2.5 Üst ve KG Var oranlarını şaşırtıcı derecede düşük açarak 'gollü maç' illüzyonu yaratıyor. Aslında bu, herkesi Üst'e çekip maçın 0-0 veya 1-0 gibi son derece kısır bir skorla bitirilmesi planıdır! Karşılıklı Gol Yok ve 2.5 Alt idealdir."
        return False, ""

'''

if 'RuleLIG_ASYA' not in content:
    content = content.replace('def get_all_rules():', new_rules + 'def get_all_rules():')
    
    # Update the get_all_rules return list
    content = content.replace(
        'RuleY1, RuleY2, RuleY3, RuleY4, RuleY5, RuleY6, RuleY7',
        'RuleY1, RuleY2, RuleY3, RuleY4, RuleY5, RuleY6, RuleY7, RuleLIG_ASYA, RuleLIG_LATAM'
    )
    
    with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
        f.write(content)
