import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '2001' in line or '2002' in line:
        print(f"{i+1}: {line.rstrip()}")
