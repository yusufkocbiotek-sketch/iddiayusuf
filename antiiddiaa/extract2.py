import json

out = open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\recovered_rules.py', 'w', encoding='utf-8')

with open(r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if 'class Rule15' in line and 'ReplacementContent' in line:
            try:
                data = json.loads(line)
                for tc in data.get('tool_calls', []):
                    args = tc.get('arguments', {})
                    if 'ReplacementChunks' in args:
                        for chunk in args['ReplacementChunks']:
                            if 'ReplacementContent' in chunk:
                                text = chunk['ReplacementContent']
                                if 'class Rule15' in text:
                                    out.write(text + "\n")
            except: pass
        if 'class Rule15' in line and 'CodeContent' in line:
            try:
                data = json.loads(line)
                for tc in data.get('tool_calls', []):
                    args = tc.get('arguments', {})
                    if 'CodeContent' in args:
                        text = args['CodeContent']
                        if 'class Rule15' in text:
                            out.write(text + "\n")
            except: pass

out.close()
print("Done extracting rules by json parsing.")
