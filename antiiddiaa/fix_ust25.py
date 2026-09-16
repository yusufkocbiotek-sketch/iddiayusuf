import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

bad = '''        if ms1 <= 1.25 and ust25 <= 1.30 and ev_15_alt >= 2.50:'''
good = '''        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        if ms1 <= 1.25 and ust25 > 0 and ust25 <= 1.30 and ev_15_alt >= 2.50:'''

content = content.replace(bad, good)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)
