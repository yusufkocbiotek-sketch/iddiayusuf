import json, sys
sys.path.append(r'C:\Users\YUSUF\.gemini\antigravity\scratch')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

for mac in matches:
    if mac.get('index') == 23800:
        od = mac.get('oranlar', {})
        print("2.5 Alt:", od.get("Alt/Üst 2.5_Alt") or od.get("Altı/Üstü 2.5_Alt"))
        print("2.5 Ust:", od.get("Alt/Üst 2.5_Üst") or od.get("Altı/Üstü 2.5_Üst"))
        print("KG Var:", od.get("Karşılıklı Gol_Var"))
        print("KG Yok:", od.get("Karşılıklı Gol_Yok"))
        print("1.5 Ust:", od.get("Alt/Üst 1.5_Üst") or od.get("Altı/Üstü 1.5_Üst"))
        print("IY 0.5 Ust:", od.get("İlk Yarı Alt/Üst 0.5_Üst") or od.get("İlk Yarı Altı/Üstü 0.5_Üst"))
        print("IY 1.5 Ust:", od.get("İlk Yarı Alt/Üst 1.5_Üst") or od.get("İlk Yarı Altı/Üstü 1.5_Üst"))
