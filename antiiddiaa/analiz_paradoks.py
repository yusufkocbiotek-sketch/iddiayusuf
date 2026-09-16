import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

print('\n=== PARADOKS TARAMASI (2.5 ALT FAVORI AMA MS2+ÜST DAHA DÜŞÜK) ===')
found = []
for mac in matches:
    od = mac.get('oranlar', {})
    alt25 = od.get('Alt/Üst 2.5_Alt', 99)
    ust25 = od.get('Alt/Üst 2.5_Üst', 99)
    ms2_alt = od.get('Maç Sonucu ve Alt/Üst 2.5_2 ve Alt', 99)
    ms2_ust = od.get('Maç Sonucu ve Alt/Üst 2.5_2 ve Üst', 99)
    ms2 = od.get('Maç Sonucu_2', 99)
    sev = mac.get('skor_ev', -1)
    sdep = mac.get('skor_dep', -1)
    
    # 2.5 Alt favori (<= 1.70) AMA MS2+Üst < MS2+Alt
    if alt25 <= 1.70 and alt25 < ust25 and ms2_ust < ms2_alt and ms2_ust != 99 and ms2 <= 1.70 and sev >= 0:
        found.append({
            'ms2': ms2, 'alt25': alt25, 'ust25': ust25,
            'ms2_alt': ms2_alt, 'ms2_ust': ms2_ust,
            'skor': f"{sev}-{sdep}", 'ev_kazandi': sev > sdep, 'beraber': sev == sdep,
            'idx': mac.get('index', '?'),
            'ev': mac.get('ev_sahibi', '?'),
            'dep': mac.get('deplasman', '?')
        })

print(f"Toplam mac: {len(found)}")
ev_kazananlar = [x for x in found if x['ev_kazandi']]
beraberler = [x for x in found if x['beraber']]
dep_kazananlar = [x for x in found if not x['ev_kazandi'] and not x['beraber']]

print(f"Ev kazanan (Sürpriz 1): {len(ev_kazananlar)} ({(len(ev_kazananlar)/len(found))*100:.1f}%)")
print(f"Beraberlik (Sürpriz X): {len(beraberler)} ({(len(beraberler)/len(found))*100:.1f}%)")
print(f"Dep kazanan (Normal): {len(dep_kazananlar)} ({(len(dep_kazananlar)/len(found))*100:.1f}%)")
print(f"1X Çifte Şans Toplam: {len(ev_kazananlar) + len(beraberler)} ({((len(ev_kazananlar)+len(beraberler))/len(found))*100:.1f}%)")

print("\n1X Biten Maçlar:")
for x in ev_kazananlar + beraberler:
    print(f" #{x['idx']} {x['ev']} vs {x['dep']} | MS2:{x['ms2']} Alt:{x['alt25']} MS2+Alt:{x['ms2_alt']} MS2+Ust:{x['ms2_ust']} Skor:{x['skor']}")
