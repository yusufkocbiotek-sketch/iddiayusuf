import sys
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'a', encoding='utf-8') as f:
    f.write('''
class Rule1549(BaseRule):
    code = "1549"
    name = "Deplasman Favorisi Gol Tuzağı (Zayıf Ev Sahibi 0.5 Üst)"
    category = "TUZAK"
    description = "Zayıf ev sahibinin yüksek gol beklentisi (Deplasman favorisi MS2 tuzağı)"
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst", "Ev Sahibi Altı/Üstü 0.5_Üst"])
        if ms2 != 99.0 and 1.30 <= ms2 <= 1.65 and ev_05_ust != 99.0 and ev_05_ust <= 1.60:
            return True, "GİZLİ EV SAHİBİ BEKLENTİSİ (MS2 TUZAĞI): Deplasman takımı 1.65 ve altı oranla çok net favori. Ancak zayıf ev sahibinin gol atma oranı (0.5 Üst) 1.60 ve altında! Matematiksel olarak zayıf takımın gol atacağı bu kadar net fiyatlanmışsa, deplasman takımının kazanma ihtimali riske girmiş demektir. Bu maç 1X çifte şans sürprizine veya gollü beraberliğe çok daha yakındır."
        return False, ""
''')
