import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

total = len(matches)
m = matches[total - 590]
o = m.get('oranlar', {})

print('='*70)
print('IDX: -590 | Güney Afrika vs Güney Kore')
print('Gercek: IY', str(m.get('skor_1y_ev'))+'-'+str(m.get('skor_1y_dep')),
      '| MS', str(m.get('skor_ev'))+'-'+str(m.get('skor_dep')))
print()
print('--- TUM ORANLAR ---')
for k, v in sorted(o.items()):
    print('  ' + k + ' = ' + str(v))
print()

# Anomalileri tarama
print('--- ANOMALI KONTROLU ---')

ms1 = o.get('Maç Sonucu_1', 99)
ms2 = o.get('Maç Sonucu_2', 99)
iy_ms1 = o.get('İlk Yarı Sonucu_1', 99)
iy_ms2 = o.get('İlk Yarı Sonucu_2', 99)
kg_yok = o.get('Karşılıklı Gol_Yok', 99)
kg_var = o.get('Karşılıklı Gol_Var', 99)
ev_05u = o.get('Ev Sahibi Alt/Üst 0.5_Üst', 99)
dep_05u = o.get('Deplasman Alt/Üst 0.5_Üst', 99)
dep_15u = o.get('Deplasman Alt/Üst 1.5_Üst', 99)
iy_05_alt = o.get('İlk Yarı Alt/Üst 0.5_Alt', 99)

print('MS1=', ms1, '| IY MS1=', iy_ms1, '| FARK:', iy_ms1 - ms1)
print('MS2=', ms2, '| IY MS2=', iy_ms2, '| FARK:', iy_ms2 - ms2)
print('Ev 0.5 Ust=', ev_05u)
print('Dep 0.5 Ust=', dep_05u)
print('Dep 1.5 Ust=', dep_15u)

# Tarihsel veride IY MS1 vs MS1 darbe oranları
print('\n=== TARIHSEL TARAMA (MS2 <= 1.55 & Ev MS1 <= 5.5) ===')
found = []
for mac in matches:
    od = mac.get('oranlar', {})
    _ms2 = od.get('Maç Sonucu_2', 99)
    _ms1 = od.get('Maç Sonucu_1', 99)
    _iy1 = od.get('İlk Yarı Sonucu_1', 99)
    _ev05 = od.get('Ev Sahibi Alt/Üst 0.5_Üst', 99)
    _dep15 = od.get('Deplasman Alt/Üst 1.5_Üst', 99)
    _sev = mac.get('skor_ev', -1)
    _sdep = mac.get('skor_dep', -1)
    
    if 1.40 <= _ms2 <= 1.55 and _ms1 >= 4.5 and _sev >= 0:
        found.append({
            'ms1': _ms1, 'ms2': _ms2, 'iy1': _iy1, 'ev05': _ev05, 'dep15': _dep15,
            'skor': f"{_sev}-{_sdep}", 'ev_kazandi': _sev > _sdep, 'idx': mac.get('index', '?')
        })

print(f"Toplam bu profildeki mac: {len(found)}")
ev_kazananlar = [x for x in found if x['ev_kazandi']]
print(f"Ev kazanan: {len(ev_kazananlar)} ({(len(ev_kazananlar)/len(found))*100:.1f}%)")

print("\nEv kazanan maclarin ortalama detaylari:")
for x in ev_kazananlar[:15]:
    print(f" #{x['idx']} MS1:{x['ms1']} IY1:{x['iy1']} (Fark:{x['iy1']-x['ms1']:.2f}) Ev05U:{x['ev05']} Dep15U:{x['dep15']} Skor:{x['skor']}")

print("\nDep Kazananlardan Ornekler (Fark gostermek icin):")
dep_kazananlar = [x for x in found if not x['ev_kazandi']]
for x in dep_kazananlar[:5]:
    print(f" #{x['idx']} MS1:{x['ms1']} IY1:{x['iy1']} (Fark:{x['iy1']-x['ms1']:.2f}) Ev05U:{x['ev05']} Dep15U:{x['dep15']} Skor:{x['skor']}")
