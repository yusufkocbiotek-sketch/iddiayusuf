import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    content = f.read()

import re
m = re.search(r'matched_rules = find_triggering_rules\(.*?active_rule = None', content, re.DOTALL)
if m:
    print(m.group(0))
