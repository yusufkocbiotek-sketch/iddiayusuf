import os

path = r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

kombine_block = """    elif any(r['code'] == 'G6' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (Tek Taraflı Ev Şovu)")
        output.append(f"- **Kombine Öneri:** MS 1 + 2.5 Gol Üst (Sürpriz: KG Yok)")"""

new_kombine_block = kombine_block + """
    elif any(r['code'] == '1469' and 'ASYA TUZAĞI' in r['story'] for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Gol Düellosu (Asya Tuzağı)")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)")
    elif any(r['code'] == '1469' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 0 (Kısır Beraberlik Tuzağı)")
        output.append(f"- **Kombine Öneri:** MS 0 + 2.5 Gol Altı (Sürpriz: 1-1 / 0-0)")"""

text = text.replace(kombine_block, new_kombine_block)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched Asya.')
