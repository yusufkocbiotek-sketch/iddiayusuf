import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_sort = """    for r in rules:
        if r.code.isdigit():
            anomaly_rules.append(r)
        else:
            trend_rules.append(r)
            
    # Sort anomaly descending (1556 -> 1460)
    anomaly_rules.sort(key=lambda x: int(x.code), reverse=True)"""

new_sort = """    for r in rules:
        if r.code and r.code[0].isdigit():
            anomaly_rules.append(r)
        else:
            trend_rules.append(r)
            
    # Sort anomaly descending (1556 -> 1460). Strip non-digits for sorting (e.g. 1467B -> 1467)
    import re
    anomaly_rules.sort(key=lambda x: int(re.sub(r'\\D', '', x.code)), reverse=True)
    
    # Ensure T70 comes before T27 if we want to prioritize it, but better yet, 
    # let's just make sure T70 is dominant by giving it a higher priority or sorting T rules properly.
    # Actually, alphabetical string sort: "T27" < "T70", so T27 is first. 
    # Let's sort trend rules such that T70 comes before T27. 
    # For trend rules, we can sort them by the number inside them descending!
    trend_rules.sort(key=lambda x: int(re.sub(r'\\D', '', x.code)) if re.sub(r'\\D', '', x.code) else 0, reverse=True)"""

content = content.replace(old_sort, new_sort)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Sorting bug in rule_engine.py fixed!")
