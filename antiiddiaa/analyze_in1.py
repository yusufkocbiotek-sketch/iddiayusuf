import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']
    
target_matches = []
for m in matches:
    if m.get('lig', '').strip() == 'İN 1':
        o = m.get('oranlar', {})
        ms1 = o.get('Maç Sonucu_1', 99)
        alt = o.get('Alt/Üst 2.5_Alt', 99)
        ust = o.get('Alt/Üst 2.5_Üst', 0)
        
        # Check rule IN1-14 conditions
        if 1.30 <= ms1 <= 1.50 and alt < ust:
            target_matches.append(m)

print(f"Toplam IN1-14 maci: {len(target_matches)}")
for m in target_matches:
    print(f"{m['ev_sahibi']} - {m['deplasman']} | IY: {m.get('skor_1y_ev')}-{m.get('skor_1y_dep')} | MS: {m.get('skor_ev')}-{m.get('skor_dep')}")
