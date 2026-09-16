import codecs

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1510 = '''
class Rule1510(BaseRule):
    code = "1510"
    name = "Sahte 3.5 Alt İllüzyonu (Ağır Favori Patlaması)"
    category = "SKOR"
    description = "Ağır favori ve deplasman gol atar beklenirken 3.5 Alt oranının aşırı düşük açılması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ev_15_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Üst", "Ev Sahibi Altı/Üstü 1.5_Üst"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        alt_35 = get_odd(odds, ["Alt/Üst 3.5_Alt", "Altı/Üstü 3.5_Alt"])
        
        if (ms1 > 0 and ev_15_ust > 0 and dep_05_ust > 0 and alt_35 > 0):
            if ms1 <= 1.35 and ev_15_ust <= 1.45 and dep_05_ust <= 1.60 and alt_35 <= 1.30:
                return True, "SAHTE 3.5 ALT İLLÜZYONU: Ev sahibi çok ağır favori (1.35 altı) ve en az 2 gol atması bekleniyor (Ev 1.5 Üst <= 1.45). Aynı zamanda deplasmanın da gol atması güçlü ihtimal (Dep 0.5 Üst <= 1.60). Matematiksel olarak maç zaten 2-1'den başlıyor (3 gol garanti). Buna rağmen iddaa 3.5 Alt oranını 1.30'un altında açarak 'Maç en fazla 2-1 veya 3-0 biter' yalanını pompalıyor. Bu tuzağın amacı insanları 3.5 Alt'a ve kısır skorlara yönlendirmektir. Maç 3-1, 4-1 gibi gollü bir şova (3.5 Üst) dönüşecektir!"
        return False, ""
'''

content = content.replace('def get_all_rules():', rule_1510 + '\ndef get_all_rules():')
content = content.replace('Rule1509, Rule1508', 'Rule1510, Rule1509, Rule1508')

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

story_analyzer_path = 'story_analyzer.py'
with codecs.open(story_analyzer_path, 'r', 'utf-8') as f:
    story_content = f.read()

story_addition = '''
    elif any(r['code'] == '1510' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 3.5 Gol Üst (Gol Şovu Tuzağı)")
        output.append(f"- **Kombine Öneri:** MS 1 + 3.5 Gol Üst (Sürpriz Skor: 3-1 / 4-1)")
'''

story_content = story_content.replace("    elif any(r['code'] == '1509'", story_addition.strip('\n') + "\n    elif any(r['code'] == '1509'")
with codecs.open(story_analyzer_path, 'w', 'utf-8') as f:
    f.write(story_content)

print("Rule 1510 deployed.")
