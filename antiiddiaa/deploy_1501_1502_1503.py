import codecs
import re

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

rule_1501_1502_1503 = '''
class Rule1501(BaseRule):
    code = "1501"
    name = "İlk Yarı Beton Tuzağı (0-0 Garantisi)"
    category = "SKOR"
    description = "Her iki takımın İlk Yarı 0.5 Alt oranlarının aşırı düşük olması."
    @classmethod
    def evaluate(cls, odds):
        iy_05_alt = get_odd(odds, ["1. Yarı Alt/Üst 0.5_Alt", "1. Yarı Altı/Üstü 0.5_Alt"])
        ev_1y_05_alt = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Alt", "Ev Sahibi 1. Yarı Alt/Üst 0.5_Alt"])
        dep_1y_05_alt = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Alt", "Deplasman 1. Yarı Alt/Üst 0.5_Alt"])
        
        if iy_05_alt > 0 and ev_1y_05_alt > 0 and dep_1y_05_alt > 0 and iy_05_alt <= 2.25 and ev_1y_05_alt <= 1.45 and dep_1y_05_alt <= 1.45:
            return True, "İLK YARI BETON TUZAĞI: İlk yarı 0.5 Alt oranı makul seviyedeyse (2.20 civarı) VE özellikle her iki takımın da ayrı ayrı İlk Yarı 0.5 Alt oranları 1.45'in altındaysa; maçın başlama vuruşundan itibaren sahada inanılmaz bir kilitlenme olacağı, takımların kaleye bile gidemeyeceği iddaa tarafından arka planda fiyatlanmıştır. İlk yarı %90 ihtimalle 0-0 biter. Maç da kuvvetle muhtemel 0-0 veya tek şanslı bir golle (1-0/0-1) tamamlanır. Tüm 'Üst' ve 'KG Var' beklentileri (diğer kurallar) çöpe atılmalıdır. Bu maç betondur, 2.5 Alt ve KG Yok bankodur."
        return False, ""

class Rule1502(BaseRule):
    code = "1502"
    name = "Handikaplı Şov Başlangıcı (1.50 Ev Sahibi Patlaması)"
    category = "YÖN_VE_GOL"
    description = "Alt beklentisi varken Ev Sahibinin handikap oranının şov vadetmesi."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        h01_1 = get_odd(odds, ["Handikaplı Maç Sonucu 0:1_1"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        
        if ms1 > 0 and h01_1 > 0 and ms1 <= 1.55 and h01_1 <= 2.60 and alt25 <= 1.65:
            return True, "HANDİKAPLI ŞOV BAŞLANGICI: Ev sahibi takım maçın ağır favorisi (1.55 altı) olarak açılmış. Vitrinde 2.5 Alt oranı çok düşük (1.65 altı) tutularak maçı 1-0 gibi kısır bir skorla kazanacağı algısı yaratılmış. ANCAK Handikaplı Maç Sonucu (0:1) 1 oranı 2.60'ın altındadır! Bu gizli fiyatlama, iddaanın arka planda ev sahibinin rahatlıkla en az 2 farkla (2-0, 3-0) şov yaparak kazanacağını bildiğini ama milleti 1-0 veya kısır skorlara yönlendirmeye çalıştığını gösterir. Doğrudan MS1 ve Handikap 1 (H1) oynanmalı, 'Alt' illüzyonuna düşülmemelidir."
        return False, ""

class Rule1503(BaseRule):
    code = "1503"
    name = "Sahte Ev Sahibi Düellosu (Deplasman Vurgunu)"
    category = "YÖN_VE_GOL"
    description = "KG Var çok düşük, MS1 favoriyken, MS2 oranının gizli bir tehdit barındırması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms1 >= 1.55 and ms1 <= 1.85 and kg_var > 0 and kg_var <= 1.35 and ms2 <= 3.35:
            return True, "SAHTE EV SAHİBİ DÜELLOSU: Maçta Ev sahibi favori (1.60-1.80) ve KG Var oranı muazzam düşük (1.35 altı). Vitrinde maçın 2-1 veya 3-1 biteceği, gollü bir ev sahibi galibiyeti hikayesi sunuluyor. Ancak MS2 oranı 3.35'in altındadır (Yani deplasman hiç de zayıf değil, kazanma ihtimali yüksek). KG Var banko gösterilip tüm bahisler Ev sahibinin gollü galibiyetine yönlendiriliyorsa, bu bir deplasman tuzağıdır! Maçı ev sahibi değil, hızlı hücumlarla deplasman takımı kazanır (1-2, 1-3). MS2 veya X2 Çifte Şans değerlendirilmelidir."
        return False, ""
'''

content = content.replace('def get_all_rules():', rule_1501_1502_1503 + '\ndef get_all_rules():')
content = content.replace('Rule1500, Rule1499', 'Rule1503, Rule1502, Rule1501, Rule1500, Rule1499')

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

story_analyzer_path = 'story_analyzer.py'
with codecs.open(story_analyzer_path, 'r', 'utf-8') as f:
    story_content = f.read()

story_addition = '''
    elif any(r['code'] == '1501' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 0 (Kilitlenmiş Kısır Maç)")
        output.append(f"- **Kombine Öneri:** 2.5 Gol Altı + Karşılıklı Gol Yok (Sürpriz Skor: 0-0)")
    elif any(r['code'] == '1502' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Handikaplı MS 1 (Tek Taraflı Ev Şovu)")
        output.append(f"- **Kombine Öneri:** MS 1 + 2.5 Gol Üst (Sürpriz Skor: 3-0)")
    elif any(r['code'] == '1503' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Sürpriz Deplasman Galibiyeti (Sahte Düello)")
        output.append(f"- **Kombine Öneri:** X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2)")
'''

story_content = story_content.replace("    elif any(r['code'] == '1500'", story_addition.strip('\n') + "\n    elif any(r['code'] == '1500'")
with codecs.open(story_analyzer_path, 'w', 'utf-8') as f:
    f.write(story_content)

print("Rules 1501, 1502, and 1503 deployed.")
