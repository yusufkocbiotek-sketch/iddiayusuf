import os

path = r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    "['T32', 'T35', 'T9', '1470', '1478', '1479', '1480', '1481', '1482', '1483', '1484', '1485']",
    "['T32', 'T35', 'T9', '1470', '1478', '1479', '1480', '1481', '1482', '1483', '1484', '1485', 'G6']"
)

kombine_block = """    elif any(r['code'] == '1485' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Gol Düellosu (Alt Tuzağı Çözüldü)")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)")"""

new_kombine_block = kombine_block + """
    elif any(r['code'] == 'G6' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (Tek Taraflı Ev Şovu)")
        output.append(f"- **Kombine Öneri:** MS 1 + 2.5 Gol Üst (Sürpriz: KG Yok)")"""

text = text.replace(kombine_block, new_kombine_block)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched G6.')
