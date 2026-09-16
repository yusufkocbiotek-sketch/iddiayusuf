import json
import codecs
from rule_engine import Rule2001, CURRENT_MATCH
import sys
import rule_engine

with codecs.open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', 'utf8') as f:
    matches = json.load(f)['matches']

match = matches[-430]
rule_engine.CURRENT_MATCH = match
print("MATCH IS MILLI MAC?", rule_engine.is_milli_mac(match))
res, text = Rule2001.evaluate(match.get('oranlar', {}))
print("Rule2001 RESULT:", res)
