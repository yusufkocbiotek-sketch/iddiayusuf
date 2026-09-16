import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

for mac in matches:
    if mac.get('index') == 23749:
        od = mac.get('oranlar', {})
        print("23749 (Gardabaer vs Dalverik) Oranlar (ilk 20):", list(od.items())[:20])
        print("KG Var:", od.get("Karşılıklı Gol_Var"))
        print("2.5 Alt:", od.get("Alt/Üst 2.5_Alt") or od.get("Altı/Üstü 2.5_Alt"))
        print("3.5 Ust:", od.get("Alt/Üst 3.5_Üst") or od.get("Altı/Üstü 3.5_Üst"))
        break
