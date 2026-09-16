with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure 1468 is included in upsets if it triggers.
# The upset list is currently:
# elif any(r['code'] in ['T32', 'T33', 'T34', 'T36', '1465', '1466'] for r in triggered_rules):
content = content.replace(
    "elif any(r['code'] in ['T32', 'T33', 'T34', 'T36', '1465', '1466'] for r in triggered_rules):",
    "elif any(r['code'] in ['T32', 'T33', 'T34', 'T36', '1465', '1466', '1468'] for r in triggered_rules):"
)

# And add 1468 to the high goals list (if we want, though maybe not strictly necessary, let's just do upset list)
content = content.replace(
    "if any(r['code'] in ['G1', 'G8', 'T27'] for r in triggered_rules) or ust25 < 1.60:",
    "if any(r['code'] in ['G1', 'G8', 'T27', '1468'] for r in triggered_rules) or ust25 < 1.60:"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Rule 1468 integrated into story_analyzer.")
