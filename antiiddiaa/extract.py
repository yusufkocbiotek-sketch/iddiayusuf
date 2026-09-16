import json
with open(r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if 'class Rule1552' in line:
            try:
                data = json.loads(line)
                print('type:', data.get('type'))
                if data.get('type') == 'PLANNER_RESPONSE':
                    for tc in data.get('tool_calls', []):
                        args = tc.get('arguments', {})
                        if 'ReplacementContent' in args and 'class Rule1552' in args['ReplacementContent']:
                            with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\recovered_rules.py', 'w', encoding='utf-8') as out:
                                out.write(args['ReplacementContent'])
                            print("Saved from ReplacementContent")
                        elif 'CodeContent' in args and 'class Rule1552' in args['CodeContent']:
                            with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\recovered_rules.py', 'w', encoding='utf-8') as out:
                                out.write(args['CodeContent'])
                            print("Saved from CodeContent")
                        elif 'ReplacementChunks' in args:
                            for chunk in args['ReplacementChunks']:
                                if 'ReplacementContent' in chunk and 'class Rule1552' in chunk['ReplacementContent']:
                                    with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\recovered_rules.py', 'w', encoding='utf-8') as out:
                                        out.write(chunk['ReplacementContent'])
                                    print("Saved from ReplacementChunks")
            except Exception as e:
                print('Error:', e)
