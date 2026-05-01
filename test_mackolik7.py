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

# İlk maç satırını bul ve tıkla
print("🖱️ İLK MAÇA TIKLANIYOR...")
print("="*60)

tables = driver.find_elements(By.TAG_NAME, "table")
for table in tables:
    rows = table.find_elements(By.TAG_NAME, "tr")
    if len(rows) < 20:
        continue
    
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, "td")
        if len(cells) < 10:
            continue
        
        hucre = [c.text.strip() for c in cells]
        saat = hucre[0]
        
        if ":" not in saat or len(saat) > 5:
            continue
        
        # Takım adını bul
        takim = ""
        for h in hucre:
            if " - " in h and len(h) > 5:
                takim = h
                break
        
        if not takim:
            continue
        
        print(f"  Maç: {saat} {takim}")
        
        # Takım adı linkine tıkla
        links = row.find_elements(By.TAG_NAME, "a")
        for link in links:
            txt = link.text.strip()
            href = link.get_attribute("href") or ""
            if " - " in txt or "Match" in href or "mac" in href.lower():
                print(f"  Link: '{txt[:40]}' → {href[:60]}")
                
                # Tıkla
                try:
                    driver.execute_script("arguments[0].click();", link)
                    time.sleep(8)
                    
                    print(f"  URL: {driver.current_url}")
                    print(f"  Başlık: {driver.title[:60]}")
                    
                    # Yeni sayfadaki veriyi oku
                    body = driver.find_element(By.TAG_NAME, "body")
                    text = body.text
                    lines = text.split("\n")
                    
                    print(f"\n  📄 {len(lines)} satır")
                    print("\n  İLK 100 SATIR:")
                    for i in range(min(100, len(lines))):
                        if lines[i].strip():
                            print(f"    {i}: {lines[i].strip()[:70]}")
                    
                    # Oran tablosu var mı?
                    print("\n  🔍 ORAN TABLOLARI:")
                    new_tables = driver.find_elements(By.TAG_NAME, "table")
                    print(f"  {len(new_tables)} tablo")
                    
                    for ti, t in enumerate(new_tables):
                        trows = t.find_elements(By.TAG_NAME, "tr")
                        if len(trows) > 3:
                            print(f"\n  Tablo {ti}: {len(trows)} satır")
                            for ri, r in enumerate(trows[:10]):
                                tcells = r.find_elements(By.CSS_SELECTOR, "td, th")
                                txt = " | ".join([c.text.strip()[:20] for c in tcells if c.text.strip()])
                                if txt:
                                    print(f"    [{ri}] {txt}")
                    
                except Exception as e:
                    print(f"  ❌ Tıklama hatası: {e}")
                
                break
        break
    break

# Eğer sayfa değişmediyse, satır tıklanabilir mi dene
if driver.current_url == "https://arsiv.mackolik.com/Iddaa-Programi":
    print("\n\n🖱️ SATIR TIKLAMASI DENENİYOR...")
    print("="*60)
    
    tables = driver.find_elements(By.TAG_NAME, "table")
    for table in tables:
        rows = table.find_elements(By.TAG_NAME, "tr")
        if len(rows) < 20:
            continue
        
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            if len(cells) < 10:
                continue
            
            hucre = [c.text.strip() for c in cells]
            if ":" not in hucre[0]:
                continue
            
            # Satırın kendisine tıkla
            print(f"  Satıra tıklanıyor: {hucre[0]}")
            try:
                row.click()
                time.sleep(5)
                
                # Sayfada değişiklik oldu mu?
                body = driver.find_element(By.TAG_NAME, "body")
                new_text = body.text
                
                if "Maç Sonucu" in new_text or "Alt/Üst" in new_text or "Handikap" in new_text:
                    print("  ✅ Detay oranlar açıldı!")
                    lines = new_text.split("\n")
                    for i, line in enumerate(lines):
                        if any(k in line for k in ["Maç Sonucu", "Alt/Üst", "Handikap", "Karşılıklı", "İlk Yarı"]):
                            print(f"    {i}: {line[:70]}")
                else:
                    print(f"  URL: {driver.current_url}")
                    
            except:
                # Hücrelere tek tek tıkla
                for ci, cell in enumerate(cells):
                    try:
                        cell.click()
                        time.sleep(3)
                        if driver.current_url != "https://arsiv.mackolik.com/Iddaa-Programi":
                            print(f"  ✅ Hücre [{ci}] tıklandı! URL: {driver.current_url}")
                            break
                    except:
                        continue
            break
        break

print("\n" + "="*60)
input("⏸️ Enter'a basın...")
driver.quit()