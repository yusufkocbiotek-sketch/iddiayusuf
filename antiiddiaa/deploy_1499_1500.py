import codecs
import re

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1499_1500 = '''
class Rule1499(BaseRule):
    code = "1499"
    name = "Kilitli Favori Çöküşü (Ev Sahibi Altı Paradoksu)"
    category = "SKOR"
    description = "Ev Sahibi favoriyken kendi Alt sınırlarına takılıp maçı kaybetmesi veya berabere kalması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_alt15 = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        
        if ms1 <= 2.20 and ms2 >= 2.90 and ev_alt15 > 0 and ev_alt15 <= 1.45:
            return True, "KİLİTLİ FAVORİ ÇÖKÜŞÜ: Ev sahibi takım maçın favorisi olarak gösteriliyor (2.20 altı) ancak iddaa Ev Sahibinin 1.5 Alt oranını (max 1 gol atar) 1.45 ve altı gibi bir seviyede kilitlemiş. Bir takım hem maçı kazanacak favoriyse hem de 2 gol bile atamıyorsa bu koca bir yalandır. Bu oranlar tamamen Ev Sahibine oynatmak içindir. Ev sahibi tek golle kilitlenip sürpriz bir beraberlik (1-1) alır veya maçı tamamen kaybeder (0-2). Deplasman Çifte Şans (X2) devasa bir fırsattır."
        return False, ""

class Rule1500(BaseRule):
    code = "1500"
    name = "Sahte Ev Sahibi Baskısı (Yüksek KG Yok Yemi)"
    category = "YÖN_VE_GOL"
    description = "KG Yok oranı 2.00+ olup Ev Sahibi'nin kazanmasının beklendiği maçta deplasmanın patlama yapması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kgy = get_odd(odds, ["Karşılıklı Gol_Yok"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        
        if ms1 <= 1.65 and kgy >= 1.95 and kg_var <= 1.50 and ust <= 1.55:
            return True, "SAHTE EV SAHİBİ BASKISI: Ev sahibi (1.65 altı) ile favori, maç kesin Üst (1.55 altı) ve KG Yok 2.00'lere fırlamış (KG Var banko görülüyor). Klasik bir 2-1, 3-1 ev sahibi galibiyeti hikayesi yazılmış. BU KLASİK BİR KATLİAM TUZAĞIDIR. İddaa böylesine bariz bir 'Fav kazanır ve maç gollü geçer' şablonunu vitrine koyduğunda Ev Sahibi darmadağın olur. Deplasman maçı 1-2 veya sürpriz bir 1-3/2-3 ile alır. Kesinlikle X2 Çifte Şans ve Deplasman tarafı oynanmalıdır."
        return False, ""
'''

content = content.replace('def get_all_rules():', rule_1499_1500 + '\ndef get_all_rules():')
content = content.replace('Rule1498, Rule1497', 'Rule1500, Rule1499, Rule1498, Rule1497')

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

story_analyzer_path = 'story_analyzer.py'
with codecs.open(story_analyzer_path, 'r', 'utf-8') as f:
    story_content = f.read()

story_addition = '''
    elif any(r['code'] == '1499' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Deplasman Çifte Şans (Favori Kilitlenir)")
        output.append(f"- **Kombine Öneri:** X2 Çifte Şans + Ev Sahibi 1.5 Alt (Sürpriz Skor: 0-2 / 1-1)")
    elif any(r['code'] == '1500' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Sürpriz Deplasman Galibiyeti (Sahte Favori)")
        output.append(f"- **Kombine Öneri:** X2 Çifte Şans + 2.5 Gol Üst (Sürpriz Skor: 1-2 / 2-3)")
'''

story_content = story_content.replace("    elif any(r['code'] == '1498'", story_addition.strip('\n') + "\n    elif any(r['code'] == '1498'")
with codecs.open(story_analyzer_path, 'w', 'utf-8') as f:
    f.write(story_content)

print("Rules 1499 and 1500 deployed.")
