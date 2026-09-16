import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    lines = f.readlines()

for i in range(30, 45):
    if i < len(lines):
        print(f"{i}: {lines[i].rstrip()}")
