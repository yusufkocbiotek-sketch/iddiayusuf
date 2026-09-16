with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "### 💎 KOMBİNE & TAHMİN ÖNERİLERİ" in line:
        new_lines.append("    # DEVASA DÜELLO TESPİTİ\n")
        new_lines.append("    is_massive_duel = ('İlk Yarı Düellosu (KG)' in ''.join(output) and 'İkinci Yarı Şovu (KG)' in ''.join(output)) or 'TARİHİ DÜELLO' in ''.join(output) or any(r['code'] == 'G11' for r in triggered_rules)\n\n")
        new_lines.append(line)
        new_lines.append("    if is_massive_duel:\n")
        new_lines.append("        output.append(f\"- **Ana Tahmin:** Taraf bahsi çok riskli, gol düellosu (KG Var/Üst) tercih edilmeli.\")\n")
        new_lines.append("        output.append(f\"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)\")\n")
        continue
    
    if "if any(r['code'] in ['T15', 'T22', 'T35'] for r in triggered_rules) and gol_beklentisi ==" in line:
        # Change if to elif
        new_lines.append(line.replace("if any", "elif any"))
        continue
        
    if "elif any(r['code'] in ['T32', 'T33', 'T34'] for r in triggered_rules):" in line:
        new_lines.append("    elif any(r['code'] in ['T32', 'T33', 'T34', 'T36'] for r in triggered_rules):\n")
        continue

    new_lines.append(line)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
    
print("story_analyzer.py properly patched!")
