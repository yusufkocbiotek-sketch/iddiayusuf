import json
import os
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

CIKTI_DOSYA = "public/data/mac_test.json"   # Test için ayrı dosya

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor (Test Modu)...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("✅ Chrome başlatıldı!")
    return driver

def scroll_down(driver, times=12):
    print(f"   ⬇️ Sayfa {times} kez aşağı kaydırılıyor (Tüm maçlar yükleniyor)...")
    for i in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.2)
        if i % 3 == 0:  # Her 3 kaydırmada bir yukarı da az kaydır
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 900);")
            time.sleep(1)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

def main():
    print("="*70)
    print("🧪 SCRAPER TEST VERSİYONU - TÜM MAÇLARI ÇEKME TESTİ")
    print("="*70)
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    driver = None
    try:
        driver = tarayici_baslat()
        url = "https://www.iddaa.com/program/futbol"
        
        print(f"📡 Siteye gidiliyor: {url}")
        driver.get(url)
        time.sleep(5)

        # === TÜM MAÇLARI YÜKLEMEK İÇİN SCROLL ===
        scroll_down(driver, times=15)

        # Sayfadaki tüm maç satırlarını bul
        mac_elements = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
        
        print(f"\n✅ Toplam {len(mac_elements)} maç satırı tespit edildi!\n")

        mac_listesi = []
        for ta in mac_elements:
            try:
                txt = ta.text.strip()
                lines = [line.strip() for line in txt.split("\n") if line.strip()]
                if len(lines) >= 3:
                    ev = lines[1]
                    dep = lines[3]
                    saat = lines[0] if len(lines[0]) == 5 and ":" in lines[0] else ""
                    if ev and dep:
                        mac_listesi.append({"ev": ev, "dep": dep, "saat": saat})
            except:
                continue

        print(f"📋 İşlenen maç sayısı: {len(mac_listesi)}\n")
        for i, m in enumerate(mac_listesi[:20], 1):   # İlk 20'sini göster
            print(f"   {i:2}. {m['saat']} | {m['ev']} - {m['dep']}")
        if len(mac_listesi) > 20:
            print(f"   ... ve {len(mac_listesi)-20} maç daha var.")

        # Test amaçlı basit JSON oluştur
        test_data = {
            "version": 2,
            "updated": datetime.datetime.now().isoformat(),
            "test_info": f"{len(mac_listesi)} maç tespit edildi",
            "matches": []
        }
        
        for m in mac_listesi:
            test_data["matches"].append({
                "ev_sahibi": m["ev"],
                "deplasman": m["dep"],
                "saat": m["saat"],
                "tarih": datetime.date.today().isoformat(),
                "durum": "baslamadi"
            })

        with open("mac_test_sonuc.json", "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Test tamamlandı! Toplam {len(mac_listesi)} maç tespit edildi.")
        print("💾 Sonuçlar 'mac_test_sonuc.json' dosyasına kaydedildi.")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
    finally:
        if driver:
            driver.quit()
        print("\nTest bitti. Pencereyi kapatabilirsiniz.")

if __name__ == "__main__":
    main()