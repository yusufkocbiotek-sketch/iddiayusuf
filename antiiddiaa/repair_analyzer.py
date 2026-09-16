with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the corruption at line 111
content = content.replace(
    '''    # G10 gibi çok baskın bir tuzak kuralı aktifse gol beklentisini zorla Düşük yap.
    elif any(r['code'] in ['T15', 'T22', 'T35', '1467'] for r in triggered_rules) and gol_beklentisi == "DÜŞÜK":
        pass''',
    '''    # G10 gibi çok baskın bir tuzak kuralı aktifse gol beklentisini zorla Düşük yap.
    if any(r['code'] == 'G10' for r in triggered_rules):
        gol_beklentisi = "DÜŞÜK"'''
)

# Apply the actual fix for 1467
content = content.replace(
    'elif any(r[\'code\'] in [\'T15\', \'T22\', \'T35\'] for r in triggered_rules) and gol_beklentisi == "DÜŞÜK":',
    'elif any(r[\'code\'] in [\'T15\', \'T22\', \'T35\', \'1467\'] for r in triggered_rules) and (gol_beklentisi == "DÜŞÜK" or "1467" in [r[\'code\'] for r in triggered_rules]):'
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Repaired story_analyzer.py")
