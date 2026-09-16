import json, os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = r'C:\Users\YUSUF\Desktop\antiiddiaa'
with open(os.path.join(SRC, 'veri_seti.json'), encoding='utf-8') as f:
    DATA = json.load(f)

# Kural mesajlarindan tahmini cikarmak icin kural -> test fonksiyonu.
# Test, macin sonucuna gore kuralin tahmininin dogru olup olmadigini doner (True/False/None)

def result(ev, dep):
    """(skor_ev, skor_dep) -> 1/0/2, kg_var, ust25, iy0"""
    ms = 1 if ev > dep else (0 if ev == dep else 2)
    kg = ev > 0 and dep > 0
    ust25 = ev + dep > 2
    return ms, kg, ust25

# Kural -> tahmin tespit regex veya ozel fonksiyon
RULE_TESTS = {
    'G1': lambda ev, dep, iy: ev + dep >= 2,
    'G2': lambda ev, dep, iy: 2 <= ev + dep <= 3,
    'G3': lambda ev, dep, iy: ev > 0 and dep > 0,
    'G4': lambda ev, dep, iy: dep == 0,
    'G5': lambda ev, dep, iy: ev + dep <= 2,
    'G6': lambda ev, dep, iy: ev > 0 and dep == 0 and ev >= 2,
    'G7': lambda ev, dep, iy: ev + dep >= 4,
    'G8': lambda ev, dep, iy: dep == 0,
    'G9': lambda ev, dep, iy: iy == (0, 0) and ev == dep and ev > 0,
    'G10': lambda ev, dep, iy: ev + dep <= 2,
    'G11': lambda ev, dep, iy: ev > 0 and dep > 0,
    'G12': lambda ev, dep, iy: ev + dep >= 3,
    'Y1': lambda ev, dep, iy: iy == (0, 0),
    'Y2': lambda ev, dep, iy: iy == (0, 0) and (ev > 0 or dep > 0),
    'Y3': lambda ev, dep, iy: iy != (0, 0) and iy[0] != iy[1],
    'Y4': lambda ev, dep, iy: sum(iy) <= 1,
    'Y5': lambda ev, dep, iy: sum(iy) == 1 and (ev > 0 or dep > 0) and ev + dep <= 2,
    'Y6': lambda ev, dep, iy: sum(iy) <= 1 and (ev > 0 or dep > 0),
    'Y7': lambda ev, dep, iy: sum(iy) <= 1 and ev + dep <= 2,
    'Y8': lambda ev, dep, iy: iy[0] > 0 and iy[1] > 0,
    'Y9': lambda ev, dep, iy: iy[0] > 0 and iy[1] > 0,
    'Y10': lambda ev, dep, iy: iy[0] > 0 and iy[1] > 0 and ev > 0 and dep > 0,
    'Y11': lambda ev, dep, iy: iy == (0, 0),
    'T6': lambda ev, dep, iy: dep > ev,
    'T7': lambda ev, dep, iy: dep <= ev,
    'T8': lambda ev, dep, iy: ev > dep,
    'T8-B': lambda ev, dep, iy: dep > ev,
    'T9': lambda ev, dep, iy: ev == dep,
    'T10': lambda ev, dep, iy: ev == dep,
    'T11': lambda ev, dep, iy: dep > ev,
    'T18': lambda ev, dep, iy: ev + dep == 1,
    'T19': lambda ev, dep, iy: ev == 0 and dep == 0,
    'T20': lambda ev, dep, iy: dep == 2 and ev == 0,
    'T21': lambda ev, dep, iy: dep >= 2 and ev == 0,
    'T22': lambda ev, dep, iy: ev >= 3 and dep <= 1,
    'T27': lambda ev, dep, iy: ev > dep and ev + dep <= 2,
    'T28': lambda ev, dep, iy: dep > ev and ev + dep <= 2,
    'T30': lambda ev, dep, iy: dep > ev and ev + dep <= 2,
    'T31': lambda ev, dep, iy: ev + dep >= 3 and ev > 0 and dep > 0,
    'T32': lambda ev, dep, iy: ev == dep,
    'T33': lambda ev, dep, iy: dep == 0 or ev == 0,
    'T34': lambda ev, dep, iy: ev == dep,
    'T35': lambda ev, dep, iy: ev == dep,
    'T36': lambda ev, dep, iy: dep >= ev or ev == 0,
    'T68': lambda ev, dep, iy: ev == dep or (ev > 0 and dep > 0),
    'T70': lambda ev, dep, iy: ev <= dep,
    'S2': lambda ev, dep, iy: ev + dep >= 3,
    '1466': lambda ev, dep, iy: ev >= dep,
    '1467': lambda ev, dep, iy: ev == dep,
    '1469': lambda ev, dep, iy: ev == dep,
    '1474': lambda ev, dep, iy: ev + dep >= 3,
    '1475': lambda ev, dep, iy: ev + dep >= 4,
    '1477': lambda ev, dep, iy: ev + dep <= 3 and dep > 0,
    '1478': lambda ev, dep, iy: ev + dep >= 4,
    '1482': lambda ev, dep, iy: ev + dep <= 2,
    '1483': lambda ev, dep, iy: ev == dep,
    '1486': lambda ev, dep, iy: ev + dep <= 2,
    '1487': lambda ev, dep, iy: ev >= 2,
    '1491': lambda ev, dep, iy: ev + dep >= 3,
    '1558': lambda ev, dep, iy: ev + dep <= 2,
}

stats = {}
for m in DATA:
    ev, dep = m['skor']
    iy = m['iy'] or (0, 0)
    for rule in m['kurallar']:
        base = rule.split('_')[0].strip()
        if base == 'TUZAK' or base == '':
            continue
        if base not in RULE_TESTS:
            if base not in stats:
                stats[base] = {'n': 0}
            stats[base]['n'] += 1
            continue
        test = RULE_TESTS[base]
        try:
            ok = test(ev, dep, iy)
        except Exception:
            ok = None
        s = stats.setdefault(base, {'n': 0, 'hit': 0})
        s['n'] += 1
        if ok:
            s['hit'] += 1

print('KURAL  |  N  |  ISABET  |  %')
print('------+-----+----------+-----')
rows = []
for k, v in stats.items():
    n = v.get('n', 0)
    hit = v.get('hit', 0)
    pct = round(100 * hit / n, 1) if n else 0
    rows.append((pct, k, n, hit))
rows.sort(reverse=True)
for pct, k, n, hit in rows:
    mark = '  <-- KURAL YOK/BOYUT' if k not in RULE_TESTS else ''
    print(f'{k:6} | {n:3} | {hit:5} | {pct:5.1f}%{mark}')
