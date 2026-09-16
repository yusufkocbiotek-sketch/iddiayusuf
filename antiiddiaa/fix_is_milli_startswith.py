import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

old_is_milli = '''    for ulke in MILLI_TAKIMLAR:
        if ulke.upper() == ev or ulke.upper() == dep:
            return True'''

new_is_milli = '''    for ulke in MILLI_TAKIMLAR:
        if ev.startswith(ulke.upper()) or dep.startswith(ulke.upper()):
            return True'''

content = content.replace(old_is_milli, new_is_milli)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)
