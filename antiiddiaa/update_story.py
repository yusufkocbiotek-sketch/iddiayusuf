import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf8') as f:
    analyzer = f.read()

# Update T68
analyzer = analyzer.replace(
    "'T68': (\"Beraberlik İptali (Sürpriz Taraf Kazanır)\", \"Çifte Şans 12 + 2.5 Gol Altı\"),",
    "'T68': (\"Beraberlik İptali (Sürpriz Taraf Kazanır)\", \"Çifte Şans 12 + 1.5 Gol Üstü (Sürpriz Skor: 1-2 / 2-1)\"),"
)

# Insert 1515
new_1515 = "\n        '1515': (\"Sahte Ev Sahibi Golü Tuzağı (Deplasman Katliamı)\", \"MS 2 + Karşılıklı Gol Yok (Sürpriz Skor: 0-3 / 0-4)\"),"
analyzer = analyzer.replace("predictions = {", "predictions = {" + new_1515)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf8') as f:
    f.write(analyzer)

print("Updated story_analyzer.py!")
