import json
from collections import Counter

JSON_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json'
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

print("--- CANLI MAÇ ÖZEL ANALİZİ (MS2: 1.20-1.40 | KG YOK Fav | ÜST Fav) ---")

# Bu oran yapısına benzer (Şampiyonlar Ligi veya tüm liglerde) tüm geçmiş maçları bulalım.
# MS2 ağır favori (1.20 - 1.45)
# KG Yok favori (Yok < Var)
# Üst favori (Üst < Alt)

target_smp = []
target_all = []

for m in matches:
    o = m.get('oranlar', {})
    ms2 = o.get('Maç Sonucu_2', 99)
    kgy = o.get('Karşılıklı Gol_Yok', 99)
    kgv = o.get('Karşılıklı Gol_Var', 0)
    alt = o.get('Alt/Üst 2.5_Alt', 99)
    ust = o.get('Alt/Üst 2.5_Üst', 0)
    
    if 1.20 <= ms2 <= 1.45 and kgy < kgv and ust < alt:
        target_all.append(m)
        if m.get('lig') == 'ŞMP':
            target_smp.append(m)

def analyze(match_list, title):
    if not match_list:
        print(f"\n{title}: Eşleşen maç bulunamadı.")
        return
        
    print(f"\n{title} (Toplam {len(match_list)} Maç):")
    ms2_count = sum(1 for m in match_list if m.get('skor_ev', 99) < m.get('skor_dep', 0))
    ust_count = sum(1 for m in match_list if (m.get('skor_ev', 0) + m.get('skor_dep', 0)) >= 3)
    kgyok_count = sum(1 for m in match_list if m.get('skor_ev', 0) == 0 or m.get('skor_dep', 0) == 0)
    
    print(f"MS 2 (Deplasman Kazanır): %{round(ms2_count/len(match_list)*100, 1)}")
    print(f"2.5 Üst Biter: %{round(ust_count/len(match_list)*100, 1)}")
    print(f"KG Yok Biter: %{round(kgyok_count/len(match_list)*100, 1)}")
    
    scores = [f"{m.get('skor_ev')}-{m.get('skor_dep')}" for m in match_list]
    print(f"En Çok Gelen Skorlar: {Counter(scores).most_common(3)}")

analyze(target_smp, "SADECE ŞAMPİYONLAR LİGİ (ŞMP)")
analyze(target_all, "TÜM LİGLER GENELİNDE BU ORAN YAPISI")
