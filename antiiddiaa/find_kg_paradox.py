import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', encoding='utf-8') as f:
    data = json.load(f)

for idx, m in enumerate(data['matches']):
    o = m['oranlar']
    alt25 = o.get('Alt/Üst 2.5_Alt') or o.get('Altı/Üstü 2.5_Alt')
    kgy = o.get('Karşılıklı Gol_Yok')
    ev_05 = o.get('Ev Sahibi Alt/Üst 0.5_Üst') or o.get('Ev Sahibi Altı/Üstü 0.5_Üst')
    dep_05 = o.get('Deplasman Alt/Üst 0.5_Üst') or o.get('Deplasman Altı/Üstü 0.5_Üst')
    
    if alt25 and kgy and ev_05 and dep_05:
        if alt25 <= 1.65 and kgy <= 1.65 and ev_05 <= 1.55 and dep_05 <= 1.20:
            print(f'Match {-idx}: {m["ev_sahibi"]} - {m["deplasman"]}: 2.5Alt: {alt25}, KGY: {kgy}, Ev0.5Üst: {ev_05}, Dep0.5Üst: {dep_05} -> Skor: {m.get("skor_mac_sonucu")}')
