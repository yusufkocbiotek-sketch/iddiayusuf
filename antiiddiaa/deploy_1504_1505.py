import codecs
import re

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1504_1505 = '''
class Rule1504(BaseRule):
    code = "1504"
    name = "Kısır Favori Katliamı (1.5 Üst Uyumsuzluğu)"
    category = "YÖN_VE_GOL"
    description = "Ağır favori takımın kendi 1.5 Üst oranının beklenenden yüksek olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_ust15 = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Üst", "Ev Sahibi Altı/Üstü 1.5_Üst"])
        
        if ms1 > 0 and ms1 <= 1.35 and ev_ust15 > 0 and ev_ust15 >= 1.45:
            return True, "KISIR FAVORİ KATLİAMI: Ev sahibi takım 1.35 altı oranla devasa bir favori (banko) olarak gösteriliyor. ANCAK Ev Sahibinin '1.5 Üst' (en az 2 gol atar) oranı 1.45 ve üzerinde! Normalde 1.30'luk bir favorinin 1.5 Üst oranı 1.20-1.25 civarında olmalıdır. İddaa ev sahibinin 2 gol atacağından şüpheliyse, bu takımın o maçı kazanması da kocaman bir yalandır. Tüm piyasa 1.30'luk banko MS1'e abanırken, deplasman takımı tarihi bir vurgun yapar (1-2, 1-3). MS2 sürprizi veya X2 Çifte Şans değerlendirilmelidir."
        return False, ""

class Rule1505(BaseRule):
    code = "1505"
    name = "Süper Düşük Beraberlik Tuzağı (Açık Hedef)"
    category = "YÖN_VE_GOL"
    description = "Beraberlik oranının inanılmaz seviyelere inip (2.70 altı) piyasayı çekmesi."
    @classmethod
    def evaluate(cls, odds):
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if ms0 > 0 and ms0 <= 2.70 and ms2 <= 2.60:
            return True, "SÜPER DÜŞÜK BERABERLİK TUZAĞI: Maçın beraberlik (MS0) oranı 2.70 ve altına kadar indirilmiş! Bu, iddaanın futbol dünyasında çok nadir yaptığı 'Süper Düşük Beraberlik' tuzağıdır. Tüm bahisçilerin aklına 'Maç kesin berabere bitecek' fikri sokulur. Ancak arka planda bu maç çoktan deplasman takımı tarafına (0-1, 0-2) yazılmıştır. Piyasayı MS0'a kilitlerken Deplasman aradan sıyrılır. Doğrudan Deplasman galibiyeti (MS2) çok değerli bir tahmindir."
        return False, ""
'''

content = content.replace('def get_all_rules():', rule_1504_1505 + '\ndef get_all_rules():')
content = content.replace('Rule1503, Rule1502', 'Rule1505, Rule1504, Rule1503, Rule1502')

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

story_analyzer_path = 'story_analyzer.py'
with codecs.open(story_analyzer_path, 'r', 'utf-8') as f:
    story_content = f.read()

story_addition = '''
    elif any(r['code'] == '1504' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Sürpriz Deplasman Galibiyeti (Favori Katliamı)")
        output.append(f"- **Kombine Öneri:** X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-3)")
    elif any(r['code'] == '1505' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 2 (Sahte Beraberlik)")
        output.append(f"- **Kombine Öneri:** MS 2 + 2.5 Gol Altı (Sürpriz Skor: 0-2)")
'''

story_content = story_content.replace("    elif any(r['code'] == '1503'", story_addition.strip('\n') + "\n    elif any(r['code'] == '1503'")
with codecs.open(story_analyzer_path, 'w', 'utf-8') as f:
    f.write(story_content)

print("Rules 1504 and 1505 deployed.")
