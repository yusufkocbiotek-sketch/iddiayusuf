import json, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import safe_fuzzy_match, normalize_key
f=open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', encoding='utf-8')
d=json.load(f)
o = d['matches'][-743]['oranlar']
norm_keys = [normalize_key(k) for k in o.keys()]
res = safe_fuzzy_match(normalize_key('İlk Yarı Karşılıklı Gol_Yok'), norm_keys)
print('Match 743 IY KG Yok matched to:', res)
res2 = safe_fuzzy_match(normalize_key('İkinci Yarı Karşılıklı Gol_Yok'), norm_keys)
print('Match 743 2Y KG Yok matched to:', res2)
