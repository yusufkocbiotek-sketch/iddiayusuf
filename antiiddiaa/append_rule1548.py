import sys
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'a', encoding='utf-8') as f:
    f.write('''
class Rule1548(BaseRule):
    code = "1548"
    name = "Şişirilmiş İlk Yarı Şöleni (Suni 1.5 Üst Tuzağı)"
    category = "YARI"
    description = "İlk Yarı 1 ve 1.5 Üst oranının Alt oranından daha düşük olması tuzağı."
    @classmethod
    def evaluate(cls, odds):
        iy_ms1_15_alt = get_odd(odds, ["1. Yarı Sonucu ve Altı/Üstü 1.5_1 ve Alt", "İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Alt"])
        iy_ms1_15_ust = get_odd(odds, ["1. Yarı Sonucu ve Altı/Üstü 1.5_1 ve Üst", "İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Üst"])
        iy_05_ust = get_odd(odds, ["1. Yarı Alt/Üst 0.5_Üst", "İlk Yarı Alt/Üst 0.5_Üst"])
        
        if iy_ms1_15_alt != 99.0 and iy_ms1_15_ust != 99.0 and iy_05_ust <= 1.15:
            if iy_ms1_15_ust < iy_ms1_15_alt:
                return True, "ŞİŞİRİLMİŞ İLK YARI ŞÖLENİ: İddaa, İlk Yarıda Ev Sahibinin galibiyetini 1.5 ÜST ile (2-0, 3-0 vb.) bekliyor ve bu oranı 1.5 ALT (1-0) oranından daha düşük tutmuş! Normal bir maçta 1-0 skoru her zaman 2-0'dan daha olasıdır. Bu inanılmaz bir anormalliktir ve insanları 'İlk yarı banko gol yağmuru var' algısına çekmek için tasarlanmış sinsi bir tuzaktır. Maç ilk yarı kilitlenecek (0-0 veya 1-1) ve beklentilerin tam tersi olacaktır. İlk Yarı 0 veya İY 1.5 Alt denenmelidir!"
        return False, ""
''')
