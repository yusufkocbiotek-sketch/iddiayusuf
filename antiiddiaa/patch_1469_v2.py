import os

path = r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_1469 = """        if ms1 < ms2 and ms1 >= 1.50 and ms0 <= 3.05 and ev_15_alt <= 1.55:
            return True, "GİZLİ BERABERLİK KİLİDİ: Ev sahibi favori gösterilse de (Örn: 1.90), beraberlik oranı anormal derecede düşüktür (3.05 ve altı). Üstelik favorinin 2 gol atması beklenmemektedir (Ev 1.5 Alt <= 1.55). Bu maçta favorinin galibiyet gücü yoktur, maç 0-0 veya 1-1 kilitlenir. MS 0 denenmelidir."
        return False, ""\"""

new_1469 = """        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        if ms1 < ms2 and ms1 >= 1.50 and ms0 <= 3.05 and ev_15_alt <= 1.55:
            if kg_var <= 1.65:
                return True, "ASYA TUZAĞI (GOLLÜ BERABERLİK İLLÜZYONU): Beraberlik oranı anormal düşük ve aynı zamanda KG Var da güçlü fiyatlanmış. Bu maç asla 0-0 gibi kısır bir skora kilitlenmez. İddaa düşük beraberlik oranıyla maçın sıkıcı geçeceği algısı yaratır ancak maç gollü bir kaosa (1-1, 2-2, 3-2 vb.) döner."
            else:
                return True, "GİZLİ BERABERLİK KİLİDİ: Ev sahibi favori gösterilse de (Örn: 1.90), beraberlik oranı anormal derecede düşüktür (3.05 ve altı). Üstelik favorinin 2 gol atması beklenmemektedir (Ev 1.5 Alt <= 1.55). Bu maçta favorinin galibiyet gücü yoktur, maç 0-0 veya 1-1 kilitlenir. MS 0 denenmelidir."
        return False, ""\"""

text = text.replace(old_1469, new_1469)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched 1469.')
