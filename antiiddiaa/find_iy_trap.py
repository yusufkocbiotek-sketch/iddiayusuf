import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', encoding='utf-8') as f:
    data = json.load(f)

for idx, m in enumerate(data['matches']):
    o = m['oranlar']
    iy_ms1 = o.get('1. Yarı Sonucu_1') or o.get('İlk Yarı Sonucu_1')
    iy_ms1_15_alt = o.get('1. Yarı Sonucu ve Altı/Üstü 1.5_1 ve Alt') or o.get('İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Alt')
    iy_ms1_15_ust = o.get('1. Yarı Sonucu ve Altı/Üstü 1.5_1 ve Üst') or o.get('İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Üst')
    
    if iy_ms1 and iy_ms1_15_alt and iy_ms1_15_ust:
        if iy_ms1 <= 1.50 and iy_ms1_15_ust < iy_ms1_15_alt:
            print(f'Match {-idx}: {m["ev_sahibi"]} - {m["deplasman"]}: IY 1: {iy_ms1}, IY 1 + 1.5 Üst: {iy_ms1_15_ust} (Alt: {iy_ms1_15_alt}), Skor: IY {m.get("skor_ilk_yari")} MS {m.get("skor_mac_sonucu")}')
