import os
import re

path = r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'class Rule1469.*?return False, ""', text, re.DOTALL)
if match:
    old_block = match.group(0)
    new_block = '''class Rule1469(BaseRule):
    code = "1469"
    category = "SKOR"
    name = "Aşırı Düşük Beraberlik Tuzağı (Kısır Favori)"
    description = "Ev favori iken MS0 3.05 altındaysa ve kısır bekleniyorsa maç kilitlenir."

    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms1 < ms2 and ms1 >= 1.50 and ms0 <= 3.05 and ev_15_alt <= 1.55:
            if kg_var <= 1.65:
                return True, "ASYA TUZAĞI (GOLLÜ BERABERLİK İLLÜZYONU): Beraberlik oranı anormal düşük ve aynı zamanda KG Var da güçlü fiyatlanmış. Bu maç asla 0-0 gibi kısır bir skora kilitlenmez. İddaa düşük beraberlik oranıyla maçın sıkıcı geçeceği algısı yaratır ancak maç gollü bir kaosa (1-1, 2-2, 3-2 vb.) döner."
            else:
                return True, "GİZLİ BERABERLİK KİLİDİ: Ev sahibi favori gösterilse de (Örn: 1.90), beraberlik oranı anormal derecede düşüktür (3.05 ve altı). Üstelik favorinin 2 gol atması beklenmemektedir (Ev 1.5 Alt <= 1.55). Bu maçta favorinin galibiyet gücü yoktur, maç 0-0 veya 1-1 kilitlenir. MS 0 denenmelidir."
        return False, ""'''
    text = text.replace(old_block, new_block)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Patched successfully via regex script.')
else:
    print('Rule1469 block not found!')
