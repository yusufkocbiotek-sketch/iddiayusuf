import codecs

with codecs.open('story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()

# The fuzzy replace deleted:
#     elif any(r['code'] == 'T35' for r in triggered_rules):
#         output.append(f"- **Ana Tahmin:** Maç Sonucu 0 (Beraberlik İllüzyonu Tuzağı)")
#         output.append(f"- **Kombine Öneri:** MS 0 + 2.5 Gol Altı (Sürpriz: 1-1 / 0-0)")
#     elif any(r['code'] == '1482' for r in triggered_rules): ... (deleted)
#     elif any(r['code'] == '1485' for r in triggered_rules):
#         output.append(f"- **Ana Tahmin:** Gol Düellosu (Alt Tuzağı Çözüldü)")
#         output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)")
#     elif any(r['code'] == 'G6' for r in triggered_rules):
#         output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (Tek Taraflı Ev Şovu)")
#         output.append(f"- **Kombine Öneri:** MS 1 + Karşılıklı Gol Yok (Sürpriz: MS 1 + 2.5 Alt)")

repair_block = '''    elif any(r['code'] == 'LIG_LATAM' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Kısır Maç (Güney Amerika Sertliği)")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Yok + 2.5 Gol Altı")
    elif any(r['code'] == '1511' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 12 Çifte Şans (Beraberliksiz Düello)")
        output.append(f"- **Kombine Öneri:** 12 Çifte Şans + 2.5 Gol Üst + KG Var (Sürpriz Skor: 3-1 / 1-3)")
    elif any(r['code'] == 'T35' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 0 (Beraberlik İllüzyonu Tuzağı)")
        output.append(f"- **Kombine Öneri:** MS 0 + 2.5 Gol Altı (Sürpriz: 1-1 / 0-0)")
    elif any(r['code'] == '1485' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Gol Düellosu (Alt Tuzağı Çözüldü)")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)")
    elif any(r['code'] == 'G6' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (Tek Taraflı Ev Şovu)")
        output.append(f"- **Kombine Öneri:** MS 1 + Karşılıklı Gol Yok (Sürpriz: MS 1 + 2.5 Alt)")'''

story = story.replace('''    elif any(r['code'] == 'LIG_LATAM' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Kısır Maç (Güney Amerika Sertliği)")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Yok + 2.5 Gol Altı")''', repair_block)

with codecs.open('story_analyzer.py', 'w', 'utf-8') as f:
    f.write(story)
