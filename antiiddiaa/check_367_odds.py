import sys
import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

m = data['matches'][-367]
print("MATCH 367 ODDS:")
for k, v in m['oranlar'].items():
    print(f"{k}: {v}")
