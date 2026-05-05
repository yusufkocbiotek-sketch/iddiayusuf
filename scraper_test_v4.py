import json
import os
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

CIKTI_DOSYA = "mac_test_v4_sonuc.json"

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor (Test V4 - Sayfa Metni Analizi)...")
    options = Options()
    # options.add_argument("--headless")   # Test için kapatıldı, ekranı görmek için
    options.add_argument("--window-size=1400,900")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("✅ Chrome başlatıldı!")
    return driver

def yumusak_scroll(driver):
    print("   ⬇️ Sayfayı yavaş yavaş aşağı kaydırıyorum (20 adım)...")
    for i in range(20):
        driver.execute_script("window.scrollBy(0, 650);")
        time.sleep(2.4)
        if i % 5 == 0:
            driver.execute_script("window.scrollBy(0, -350);")
            time.sleep(1.3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

def main():
    print("="*85)
    print("🧪 SCRAPER TEST V4 - TÜM SAYFA METNİ İLE AKILLI ANALİZ")
    print("="*85)
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    driver = None
    try:
        driver = tarayici_baslat()
        url = "https://www.iddaa.com/program/futbol"
        
        print(f"📡 Siteye gidiliyor → {url}")
        driver.get(url)
        time.sleep(6)

        yumusak_scroll(driver)

        # TÜM SAYFA METNİNİ AL
        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = [line.strip() for line in body_text.split("\n") if line.strip()]

        print(f"\n✅ Toplam satır sayısı: {len(lines)}")
        
        # Debug için ilk 80 satırı kaydet
        with open("sayfa_metni_debug.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(lines[:80]))

        mac_listesi = []
        i = 0
        while i < len(lines) - 2:
            line = lines[i]
            # Saat formatı bul (örnek: 21:45, 00:00)
            if len(line) == 5 and line[2] == ":":
                try:
                    saat = line
                    ev = lines[i+1]
                    dep = lines[i+2]
                    
                    if (len(ev) > 3 and len(dep) > 3 and 
                        ev != dep and "-" not in ev and "Tümü" not in ev):
                        mac_listesi.append({
                            "saat": saat,
                            "ev": ev,
                            "dep": dep
                        })
                        i += 3
                        continue
                except:
                    pass
            i += 1

        print(f"\n📋 Bulunan maç sayısı: {len(mac_listesi)}\n")
        
        for i, m in enumerate(mac_listesi, 1):
            print(f"   {i:2}. {m['saat']} | {m['ev']} - {m['dep']}")

        # Sonucu kaydet
        sonuc = {
            "test_tarihi": datetime.datetime.now().isoformat(),
            "toplam_satir": len(lines),
            "bulunan_mac_sayisi": len(mac_listesi),
            "matches": mac_listesi
        }

        with open(CIKTI_DOSYA, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Test V4 tamamlandı!")
        print(f"   → Bulunan maç: {len(mac_listesi)} adet")
        print(f"   → Sonuç '{CIKTI_DOSYA}' ve 'sayfa_metni_debug.txt' dosyalarına kaydedildi.")

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            input("\nPencereyi kapatmak için ENTER tuşuna basın...")
            driver.quit()

if __name__ == "__main__":
    main()