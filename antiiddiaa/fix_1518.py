import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', 'utf8') as f:
    text = f.read()

# Rename the second occurrence of class Rule1485(BaseRule): to Rule1518
# It's followed by code = "1485" and category = "GOL" and name = "Gizli Düello (Alt/KG Yok İllüzyonu)"

target = '''class Rule1485(BaseRule):
    code = "1485"
    category = "GOL"
    name = "Gizli Düello (Alt/KG Yok İllüzyonu)"'''

replacement = '''class Rule1518(BaseRule):
    code = "1518"
    category = "GOL"
    name = "Gizli Düello (Alt/KG Yok İllüzyonu)"'''

if target in text:
    text = text.replace(target, replacement)
    
    # Also add Rule1518 to anomaly_rules
    if 'Rule1518' not in text:
        text = text.replace('anomaly_rules = [Rule1517', 'anomaly_rules = [Rule1518, Rule1517')
        
    with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', 'utf8') as f:
        f.write(text)
    print("rule_engine.py fixed!")
else:
    print("Target not found in rule_engine.py")

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf8') as f:
    text2 = f.read()

target2 = "        '1517':"
replacement2 = """        '1518': ("Gizli Düello (Alt/KG Yok İllüzyonu)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 3-1 / 1-2)"),
        '1517':"""

if target2 in text2:
    if '1518' not in text2:
        text2 = text2.replace(target2, replacement2)
        with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf8') as f:
            f.write(text2)
        print("story_analyzer.py fixed!")
    else:
        print("1518 already in story_analyzer.py")
else:
    print("Target not found in story_analyzer.py")
