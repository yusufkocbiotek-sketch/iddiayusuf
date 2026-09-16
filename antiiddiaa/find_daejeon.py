import json
import codecs

with codecs.open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', 'utf8') as f:
    matches = json.load(f)['matches']

count = 0
for m in reversed(matches):
    ev = m.get('ev_sahibi', '')
    if ev and 'Daejeon' in ev:
        print(f"Match: {ev} - {m.get('deplasman')} (Index: -{len(matches)-matches.index(m)})")
        for k, v in m.get('oranlar', {}).items():
            if 'Maç Sonucu' in k or '3.5' in k:
                print(f"{k}: {v}")
        count += 1
        if count >= 3:
            break
