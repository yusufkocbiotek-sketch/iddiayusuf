import re
with open(r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all class Rule15... definitions
matches = set(re.findall(r'(class Rule15\d\d\(BaseRule\):.*?return False, "")', text, re.DOTALL))

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\all_rules_dump.txt', 'w', encoding='utf-8') as out:
    for m in matches:
        out.write(m + "\n\n")

print(f"Extracted {len(matches)} rules.")
