import codecs

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1508 = '''
class Rule1508(BaseRule):
    code = "1508"
    name = "Deplasman Gol Paradoksu (0-0 Kapanı)"
    category = "SKOR"
    description = "MS1 ve KG Yok favoriyken, Deplasman gol atar oranının aşırı düşük olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms1_kg_yok = get_odd(odds, ["Maç Sonucu ve Karşılıklı Gol_1 ve Yok"])
        ms1_kg_var = get_odd(odds, ["Maç Sonucu ve Karşılıklı Gol_1 ve Var"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        
        if (ms1 > 0 and ms1_kg_yok > 0 and ms1_kg_var > 0 and dep_05_ust > 0):
            if ms1 <= 1.65 and ms1_kg_yok < ms1_kg_var and dep_05_ust <= 1.40:
                return True, "DEPLASMAN GOL PARADOKSU: İddaa 'Maç Sonucu 1 ve KG Yok' oranını düşük tutarak (örneğin 2.65) millete 'Ev sahibi maçı 1-0, 2-0 gol yemeden kazanır' algısı pompalıyor. Ancak aynı iddaa alt oranlarda 'Deplasman 0.5 Üst' oranını 1.40'ın altına (örneğin 1.36) çekmiş! Yani 'Deplasman kesin gol atar' diyor. Eğer deplasman gol atacaksa ve ev sahibi kazanacaksa, neden MS1+KG Var oranı daha yüksek? Çünkü Ev sahibinin kazanması tamamen YALANDIR. Bu bir kilitlenme maçı (0-0) veya sürpriz puan kaybı maçıdır. MS 0 denenmelidir."
        return False, ""
'''

content = content.replace('def get_all_rules():', rule_1508 + '\ndef get_all_rules():')
content = content.replace('Rule1507, Rule1506', 'Rule1508, Rule1507, Rule1506')

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

story_analyzer_path = 'story_analyzer.py'
with codecs.open(story_analyzer_path, 'r', 'utf-8') as f:
    story_content = f.read()

story_addition = '''
    elif any(r['code'] == '1508' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 0 veya Alt (Ölümcül Kilitlenme)")
        output.append(f"- **Kombine Öneri:** 2.5 Gol Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0)")
'''

story_content = story_content.replace("    elif any(r['code'] == '1507'", story_addition.strip('\n') + "\n    elif any(r['code'] == '1507'")
with codecs.open(story_analyzer_path, 'w', 'utf-8') as f:
    f.write(story_content)

print("Rule 1508 deployed.")
