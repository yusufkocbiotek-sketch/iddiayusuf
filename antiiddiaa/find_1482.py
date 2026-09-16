import codecs

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    lines = f.readlines()
    
for i, line in enumerate(lines):
    if '1482' in line:
        for j in range(max(0, i-2), min(len(lines), i+15)):
            print(f"{j}: {lines[j].strip()}")
        break
