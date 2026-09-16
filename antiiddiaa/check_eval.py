import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

eval_matches = re.findall(r'def evaluate\(cls, odds\):', content)
print(f"Found {len(eval_matches)} evaluate definitions.")
