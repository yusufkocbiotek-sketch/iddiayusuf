import json
import os
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

OUTPUT = "public/data/nesine_skorlar.json"

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome başlatıldı!")
    return driver

def skorlari_cek():
    driver = tarayici_baslat()
    
    url = "https://www.nesine.com/iddaa/sonuclar"
    print(f"📡 {url} açılıyor...")
    driver.get(url)
    time.sleep(12)
    
    # Tüm sayfaları gez
    sayfa = 1
    toplam = []
    
    while True:
        print(f"\n📄 Sayfa {sayfa} çekiliyor...")
        
        # Maçları topla
        body = driver.find_element(By.TAG_NAME, "body")
        text = body.text
        
        maclar = []
        for line in text.split("\n"):
            line = line.strip()
            # Maç satırı mı?
            if any(x in line for x in ["-", "vs", "MAÇ"]) and len(line) > 5 and len(line) < 100:
                if not any(bad in line for bad in ["E-FUTBOL", "Copyright", "Nesine", "YARDIM", "GİRİŞ"]):
                    maclar.append(line)
        
        print(f"   📋 {len(maclar)} maç bulundu")
        
        for m in maclar:
            if m not in toplam:
                toplam.append(m)
        
        # Sıradaki sayfa var mı?
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "a[rel='next']")
            if next_btn and next_btn.is_displayed():
                print(f"   ➡️ Sonraki sayfa var")
                next_btn.click()
                time.sleep(8)
                sayfa += 1
                continue
        except:
            pass
        
        break
    
    driver.quit()
    return toplam

def main():
    print("⚽ Nesine Skor Çekici")
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)
    
    skorlar = skorlari_cek()
    
    print(f"\n{'='*60}")
    print(f"📊 SONUÇ")
    print(f"   ✅ {len(skorlar)} maç çekildi")
    print(f"{'='*60}")
    
    if skorlar:
        print(f"\n📋 İlk 20 maç:")
        for m in skorlar[:20]:
            print(f"   {m}")
        
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(skorlar, f, ensure_ascii=False, indent=2)
        print(f"\n💾 {OUTPUT} olarak kaydedildi")

if __name__ == "__main__":
    main()