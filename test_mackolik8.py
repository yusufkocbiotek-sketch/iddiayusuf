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

print("📡 mackolik açılıyor...")
driver.get("https://arsiv.mackolik.com/Iddaa-Programi")
time.sleep(10)

# Cookie kapat
try:
    for btn in driver.find_elements(By.TAG_NAME, "button"):
        if "Kabul" in btn.text:
            btn.click()
            time.sleep(2)
            break
except:
    pass

# İlk maç satırına tıkla
print("🖱️ İlk maça tıklanıyor...")
tables = driver.find_elements(By.TAG_NAME, "table")
for table in tables:
    rows = table.find_elements(By.TAG_NAME, "tr")
    if len(rows) < 20:
        continue
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, "td")
        if len(cells) < 10:
            continue
        if ":" not in cells[0].text.strip():
            continue
        
        print(f"  Maç: {cells[0].text.strip()}")
        row.click()
        time.sleep(8)
        
        # Scroll aşağı (detay panel aşağıda olabilir)
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        
        # Sayfadaki TÜM metni tara - oran anahtar kelimeleri
        body = driver.find_element(By.TAG_NAME, "body")
        text = body.text
        lines = text.split("\n")
        
        # "Maç Sonucu" kelimesini bul ve etrafını göster
        print("\n📊 DETAY ORAN İÇERİĞİ:")
        print("="*60)
        
        for i, line in enumerate(lines):
            ls = line.strip()
            if any(k in ls for k in ["Maç Sonucu", "Alt Üst", "Çifte Şans", "İlk Yarı", "Karş. Gol", "Toplam Gol", "Handikap"]):
                # Bu satır ve sonraki 30 satırı göster
                print(f"\n  >>> BÖLÜM BULUNDU (satır {i}): {ls}")
                for j in range(i, min(i+30, len(lines))):
                    if lines[j].strip():
                        print(f"    {j}: {lines[j].strip()[:70]}")
        
        # Popup/modal/panel var mı?
        print("\n🔍 POPUP/PANEL ANALİZİ:")
        print("="*60)
        
        popups = driver.find_elements(By.CSS_SELECTOR, "[class*='popup'], [class*='modal'], [class*='panel'], [class*='detail'], [class*='detay'], [class*='overlay'], iframe")
        for p in popups:
            cls = p.get_attribute("class") or ""
            txt = p.text.strip()[:200]
            tag = p.tag_name
            if txt:
                print(f"  <{tag}> class='{cls[:40]}' text='{txt[:100]}'")
        
        # iframe var mı?
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"\n  {len(iframes)} iframe bulundu")
        for idx, iframe in enumerate(iframes):
            src = iframe.get_attribute("src") or ""
            cls = iframe.get_attribute("class") or ""
            style = iframe.get_attribute("style") or ""
            print(f"  iframe {idx}: src='{src[:60]}' class='{cls[:30]}' style='{style[:40]}'")
            
            # iframe'e geç ve içeriğini oku
            if src:
                try:
                    driver.switch_to.frame(iframe)
                    time.sleep(3)
                    
                    ibody = driver.find_element(By.TAG_NAME, "body")
                    itext = ibody.text
                    ilines = itext.split("\n")
                    
                    print(f"  iframe {idx} İÇERİĞİ ({len(ilines)} satır):")
                    for j, il in enumerate(ilines[:50]):
                        if il.strip():
                            print(f"    {j}: {il.strip()[:70]}")
                    
                    driver.switch_to.default_content()
                except:
                    driver.switch_to.default_content()
        
        break
    break

print("\n" + "="*60)
input("⏸️ Enter'a basın...")
driver.quit()