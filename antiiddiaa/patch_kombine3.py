with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "elif any(r['code'] in ['T32', 'T33', 'T34', 'T36'] for r in triggered_rules):",
    "elif any(r['code'] in ['T32', 'T33', 'T34', 'T36', '1465', '1466'] for r in triggered_rules):"
)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Kombine upset patched successfully.")
