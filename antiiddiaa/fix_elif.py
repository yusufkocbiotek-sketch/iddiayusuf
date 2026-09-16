import codecs

with codecs.open('story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()

bad_block = '''    elif any(r['code'] == 'LIG_LATAM' for r in triggered_rules):
    elif any(r['code'] == '1469' for r in triggered_rules):'''

good_block = '''    elif any(r['code'] == '1511' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 12 Çifte Şans (Beraberliksiz Düello)")
        output.append(f"- **Kombine Öneri:** 12 Çifte Şans + 2.5 Gol Üst + KG Var (Sürpriz Skor: 3-1 / 1-3)")
    elif any(r['code'] == '1469' for r in triggered_rules):'''

story = story.replace(bad_block, good_block)

with codecs.open('story_analyzer.py', 'w', 'utf-8') as f:
    f.write(story)
