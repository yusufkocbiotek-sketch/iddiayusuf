import sys
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'a', encoding='utf-8') as f:
    f.write('''
class Rule1551(BaseRule):
    code = "1551"
    name = "Ağır Favori Gollü Sürpriz Tuzağı (KG Var Patlaması)"
    category = "TUZAK"
    description = "MS1/MS2 <= 1.30 ve KG Var <= 1.45"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        if (ms1 != 99.0 and ms1 <= 1.30) or (ms2 != 99.0 and ms2 <= 1.30):
            if kg_var != 99.0 and kg_var <= 1.45:
                return True, "GOLLÜ SÜRPRİZ (AĞIR FAVORİ ÇELMESİ): 1.30 altı devasa bir favorinin oynadığı maçta İddaa, zayıf takımın da kesinlikle gol atacağını (KG Var < 1.45) söyleyerek bağıra bağıra 'bol gollü favori galibiyeti (3-1, 4-1)' satmaktadır. ANCAK bu tamamen bir manipülasyondur. İki takımın da kesin gol atması ve ağır favorinin bu maçı alması iddaa için çok maliyetlidir. Favori takım kazanmayı başaramaz! Bu devasa bir sürpriz tuzağıdır (Çifte Şans 1X/X2) veya karşılıklı gollerin hiç olmadığı kısır bir maça döner."
        return False, ""
''')
