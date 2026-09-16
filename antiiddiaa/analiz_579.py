import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

total = len(matches)
m = matches[total - 579]
o = m.get('oranlar', {})

print('='*70)
print('IDX: -579 | Tromsdalen vs STOR/BLINK')
print('Tarih:', m.get('tarih'))
print('Gercek: IY', str(m.get('skor_1y_ev'))+'-'+str(m.get('skor_1y_dep')),
      '| MS', str(m.get('skor_ev'))+'-'+str(m.get('skor_dep')))
print()
print('--- TUM ORANLAR ---')
for k, v in sorted(o.items()):
    print('  ' + k + ' = ' + str(v))
print()

# Kritik oranları al
ms1 = o.get('Maç Sonucu_1', 99)
ms0 = o.get('Maç Sonucu_0', 99)
ms2 = o.get('Maç Sonucu_2', 99)
kg_var = o.get('Karşılıklı Gol_Var', 99)
kg_yok = o.get('Karşılıklı Gol_Yok', 99)
alt25 = o.get('Alt/Üst 2.5_Alt', 99)
ust25 = o.get('Alt/Üst 2.5_Üst', 99)
alt35 = o.get('Alt/Üst 3.5_Alt', 99)
ust35 = o.get('Alt/Üst 3.5_Üst', 99)
iy_kg_var = o.get('İlk Yarı Karşılıklı Gol_Var', 99)
iy_kg_yok = o.get('İlk Yarı Karşılıklı Gol_Yok', 99)
iy2_kg_var = o.get('İkinci Yarı Karşılıklı Gol_Var', 99)
iy_05_ust = o.get('İlk Yarı Alt/Üst 0.5_Üst', 99)
iy_15_ust = o.get('İlk Yarı Alt/Üst 1.5_Üst', 99)
ev_15_alt = o.get('Ev Sahibi Alt/Üst 1.5_Alt', 99)
dep_15_ust = o.get('Deplasman Alt/Üst 1.5_Üst', 99)
dep_25_ust = o.get('Deplasman Alt/Üst 2.5_Üst', 99)
h1 = o.get('Handikaplı Maç Sonucu 0:1_1', 99)
h2 = o.get('Handikaplı Maç Sonucu 0:1_2', 99)
x1 = o.get('Çifte Şans_1 ve 0', o.get('Çifte Şans_1X', 99))
x2 = o.get('Çifte Şans_0 ve 2', o.get('Çifte Şans_X2', 99))

print('--- KRİTİK SINYALLER ---')
print('MS: Ev=%s Ber=%s Dep=%s' % (ms1, ms0, ms2))
print('KG: Var=%s Yok=%s' % (kg_var, kg_yok))
print('2.5: Alt=%s Ust=%s' % (alt25, ust25))
print('3.5: Alt=%s Ust=%s' % (alt35, ust35))
print('IY KG: Var=%s Yok=%s' % (iy_kg_var, iy_kg_yok))
print('IY 0.5Ust=%s IY 1.5Ust=%s' % (iy_05_ust, iy_15_ust))
print('EvSahibi 1.5Alt=%s' % ev_15_alt)
print('Dep 1.5Ust=%s Dep 2.5Ust=%s' % (dep_15_ust, dep_25_ust))
print('Handikap_Ev(0:1)=%s Handikap_Dep(0:1)=%s' % (h1, h2))
print('CS_X1=%s CS_X2=%s' % (x1, x2))
print()

print('--- ANALIZ ---')
print('1) Ev MS1=1.44 → Ev FAVORI ama...')
print('2) Dep 1.5 Ust=%s → Dep 2+ gol atar!' % dep_15_ust)
print('3) Dep 2.5 Ust=%s → Dep 3+ gol atar!' % dep_25_ust)
print('4) IY KG Var=%s → IY karşılıklı gol bekleniyor' % iy_kg_var)
print('5) KG Var=%s (düşük) → Maç gollü' % kg_var)
print()
print('SONUC: Ev 1.44 favori AMA dep 1.5 Ust (%.2f) ve dep 2.5 Ust (%.2f)' % (dep_15_ust, dep_25_ust))
print('       Bu dep sahte favori degil, GERCEK GOL MAKİNESİ!')
print('       Yani: Ev favori = SAHTE! Dep golde üstün!')
print()

# İstatistik tarama: MS1 <= 1.50 + Dep 2.5 Üst <= 1.85
print('=== İSTATİSTİK TARAMA ===')
print('MS1<=1.50 (Ev favori) AMA Dep 2.5 Ust<=1.85 (Dep 3+ gol atar) maçları:')
found = []
for mac in matches:
    od = mac.get('oranlar', {})
    _ms1 = od.get('Maç Sonucu_1', 99)
    _ms2 = od.get('Maç Sonucu_2', 99)
    _dep25u = od.get('Deplasman Alt/Üst 2.5_Üst', 99)
    _dep15u = od.get('Deplasman Alt/Üst 1.5_Üst', 99)
    _sev = mac.get('skor_ev', -1)
    _sdep = mac.get('skor_dep', -1)
    if _ms1 <= 1.50 and _ms1 != 99 and _dep25u <= 1.90 and _dep25u != 99 and _sev >= 0:
        found.append({
            'ms1': _ms1, 'ms2': _ms2, 'dep25u': _dep25u, 'dep15u': _dep15u,
            'sev': _sev, 'sdep': _sdep, 'skor': str(_sev)+'-'+str(_sdep),
            'ev': mac.get('ev_sahibi','?'), 'dep': mac.get('deplasman','?'), 'idx': mac.get('index','?')
        })

dep_kazandi = [x for x in found if x['sdep'] > x['sev']]
ev_kazandi = [x for x in found if x['sev'] > x['sdep']]
berab = [x for x in found if x['sev'] == x['sdep']]
print('Toplam:', len(found))
print('Ev kazandı:', len(ev_kazandi), '%.1f%%' % (100*len(ev_kazandi)/len(found) if found else 0))
print('Dep kazandı:', len(dep_kazandi), '%.1f%%' % (100*len(dep_kazandi)/len(found) if found else 0))
print('Beraberlik:', len(berab), '%.1f%%' % (100*len(berab)/len(found) if found else 0))
print()
print('--- Dep kazandığı maçlar (MS1<=1.50 ama dep galip):---')
for x in dep_kazandi[:12]:
    print('  #%s %s vs %s | MS1=%.2f MS2=%.2f Dep2.5U=%.2f → %s' %
          (x['idx'], x['ev'], x['dep'], x['ms1'], x['ms2'], x['dep25u'], x['skor']))
