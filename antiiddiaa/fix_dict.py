import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf8') as f:
    text = f.read()

# Replace duplicates and old 1512 in the PREDICTIONS dictionary

bad_block = """        '1505': ("Maç Sonucu 2 (Sahte Beraberlik)", "MS 2 + 2.5 Gol Altı (Sürpriz Skor: 0-2)"),
        '1503': ("Sürpriz Deplasman Galibiyeti (Sahte Düello)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2)"),
        '1500': ("X2 Çifte Şans (Sahte Ev Sahibi)", "02 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-1 / 1-2)"),
        '1512A': ("Gol Düellosu (Gizli Barem - Şov Patlaması)", "3.5 Gol Üst + Karşılıklı Gol Var"),
        '1512B': ("Gizli Barem (Alt Tuzağı)", "2.5 Gol Altı (Sürpriz Skor: 1-0 / 2-0)"),
        '1513': ("Handikaplı Deplasman Yemi (Zayıf Ev Sahibi)", "MS 1 (veya 1X) + 2.5 Alt"),
        '1512': ("Ev Sahibi Puan Kaybı (X2 ÇŞ)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2 / 2-2)"),
        '1513': ("Ev Sahibi Kaybetmez (1X ÇŞ)", "1X Çifte Şans + 2.5 Gol Altı (Sürpriz Skor: 1-1 / 1-0)"),"""

good_block = """        '1505': ("Maç Sonucu 2 (Sahte Beraberlik)", "MS 2 + 2.5 Gol Altı (Sürpriz Skor: 0-2)"),
        '1503': ("Sürpriz Deplasman Galibiyeti (Sahte Düello)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2)"),
        '1500': ("X2 Çifte Şans (Sahte Ev Sahibi)", "02 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-1 / 1-2)"),
        '1512A': ("Gol Düellosu (Gizli Barem - Şov Patlaması)", "3.5 Gol Üst + Karşılıklı Gol Var"),
        '1512B': ("Gizli Barem (Alt Tuzağı)", "2.5 Gol Altı (Sürpriz Skor: 1-0 / 2-0)"),
        '1513': ("Handikaplı Deplasman Yemi (Zayıf Ev Sahibi)", "MS 1 (veya 1X) + 2.5 Alt"),"""

text_normalized = text.replace('\r\n', '\n')
bad_block_normalized = bad_block.replace('\r\n', '\n')
if bad_block_normalized in text_normalized:
    text_normalized = text_normalized.replace(bad_block_normalized, good_block.replace('\r\n', '\n'))
    with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf8') as f:
        f.write(text_normalized)
    print("FIXED")
else:
    print("COULD NOT FIND BLOCK")
