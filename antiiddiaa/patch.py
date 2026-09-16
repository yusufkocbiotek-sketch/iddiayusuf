import os

path = r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    "['T32', 'T35', 'T9', '1470', '1478', '1479', '1480', '1481', '1482', '1483', '1484']",
    "['T32', 'T35', 'T9', '1470', '1478', '1479', '1480', '1481', '1482', '1483', '1484', '1485']"
)

text = text.replace(
    "elif any(r['code'] == '1482' for r in triggered_rules):\n            ana_tahmin = \"Maç Sonucu 1 veya 1X Çifte Şans (Sahte Düello)\"\n            kombine_oneri = \"1X Çifte Şans + 2.5 Gol Altı (veya KG Yok)\"",
    "elif any(r['code'] == '1482' for r in triggered_rules):\n            ana_tahmin = \"Maç Sonucu 1 veya 1X Çifte Şans (Sahte Düello)\"\n            kombine_oneri = \"1X Çifte Şans + 2.5 Gol Altı (veya KG Yok)\"\n        elif any(r['code'] == '1485' for r in triggered_rules):\n            ana_tahmin = \"Gol Düellosu (Alt Tuzağı Çözüldü)\"\n            kombine_oneri = \"Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)\""
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
