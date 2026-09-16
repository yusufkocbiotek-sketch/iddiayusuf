import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

print('\n=== TARIHSEL TARAMA (MS2 <= 1.55 & MS1 >= 4.5 & IY1 != 99) ===')
found = []
for mac in matches:
    od = mac.get('oranlar', {})
    _ms2 = od.get('Maç Sonucu_2', 99)
    _ms1 = od.get('Maç Sonucu_1', 99)
    _iy1 = od.get('İlk Yarı Sonucu_1', 99)
    _sev = mac.get('skor_ev', -1)
    _sdep = mac.get('skor_dep', -1)
    
    if 1.40 <= _ms2 <= 1.55 and _ms1 >= 4.5 and _iy1 != 99 and _sev >= 0:
        found.append({
            'ms1': _ms1, 'ms2': _ms2, 'iy1': _iy1, 'fark': _iy1 - _ms1,
            'skor': f"{_sev}-{_sdep}", 'ev_kazandi': _sev > _sdep, 'idx': mac.get('index', '?')
        })

print(f"Toplam mac: {len(found)}")
ev_kazananlar = [x for x in found if x['ev_kazandi']]
dep_kazananlar = [x for x in found if not x['ev_kazandi'] and x['skor'].split('-')[0] < x['skor'].split('-')[1]]
beraber = [x for x in found if x['skor'].split('-')[0] == x['skor'].split('-')[1]]

print(f"Ev kazanan: {len(ev_kazananlar)} ({(len(ev_kazananlar)/len(found))*100:.1f}%)")
print(f"Dep kazanan: {len(dep_kazananlar)} ({(len(dep_kazananlar)/len(found))*100:.1f}%)")
print(f"Beraberlik: {len(beraber)} ({(len(beraber)/len(found))*100:.1f}%)")

print("\nEv kazananlardan Ornekler:")
for x in ev_kazananlar[:10]:
    print(f" #{x['idx']} MS1:{x['ms1']} IY1:{x['iy1']} (Fark:{x['fark']:.2f}) Skor:{x['skor']}")

print("\nDep Kazananlardan Ornekler:")
for x in dep_kazananlar[:10]:
    print(f" #{x['idx']} MS1:{x['ms1']} IY1:{x['iy1']} (Fark:{x['fark']:.2f}) Skor:{x['skor']}")
