import json, sys
sys.stdout.reconfigure(encoding='utf-8')
f=open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', encoding='utf-8')
d=json.load(f)
for idx in [749, 754, 757, 748, 753]:
    print(f'\n--- Match {idx} ---')
    o = d['matches'][-idx]['oranlar']
    for k,v in o.items():
        if v is not None:
            print(f'{k}: {v}')
