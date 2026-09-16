import re, json, glob, os

SRC = r'C:\Users\YUSUF\Desktop\antiiddiaa'
FILES = [
    'batch_253_260.md', 'batch_261_263.md', 'batch_264_268.md', 'batch_269_273.md',
    'temp_out_utf8.txt', 'temp_out_utf8_2.txt', 'temp_out_utf8_228_232.txt',
    'block13_output_utf8.txt', 'block14_output_utf8.txt',
]

def parse_odds(lines):
    odds = {}
    for ln in lines:
        m = re.search(r'^\s*-\s*\*\*([^*]+):\*\*\s*(.*)$', ln)
        if not m:
            continue
        section, rest = m.group(1).strip(), m.group(2).strip()
        # rest like: Ev **1.71** | Beraberlik **3.35** | Konuk **3.21**
        # or: 1X **1.9** | 12 **1.08** | X2 **1.07**
        parts = re.findall(r'([^|*]+?)\s*\*\*([0-9.]+)\*\*', rest)
        for name, val in parts:
            name = name.strip()
            val = float(val)
            if section.startswith('Taraf'):
                if name.startswith('Ev'):
                    odds['Maç Sonucu_1'] = val
                elif name.startswith('Beraberlik'):
                    odds['Maç Sonucu_0'] = val
                elif name.startswith('Konuk'):
                    odds['Maç Sonucu_2'] = val
            elif 'Çifte Şans' in section or section.strip().startswith('Çifte'):
                key = {'1X': 'Çifte Şans_1X', '12': 'Çifte Şans_12', 'X2': 'Çifte Şans_X2',
                       '1 ve 0': 'Çifte Şans_1X', '1 ve 2': 'Çifte Şans_12', '0 ve 2': 'Çifte Şans_X2',
                       '1-0': 'Çifte Şans_1X', '1-2': 'Çifte Şans_12', '0-2': 'Çifte Şans_X2'}.get(name)
                if key:
                    odds[key] = val
            elif 'İlk Yarı MS' in section:
                if name.startswith('Ev'):
                    odds['1. Yarı Sonucu_1'] = val
                elif name.startswith('Beraberlik'):
                    odds['1. Yarı Sonucu_0'] = val
                elif name.startswith('Konuk'):
                    odds['1. Yarı Sonucu_2'] = val
            elif '2.5' in section:
                if name.startswith('Alt'):
                    odds['Alt/Üst 2.5_Alt'] = val
                else:
                    odds['Alt/Üst 2.5_Üst'] = val
            elif 'Karşılıklı Gol' in section:
                if name.startswith('KG Var') or name == 'Var':
                    odds['Karşılıklı Gol_Var'] = val
                elif name.startswith('KG Yok') or name == 'Yok':
                    odds['Karşılıklı Gol_Yok'] = val
            elif 'Tek/Çift' in section:
                if name.startswith('Tek'):
                    odds['Tek / Çift_Tek'] = val
                else:
                    odds['Tek / Çift_Çift'] = val
    return odds

def parse_file(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        content = f.read()
    blocks = content.split('==================================================')
    matches = []
    for b in blocks:
        m = re.search(r'İndex:\s*(-?\d+)\s*\|', b)
        if not m:
            continue
        idx = m.group(1)
        sm = re.search(r'GERÇEK SKOR:\s*(\d+)\s*-\s*(\d+)', b)
        if not sm:
            continue
        skor = (int(sm.group(1)), int(sm.group(2)))
        iym = re.search(r'İlk Yarı:\s*(\d+)\s*-\s*(\d+)', b) or re.search(r'İY:\s*(\d+)\s*-\s*(\d+)', b)
        iy = (int(iym.group(1)), int(iym.group(2))) if iym else None
        kural = re.search(r'\*\*Kural Sırası:\*\*\s*\*\*(.+?)\*\*', b)
        if not kural:
            kural = re.search(r'Kural Sırası:\s*\*\*(.+?)\*\*', b)
        if kural:
            kurallar = [k.strip() for k in kural.group(1).split('→') if k.strip()]
        else:
            kurallar = []
        oranlar = parse_odds(b.split('\n'))
        matches.append({'index': idx, 'skor': skor, 'iy': iy, 'kurallar': kurallar, 'oranlar': oranlar})
    return matches

all_m = []
for f in FILES:
    p = os.path.join(SRC, f)
    if not os.path.exists(p):
        continue
    ms = parse_file(p)
    all_m.extend(ms)
    print(f'{f}: {len(ms)} mac')

print('TOPLAM:', len(all_m))
with open(os.path.join(SRC, 'veri_seti.json'), 'w', encoding='utf-8') as f:
    json.dump(all_m, f, ensure_ascii=False, indent=1)
print('veri_seti.json yazildi')

# ornek: kural oncelik dagilimi
from collections import Counter
c = Counter()
for m in all_m:
    for k in m['kurallar']:
        c[k] += 1
print('\nEn cok tetiklenen kurallar:')
for k, v in c.most_common(25):
    print(f'  {k}: {v}')
