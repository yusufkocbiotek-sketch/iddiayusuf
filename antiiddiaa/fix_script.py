import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    lines = f.readlines()

out_lines = []
for line in lines:
    if line.strip() == "elif any(r['code'] == '1486' for r in triggered_rules):":
        # Insert the missing parts right before this
        missing = """            output.append(f"- 📉 **Standart Akış:** Zamanlama (yarı) bahisleri için ekstra bir anomali veya belirgin bir sinyal tespit edilemedi.")

    # DEVASA DÜELLO TESPİTİ
    is_massive_duel = ('İlk Yarı Düellosu (KG)' in ''.join(output) and 'İkinci Yarı Şovu (KG)' in ''.join(output)) or 'TARİHİ DÜELLO' in ''.join(output) or any(r['code'] == 'G11' for r in triggered_rules)

    output.append(f"\\n### 💎 KOMBİNE & TAHMİN ÖNERİLERİ")
    if any(r['code'] == '2001' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 2.5 Gol Altı (Milli Maç Kısırlığı)")
        output.append(f"- **Kombine Öneri:** 2.5 Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0 / 1-1 / 1-0)")
    elif any(r['code'] == '2002' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1/2 (Milli Maç Fark Patlaması)")
        output.append(f"- **Kombine Öneri:** Favori Kazanır + 3.5 Gol Üst (Sürpriz Skor: 4-0 / 5-0)")
    elif any(r['code'] == '1481' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Sürpriz Deplasman Galibiyeti (MS 2) veya 02 Çifte Şans")
        output.append(f"- **Kombine Öneri:** 02 Çifte Şans + 2.5 Gol Üst (Sürpriz Skor: 1-3 / 2-2)")
    elif any(r['code'] == '1469' and 'ASYA TUZAĞI' in r['insight'] for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Gol Düellosu (Asya Tuzağı)")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)")
    """
        out_lines.append(missing)
    out_lines.append(line)

# Wait, if there was an empty `else:` block, we need to fix it.
final_lines = []
for line in out_lines:
    if line.strip() == "else:" and len(final_lines) > 0 and "for insight in timing_insights:" in final_lines[-1]:
        pass # this else is fine
    elif line.strip() == "else:" and "for insight in timing_insights:" not in final_lines[-1] and "output.append" not in final_lines[-1] and "output.append" not in final_lines[-2]:
        # we might have a broken else
        pass
    final_lines.append(line)

# Let's just fix it completely.
# Actually I will just view lines 260-280 to see what the mess is.
