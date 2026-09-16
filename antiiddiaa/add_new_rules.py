import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_rules = '''
class Rule1553(BaseRule):
    code = "1553"
    name = "Dengeli KG Patlaması (Sahte Kısır - 3-2/2-2)"
    category = "TUZAK"
    description = "Dengeli maçta KG Var banko (<1.50) iken 2.5 Alt cazip gösterilmiş."

    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        
        if ms1 != 99.0 and ms2 != 99.0 and ms1 >= 2.00 and ms2 >= 2.00:
            if kg_var != 99.0 and kg_var <= 1.50 and alt25 != 99.0 and alt25 <= 1.65:
                return True, "DENGELİ KG PATLAMASI (SAHTE KISIR): Maç tamamen dengeli (Taraf yok) ve İddaa her iki takımın da kesinlikle gol atacağını (KG Var < 1.50) itiraf ediyor. Ancak 2.5 Alt oranı (1.65 altı) ile maçı 1-1 bitmeye kilitli gibi gösteriyor. Bu bir tuzaktır! İki takımın da gol atacağı garanti olan bir maçta, beraberlik bozucu bir 3. gol kesinlikle çıkacaktır. Maç 3-2 veya 2-2 gibi bol gollü bir skora patlayacaktır (2.5 Üst bankodur)."
        return False, ""

class Rule1554(BaseRule):
    code = "1554"
    name = "Ağır Favori Oran Çelişkisi (Puan Kaybı Tuzağı - 1-1/0-0)"
    category = "TUZAK"
    description = "MS1 < 1.25 iken MS0 ve MS2 oranlarının anormal düşük olması."

    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if ms1 != 99.0 and ms1 <= 1.25 and ms0 != 99.0 and ms0 <= 4.50 and ms2 != 99.0 and ms2 <= 8.50:
            return True, "AĞIR FAVORİ ORAN ÇELİŞKİSİ (PUAN KAYBI): Ev sahibi 1.25 altı oranla devasa bir favori. Ancak Beraberlik (4.50 altı) ve Deplasman (8.50 altı) oranları, bir ağır favori maçına göre İNANILMAZ DERECEDE DÜŞÜK! İddaa, MS1'i cazip bir banko yemi olarak sunarken aslında içeride konuk ekibin direneceğini çok iyi biliyor. Bu maçta ağır favori kesinlikle puan kaybedecektir (1-1 veya 0-0). MS1 uzak durulması gereken ölümcül bir tuzaktır."
        return False, ""

class Rule1555(BaseRule):
    code = "1555"
    name = "Favori KG-Beraberlik Tuzağı (1-1 Sendromu)"
    category = "TUZAK"
    description = "MS1 favori iken MS0'ın ve KG Var'ın çok düşük olması."

    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms1 != 99.0 and 1.30 <= ms1 <= 1.55 and ms0 != 99.0 and ms0 <= 3.40 and kg_var != 99.0 and kg_var <= 1.55:
            return True, "FAVORİ KG-BERABERLİK TUZAĞI (1-1 SENDROMU): Ev sahibi favori (1.30-1.55 arası). Ancak beraberlik oranı (3.40 altı) oldukça şüpheli bir şekilde düşük ve KG Var (1.55 altı) neredeyse banko gösteriliyor. Bu, konuk ekibin kesinlikle gol bulacağı ve ev sahibinin galibiyet golünü atamayarak maçın 1-1 kilitleneceği anlamına gelir. Çifte Şans X2 veya KG Var mükemmel bir tercihtir."
        return False, ""
'''

if 'class Rule1553' not in content:
    content = content.replace('class Rule1523(BaseRule):', new_rules + '\nclass Rule1523(BaseRule):')
    
    # Update get_all_rules array
    content = content.replace('[Rule1552, Rule1551,', '[Rule1555, Rule1554, Rule1553, Rule1552, Rule1551,')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Kurallar_Kitabi.md', 'a', encoding='utf-8') as f:
    f.write('\n### 🚨 Rule 1553: Dengeli KG Patlaması (Sahte Kısır)\n')
    f.write('**Koşul:** `MS1 >= 2.0` & `MS2 >= 2.0` VE `KG Var <= 1.50` VE `Alt 2.5 <= 1.65`\n')
    f.write('**Hikaye:** Dengeli maçta İddaa her iki takımın gol atacağını (KG Var) garanti görüyor ama maçı 1-1 kilitli gibi göstermek için Alt oranını düşük tutuyor. Bu bir Alt tuzağıdır, maç 3-2 veya 2-2 patlar.\n\n')
    f.write('### 🚨 Rule 1554: Ağır Favori Oran Çelişkisi (Puan Kaybı)\n')
    f.write('**Koşul:** `MS1 <= 1.25` VE `MS0 <= 4.50` VE `MS2 <= 8.50`\n')
    f.write('**Hikaye:** Ev sahibi çok ağır favori (1.15 gibi) ama beraberlik ve deplasman oranları olması gerekenden çok daha düşük (örn. MS0 4.26). MS1 oranı tamamen kombine kuponları yatırmak için açılmış bir yemdir. Ağır favori evinde kilitlenir (1-1/0-0).\n\n')
    f.write('### 🚨 Rule 1555: Favori KG-Beraberlik Tuzağı (1-1 Sendromu)\n')
    f.write('**Koşul:** `1.30 <= MS1 <= 1.55` VE `MS0 <= 3.40` VE `KG Var <= 1.55`\n')
    f.write('**Hikaye:** Standart bir favori maçı gibi görünse de beraberlik ve KG Var oranları inanılmaz düşük. Konuk ekip kesinlikle gol bulacak ve favori galibiyeti alamayacaktır. 1-1 kilitlenme kokar.\n')

print("Patch applied successfully.")
