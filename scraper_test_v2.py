import json
import os
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

CIKTI_DOSYA = "mac_test_v2_sonuc.json"

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor (Test V2 - Agresif Scroll)...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("✅ Chrome başlatıldı!")
    return driver

def agresif_scroll(driver, tekrar=25):
    print(f"   ⬇️ Agresif Scroll başlatılıyor ({tekrar} kez aşağı kaydırma)...")
    onceki_sayi = 0
    for i in range(tekrar):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        
        # Her 5 kaydırmada bir yukarı da kaydır (yeni yüklemeleri tetiklemek için)
        if i % 5 == 0:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1200);")
            time.sleep(1.5)
        
        # Kaç maç yüklendiğini kontrol et
        mac_sayisi = len(driver.find_elements(By.CSS_SELECTOR, "div, a, span"))
        if mac_sayisi > onceki_sayi:
            print(f"   Scroll {i+1}: Yeni maçlar yüklendi → Toplam ~{mac_sayisi} element")
            onceki_sayi = mac_sayisi
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

def main():
    print("="*75)
    print("🧪 SCRAPER TEST V2 - AGRESİF SCROLL + TÜM MAÇLARI ÇEKME")
    print("="*75)
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    driver = None
    try:
        driver = tarayici_baslat()
        url = "https://www.iddaa.com/program/futbol"
        
        print(f"📡 Siteye gidiliyor → {url}")
        driver.get(url)
        time.sleep(6)

        # Agresif scroll ile tüm maçları yüklemeye çalış
        agresif_scroll(driver, tekrar=25)

        # Farklı selector'larla maç satırlarını bulmaya çalış
        selectors = [
            ".i_tnw__t8AmC",
            "div[class*='match']",
            "a[href*='mac']",
            "div[style*='cursor']",
            "span"
        ]
        
        mac_elements = []
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if len(elements) > len(mac_elements):
                mac_elements = elements
                print(f"   En iyi selector: {selector} → {len(elements)} element bulundu")

        print(f"\n✅ Toplam bulunan element sayısı: {len(mac_elements)}")

        # Maçları ayıklama denemesi
        mac_listesi = []
        for element in mac_elements:
            try:
                text = element.text.strip()
                if len(text) > 10 and (" - " in text or " vs " in text):
                    lines = [line.strip() for line in text.split("\n") if line.strip()]
                    if len(lines) >= 2:
                        ev = lines[0]
                        dep = lines[1] if len(lines) > 1 else ""
                        if ev and dep and len(ev) > 2 and len(dep) > 2:
                            mac_listesi.append({"ev": ev, "dep": dep})
            except:
                continue

        # Tekrarları temizle
        gorulen_maclar = []
        for m in mac_listesi:
            key = f"{m['ev']}_{m['dep']}"
            if key not in [f"{x['ev']}_{x['dep']}" for x in gorulen_maclar]:
                gorulen_maclar.append(m)

        print(f"\n📋 Tekrarlardan arındırılmış maç sayısı: {len(gorulen_maclar)}")

        for i, m in enumerate(gorulen_maclar[:25], 1):
            print(f"   {i:2}. {m['ev']} - {m['dep']}")
        if len(gorulen_maclar) > 25:
            print(f"   ... ve {len(gorulen_maclar)-25} maç daha var.")

        # Sonucu kaydet
        sonuc = {
            "test_tarihi": datetime.datetime.now().isoformat(),
            "toplam_bulunan_element": len(mac_elements),
            "toplam_mac": len(gorulen_maclar),
            "matches": gorulen_maclar
        }

        with open(CIKTI_DOSYA, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Test tamamlandı! Sonuç '{CIKTI_DOSYA}' dosyasına kaydedildi.")

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            driver.quit()
        print("\nTest bitti.")

if __name__ == "__main__":
    main()