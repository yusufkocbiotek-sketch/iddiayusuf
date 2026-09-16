import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1530 mapping
old_1530 = """'1530': ("İlk Yarı Şifresi (Kısır Maç, Hızlı Gol)", "İlk Yarı 0.5 Üst veya İlk Yarı 1.5 Üst (Sürpriz Skor: İlk Yarı 2-1)"),"""
new_1530 = """'1530': ("İlk Yarı Şifresi (Kısır Maç, Hızlı Gol)", "İlk Yarı 0.5 Üst (Sürpriz Skor: İlk Yarı 1-0 veya 1-1)"),"""
content = content.replace(old_1530, new_1530)

# Fix G1 mapping
old_g1 = """'G1': ("Karşılıklı Gol Var (Sahte KG Yok Tuzağı)", "KG Var + 2.5 Gol Üst (Sürpriz Skor: 2-1 veya 1-2)"),"""
new_g1 = """'G1': ("Kesin 2 Gol Sinyali (Piyasa Yanılgısı)", "1.5 Gol Üst veya 2.5 Gol Üst (Şov İhtimali: 3-0 veya 0-3)"),"""
content = content.replace(old_g1, new_g1)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("story_analyzer.py patched successfully!")
