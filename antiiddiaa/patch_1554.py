import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_1554 = """if ms1 != 99.0 and ms1 <= 1.30 and ms0 != 99.0 and ms0 <= 4.50 and ms2 != 99.0 and ms2 <= 8.50:"""
new_1554 = """if ms1 != 99.0 and ms1 <= 1.25 and ms0 != 99.0 and ms0 <= 4.40 and ms2 != 99.0 and ms2 <= 7.50:"""
content = content.replace(old_1554, new_1554)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("1554 threshold tightened to avoid false positives on 1.30 favorites!")
