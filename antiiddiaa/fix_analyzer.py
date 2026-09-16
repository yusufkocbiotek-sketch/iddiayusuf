import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the wrong 1479 entry
old_val = "'1479': (\"Gol Düellosu (Altın Çelişki)\", \"Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)\"),"
new_val = "'1479': (\"Favori Gol Kısırlığı Tuzağı (X2/MS2)\", \"Deplasman Puan Alır (02 ÇŞ) veya MS2\"),"

content = content.replace(old_val, new_val)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)
