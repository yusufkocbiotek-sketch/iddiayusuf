import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

import re
match = re.search(r'def get_all_rules\(\):(.*?)$', content, re.DOTALL)
if match:
    print(match.group(1)[:500])
else:
    print("get_all_rules not found!")
