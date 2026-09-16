import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

total = len(matches)

for i in range(578, 588):
    m = matches[total - i]
    odds = m.get('oranlar', {})
    ms1 = odds.get('Maç Sonucu_1', 99)
    ms0 = odds.get('Maç Sonucu_0', 99)
    ms2 = odds.get('Maç Sonucu_2', 99)
    alt25 = odds.get('Alt/Üst 2.5_Alt', 99)
    ust25 = odds.get('Alt/Üst 2.5_Üst', 99)
    kg_var = odds.get('Karşılıklı Gol_Var', 99)
    kg_yok = odds.get('Karşılıklı Gol_Yok', 99)
    story = generate_story(m)
    kural = ''
    for line in story.split('\n'):
        if 'Kural Sırası' in line or 'TUZAK YOK' in line:
            kural = line.strip()
            break

    print('IDX:', -i, '|', m.get('ev_sahibi'), 'vs', m.get('deplasman'), '|', m.get('tarih'))
    print('  MS:', ms1, '/', ms0, '/', ms2, '| 2.5:', alt25, '/', ust25, '| KG:', kg_var, '/', kg_yok)
    print('  KURAL:', kural)
    print('  GERCEK: IY', str(m.get('skor_1y_ev'))+'-'+str(m.get('skor_1y_dep')),
          '| MS', str(m.get('skor_ev'))+'-'+str(m.get('skor_dep')))
    print('-'*65)
