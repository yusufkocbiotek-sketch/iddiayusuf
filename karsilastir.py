import json
from pathlib import Path

# DOSYA YOLLARI
OUT_DIR = Path(r"C:\Users\YUSUF\OneDrive\Desktop\iddaa_scraper_output")
MAC_JSON_PATH = Path(r"C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main\public\data\mac.json")

def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ {file_path} okunamadı: {e}")
        return None

def extract_list(data):
    """JSON verisi liste değilse (örneğin sözlükse), içindeki listeyi veya değerleri çıkarır."""
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # 1. Değerlerde liste var mı kontrol et (örn: {"matches": [...], "status": "ok"})
        for v in data.values():
            if isinstance(v, list):
                return v
        # 2. Değerlerin hepsi sözlükse (örn: {"id1": {...}, "id2": {...}})
        if all(isinstance(v, dict) for v in data.values()):
            return list(data.values())
    return []

def get_match_key(match):
    """Maçı benzersiz kılan anahtar (Ev Sahibi + Deplasman + Lig)"""
    if not isinstance(match, dict):
        return ("?", "?", "?")
        
    home = match.get('home') or match.get('ev_sahibi') or match.get('ev') or match.get('homeTeam') or "?"
    away = match.get('away') or match.get('deplasman') or match.get('dep') or match.get('awayTeam') or "?"
    league = match.get('league') or match.get('lig') or match.get('tournament') or "?"
    
    return (str(home).strip(), str(away).strip(), str(league).strip())

def main():
    print("="*60)
    print("🔍 MAÇ VERİLERİ KARŞILAŞTIRMA ARACI")
    print("="*60)

    if not OUT_DIR.exists():
        print(f"❌ '{OUT_DIR}' klasörü bulunamadı!")
        input("\nÇıkmak için Enter'a basın...")
        return

    scraped_files = list(OUT_DIR.glob("matches_*.json"))
    if not scraped_files:
        print(f"❌ '{OUT_DIR}' içinde hiç maç JSON dosyası bulunamadı!")
        input("\nÇıkmak için Enter'a basın...")
        return

    latest_scraped = max(scraped_files, key=lambda p: p.stat().st_mtime)
    print(f"📄 Çekilen Veri : {latest_scraped.name}")
    
    if not MAC_JSON_PATH.exists():
        print(f"❌ '{MAC_JSON_PATH}' dosyası bulunamadı!")
        input("\nÇıkmak için Enter'a basın...")
        return
    
    print(f"📄 Mevcut Veri  : mac.json\n")

    # Verileri Yükle
    raw_scraped = load_json(latest_scraped)
    raw_mac = load_json(MAC_JSON_PATH)

    if raw_scraped is None or raw_mac is None:
        input("\nÇıkmak için Enter'a basın...")
        return

    # AKILLI LİSTE ÇIKARICI (Hatanın çözüldüğü yer)
    scraped_data = extract_list(raw_scraped)
    mac_data = extract_list(raw_mac)

    print(f"✅ Çekilen JSON'da {len(scraped_data)} maç var.")
    print(f"✅ mac.json'da {len(mac_data)} maç var.\n")

    # Sözlüklere Çevir
    scraped_dict = {get_match_key(m): m for m in scraped_data if isinstance(m, dict)}
    mac_dict = {get_match_key(m): m for m in mac_data if isinstance(m, dict)}

    scraped_keys = set(scraped_dict.keys())
    mac_keys = set(mac_dict.keys())

    # Karşılaştırma Mantığı
    only_in_scraped = scraped_keys - mac_keys
    only_in_mac = mac_keys - scraped_keys
    common_keys = scraped_keys & mac_keys

    print("-" * 60)
    print("📊 KARŞILAŞTIRMA SONUÇLARI:")
    print("-" * 60)

    # A) Sadece Çekilen Veride Olanlar
    print(f"\n🟢 SADECE ÇEKİLEN VERİDE OLANLAR ({len(only_in_scraped)} maç):")
    if only_in_scraped:
        for key in list(only_in_scraped)[:10]:
            m = scraped_dict[key]
            score = m.get('score') or m.get('skor') or "?"
            print(f"   + {m.get('home')} {score} {m.get('away')}")
        if len(only_in_scraped) > 10:
            print(f"   ... ve {len(only_in_scraped) - 10} maç daha.")
    else:
        print("   (Yok - Her ikisinde de mevcut)")

    # B) Sadece mac.json'da Olanlar
    print(f"\n🔴 SADECE mac.json'DA OLANLAR ({len(only_in_mac)} maç):")
    if only_in_mac:
        for key in list(only_in_mac)[:10]:
            m = mac_dict[key]
            home = m.get('home') or m.get('ev_sahibi') or "?"
            away = m.get('away') or m.get('deplasman') or "?"
            score = m.get('score') or m.get('skor') or "?"
            print(f"   - {home} {score} {away}")
        if len(only_in_mac) > 10:
            print(f"   ... ve {len(only_in_mac) - 10} maç daha.")
    else:
        print("   (Yok - Hiç eksik maç yok!)")

    # C) Ortak Maçlar ama Farklı Skor/Durum
    print(f"\n🟡 ORTAK MAÇLARDAKİ FARKLILIKLAR:")
    diff_count = 0
    for key in common_keys:
        m_scraped = scraped_dict[key]
        m_mac = mac_dict[key]
        
        s_score = str(m_scraped.get('score') or m_scraped.get('skor') or "")
        m_score = str(m_mac.get('score') or m_mac.get('skor') or "")
        
        s_status = str(m_scraped.get('status') or m_scraped.get('durum') or "")
        m_status = str(m_mac.get('status') or m_mac.get('durum') or "")

        if s_score != m_score or s_status != m_status:
            diff_count += 1
            if diff_count <= 10:
                home = m_scraped.get('home') or m_scraped.get('ev_sahibi')
                away = m_scraped.get('away') or m_scraped.get('deplasman')
                print(f"   ⚠️ {home} - {away}")
                print(f"      Çekilen: Skor {s_score} | Durum {s_status}")
                print(f"      mac.json: Skor {m_score} | Durum {m_status}")
    
    if diff_count == 0:
        print("   (Yok - Tüm ortak maçların skor ve durumları birebir aynı!)")
    elif diff_count > 10:
        print(f"   ... ve {diff_count - 10} maçta daha fark var.")

    print("\n" + "="*60)
    print("✅ Karşılaştırma Tamamlandı!")
    print("="*60)
    
    input("\nÇıkmak için Enter tuşuna basın...")

if __name__ == "__main__":
    main()