import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

import re
m = re.search(r'class Rule1513.*?return False, ""\s*', content, re.DOTALL)
if m:
    print(m.group(0))
