import sys
lines = open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\run_block13.py', encoding='utf-8').readlines()
new_lines = []
skip = False
for line in lines:
    if 'if R.code in ["1475", "1493"]:' in line:
        skip = True
        continue
    if skip and 'kural_zinciri.append(R.code)' in line:
        skip = False
    if not skip:
        new_lines.append(line)
open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\run_block13.py', 'w', encoding='utf-8').writelines(new_lines)
print("Reverted.")
