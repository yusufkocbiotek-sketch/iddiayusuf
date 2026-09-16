import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add mappings for 1485 and T70
old_mappings = """    '1467B': ("Gollü Beraberlik Tuzağı (2-2 / 3-3)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 2-2 veya 3-3)"),"""
new_mappings = """    '1467B': ("Gollü Beraberlik Tuzağı (2-2 / 3-3)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 2-2 veya 3-3)"),\n    '1485': ("Sahte Düello Tuzağı (1-0 Kilitlenmesi)", "Maç Sonucu 1 veya 0 + 2.5 Gol Altı (Sürpriz Skor: 1-0 veya 0-0)"),\n    'T70': ("Sahte Ağır Favori (Düşük Beraberlik Tuzağı)", "Çifte Şans X2 veya Maç Sonucu 0 (Sürpriz Skor: 0-1 veya 1-1)"),"""
content = content.replace(old_mappings, new_mappings)

# Add anomaly detection for T70
old_anomaly = """if has_anomaly or any(r['code'] in ['T32', 'T35', 'T9', 'G6', 'G10'] for r in triggered_rules):"""
new_anomaly = """if has_anomaly or any(r['code'] in ['T32', 'T35', 'T9', 'G6', 'G10', 'T70'] for r in triggered_rules):"""
content = content.replace(old_anomaly, new_anomaly)

# Add score logic for 1485 and T70
old_score_if = """    if has_1467B:
        skorlar = "2-2 > 3-3 > 1-1"
        kacin = "0-0 / 1-0 / 0-1 gibi kısır skorlar"
    elif has_g1:"""
new_score_if = """    has_1485 = any(r['code'] == '1485' for r in triggered_rules)
    has_t70 = any(r['code'] == 'T70' for r in triggered_rules)
    
    if has_1467B:
        skorlar = "2-2 > 3-3 > 1-1"
        kacin = "0-0 / 1-0 / 0-1 gibi kısır skorlar"
    elif has_1485:
        skorlar = "1-0 > 0-0 > 1-1"
        kacin = "2-1 / 2-2 / 3-1 gibi gollü skorlar"
    elif has_t70:
        skorlar = "0-1 > 1-1 > 0-0 > 1-2"
        kacin = "2-0 / 3-0 gibi farklı ev sahibi skorları"
    elif has_g1:"""
content = content.replace(old_score_if, new_score_if)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("story_analyzer.py patched for 1485 and T70!")
