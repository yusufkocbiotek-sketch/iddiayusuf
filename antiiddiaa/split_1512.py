import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1512_old = '''
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

rule_1512_new = '''
class Rule1512(BaseRule):
    code = "1512"
    name = "Gizli 2.5 Barajı (Barem Saklama Tuzağı)"
    category = "GOL"
    description = "Ağır Favori maçında 2.5 Alt/Üst baremi açılmamışsa, 3.5 Üst oranına göre Kısır veya Şov analizi yapılır."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        
        has_25 = any('2.5' in k for k in odds.keys() if 'Alt/Üst 2.5' in k and not 'Ev Sahibi' in k and not 'Deplasman' in k)
        has_35 = any('3.5' in k for k in odds.keys())
        
        if not has_25 and has_35 and 0 < ms1 <= 1.55 and 0 < kg_var <= 1.50 and ust35 > 0:
            if ust35 < 1.80:
                return True, "GİZLİ BAREM İLLÜZYONU (ŞOV PATLAMASI): İddaa 2.5 baremini açmayarak 3.5 Üst oynamayı zorunlu kılmış. 3.5 Üst oranının 1.80'in altında olması, maçın 4-5 gollü bir şova dönüşeceğini bas bas bağırıyor! 2.5 Üst açsalar herkes kazanacaktı, bu yüzden kapattılar. Bu maçta 3.5 Üst ve KG Var bankodur."
            else:
                return True, "GİZLİ BAREM İLLÜZYONU (ALT TUZAĞI): İddaa 2.5 baremini açmayarak 3.5 Üst oynamayı zorunlu kılmış. Ancak 3.5 Üst oranının 1.80'in üzerinde olması, aslında maçın kısır (1-0, 2-0) geçeceğini gösteriyor. İnsanları 'zaten gollü geçecek' algısıyla 3.5 Üst'e veya KG Var'a yönlendirip kucağa düşürüyorlar. 2.5 Alt en mantıklı seçimdir."
        return False, ""
'''

content = content.replace(rule_1512_old, rule_1512_new)
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)
    
# story_analyzer.py
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()

correct_state = '''    elif any(r['code'] == '1512' and 'ŞOV PATLAMASI' in r['insight'] for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 3.5 Gol Üstü (Gizli Barem Patlaması)")
        output.append(f"- **Kombine Öneri:** MS 1 + 3.5 Gol Üst (Sürpriz Skor: 4-1 / 3-2)")
    elif any(r['code'] == '1512' and 'ALT TUZAĞI' in r['insight'] for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (Gizli 2.5 Baremi Tuzağı)")
        output.append(f"- **Kombine Öneri:** MS 1 + Karşılıklı Gol Yok (Sürpriz Skor: 2-0 / 1-0)")'''
    
bad_state = '''    elif any(r['code'] == '1512' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (Gizli 2.5 Baremi Tuzağı)")
        output.append(f"- **Kombine Öneri:** MS 1 + Karşılıklı Gol Yok (Sürpriz Skor: 2-0 / 1-0)")'''
    
story = story.replace(bad_state, correct_state)
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf-8') as f:
    f.write(story)
