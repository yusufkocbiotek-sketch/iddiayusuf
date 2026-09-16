import codecs
import re

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1506_1507 = '''
class Rule1506(BaseRule):
    code = "1506"
    name = "Sahte Karşılıklı Gol (Gollü Favori Şovu)"
    category = "SKOR"
    description = "Ağır favori varken KG Var oranının aşırı düşük olmasıyla KG Var oynatıp KG Yok bitirmek."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms1 > 0 and ms1 <= 1.35 and kg_var > 0 and kg_var <= 1.25:
            return True, "SAHTE KARŞILIKLI GOL TUZAĞI: Ev sahibi ağır favori (1.35 altı) ve maçın KG Var oranı inanılmaz düşük (1.25 altı). İddaa, herkesin aklına 'Zayıf takım kontradan 1 gol atar, ev sahibi maçı 3-1, 4-1 kazanır' senaryosunu sokarak tüm piyasaya KG Var oynatmayı hedeflemektedir. Ancak gerçekte ağır favori takım kalesini tamamen kapatır ve tek taraflı bir gol şovu (4-0, 5-0) izletir. Bu, KG Var beklentisiyle milleti soymak için kurulmuş devasa bir tuzaktır. Maç kesinlikle KG Yok biter!"
        return False, ""

class Rule1507(BaseRule):
    code = "1507"
    name = "Sahte Favori Kilitlenmesi (Handikap 2 Tuzağı)"
    category = "YÖN_VE_GOL"
    description = "Ev sahibi banko görünürken Handikap 2 oranının tehlikeli derecede düşük olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        h01_2 = get_odd(odds, ["Handikaplı Maç Sonucu 0:1_2"])
        
        if ms1 > 0 and ms1 <= 1.45 and h01_2 > 0 and h01_2 <= 2.15:
            return True, "SAHTE FAVORİ KİLİTLENMESİ: Ev sahibi takım 1.45 altı oranla net banko favori olarak açılmış. ANCAK Handikap (0:1) 2 oranı (yani deplasmanın kaybetmeme veya tek farkla yenilme opsiyonu) 2.15 ve altına indirilmiş. İddaa ev sahibinin asla fark atamayacağını, hatta zorlanıp puan kaybedeceğini arka planda fiyatlamıştır. Bu sahte bir bankodur, maç 0-0 veya 1-1 kilitlenir. X2 Çifte Şans ve 2.5 Alt çok değerlidir."
        return False, ""
'''

content = content.replace('def get_all_rules():', rule_1506_1507 + '\ndef get_all_rules():')
content = content.replace('Rule1505, Rule1504', 'Rule1507, Rule1506, Rule1505, Rule1504')

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

story_analyzer_path = 'story_analyzer.py'
with codecs.open(story_analyzer_path, 'r', 'utf-8') as f:
    story_content = f.read()

story_addition = '''
    elif any(r['code'] == '1506' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (Tek Taraflı Şov)")
        output.append(f"- **Kombine Öneri:** MS 1 + Karşılıklı Gol Yok (Sürpriz Skor: 4-0)")
    elif any(r['code'] == '1507' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Deplasman Çifte Şans (Sahte Favori)")
        output.append(f"- **Kombine Öneri:** X2 Çifte Şans + 2.5 Gol Altı (Sürpriz Skor: 0-0)")
'''

story_content = story_content.replace("    elif any(r['code'] == '1505'", story_addition.strip('\n') + "\n    elif any(r['code'] == '1505'")
with codecs.open(story_analyzer_path, 'w', 'utf-8') as f:
    f.write(story_content)

print("Rules 1506 and 1507 deployed.")
