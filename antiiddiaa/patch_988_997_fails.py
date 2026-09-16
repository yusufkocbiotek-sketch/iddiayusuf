import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1467B (Match 988)
old_1467b = """        if ms1 >= 2.20 and ms2 >= 2.20 and ms0 <= 2.80 and alt25 <= 1.50:"""
new_1467b = """        if ms1 >= 2.00 and ms2 >= 2.00 and ms0 <= 2.85 and alt25 <= 1.55:"""
content = content.replace(old_1467b, new_1467b)

# Add 1485 (Match 993)
rule_1485 = """class Rule1485(BaseRule):
    code = "1485"
    category = "SKOR"
    name = "Sahte Düello Tuzağı (1-0 Kilitlenmesi)"
    description = "Düşük Beraberlik (MS0 <= 3.05) + KG Var <= 1.50 + Üst <= 1.60"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Alt/Üst 2,5_Üst"])
        
        if ms0 <= 3.05 and ms1 <= 2.10 and kg_var <= 1.50 and ust25 <= 1.60:
            return True, "SAHTE DÜELLO TUZAĞI (1-0/0-0): Maçın KG Var ve Üst oranları çok düşük açılarak gollü geçeceği algısı yaratılmış. FAKAT beraberlik oranı (MS0 <= 3.05) anormal derecede düşük. Bu kadar düşük beraberlik oranı, maçın inanılmaz sıkı ve kısır geçeceğinin kanıtıdır. Piyasa gollere hücum ederken maç 1-0, 0-0 veya 1-1 gibi çok kısır skorlarla kilitlenir. Gol bahislerinden (KG Var, Üst) KESİNLİKLE uzak durulmalıdır!"
        return False, ""

"""
content = content.replace("class Rule1516(BaseRule):", rule_1485 + "class Rule1516(BaseRule):")

# Add T70 (Match 992)
rule_t70 = """class RuleT70(BaseRule):
    code = "T70"
    category = "YÖN"
    name = "Sahte Ağır Favori (Düşük Beraberlik Tuzağı)"
    description = "MS1 <= 1.55 iken MS0 <= 3.30 ise Favori takılır (0-1 / 1-1)"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        
        if ms1 <= 1.55 and ms0 <= 3.30 and ms1 != 99.0 and ms0 != 99.0:
            return True, "SAHTE AĞIR FAVORİ (PATLAMA RİSKİ): Ev sahibi 1.55 ve altı oranla çok net favori gösterilmiş. Ancak beraberlik oranı (<= 3.30) böyle bir favori için İMKANSIZ derecede düşüktür (Normalde 3.80+ olmalıdır). Bu oran matematiği, ev sahibinin çok büyük zorluk çekeceğini, maçın kilitleneceğini ve konuk takımın sürpriz yapabileceğini (0-1, 1-1) gösterir. MS1 kesinlikle oynanmamalı, sürpriz X2 denenmelidir."
        return False, ""

"""
content = content.replace("class RuleT68(BaseRule):", rule_t70 + "class RuleT68(BaseRule):")

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("1467B relaxed, 1485 and T70 added successfully!")
