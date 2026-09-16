import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix encoding issue in RuleT70
import re
# Replace the bad get_odd calls in RuleT70
pattern = r'(class RuleT70.*?get_odd\(odds, \["Ma)(.*?)(Sonucu_1"\]\).*?get_odd\(odds, \["Ma)(.*?)(Sonucu_0"\]\))'

def replacer(match):
    return match.group(1) + 'ç ' + match.group(3) + 'ç ' + match.group(5)

content = re.sub(pattern, replacer, content, flags=re.DOTALL)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Encoding in T70 fixed!")
