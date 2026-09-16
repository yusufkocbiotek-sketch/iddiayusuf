import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

total = len(matches)

# -558'den -567'ye kadar 10 mac
results = []
for i in range(558, 568):
    m = matches[total - i]
    idx = -i
    ev = m.get('ev_sahibi', '?')
    dep = m.get('deplasman', '?')
    tarih = m.get('tarih', '?')
    skor_ev = m.get('skor_ev', '?')
    skor_dep = m.get('skor_dep', '?')
    skor_1y_ev = m.get('skor_1y_ev', '?')
    skor_1y_dep = m.get('skor_1y_dep', '?')
    odds = m.get('oranlar', {})

    ms1 = odds.get('Maç Sonucu_1', 99)
    ms0 = odds.get('Maç Sonucu_0', 99)
    ms2 = odds.get('Maç Sonucu_2', 99)
    alt25 = odds.get('Alt/Üst 2.5_Alt', 99)
    ust25 = odds.get('Alt/Üst 2.5_Üst', 99)
    kg_var = odds.get('Karşılıklı Gol_Var', 99)
    kg_yok = odds.get('Karşılıklı Gol_Yok', 99)

    story = generate_story(m)
    # Kural satirini al
    kural_satiri = ''
    for line in story.split('\n'):
        if 'Kural Sırası' in line or 'TUZAK YOK' in line:
            kural_satiri = line.strip()
            break

    results.append({
        'idx': idx,
        'ev': ev,
        'dep': dep,
        'tarih': tarih,
        'skor': str(skor_ev)+'-'+str(skor_dep),
        'iy': str(skor_1y_ev)+'-'+str(skor_1y_dep),
        'ms1': ms1, 'ms0': ms0, 'ms2': ms2,
        'alt25': alt25, 'ust25': ust25,
        'kg_var': kg_var, 'kg_yok': kg_yok,
        'kural': kural_satiri,
        'story': story
    })

# Ozet tablosu yaz
print('='*80)
print('ANALIZ OZETI - Index -558 den -567 ye')
print('='*80)
for r in results:
    print()
    print('IDX:', r['idx'], '|', r['ev'], 'vs', r['dep'], '|', r['tarih'])
    print('  MS: Ev', r['ms1'], '| Ber', r['ms0'], '| Dep', r['ms2'])
    print('  2.5 Alt:', r['alt25'], '| Ust:', r['ust25'], '| KGVar:', r['kg_var'], '| KGYok:', r['kg_yok'])
    print('  KURAL:', r['kural'])
    print('  GERCEK: IY', r['iy'], '| MS', r['skor'])
    print('-'*60)
