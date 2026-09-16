import codecs

with codecs.open('story_analyzer.py', 'r', 'utf-8') as f:
    lines = f.readlines()

for i in range(350, 375):
    print(f"{i}: {lines[i].rstrip()}")
