import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def patch_line(line):
    # Ignore lines that are comments or don't have python keywords like 'if ' or 'and ' or 'or ' or assignments
    if line.strip().startswith('#') or 'description =' in line or 'name =' in line:
        return line
    
    # We want to match: variable >= number or variable > number
    # and replace with: variable != 99.0 and variable >= number
    # But ONLY if variable != 99.0 isn't already there.
    
    pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(>=|>)\s*([0-9]+\.[0-9]+|[0-9]+)\b'
    
    def repl(m):
        var_name = m.group(1)
        op = m.group(2)
        val = m.group(3)
        
        # Don't touch variables that are obviously not odds
        if var_name in ['len', 'cls', 'self', 'i', 'j', 'idx', 'odds', 'code', 'category', 'index']:
            return m.group(0)
            
        # Avoid redundancy if '!= 99.0' is already in the line for this variable
        if f"{var_name} != 99.0" in line:
            return m.group(0)
            
        return f"{var_name} != 99.0 and {var_name} {op} {val}"
        
    new_line = re.sub(pattern, repl, line)
    return new_line

new_lines = []
changes = 0
for i, line in enumerate(lines):
    new_l = patch_line(line)
    if new_l != line:
        print(f"Line {i+1}:")
        print(f" - {line.strip()}")
        print(f" + {new_l.strip()}")
        changes += 1
    new_lines.append(new_l)

print(f"\nTotal lines changed: {changes}")

if changes > 0:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("rule_engine.py successfully patched!")
