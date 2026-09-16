import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

total = len(matches)

for idx in [571, 574]:
    m = matches[total - idx]
    print('='*70)
    print('IDX:', -idx, '|', m.get('ev_sahibi'), 'vs', m.get('deplasman'))
    print('Tarih:', m.get('tarih'))
    print('Gercek: IY', str(m.get('skor_1y_ev'))+'-'+str(m.get('skor_1y_dep')),
          '| MS', str(m.get('skor_ev'))+'-'+str(m.get('skor_dep')))
    print()
    print('--- ORANLAR ---')
    for k, v in sorted(m.get('oranlar', {}).items()):
        print('  ' + k + ' = ' + str(v))
    print()
    print('--- STORY ---')
    print(generate_story(m))
    print()
