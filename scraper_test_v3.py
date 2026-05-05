import json
import os
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

CIKTI_DOSYA = "mac_test_v3_sonuc.json"

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor (Test V3 - Akıllı Ayrıştırma)...")
    options = Options()
    # options.add_argument("--headless")  # Test için kapatıldı, ekranı görmek için
    options.add_argument("--window-size=1400,900")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("✅ Chrome başlatıldı!")
    return driver

def yumusak_scroll(driver, tekrar=18):
    print(f"   ⬇️ Yumuşak scroll yapılıyor ({tekrar} adım)...")
    for i in range(tekrar):
        driver.execute_script("window.scrollBy(0, 700);")
        time.sleep(2.3)
        if i % 5 == 0:
            driver.execute_script("window.scrollBy(0, -400);")
            time.sleep(1.2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

def main():
    print("="*80)
    print("🧪 SCRAPER TEST V3 - AKILLI MAÇ AYIKLAMA")
    print("="*80)
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    driver = None
    try:
        driver = tarayici_baslat()
        url = "https://www.iddaa.com/program/futbol"
        
        print(f"📡 Siteye gidiliyor → {url}")
        driver.get(url)
        time.sleep(6)

        yumusak_scroll(driver, tekrar=20)

        # Birden fazla yöntemle maç satırlarını ara
        selectors = [
            ".i_tnw__t8AmC",
            "div[class*='match']",
            "div[class*='event']",
            "a[href*='mac']",
            "div[style*='cursor']"
        ]

        all_elements = []
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"   Selector '{selector}' → {len(elements)} element bulundu")
            all_elements.extend(elements)

        print(f"\n✅ Toplam bulunan element: {len(all_elements)}")

        mac_listesi = []
        for el in all_elements:
            text = el.text.strip()
            if len(text) < 10:
                continue
                
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            
            # Saat + Takım1 + Takım2 formatı arıyoruz
            for i in range(len(lines)-2):
                if len(lines[i]) == 5 and ":" in lines[i]:  # Saat formatı
                    saat = lines[i]
                    ev = lines[i+1]
                    dep = lines[i+2]
                    if len(ev) > 3 and len(dep) > 3 and ev != dep:
                        mac_listesi.append({"saat": saat, "ev": ev, "dep": dep})
                        break

        # Tekrarları temizle
        temiz_maclar = []
        gorulen = set()
        for m in mac_listesi:
            key = f"{m['ev']}_{m['dep']}"
            if key not in gorulen:
                gorulen.add(key)
                temiz_maclar.append(m)

        print(f"\n📋 Temizlenmiş maç sayısı: {len(temiz_maclar)}\n")
        
        for i, m in enumerate(temiz_maclar[:30], 1):
            print(f"   {i:2}. {m['saat']} | {m['ev']} - {m['dep']}")
        
        if len(temiz_maclar) > 30:
            print(f"\n   ... ve {len(temiz_maclar)-30} maç daha var.")

        # Sonucu kaydet
        sonuc = {
            "test_tarihi": datetime.datetime.now().isoformat(),
            "toplam_element": len(all_elements),
            "toplam_mac": len(temiz_maclar),
            "matches": temiz_maclar[:50]  # İlk 50'sini kaydet
        }

        with open(CIKTI_DOSYA, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Test V3 tamamlandı! Sonuç '{CIKTI_DOSYA}' dosyasına kaydedildi.")

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            input("\nPencereyi kapatmak için ENTER tuşuna basın...")
            driver.quit()

if __name__ == "__main__":
    main()