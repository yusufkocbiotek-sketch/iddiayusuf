import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1530 logic
old_1530 = """        if 1.48 <= alt25 <= 1.60 and iy_05_ust <= 1.30 and iy_05_ust != 99.0 and ms1 >= 1.60 and ms2 >= 1.60 and ms1 != 99.0 and ms2 != 99.0:"""
new_1530 = """        # Eğer ev sahibi net favori ise (MS1 < 1.95), bu kural çalışmamalıdır çünkü o maçlar gerçekten kısır geçebilir (1-0 gibi).
        if 1.48 <= alt25 <= 1.60 and iy_05_ust <= 1.30 and iy_05_ust != 99.0 and ms1 >= 1.95 and ms2 >= 1.60 and ms1 != 99.0 and ms2 != 99.0:"""
content = content.replace(old_1530, new_1530)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("1530 fixed to avoid false positives on home favorites!")
