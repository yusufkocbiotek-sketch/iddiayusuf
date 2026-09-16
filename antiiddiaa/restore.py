import codecs

with codecs.open('story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()

# I need to restore the deleted block correctly.
bad_state = '''    elif any(r['code'] == '1491' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Gol Düellosu (Gerçek Yüksek Skor)")
    elif any(r['code'] == 'G10' for r in triggered_rules):'''

correct_state = '''    elif any(r['code'] == '1491' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Gol Düellosu (Gerçek Yüksek Skor)")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst")
    elif any(r['code'] == 'LIG_ASYA' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Gol Düellosu (Asya Ligi Özelliği)")
        output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst")
    elif any(r['code'] == '1511' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 12 Çifte Şans (Beraberliksiz Düello)")
        output.append(f"- **Kombine Öneri:** 12 Çifte Şans + 2.5 Gol Üst + KG Var (Sürpriz Skor: 3-1 / 1-3)")
    elif any(r['code'] == '1469' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 0 (Kısır Beraberlik Tuzağı)")
        output.append(f"- **Kombine Öneri:** MS 0 + 2.5 Gol Altı (Sürpriz: 1-1 / 0-0)")
    elif any(r['code'] == '1483' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (Net 1-0 Beklentisi)")
        output.append(f"- **Kombine Öneri:** MS 1 + 2.5 Gol Altı")
    elif any(r['code'] == 'G10' for r in triggered_rules):'''

story = story.replace(bad_state, correct_state)

with codecs.open('story_analyzer.py', 'w', 'utf-8') as f:
    f.write(story)
