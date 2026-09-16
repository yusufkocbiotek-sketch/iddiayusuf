import codecs

with codecs.open('story_analyzer.py', 'r', 'utf-8') as f:
    lines = f.readlines()
    
for i, line in enumerate(lines):
    if 'Yalancı Üst Tuzağı' in line:
        for j in range(max(0, i-2), min(len(lines), i+3)):
            print(f"{j}: {lines[j].strip()}")
        print("---")
