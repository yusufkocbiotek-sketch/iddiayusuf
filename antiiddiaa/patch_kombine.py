import re

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace massive duel logic
old_kombine = """    output.append(f"\\n### 💎 KOMBİNE & TAHMİN ÖNERİLERİ")
    
    if any(r['code'] in ['T15', 'T22', 'T35'] for r in triggered_rules) and gol_beklentisi == "DÜŞÜK":"""

new_kombine = """    # DEVASA DÜELLO TESPİTİ
    is_massive_duel = ("İlk Yarı Düellosu (KG)" in "".join(output) and "İkinci Yarı Şovu (KG)" in "".join(output)) or "TARİHİ DÜELLO" in "".join(output) or any(r['code'] == 'G11' for r in triggered_rules)

    output.append(f"\\n### 💎 KOMBİNE & TAHMİN ÖNERİLERİ")
    
    if is_massive_duel:
        output.append(f"- **Ana Tahmin:** Taraf bahsi çok riskli, gol düellosu (KG Var/Üst) tercih edilmeli.")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)")
    elif any(r['code'] in ['T15', 'T22', 'T35'] for r in triggered_rules) and gol_beklentisi == "DÜŞÜK":"""
content = content.replace(old_kombine, new_kombine)

# Replace T32, T33, T34 with T32, T33, T34, T36
t36_old = """    elif any(r['code'] in ['T32', 'T33', 'T34'] for r in triggered_rules):"""
t36_new = """    elif any(r['code'] in ['T32', 'T33', 'T34', 'T36'] for r in triggered_rules):"""
content = content.replace(t36_old, t36_new)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('story_analyzer.py patched successfully.')
