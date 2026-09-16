import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

total = len(matches)

# Hatali maclar: -563 (2-1) ve -566 (2-1)
# Profil: KGYok favori (~1.37), KGVar yuksek (~2.16), 2.5 Alt yok
# Ama sonuc: Gol oldu (2-1)
# Kontrol: Tam oran tablolarini goster

for idx in [563, 566, 560, 565]:
    m = matches[total - idx]
    print('='*70)
    print('IDX:', -idx, '|', m.get('ev_sahibi'), 'vs', m.get('deplasman'))
    print('Tarih:', m.get('tarih'), '| Skor:', m.get('skor_ev'), '-', m.get('skor_dep'),
          '| IY:', m.get('skor_1y_ev'), '-', m.get('skor_1y_dep'))
    print()
    odds = m.get('oranlar', {})
    for k, v in sorted(odds.items()):
        print('  ' + k + ' = ' + str(v))
    print()
