import re

def get_missing_rules():
    with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf8') as f:
        engine = f.read()
        all_codes = set(re.findall(r'code\s*=\s*[\'"](.*?)[\'"]', engine))
        
    with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', encoding='utf8') as f:
        analyzer = f.read()
        dict_match = re.search(r'predictions = \{(.*?)\}', analyzer, re.DOTALL)
        dict_str = dict_match.group(1) if dict_match else ''
        defined_codes = set(re.findall(r'\'(.*?)\':', dict_str))

    missing = all_codes - defined_codes
    
    for rule in missing:
        match = re.search(r'class Rule' + rule + r'.*?name = [\'"](.*?)[\'"]', engine, re.DOTALL)
        name = match.group(1) if match else "Unknown"
        print(f"'{rule}': ('{name}', '???'),")

get_missing_rules()
