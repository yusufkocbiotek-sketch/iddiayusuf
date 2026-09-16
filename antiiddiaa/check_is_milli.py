import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

import re
m = re.search(r'def is_milli_mac.*?return False', content, re.DOTALL)
if m:
    print(m.group(0))
