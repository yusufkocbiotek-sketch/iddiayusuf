import json
from collections import Counter

def run_correlation():
    JSON_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json'
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        matches = json.load(f)['matches']

    print("==========================================================")
    print("🧬 ORAN UYUMU (HARMONY) & DENGESİZLİK (DISCREPANCY) MATRİSİ")
    print("Test Senaryosu: Ev Sahibi Ağır Favori (MS1: 1.10 - 1.40)")
    print("Kırılma Noktası Analizi: KG Yok Oranının Skora Etkisi")
    print("==========================================================\n")

    # Temel Senaryo: MS1 Ağır Favori olan tüm maçlar
    base_matches = [m for m in matches if m.get('oranlar') and 1.10 <= m['oranlar'].get('Maç Sonucu_1', 99) <= 1.40]

    # Gruplar (Kırılma Noktaları)
    groups = {
        "1. UYUM BÖLGESİ (KG Yok < 1.40)": lambda o: o.get('Karşılıklı Gol_Yok', 99) < 1.40,
        "2. GEÇİŞ BÖLGESİ (KG Yok 1.40 - 1.59)": lambda o: 1.40 <= o.get('Karşılıklı Gol_Yok', 99) < 1.60,
        "3. DENGESİZLİK/TUZAK BÖLGESİ (KG Yok 1.60 - 1.79)": lambda o: 1.60 <= o.get('Karşılıklı Gol_Yok', 99) < 1.80,
        "4. TERS KORELASYON BÖLGESİ (KG Yok >= 1.80 | KG VAR Fav)": lambda o: o.get('Karşılıklı Gol_Yok', 0) >= 1.80
    }

    for group_name, condition in groups.items():
        g_matches = [m for m in base_matches if condition(m['oranlar'])]
        if not g_matches: continue
        
        tot = len(g_matches)
        ms1 = sum(1 for m in g_matches if m.get('skor_ev', 0) > m.get('skor_dep', 0))
        kgyok = sum(1 for m in g_matches if m.get('skor_ev', 0) == 0 or m.get('skor_dep', 0) == 0)
        
        scores = [f"{m.get('skor_ev')}-{m.get('skor_dep')}" for m in g_matches]
        top_scores = Counter(scores).most_common(4)
        
        # Ev sahibi kaç gol atmış ortalama
        total_ev_gol = sum(m.get('skor_ev', 0) for m in g_matches)
        avg_ev_gol = total_ev_gol / tot
        
        # Deplasman gol atma oranı (KG Var oranı)
        kgvar = sum(1 for m in g_matches if m.get('skor_ev', 0) > 0 and m.get('skor_dep', 0) > 0)
        
        print(f"🔹 {group_name}")
        print(f"   Maç Sayısı: {tot}")
        print(f"   MS1 (Favori Kazanır): %{round(ms1/tot*100, 1)}")
        print(f"   KG VAR (Sürpriz Gol): %{round(kgvar/tot*100, 1)}")
        print(f"   Ev Sahibi Gol Ortalaması: {round(avg_ev_gol, 2)}")
        
        score_str = " | ".join([f"{s} (%{round(c/tot*100,1)})" for s, c in top_scores])
        print(f"   🔥 ZİRVE SKORLAR: {score_str}\n")

if __name__ == "__main__":
    run_correlation()
