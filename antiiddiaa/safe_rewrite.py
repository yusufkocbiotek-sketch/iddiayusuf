import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "elif iy_ms2 != 99.0 and iy_ms2 <= 2.80:" in line:
        new_lines.append(line)
        new_lines.append('            timing_insights.append(f"✈️ **Deplasman Baskını:** Deplasman takımının ilk yarıda şok bir üstünlük kurma potansiyeli var (İlk Yarı MS2).")\n')
        new_lines.append('\n')
        new_lines.append('        if timing_insights:\n')
        new_lines.append('            for insight in timing_insights:\n')
        new_lines.append('                output.append(f"- {insight}")\n')
        new_lines.append('        else:\n')
        new_lines.append('            output.append(f"- 📉 **Standart Akış:** Zamanlama (yarı) bahisleri için ekstra bir anomali veya belirgin bir sinyal tespit edilemedi.")\n')
        new_lines.append('\n')
        new_lines.append("    # DEVASA DÜELLO TESPİTİ\n")
        new_lines.append("    is_massive_duel = ('İlk Yarı Düellosu (KG)' in ''.join(output) and 'İkinci Yarı Şovu (KG)' in ''.join(output)) or 'TARİHİ DÜELLO' in ''.join(output) or any(r['code'] == 'G11' for r in triggered_rules)\n")
        new_lines.append('\n')
        new_lines.append('    output.append(f"\\n### 💎 KOMBİNE & TAHMİN ÖNERİLERİ")\n')
        new_lines.append("    if any(r['code'] == '2001' for r in triggered_rules):\n")
        new_lines.append('        output.append(f"- **Ana Tahmin:** 2.5 Gol Altı (Milli Maç Kısırlığı)")\n')
        new_lines.append('        output.append(f"- **Kombine Öneri:** 2.5 Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0 / 1-1 / 1-0)")\n')
        new_lines.append("    elif any(r['code'] == '2002' for r in triggered_rules):\n")
        new_lines.append('        output.append(f"- **Ana Tahmin:** Maç Sonucu 1/2 (Milli Maç Fark Patlaması)")\n')
        new_lines.append('        output.append(f"- **Kombine Öneri:** Favori Kazanır + 3.5 Gol Üst (Sürpriz Skor: 4-0 / 5-0)")\n')
        new_lines.append("    elif any(r['code'] == '1481' for r in triggered_rules):\n")
        new_lines.append('        output.append(f"- **Ana Tahmin:** Sürpriz Deplasman Galibiyeti (MS 2) veya 02 Çifte Şans")\n')
        new_lines.append('        output.append(f"- **Kombine Öneri:** 02 Çifte Şans + 2.5 Gol Üst (Sürpriz Skor: 1-3 / 2-2)")\n')
        new_lines.append("    elif any(r['code'] == '1469' and 'ASYA TUZAĞI' in r['insight'] for r in triggered_rules):\n")
        new_lines.append('        output.append(f"- **Ana Tahmin:** Gol Düellosu (Asya Tuzağı)")\n')
        new_lines.append('        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)")\n')
        new_lines.append("    elif any(r['code'] == '1486' for r in triggered_rules):\n")
        new_lines.append('        output.append(f"- **Ana Tahmin:** Gol Düellosu (Kısır Beraberlik Tuzağı Kırıldı)")\n')
        new_lines.append('        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)")\n')
        new_lines.append("    elif any(r['code'] == '1487' for r in triggered_rules):\n")
        new_lines.append('        output.append(f"- **Ana Tahmin:** Gol Düellosu (İlk Yarı Uyku Tuzağı Patlaması)")\n')
        skip = True
        continue
        
    if skip:
        if "output.append(f\"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)\")" in line:
            # wait, this belongs to 1487
            new_lines.append(line)
            skip = False
        continue
        
    new_lines.append(line)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf-8') as f:
    f.writelines(new_lines)
