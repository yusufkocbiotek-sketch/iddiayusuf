with open(r"C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
total = len(lines)
print(f"Total lines: {total}")
start = total - 727
end = total - 717
print(f"Block -727 to -717 => actual lines {start} to {end}")
print(f"Showing lines {start} to {end}:")
for i in range(start, end + 1):
    if 0 <= i < total:
        print(f"  Line {i+1}: {lines[i].rstrip()}")
