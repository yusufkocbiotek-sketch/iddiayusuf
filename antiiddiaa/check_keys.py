import sys

lines = open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', encoding='utf-8').readlines()
keys = set()
for l in lines:
    if 'get_odd(odds, [' in l:
        part = l.split('[')[1].split(']')[0]
        for k in part.split(','):
            keys.add(k.strip().strip('\"\''))
for k in sorted(keys): 
    print(k)
