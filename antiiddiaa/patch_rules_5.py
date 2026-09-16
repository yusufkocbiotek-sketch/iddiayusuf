import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1530 (İlk Yarı Şifresi)
# Add ms0 > 2.90 condition to prevent it from overriding real Draw/Under locks.
old_eval = 'if alt25 <= 1.60 and iy_05_ust <= 1.30 and iy_05_ust != 99.0 and ms1 >= 1.60 and ms2 >= 1.60 and ms1 != 99.0 and ms2 != 99.0:'
new_eval = '''        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        # Eğer MS0 <= 2.90 ise, beraberlik ihtimali çok yüksektir ve bu gerçek bir kısır kilitlenme (0-0/1-1) maçıdır. 1530 tuzağı değildir.
        if alt25 <= 1.60 and iy_05_ust <= 1.30 and iy_05_ust != 99.0 and ms1 >= 1.60 and ms2 >= 1.60 and ms1 != 99.0 and ms2 != 99.0 and ms0 > 2.90:'''

content = content.replace(old_eval, new_eval)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied for 1530.")
