import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    content = f.read()

# Extract all 'elif any(r['code'] == '...' for r in triggered_rules):'
codes = re.findall(r"elif any\(r\['code'\] == '([^']+)' for r in triggered_rules\):", content)
print("Order of rules in story_analyzer.py:")
print(codes)
