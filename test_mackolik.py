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

print("📡 arsiv.mackolik.com açılıyor...")
driver.get("https://arsiv.mackolik.com/")
time.sleep(10)

print(f"📋 Sayfa: {driver.title}")
print(f"🌐 URL: {driver.current_url}")
print("="*60)

# Sayfadaki metni al
body = driver.find_element(By.TAG_NAME, "body")
lines = body.text.split("\n")

print(f"📄 {len(lines)} satır")
print("\n📄 İLK 80 SATIR:")
print("="*60)
for i, line in enumerate(lines[:80]):
    if line.strip():
        print(f"  {i}: {line.strip()[:70]}")

# Linkleri analiz et
print("\n🔍 ÖNEMLİ LİNKLER:")
print("="*60)
links = driver.find_elements(By.TAG_NAME, "a")
for link in links[:100]:
    href = link.get_attribute("href") or ""
    txt = link.text.strip()
    if txt and len(txt) > 2 and ("iddaa" in href.lower() or "iddaa" in txt.lower() or "sonuc" in href.lower() or "program" in href.lower() or "bulten" in href.lower()):
        print(f"  '{txt[:40]}' → {href[:80]}")

# Tablo analizi
print("\n🔍 TABLOLAR:")
print("="*60)
tables = driver.find_elements(By.TAG_NAME, "table")
print(f"  {len(tables)} tablo")
for idx, table in enumerate(tables[:3]):
    rows = table.find_elements(By.TAG_NAME, "tr")
    print(f"\n  Tablo {idx}: {len(rows)} satır")
    for i, row in enumerate(rows[:5]):
        cells = row.find_elements(By.CSS_SELECTOR, "td, th")
        txt = " | ".join([c.text.strip()[:25] for c in cells if c.text.strip()])
        if txt:
            print(f"    [{i}] {txt}")

# İddaa sayfalarını dene
print("\n🌐 URL TESTLERİ:")
print("="*60)
test_urls = [
    "https://arsiv.mackolik.com/Iddaa-Programi",
    "https://arsiv.mackolik.com/iddaa",
    "https://arsiv.mackolik.com/Iddaa-Sonuclari",
    "https://arsiv.mackolik.com/Canli-Sonuclar",
    "https://arsiv.mackolik.com/Puan-Durumu",
]

for url in test_urls:
    try:
        driver.get(url)
        time.sleep(4)
        maclar_count = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
        print(f"  {url}")
        print(f"    Başlık: {driver.title[:50]}")
        print(f"    Satır: {maclar_count}")
        
        body = driver.find_element(By.TAG_NAME, "body")
        text = body.text[:300]
        print(f"    İçerik: {text[:150]}")
        print()
    except:
        print(f"  {url} → HATA")

print("\n" + "="*60)
input("⏸️ Enter'a basın...")
driver.quit()