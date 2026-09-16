import os
import re
path = r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()
match = re.search(r'class RuleG6.*?return False, ""', text, re.DOTALL)
if match:
    print(match.group(0))
else:
    print("Not found")
