import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'Sürpriz Patlama (Favori Kazanamaz)' in line:
        print(f"Found at line {i+1}:")
        for j in range(max(0, i-5), min(len(lines), i+5)):
            print(f"{j+1}: {lines[j].rstrip()}")
