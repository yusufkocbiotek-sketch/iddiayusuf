import codecs

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    lines = f.readlines()
    
for i, line in enumerate(lines):
    if '1475' in line or 'Sahte Düello' in line:
        for j in range(max(0, i-5), min(len(lines), i+15)):
            print(f"{j}: {lines[j].strip()}")
        break
