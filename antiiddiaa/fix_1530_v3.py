import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1530 again: Use alt25 >= 1.48
old = 'if 1.40 <= alt25 <= 1.60 and iy_05_ust <= 1.30 and iy_05_ust != 99.0 and ms1 >= 1.60 and ms2 >= 1.60 and ms1 != 99.0 and ms2 != 99.0:'
new = 'if 1.48 <= alt25 <= 1.60 and iy_05_ust <= 1.30 and iy_05_ust != 99.0 and ms1 >= 1.60 and ms2 >= 1.60 and ms1 != 99.0 and ms2 != 99.0:'

content = content.replace(old, new)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("1530 fixed with alt25 >= 1.48 limit.")
