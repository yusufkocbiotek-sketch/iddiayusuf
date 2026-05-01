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

# Ekran görüntüsü al
driver.save_screenshot("mackolik_ss.png")
print("📸 Ekran görüntüsü → mackolik_ss.png")

# 1. "Tarihe göre" linkine tıkla
print("\n1️⃣ 'Tarihe göre' LİNKİNE TIKLA:")
print("="*60)
try:
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        if "Tarihe göre" in link.text:
            print(f"  Bulundu: '{link.text}' href='{link.get_attribute('href')}'")
            link.click()
            time.sleep(8)
            print(f"  URL: {driver.current_url}")
            
            # Yeni sayfadaki metni oku
            body = driver.find_element(By.TAG_NAME, "body")
            lines = body.text.split("\n")
            
            print(f"  {len(lines)} satır")
            print("\n  İLK 30 SATIR:")
            for i in range(min(30, len(lines))):
                if lines[i].strip():
                    print(f"    {i}: {lines[i].strip()[:70]}")
            
            # Ekran görüntüsü
            driver.save_screenshot("mackolik_tarihe_gore.png")
            print("  📸 → mackolik_tarihe_gore.png")
            break
except Exception as e:
    print(f"  ❌ {e}")

# 2. Şimdi bu sayfadaki ok/tarih butonlarını ara
print("\n2️⃣ YENİ SAYFADAKİ BUTONLAR:")
print("="*60)

# Tüm elementleri tara - < > ok işaretleri
all_els = driver.find_elements(By.CSS_SELECTOR, "a, span, div, i, button, img")
for el in all_els:
    try:
        txt = el.text.strip()
        cls = el.get_attribute("class") or ""
        onclick = el.get_attribute("onclick") or ""
        href = el.get_attribute("href") or ""
        
        if txt in ["<","«","◄","‹","←",">","»","►","›","→"] or \
           any(k in cls.lower() for k in ["prev","next","arrow","chevron","nav-left","nav-right"]) or \
           any(k in onclick.lower() for k in ["prev","next","date","tarih"]):
            print(f"  <{el.tag_name}> text='{txt}' class='{cls[:40]}' onclick='{onclick[:50]}' href='{href[:50]}'")
    except:
        continue

# 3. Sayfadaki TÜM linkleri göster (tarih ile ilgili)
print("\n3️⃣ TÜM LİNKLER:")
print("="*60)
links = driver.find_elements(By.TAG_NAME, "a")
for link in links[:80]:
    href = link.get_attribute("href") or ""
    txt = link.text.strip()
    if txt and len(txt) < 40:
        print(f"  '{txt}' → {href[:60]}")

# 4. Hepsi seçiliyken maç satırlarını doğru parse et
print("\n4️⃣ MAÇ PARSE (Hepsi):")
print("="*60)

driver.get("https://arsiv.mackolik.com/Iddaa-Programi")
time.sleep(10)

try:
    for btn in driver.find_elements(By.TAG_NAME, "button"):
        if "Kabul" in btn.text:
            btn.click()
            time.sleep(2)
            break
except:
    pass

# Tabloyu doğrudan al
tables = driver.find_elements(By.TAG_NAME, "table")
for table in tables:
    rows = table.find_elements(By.TAG_NAME, "tr")
    if len(rows) < 20:
        continue
    
    print(f"  Tablo: {len(rows)} satır")
    mac_sayisi = 0
    
    for row in rows:
        cls = row.get_attribute("class") or ""
        cells = row.find_elements(By.CSS_SELECTOR, "td")
        
        # 1 hücreli = lig veya tarih başlığı
        if len(cells) == 1:
            txt = cells[0].text.strip()
            if txt and len(txt) > 2:
                if mac_sayisi < 20:
                    print(f"\n  📌 BASLIK: '{txt[:50]}' class='{cls[:30]}'")
            continue
        
        # Çok hücreli = maç veya header
        if len(cells) >= 10:
            hucre = [c.text.strip() for c in cells]
            saat = hucre[0]
            
            if ":" in saat and len(saat) <= 5:
                mac_sayisi += 1
                if mac_sayisi <= 10:
                    # Takım adlarını bul
                    takim_text = ""
                    for h in hucre:
                        if " - " in h:
                            takim_text = h
                            break
                    
                    skor = ""
                    iy_skor = ""
                    oranlar = []
                    
                    for h in hucre[1:]:
                        if " - " in h and not any(c.isalpha() for c in h.replace(" ","").replace("-","")):
                            if not skor:
                                skor = h
                            elif not iy_skor:
                                iy_skor = h
                        elif h.replace(".","").replace(",","").isdigit() and "." in h:
                            oranlar.append(h)
                    
                    print(f"  [{mac_sayisi}] {saat} | {takim_text} | MS:{skor} IY:{iy_skor} | Oranlar: {' '.join(oranlar[:6])}")
    
    print(f"\n  📊 Toplam {mac_sayisi} maç")
    break

print("\n" + "="*60)
input("⏸️ Enter'a basın...")
driver.quit()