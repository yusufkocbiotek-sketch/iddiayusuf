import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

print("📡 iddaa.com açılıyor...")
driver.get("https://www.iddaa.com/program/futbol")
time.sleep(10)

print("✅ Sayfa yüklendi!")
print("="*60)

# İlk maçın detay butonuna tıkla
print("🖱️ İlk maçın detay butonuna tıklanıyor...")
print("="*60)

try:
    # Detay butonlarını bul
    buttons = driver.find_elements(By.CSS_SELECTOR, ".i_kn__WPyeo")
    print(f"  📋 {len(buttons)} adet detay butonu bulundu")
    
    if buttons:
        # Tıklamadan önce sayfa durumu
        onceki_url = driver.current_url
        onceki_html_len = len(driver.page_source)
        
        # İlk butona tıkla
        driver.execute_script("arguments[0].scrollIntoView(true);", buttons[0])
        time.sleep(1)
        driver.execute_script("arguments[0].click();", buttons[0])
        time.sleep(5)
        
        sonraki_url = driver.current_url
        sonraki_html_len = len(driver.page_source)
        
        print(f"  🌐 Önceki URL: {onceki_url}")
        print(f"  🌐 Sonraki URL: {sonraki_url}")
        print(f"  📄 HTML boyut farkı: {sonraki_html_len - onceki_html_len} karakter")
        
        if sonraki_url != onceki_url:
            # Yeni sayfaya gitti
            print(f"\n  ✅ YENİ SAYFA AÇILDI!")
            body = driver.find_element(By.TAG_NAME, "body")
            lines = body.text.split("\n")
            print(f"\n  📄 DETAY SAYFASI İLK 150 SATIR:")
            print("  " + "="*50)
            for i, line in enumerate(lines[:150]):
                if line.strip():
                    print(f"    {i}: {line.strip()}")
        else:
            # Sayfa içinde genişledi
            print(f"\n  🔽 SAYFA İÇİNDE GENİŞLEDİ!")
            
            # İlk maç satırını tekrar bul
            ilk_mac = driver.find_elements(By.CSS_SELECTOR, ".i_mc__MDEbN")[0]
            mac_text = ilk_mac.text
            lines = mac_text.split("\n")
            
            print(f"\n  📄 GENİŞLEMİŞ MAÇ İÇERİĞİ ({len(lines)} satır):")
            print("  " + "="*50)
            for i, line in enumerate(lines):
                if line.strip():
                    print(f"    {i}: {line.strip()}")
            
            # Yeni eklenen elementleri ara
            print(f"\n  🔍 YENİ EKLENEN ELEMENTLER:")
            print("  " + "="*50)
            
            new_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='detail'], [class*='expand'], [class*='panel'], [class*='dropdown'], [class*='popup'], [class*='modal'], [class*='overlay'], [class*='content']")
            for el in new_elements[:20]:
                cls = el.get_attribute("class") or ""
                txt = el.text.strip()[:100] if el.text else ""
                if txt:
                    print(f"    class='{cls[:60]}'")
                    print(f"    text='{txt}'")
                    print()

except Exception as e:
    print(f"  ❌ Hata: {e}")

# YÖNTEM 2: Maç adına tıkla
print("\n" + "="*60)
print("🖱️ YÖNTEM 2: Maç adı alanına tıklanıyor...")
print("="*60)

try:
    driver.get("https://www.iddaa.com/program/futbol")
    time.sleep(8)
    
    # Takım adı elementine tıkla
    takim_adi = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
    print(f"  📋 {len(takim_adi)} takım adı elementi bulundu")
    
    if takim_adi:
        driver.execute_script("arguments[0].click();", takim_adi[0])
        time.sleep(5)
        
        print(f"  🌐 URL: {driver.current_url}")
        
        if driver.current_url != "https://www.iddaa.com/program/futbol":
            print(f"  ✅ YENİ SAYFA!")
            body = driver.find_element(By.TAG_NAME, "body")
            lines = body.text.split("\n")
            for i, line in enumerate(lines[:150]):
                if line.strip():
                    print(f"    {i}: {line.strip()}")
        else:
            # İlk maçı tekrar kontrol et
            ilk_mac = driver.find_elements(By.CSS_SELECTOR, ".i_mc__MDEbN")[0]
            lines = ilk_mac.text.split("\n")
            print(f"  📄 Maç satırı ({len(lines)} satır):")
            for i, line in enumerate(lines):
                if line.strip():
                    print(f"    {i}: {line.strip()}")

except Exception as e:
    print(f"  ❌ Hata: {e}")

# YÖNTEM 3: Maç kodu linkine tıkla (son sayı)
print("\n" + "="*60)
print("🖱️ YÖNTEM 3: Maç kodu numarasına tıklanıyor...")
print("="*60)

try:
    driver.get("https://www.iddaa.com/program/futbol")
    time.sleep(8)
    
    # i_mbs__NlPW_ class'ına tıkla (maç bilgi alanı)
    mbs = driver.find_elements(By.CSS_SELECTOR, ".i_mbs__NlPW_")
    print(f"  📋 {len(mbs)} adet i_mbs elementi bulundu")
    
    if mbs:
        driver.execute_script("arguments[0].click();", mbs[0])
        time.sleep(5)
        print(f"  🌐 URL: {driver.current_url}")
        
        if driver.current_url != "https://www.iddaa.com/program/futbol":
            print(f"  ✅ YENİ SAYFA!")
            body = driver.find_element(By.TAG_NAME, "body")
            lines = body.text.split("\n")
            for i, line in enumerate(lines[:150]):
                if line.strip():
                    print(f"    {i}: {line.strip()}")
                    
except Exception as e:
    print(f"  ❌ Hata: {e}")

print("\n" + "="*60)
input("⏸️ Enter'a basın Chrome kapansın...")
driver.quit()