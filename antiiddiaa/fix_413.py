import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf8') as f:
    engine = f.read()

# Fix 1516
engine = engine.replace('if ms1 <= 1.40 and ms2 >= 4.00 and kg_var <= 1.45:', 'if ms1 <= 1.40 and ms2 >= 4.00 and kg_var <= 1.50:')
engine = engine.replace('KG Var oranı 1.45 gibi çok düşük', 'KG Var oranı 1.50 ve altı gibi çok düşük')

# Fix 1504 99.0 bug
engine = engine.replace('if ms1 <= 1.35 and ev_15_ust >= 1.45:', 'if ms1 <= 1.35 and ev_15_ust >= 1.45 and ev_15_ust != 99.0:')

# Fix 1475 99.0 bug just in case
engine = engine.replace('and ev_15_alt >= 2.00', 'and ev_15_alt >= 2.00 and ev_15_alt != 99.0')

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf8') as f:
    f.write(engine)

# Fix 1512 in story_analyzer
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf8') as f:
    analyzer = f.read()

analyzer = analyzer.replace(
    "'1512': (\"Gizli 2.5 Barajı (Barem Saklama Tuzağı)\", \"X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2 / 2-2)\"),",
    "'1512': (\"Gizli 2.5 Barajı (Barem Saklama Tuzağı)\", \"3.5 Gol Üstü + Karşılıklı Gol Var (Sürpriz Skor: 2-2 / 3-2)\"),"
)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf8') as f:
    f.write(analyzer)

print("Fixes applied.")
