import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_1467_clean = """        if 2.20 <= ms1 <= 2.65 and 2.20 <= ms2 <= 2.65 and ms0 <= 3.20 and ust25 != 99.0 and ust25 >= 1.60:
            kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
            if ust25 != 99.0 and ust25 >= 2.50 and kg_yok <= 1.50:
                 return True, "DENGELİ KISIR ÇELİŞKİ (1-2 / 2-1 Üst Sürprizi): Her iki takımın oranları birbirine çok yakın (tamamen dengeli), beraberlik oranı normalden düşük (<=3.20) ve maçın Üst (2.5) oranı İNANILMAZ DERECEDE YÜKSEK (2.50+). Bu maçın 0-0 kilitleneceğini bağıran bir tablodur. İddaa hiçbir kilitlenmeyi bu kadar belli etmez! Bu tam bir tuzaktır. Maçta sürpriz bir şekilde karşılıklı goller olacak ve maç 1-2, 2-1 gibi skorlarla Üst'e (sürprize) gidecektir. 2.5 Üst aranmalıdır."
            else:
                 return True, "Her iki takımın oranları birbirine çok yakın (tamamen dengeli), beraberlik oranı normalden düşük (<=3.20) ve maçın gollü geçme ihtimali düşük (Üst >= 1.60). Bu tam bir kilitlenme senaryosudur. İki takım da risk almaz, maç 0-0 biter."
        return False, ""
"""

new_1467_safe = """        if 2.20 <= ms1 <= 2.65 and 2.20 <= ms2 <= 2.65 and ms0 <= 3.20 and ust25 != 99.0 and ust25 >= 1.60:
            kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
            alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Alt/Üst 2,5_Alt"])
            
            if ms0 <= 2.80 and alt25 <= 1.50:
                return False, ""  # 1467B will handle this trap
                
            if ust25 != 99.0 and ust25 >= 2.50 and kg_yok <= 1.50:
                 return True, "DENGELİ KISIR ÇELİŞKİ (1-2 / 2-1 Üst Sürprizi): Her iki takımın oranları birbirine çok yakın (tamamen dengeli), beraberlik oranı normalden düşük (<=3.20) ve maçın Üst (2.5) oranı İNANILMAZ DERECEDE YÜKSEK (2.50+). Bu maçın 0-0 kilitleneceğini bağıran bir tablodur. İddaa hiçbir kilitlenmeyi bu kadar belli etmez! Bu tam bir tuzaktır. Maçta sürpriz bir şekilde karşılıklı goller olacak ve maç 1-2, 2-1 gibi skorlarla Üst'e (sürprize) gidecektir. 2.5 Üst aranmalıdır."
            else:
                 return True, "Her iki takımın oranları birbirine çok yakın (tamamen dengeli), beraberlik oranı normalden düşük (<=3.20) ve maçın gollü geçme ihtimali düşük (Üst >= 1.60). Bu tam bir kilitlenme senaryosudur. İki takım da risk almaz, maç 0-0 biter."
        return False, ""
"""

content = content.replace(old_1467_clean, new_1467_safe)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("1467 updated to ignore 1467B cases!")
