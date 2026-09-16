import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Score Logic
old_score_logic = """    if gol_beklentisi == "YÜKSEK" and kg_var < kg_yok:
        skorlar = "2-1 > 1-2 > 2-2 > 3-1"
        kacin = "0-0 / 1-0 / 0-1 gibi kısır skorlar"
    elif gol_beklentisi == "YÜKSEK" and kg_yok < kg_var:
        skorlar = "3-0 > 0-3 > 4-0 > 2-0"
        kacin = "1-1 / 2-2 gibi karşılıklı gollü skorlar"
    elif gol_beklentisi == "DÜŞÜK" and kg_yok < kg_var:
        skorlar = "1-0 > 0-1 > 0-0 > 2-0"
        kacin = "2-2 / 3-1 / 1-3 gibi bol gollü skorlar"
    elif gol_beklentisi == "DÜŞÜK" and kg_var < kg_yok:
        skorlar = "1-1 > 2-1 > 1-2"
        kacin = "3-0 / 0-3 gibi farklı skorlar"
    else:
        skorlar = "1-1 > 2-1 > 1-2 > 2-0"
        kacin = "Çok farklı skorlar (Örn: 4-0)"
"""

new_score_logic = """    
    has_g1 = any(r['code'] == 'G1' for r in triggered_rules)
    has_g11 = any(r['code'] == 'G11' for r in triggered_rules)
    
    if has_g1:
        skorlar = "3-0 > 4-0 > 0-3 > 3-1"
        kacin = "0-0 / 1-1 / 1-0 gibi kısır veya beraberlik skorları"
    elif has_g11:
        skorlar = "2-2 > 2-1 > 1-2 > 3-2"
        kacin = "0-0 / 1-0 / 0-1 gibi kısır skorlar"
    elif gol_beklentisi == "YÜKSEK" and kg_var < kg_yok:
        skorlar = "2-1 > 1-2 > 2-2 > 3-1"
        kacin = "0-0 / 1-0 / 0-1 gibi kısır skorlar"
    elif gol_beklentisi == "YÜKSEK" and kg_yok < kg_var:
        skorlar = "3-0 > 0-3 > 4-0 > 2-0"
        kacin = "1-1 / 2-2 gibi karşılıklı gollü skorlar"
    elif gol_beklentisi == "DÜŞÜK" and kg_yok < kg_var:
        skorlar = "1-0 > 0-1 > 0-0 > 2-0"
        kacin = "2-2 / 3-1 / 1-3 gibi bol gollü skorlar"
    elif gol_beklentisi == "DÜŞÜK" and kg_var < kg_yok:
        skorlar = "1-1 > 2-1 > 1-2"
        kacin = "3-0 / 0-3 gibi farklı skorlar"
    else:
        skorlar = "1-1 > 2-1 > 1-2 > 2-0"
        kacin = "Çok farklı skorlar (Örn: 4-0)"
"""

content = content.replace(old_score_logic, new_score_logic)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Score logic patched!")
