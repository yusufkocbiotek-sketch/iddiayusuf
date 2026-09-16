import codecs
import re
content = codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf8').read()

match = re.search(r'class Rule1495.*?return False, ""', content, flags=re.DOTALL)
if match:
    old_code = match.group(0)
    if 'GİZLİ DEPLASMAN ŞOVU' in old_code:
        new_code = old_code.replace('Rule1495', 'Rule1472').replace('"1495"', '"1472"')
        content = content.replace(old_code, '')
        content = content.replace('class Rule1469', new_code + '\nclass Rule1469')
        content = content.replace('Rule1495, Rule1494', 'Rule1494')
        content = content.replace('Rule1473', 'Rule1473, Rule1472')
        codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf8').write(content)
        print('Rule1472 created and inserted successfully.')
    else:
        print('First Rule1495 was not the one I expected.')
else:
    print('Rule1495 not found.')
