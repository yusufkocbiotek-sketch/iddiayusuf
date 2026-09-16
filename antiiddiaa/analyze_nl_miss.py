import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

# Holland vs Sweden oranları: MS1=1.48, 2.5Alt=1.69, 2.5Ust=1.76, KGYok=1.66, KGVar=1.79
# Profil: Güçlü ev favorisi (MS1 <= 1.55), dengeli 2.5 piyasa (fark < 0.15), KGYok hafif favori
# Skor 5-1 oldu → 3.5 Üst, KG Var, tamamen tersi!

# Benzer profil: MS1 <= 1.55, dengeli 2.5 market, KGYok biraz favori
found = []
for m in matches:
    odds = m.get('oranlar', {})
    ms1 = odds.get('Mac Sonucu_1') or odds.get('Maç Sonucu_1', 99)
    alt25 = odds.get('Alt/Ust 2.5_Alt') or odds.get('Alt/Üst 2.5_Alt', 99)
    ust25 = odds.get('Alt/Ust 2.5_Ust') or odds.get('Alt/Üst 2.5_Üst', 99)
    kg_var = odds.get('Karsılikli Gol_Var') or odds.get('Karşılıklı Gol_Var', 99)
    kg_yok = odds.get('Karsılikli Gol_Yok') or odds.get('Karşılıklı Gol_Yok', 99)
    skor_ev = m.get('skor_ev', -1)
    skor_dep = m.get('skor_dep', -1)

    if ms1 <= 1.55 and 1.55 <= alt25 <= 1.85 and 1.60 <= ust25 <= 1.90 and kg_yok < kg_var and skor_ev >= 0:
        total_goals = skor_ev + skor_dep
        found.append({
            'idx': m.get('index', '?'),
            'ev': m.get('ev_sahibi', '?'),
            'dep': m.get('deplasman', '?'),
            'ms1': ms1,
            'alt25': alt25,
            'ust25': ust25,
            'kg_var': kg_var,
            'kg_yok': kg_yok,
            'skor': str(skor_ev) + '-' + str(skor_dep),
            'total': total_goals
        })

print('Benzer profil mac sayisi:', len(found))
over = [x for x in found if x['total'] > 2]
under = [x for x in found if x['total'] <= 2]
print('3+ gol (UST) olan:', len(over))
print('0-2 gol (ALT) olan:', len(under))

if over:
    print()
    print('--- 3+ GOL OLAN MACLAR ---')
    for x in over[:20]:
        line = '  #' + str(x['idx']) + ' ' + x['ev'] + ' vs ' + x['dep']
        line += ' | MS1=' + str(x['ms1'])
        line += ' | 2.5Alt=' + str(x['alt25']) + ' Ust=' + str(x['ust25'])
        line += ' | KGYok=' + str(x['kg_yok']) + ' KGVar=' + str(x['kg_var'])
        line += ' | Skor=' + x['skor']
        print(line)

if under:
    print()
    print('--- 0-2 GOL OLAN MACLAR ---')
    for x in under[:10]:
        line = '  #' + str(x['idx']) + ' ' + x['ev'] + ' vs ' + x['dep']
        line += ' | MS1=' + str(x['ms1'])
        line += ' | 2.5Alt=' + str(x['alt25']) + ' Ust=' + str(x['ust25'])
        line += ' | KGYok=' + str(x['kg_yok']) + ' KGVar=' + str(x['kg_var'])
        line += ' | Skor=' + x['skor']
        print(line)

# Hollanda maçına özel analiz: 2.5 farkı ne?
diff = 1.76 - 1.69
print()
print('=== HOLLANDA OZEL ANALIZI ===')
print('2.5 Alt/Ust farki:', round(diff, 3), '(denge < 0.10 oldugunda ULTRA DENGELI)')
print('KG Yok:', 1.66, ' KG Var:', 1.79, ' Fark:', round(1.79-1.66, 3))
print('1.5 Ust orani:', 1.18, '→ Zaten 1.5 Ust bekleniyor!')
print('MS1:', 1.48, '→ Cok guclu ev favorisi')
print()
print('KURAL HATASI: Dengeli 2.5 piyasasi + Guclu ev favorisi = FARK ATACAK SENARYO')
print('KGYok hafif favori olsa da, guclu ev favorisi + MS1 < 1.50 = EV FARK ATAR')
print('Bu profilde 2.5 USTU daha olasi cunku ev cok guclu ve fark atacak!')
