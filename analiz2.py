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

# İlk maçı bul ve tıklanabilir elementleri ara
print("🔍 İLK MAÇ ÇEVRESİNDEKİ TIKLANABILIR ELEMENTLER:")
print("="*60)

# Tüm buton ve link elementlerini bul
clickables = driver.find_elements(By.CSS_SELECTOR, "button, a, [role='button'], [onclick], [class*='detail'], [class*='expand'], [class*='arrow'], [class*='more'], [class*='info'], [class*='open'], [class*='toggle'], [class*='click'], [class*='icon'], svg")

print(f"📋 Toplam {len(clickables)} tıklanabilir element bulundu\n")

for i, el in enumerate(clickables[:40]):
    tag = el.tag_name
    cls = el.get_attribute("class") or ""
    txt = el.text.strip()[:50] if el.text else ""
    href = el.get_attribute("href") or ""
    onclick = el.get_attribute("onclick") or ""
    
    if txt or cls:
        print(f"  [{i}] <{tag}> class='{cls}' text='{txt}' href='{href[:60]}'")

print("\n" + "="*60)

# event-group içindeki tüm alt elementleri incele
print("🔍 EVENT-GROUP İÇİNDEKİ ALT ELEMENTLER:")
print("="*60)

try:
    eg = driver.find_element(By.CSS_SELECTOR, ".event-group")
    children = eg.find_elements(By.CSS_SELECTOR, "a, button, [role='button'], div[class]")
    
    for i, child in enumerate(children[:50]):
        tag = child.tag_name
        cls = child.get_attribute("class") or ""
        txt = child.text.strip()[:80] if child.text else ""
        href = child.get_attribute("href") or ""
        
        if cls and ("row" in cls.lower() or "event" in cls.lower() or "match" in cls.lower() or "detail" in cls.lower() or "button" in cls.lower() or "link" in cls.lower() or "icon" in cls.lower() or "arrow" in cls.lower() or "expand" in cls.lower()):
            print(f"  [{i}] <{tag}> class='{cls}'")
            if href:
                print(f"       href='{href[:80]}'")
            if txt:
                print(f"       text='{txt[:80]}'")
            print()
except:
    print("  event-group bulunamadı")

print("\n" + "="*60)

# Şimdi ilk maça tıklamayı deneyelim
print("🖱️ İLK MAÇA TIKLANMAYA ÇALIŞILIYOR...")
print("="*60)

try:
    # İlk maçın satırını bul
    eg = driver.find_element(By.CSS_SELECTOR, ".event-group")
    
    # event-group içindeki linkleri veya tıklanabilir div'leri bul
    links = eg.find_elements(By.CSS_SELECTOR, "a[href]")
    print(f"  📋 event-group içinde {len(links)} link bulundu")
    
    for i, link in enumerate(links[:10]):
        href = link.get_attribute("href") or ""
        txt = link.text.strip()[:60] if link.text else ""
        print(f"  [{i}] href='{href}' text='{txt}'")
    
    # İlk maç linkine tıkla
    if links:
        ilk_link = None
        for link in links:
            href = link.get_attribute("href") or ""
            if "/mac-detay/" in href or "/detail/" in href or "/program/" in href:
                ilk_link = link
                break
        
        if not ilk_link:
            ilk_link = links[0]
        
        href = ilk_link.get_attribute("href")
        print(f"\n  🖱️ Tıklanıyor: {href}")
        ilk_link.click()
        time.sleep(5)
        
        print(f"  📋 Yeni sayfa: {driver.title}")
        print(f"  🌐 URL: {driver.current_url}")
        
        # Detay sayfasının içeriğini al
        body = driver.find_element(By.TAG_NAME, "body")
        text = body.text
        lines = text.split("\n")
        
        print(f"\n  📄 DETAY SAYFASI İLK 100 SATIR:")
        print("  " + "="*50)
        for i, line in enumerate(lines[:100]):
            if line.strip():
                print(f"    {i}: {line.strip()}")
    
except Exception as e:
    print(f"  ❌ Hata: {e}")

print("\n" + "="*60)
input("⏸️ Enter'a basın Chrome kapansın...")
driver.quit()