import json
from pathlib import Path

# DOSYA YOLLARI (DOĞRU YOL GÜNCELLENDİ)
OUT_DIR = Path(r"C:\Users\YUSUF\OneDrive\Desktop\iddaa_scraper_output")
MAC_JSON_PATH = Path(r"C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main\public\data\mac.json")

def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ {file_path} okunamadı: {e}")
        return None

def get_match_key(match):
    """Maçı benzersiz kılan anahtar (Ev Sahibi + Deplasman + Lig)"""
    home = match.get('home') or match.get('ev_sahibi') or match.get('ev') or "?"
    away = match.get('away') or match.get('deplasman') or match.get('dep') or "?"
    league = match.get('league') or match.get('lig') or "?"
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

    scraped_data = load_json(latest_scraped)
    mac_data = load_json(MAC_JSON_PATH)

    if scraped_data is None or mac_data is None:
        input("\nÇıkmak için Enter'a basın...")
        return

    print(f"✅ Çekilen JSON'da {len(scraped_data)} maç var.")
    print(f"✅ mac.json'da {len(mac_data)} maç var.\n")

    scraped_dict = {get_match_key(m): m for m in scraped_data}
    mac_dict = {get_match_key(m): m for m in mac_data}

    scraped_keys = set(scraped_dict.keys())
    mac_keys = set(mac_dict.keys())

    only_in_scraped = scraped_keys - mac_keys
    only_in_mac = mac_keys - scraped_keys
    common_keys = scraped_keys & mac_keys

    print("-" * 60)
    print("📊 KARŞILAŞTIRMA SONUÇLARI:")
    print("-" * 60)

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

    print(f"\n🟡 ORTAK MAÇLARDAKİ FARKLILIKLAR:")
    diff_count = 0
    for key in common_keys:
        m_scraped = scraped_dict[key]
        m_mac = mac_dict[key]
        
        s_score = m_scraped.get('score') or m_scraped.get('skor')
        m_score = m_mac.get('score') or m_mac.get('skor')
        
        s_status = m_scraped.get('status') or m_scraped.get('durum')
        m_status = m_mac.get('status') or m_mac.get('durum')

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