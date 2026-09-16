import sys

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    # Düşük gol beklentisinde 1530 yakalanırsa diye eklediğimiz kısmı daha temiz bir şekilde değiştirelim
    if 'elif gol_beklentisi == "DÜŞÜK" and any(kural.code == "1530"' in line:
        skip = True
        new_lines.append('    elif gol_beklentisi == "DÜŞÜK" and any(kural.code == "1530" for kural in triggered_rules):\n')
        new_lines.append('        ms0 = rule_engine.get_odd(match.get(\'oranlar\', {}), ["Maç Sonucu_0", "Maç Sonucu_Beraberlik"])\n')
        new_lines.append('        if ms0 <= 2.85 and ms0 != 99.0:\n')
        new_lines.append('            skorlar = "0-0 (Kilit Maç)"\n')
        new_lines.append('            kacin = "Tüm gollü skorlar"\n')
        new_lines.append('        else:\n')
        new_lines.append('            skorlar = "1-1 > 2-1 > 1-2"\n')
        new_lines.append('            kacin = "3-0 / 0-3 gibi farklı skorlar"\n')
        continue
        
    if skip:
        # Eğer skip true ise eski bloğun bitmesini bekle.
        if 'else:' in line and 'skorlar = "1-1 > 2-1 > 1-2 > 2-0"' in lines[i+1]:
            skip = False
        else:
            continue
            
    if not skip:
        new_lines.append(line)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("story_analyzer.py fixed safely.")
