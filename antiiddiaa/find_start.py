import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith("    if any(r['code'] =="):
        print(f"Starts at line {i+1}: {line.rstrip()}")
        break
