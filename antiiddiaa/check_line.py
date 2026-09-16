import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    lines = f.readlines()

for i in range(1190, 1210):
    if i < len(lines):
        print(f"{i}: {lines[i].rstrip()}")
