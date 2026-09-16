import codecs

file_path = r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py'
with codecs.open(file_path, 'r', 'utf8') as f:
    text = f.read()

# Fix comparisons for ms1 and ms2 to exclude 99.0
text = text.replace('if ms1 < ms2 and ms1 <= 1.50:', 'if ms1 != 99.0 and ms2 != 99.0 and ms1 < ms2 and ms1 <= 1.50:')
text = text.replace('elif ms1 < ms2:', 'elif ms1 != 99.0 and ms2 != 99.0 and ms1 < ms2:')
text = text.replace('elif ms2 < ms1 and ms2 <= 1.50:', 'elif ms1 != 99.0 and ms2 != 99.0 and ms2 < ms1 and ms2 <= 1.50:')
text = text.replace('elif ms2 < ms1:', 'elif ms1 != 99.0 and ms2 != 99.0 and ms2 < ms1:')
text = text.replace('if ms1 < ms2:', 'if ms1 != 99.0 and ms2 != 99.0 and ms1 < ms2:')
text = text.replace('else:\n        if ms1 < ms2:', 'else:\n        if ms1 != 99.0 and ms2 != 99.0 and ms1 < ms2:')

with codecs.open(file_path, 'w', 'utf8') as f:
    f.write(text)

print("Fixed story_analyzer.py comparisons")
