import json
import os
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

CIKTI_DOSYA = "mac_test_yumusak_sonuc.json"

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor (Yumuşak Scroll Test)...")
    options = Options()
    # Test için headless kapatıldı (ekranı görmen için)
    # options.add_argument("--headless")  
    options.add_argument("--window-size=1400,900")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("✅ Chrome başlatıldı! (Pencere açık olacak)")
    return driver

def yumusak_scroll(driver, tekrar=18):
    print(f"   ⬇️ Yumuşak scroll başlatılıyor ({tekrar} adım)...")
    for i in range(tekrar):
        # Daha yumuşak scroll
        driver.execute_script("window.scrollBy(0, 650);")
        time.sleep(2.8)   # Her scroll'dan sonra uzun bekleme
        
        if i % 4 == 0:    # Her 4 kaydırmada bir yukarı da hafif kaydır
            driver.execute_script("window.scrollBy(0, -400);")
            time.sleep(1.5)
            
        print(f"   Scroll {i+1}/{tekrar} tamamlandı...")
    
    # En sona git ve son yüklemeleri tetikle
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

def main():
    print("="*80)
    print("🧪 SCRAPER TEST V3 - YUMUŞAK VE YAVAŞ SCROLL")
    print("="*80)
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    driver = None
    try:
        driver = tarayici_baslat()
        url = "https://www.iddaa.com/program/futbol"
        
        print(f"📡 Siteye gidiliyor → {url}")
        driver.get(url)
        time.sleep(7)

        # Yumuşak scroll ile tüm maçları yüklemeye çalış
        yumusak_scroll(driver, tekrar=20)

        # Maç satırlarını bul
        mac_elements = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
        
        print(f"\n✅ Toplam bulunan maç satırı: {len(mac_elements)}")

        mac_listesi = []
        for element in mac_elements:
            try:
                text = element.text.strip()
                if len(text) > 15:
                    lines = [line.strip() for line in text.split("\n") if line.strip()]
                    if len(lines) >= 3:
                        saat = lines[0] if ":" in lines[0] else ""
                        ev = lines[1]
                        dep = lines[3] if len(lines) > 3 else lines[2]
                        if ev and dep:
                            mac_listesi.append({"saat": saat, "ev": ev, "dep": dep})
            except:
                continue

        # Tekrarları temizle
        temiz_liste = []
        gorulen = set()
        for m in mac_listesi:
            key = f"{m['ev']}_{m['dep']}"
            if key not in gorulen:
                gorulen.add(key)
                temiz_liste.append(m)

        print(f"\n📋 Tekrarlardan arındırılmış maç sayısı: {len(temiz_liste)}\n")
        
        for i, m in enumerate(temiz_liste, 1):
            print(f"   {i:2}. {m['saat']} | {m['ev']} - {m['dep']}")

        # Sonucu kaydet
        sonuc = {
            "test_tarihi": datetime.datetime.now().isoformat(),
            "toplam_bulunan_satir": len(mac_elements),
            "temiz_mac_sayisi": len(temiz_liste),
            "matches": temiz_liste
        }

        with open(CIKTI_DOSYA, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Test tamamlandı! Sonuç '{CIKTI_DOSYA}' dosyasına kaydedildi.")

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            input("\nPencereyi kapatmak için ENTER tuşuna basın...")
            driver.quit()

if __name__ == "__main__":
    main()