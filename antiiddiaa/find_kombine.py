import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'KOMBİNE & TAHMİN ÖNERİLERİ' in line:
        for j in range(i, i+15):
            print(f"{j+1}: {lines[j].rstrip()}")
        break
