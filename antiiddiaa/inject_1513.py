import codecs

# Fix rule_engine.py
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

# Fix G10
old_g10 = "if kg_var <= 1.45 and ust25 <= 1.50 and ms0 <= 3.40 and min(ms1, ms2) >= 1.60:"
new_g10 = "if kg_var <= 1.45 and ust25 <= 1.50 and ms0 <= 3.40 and min(ms1, ms2) >= 1.90:"
content = content.replace(old_g10, new_g10)

# Add 1513
rule_1513 = '''
class Rule1513(BaseRule):
    code = "1513"
    name = "Suni Deplasman Favorisi (Handikap Uyumsuzluğu)"
    category = "GOL"
    description = "Deplasman net favori (1.50-1.75) görünmesine rağmen, Handikap 2 oranı çok yüksek (2.60+) ise ve KG Var düşükse, Ev sahibi sürpriz yapar."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        h2 = get_odd(odds, ["Handikaplı Maç Sonucu 0:1_2", "Handikaplı Maç Sonucu 1:0_2", "Handikaplı Maç Sonucu 0:2_2"])
        
        if 1.45 <= ms2 <= 1.80 and h2 >= 2.60 and 0 < kg_var <= 1.55:
            return True, "SUNİ FAVORİ VE DÜELLO: Deplasman takımı kağıt üzerinde favori. Ancak Handikap 2 oranı (2.60 ve üzeri) iddaa'nın deplasmanın maçı rahat kazanacağına inanmadığını gösteriyor. Üstelik KG Var oranının düşük olması, Ev sahibinin kesinlikle gol/goller bulacağını kanıtlıyor. Bu maçta Ev Sahibi sürprizi (1X Çifte Şans) ve Gollü bir senaryo (3-2, 2-2, 2-1) yaşanacaktır."
        return False, ""
'''

if "Rule1513" not in content:
    content = content.replace('def get_all_rules():', rule_1513 + '\ndef get_all_rules():')
    content = content.replace('Rule1512, ', 'Rule1513, Rule1512, ')

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

# Fix story_analyzer.py
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()

correct_state = '''    elif any(r['code'] == '1513' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 1X Çifte Şans (Ev Sahibi Sürprizi)")
        output.append(f"- **Kombine Öneri:** 1X Çifte Şans + 2.5 Gol Üstü (Sürpriz Skor: 3-2 / 2-2)")
    elif any(r['code'] == '1512' and 'ŞOV PATLAMASI' in r['insight'] for r in triggered_rules):'''
    
bad_state = '''    elif any(r['code'] == '1512' and 'ŞOV PATLAMASI' in r['insight'] for r in triggered_rules):'''

if "1513" not in story:
    story = story.replace(bad_state, correct_state)
    with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf-8') as f:
        f.write(story)
