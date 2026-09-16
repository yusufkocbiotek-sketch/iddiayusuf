import codecs

with codecs.open('story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()
    
# Find the exact indentation error block and fix it.
lines = story.split('\n')
for i, line in enumerate(lines):
    if "elif any(r['code'] == '1469'" in line:
        print(f"Line {i}: {line}")
        print(f"Line {i-1}: {lines[i-1]}")
        print(f"Line {i-2}: {lines[i-2]}")
        break
