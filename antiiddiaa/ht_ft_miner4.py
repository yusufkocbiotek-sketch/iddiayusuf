import json

def load_data():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        return json.load(f)['matches']

def get_odd(odds, keys):
    for k in keys:
        if k in odds and odds[k] is not None:
            return float(odds[k])
    return 99.0

def average_iy0_odds(matches):
    iy0_odds = []
    
    for mac in matches:
        if mac.get('skor_ev', -1) >= 0 and mac.get('skor_1y_ev', -1) >= 0:
            odds = mac.get('oranlar', {})
            cs12 = get_odd(odds, ["Çifte Şans_12"])
            iy0 = get_odd(odds, ["İlk Yarı Sonucu_0"])
            
            if cs12 <= 1.20 and cs12 != 99.0 and iy0 != 99.0:
                iy0_odds.append(iy0)

    if iy0_odds:
        avg = sum(iy0_odds) / len(iy0_odds)
        print(f"Filtre 2 için Ortalama IY0 Oranı: {avg:.2f}")

if __name__ == "__main__":
    matches = load_data()
    average_iy0_odds(matches)
