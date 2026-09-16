import codecs

# Add Rule 1512 to rule_engine.py
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1512 = '''
class Rule1512(BaseRule):
    code = "1512"
    name = "Gizli 2.5 Barajı (Barem Saklama Tuzağı)"
    category = "GOL"
    description = "Ağır Favori maçında 2.5 Alt/Üst baremi kasıtlı açılmamış, 3.5 açılmış ve KG Var oranı çok düşükse maç kısır biter."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        # 2.5 bareminin olup olmadığını kontrol et
        has_25 = any('2.5' in k for k in odds.keys() if 'Alt/Üst 2.5' in k and not 'Ev Sahibi' in k and not 'Deplasman' in k)
        has_35 = any('3.5' in k for k in odds.keys())
        
        if not has_25 and has_35 and 0 < ms1 <= 1.55 and 0 < kg_var <= 1.50:
            return True, "GİZLİ BAREM İLLÜZYONU: İddaa, maçın çok kısır (2-0, 1-0) geçeceğini bildiği için ana barem olan 2.5 oranlarını hiç açmamış. Sadece 3.5 baremini açarak ve KG Var oranını cazip tutarak (1.50 altı), oyuncuları 'Kesin gollü geçer' yalanıyla KG Var veya Üst oynamaya itiyor. Bu maçlarda favori takım kısır bir skorla kazanır (2-0). 2.5 Alt veya KG Yok en mantıklı seçimdir."
        return False, ""
'''

if "Rule1512" not in content:
    content = content.replace('def get_all_rules():', rule_1512 + '\ndef get_all_rules():')
    content = content.replace('Rule1511, ', 'Rule1512, Rule1511, ')
    
    with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
        f.write(content)


# Add Rule 1512 handling to story_analyzer.py
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()

if "1512" not in story:
    correct_state = '''    elif any(r['code'] == '1511' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 12 Çifte Şans (Beraberliksiz Düello)")
        output.append(f"- **Kombine Öneri:** 12 Çifte Şans + 2.5 Gol Üst + KG Var (Sürpriz Skor: 3-1 / 1-3)")
    elif any(r['code'] == '1512' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (Gizli 2.5 Baremi Tuzağı)")
        output.append(f"- **Kombine Öneri:** MS 1 + Karşılıklı Gol Yok (Sürpriz Skor: 2-0 / 1-0)")
    elif any(r['code'] == '1469' for r in triggered_rules):'''
    
    bad_state = '''    elif any(r['code'] == '1511' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 12 Çifte Şans (Beraberliksiz Düello)")
        output.append(f"- **Kombine Öneri:** 12 Çifte Şans + 2.5 Gol Üst + KG Var (Sürpriz Skor: 3-1 / 1-3)")
    elif any(r['code'] == '1469' for r in triggered_rules):'''
    
    story = story.replace(bad_state, correct_state)
    
    with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf-8') as f:
        f.write(story)

print("Rule 1512 injected successfully!")
