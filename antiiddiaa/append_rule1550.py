import sys
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'a', encoding='utf-8') as f:
    f.write('''
class Rule1550(BaseRule):
    code = "1550"
    name = "Kısır Gösterilen Katliam Tuzağı (Yalancı Alt)"
    category = "TUZAK"
    description = "Her iki takımın gol beklentisi çok yüksekken 2.5 Alt ve KG Yok oranlarının aşırı düşük açılması."
    @classmethod
    def evaluate(cls, odds):
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        kgy = get_odd(odds, ["Karşılıklı Gol_Yok"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst", "Ev Sahibi Altı/Üstü 0.5_Üst"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        
        if alt25 != 99.0 and kgy != 99.0 and ev_05_ust != 99.0 and dep_05_ust != 99.0:
            if alt25 <= 1.65 and kgy <= 1.65 and ev_05_ust <= 1.55 and dep_05_ust <= 1.25:
                return True, "YALANCI ALT (KATLİAM TUZAĞI): İddaa 2.5 Alt ve KG Yok oranlarını 1.65'in altında tutarak herkese maçın 1-0 veya 0-1 gibi kısır biteceğini empoze ediyor. ANCAK aynı anda Ev Sahibinin gol atma oranını (1.55 altı) ve Deplasmanın gol atma oranını (1.25 altı) çok düşürerek iki takımın da kesinlikle gol atacağını matematiksel olarak ifşa etmiş! İki takım da gol atacaksa maç en az 1-1 olur, peki neden KG Yok banko gösteriliyor? ÇÜNKÜ BU BİR YALANDIR! Bu maçta tam bir katliam çıkacak, 2.5 ÜST ve KG VAR çok rahat gelecektir. Ağır favori kimse şov yapacaktır (örn: 1-3, 1-4, 2-3)."
        return False, ""
''')
