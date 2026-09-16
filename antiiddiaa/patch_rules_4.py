import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1553 (Dengeli KG Patlaması)
# From ms1 >= 2.00 and ms2 >= 2.00 to ms1 >= 1.95 and ms2 >= 1.95
content = content.replace('if ms1 != 99.0 and ms2 != 99.0 and ms1 >= 2.00 and ms2 >= 2.00:', 'if ms1 != 99.0 and ms2 != 99.0 and ms1 >= 1.95 and ms2 >= 1.95:')

# Fix 1554 (Ağır Favori Oran Çelişkisi)
# From ms1 <= 1.25 to ms1 <= 1.30
content = content.replace('if ms1 != 99.0 and ms1 <= 1.25 and ms0 != 99.0 and ms0 <= 4.50 and ms2 != 99.0 and ms2 <= 8.50:', 'if ms1 != 99.0 and ms1 <= 1.30 and ms0 != 99.0 and ms0 <= 4.50 and ms2 != 99.0 and ms2 <= 8.50:')
content = content.replace('Ev sahibi 1.25 altı oranla', 'Ev sahibi 1.30 altı oranla')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied for 1553 and 1554.")
