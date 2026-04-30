import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
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

# YÖNTEM 1: Maç div'ine tıkla
print("🖱️ YÖNTEM 1: İlk maç satırına tıklanıyor...")
print("="*60)

try:
    maclar = driver.find_elements(By.CSS_SELECTOR, ".i_mc__MDEbN")
    print(f"  📋 {len(maclar)} maç satırı bulundu")
    
    if maclar:
        ilk_mac = maclar[0]
        ilk_mac_text = ilk_mac.text.split("\n")[:5]
        print(f"  📋 İlk maç: {' '.join(ilk_mac_text)}")
        
        # Tıklamayı dene
        try:
            ilk_mac.click()
            time.sleep(5)
            print(f"  📋 Sayfa: {driver.title}")
            print(f"  🌐 URL: {driver.current_url}")
            
            if driver.current_url != "https://www.iddaa.com/program/futbol":
                print(f"\n  ✅ DETAY SAYFASI AÇILDI!")
                body = driver.find_element(By.TAG_NAME, "body")
                lines = body.text.split("\n")
                print(f"\n  📄 DETAY SAYFASI İLK 120 SATIR:")
                print("  " + "="*50)
                for i, line in enumerate(lines[:120]):
                    if line.strip():
                        print(f"    {i}: {line.strip()}")
            else:
                print("  ⚠️ Sayfa değişmedi, div tıklaması çalışmadı")
                
        except Exception as e:
            print(f"  ⚠️ Tıklama hatası: {e}")
            
except Exception as e:
    print(f"  ❌ Hata: {e}")

# YÖNTEM 2: Maç kodu ile direkt URL dene
print("\n" + "="*60)
print("🌐 YÖNTEM 2: Direkt URL deneniyor...")
print("="*60)

test_urls = [
    "https://www.iddaa.com/mac-detay/40",
    "https://www.iddaa.com/mac/40",
    "https://www.iddaa.com/event/40",
    "https://www.iddaa.com/program/futbol/40",
    "https://www.iddaa.com/detay/40",
]

for url in test_urls:
    try:
        print(f"\n  🔗 Deneniyor: {url}")
        driver.get(url)
        time.sleep(3)
        title = driver.title
        current = driver.current_url
        print(f"     Sayfa: {title}")
        print(f"     URL: {current}")
        
        if "404" not in title.lower() and "bulunamadı" not in title.lower():
            body = driver.find_element(By.TAG_NAME, "body")
            text = body.text[:200]
            print(f"     İçerik: {text[:200]}")
            
            if "oran" in text.lower() or "maç" in text.lower() or "sonucu" in text.lower():
                print(f"\n  ✅ ÇALIŞAN URL BULUNDU: {url}")
                
                lines = body.text.split("\n")
                print(f"\n  📄 DETAY İLK 120 SATIR:")
                for i, line in enumerate(lines[:120]):
                    if line.strip():
                        print(f"    {i}: {line.strip()}")
                break
    except:
        print(f"     ❌ Hata")

# YÖNTEM 3: Maç satırının içinde gizli link/buton ara
print("\n" + "="*60)
print("🔍 YÖNTEM 3: Maç satırı içindeki tüm child elementler...")
print("="*60)

driver.get("https://www.iddaa.com/program/futbol")
time.sleep(8)

try:
    maclar = driver.find_elements(By.CSS_SELECTOR, ".i_mc__MDEbN")
    if maclar:
        ilk = maclar[0]
        children = ilk.find_elements(By.CSS_SELECTOR, "*")
        print(f"  📋 İlk maç satırında {len(children)} child element var\n")
        
        for i, child in enumerate(children[:30]):
            tag = child.tag_name
            cls = child.get_attribute("class") or ""
            txt = child.text.strip()[:40] if child.text else ""
            href = child.get_attribute("href") or ""
            data_attrs = ""
            
            # data-* attribute'larını kontrol et
            for attr in ["data-id", "data-event", "data-match", "data-code", "data-fixture"]:
                val = child.get_attribute(attr)
                if val:
                    data_attrs += f" {attr}='{val}'"
            
            if cls or data_attrs:
                line = f"  [{i}] <{tag}> class='{cls[:60]}'"
                if data_attrs:
                    line += data_attrs
                if txt:
                    line += f" text='{txt}'"
                if href:
                    line += f" href='{href[:60]}'"
                print(line)
                
except Exception as e:
    print(f"  ❌ Hata: {e}")

print("\n" + "="*60)
input("⏸️ Enter'a basın Chrome kapansın...")
driver.quit()