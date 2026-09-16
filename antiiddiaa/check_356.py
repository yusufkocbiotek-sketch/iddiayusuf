import json
with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

m = data['matches'][-356]
print(f"--- Match -356 ---")
print(m['ev_sahibi'], '-', m['deplasman'], f"Skor: {m.get('skor_ev')}-{m.get('skor_dep')}")
for k, v in m.get('oranlar', {}).items():
    if 'Sonucu' in k and ('1' in k or '0' in k or '2' in k):
        print(f'{k}: {v}')
    elif 'Alt' in k or 'Üst' in k or 'Karşılıklı' in k or 'Çifte' in k:
        print(f'{k}: {v}')
