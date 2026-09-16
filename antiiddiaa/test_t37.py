import json
import codecs

with codecs.open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', 'utf8') as f:
    matches = json.load(f)['matches']

count = 0
over_25 = 0
over_35 = 0

for m in matches:
    o = m.get('oranlar', {})
    ms1 = o.get('Maç Sonucu_1')
    ms2 = o.get('Maç Sonucu_2')
    alt25 = o.get('Alt/Üst 2.5_Alt')
    cs_12 = o.get('Çifte Şans_12', o.get('Çifte Şans_1 ve 2', o.get('Çifte Şans_1-2')))
    
    if ms1 and ms2 and alt25 and cs_12:
        if abs(ms1 - ms2) <= 0.30 and alt25 <= 1.65 and cs_12 <= 1.18:
            ev = m.get('skor_ev')
            dep = m.get('skor_dep')
            if ev != '?' and dep != '?':
                count += 1
                e = int(ev)
                d = int(dep)
                if (e+d) > 2: over_25 += 1
                if (e+d) > 3: over_35 += 1
                
print(f'Total matches: {count}')
print(f'Over 2.5: {over_25} | Over 3.5: {over_35}')
