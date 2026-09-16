import json
import codecs

with codecs.open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', 'utf8') as f:
    matches = json.load(f)['matches']

for i in range(-456, -500, -1):
    m = matches[i]
    odds = m.get("oranlar", {})
    ms1 = odds.get('Maç Sonucu_1')
    if ms1 is not None and str(ms1) != "99.0":
        print(f"FOUND MATCH WITH ODDS AT INDEX {i}: {m.get('takimlar')}")
        break
