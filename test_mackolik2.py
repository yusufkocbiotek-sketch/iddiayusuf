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

# Cookie popup kapat
print("📡 mackolik iddaa sayfası açılıyor...")
driver.get("https://arsiv.mackolik.com/Iddaa-Programi")
time.sleep(8)

# Cookie kabul et
try:
    btns = driver.find_elements(By.TAG_NAME, "button")
    for btn in btns:
        if "Kabul" in btn.text or "Accept" in btn.text:
            btn.click()
            time.sleep(2)
            break
except:
    pass

print(f"📋 {driver.title}")
print("="*60)

# Sayfadaki ilk 60 satır
body = driver.find_element(By.TAG_NAME, "body")
lines = body.text.split("\n")
print(f"📄 {len(lines)} satır")
print("\n📄 SATIR 10-80:")
print("="*60)
for i in range(10, min(80, len(lines))):
    if lines[i].strip():
        print(f"  {i}: {lines[i].strip()[:80]}")

# Tüm tabloları analiz et
print("\n🔍 TABLOLAR:")
print("="*60)
tables = driver.find_elements(By.TAG_NAME, "table")
print(f"  {len(tables)} tablo")

for idx, table in enumerate(tables):
    rows = table.find_elements(By.TAG_NAME, "tr")
    if len(rows) < 5:
        continue
    print(f"\n  === TABLO {idx}: {len(rows)} satır ===")
    for i, row in enumerate(rows[:8]):
        cells = row.find_elements(By.CSS_SELECTOR, "td, th")
        if cells:
            print(f"  [{i}] ({len(cells)} hücre)")
            for j, cell in enumerate(cells[:20]):
                txt = cell.text.strip()[:30]
                cls = cell.get_attribute("class") or ""
                if txt:
                    print(f"      [{j}] cls='{cls[:20]}' → '{txt}'")

# Tarih seçimi var mı?
print("\n🔍 TARİH SEÇİMİ:")
print("="*60)
selects = driver.find_elements(By.TAG_NAME, "select")
print(f"  {len(selects)} select")
for idx, sel in enumerate(selects):
    opts = sel.find_elements(By.TAG_NAME, "option")
    sel_id = sel.get_attribute("id") or ""
    sel_name = sel.get_attribute("name") or ""
    print(f"\n  Select {idx}: id='{sel_id}' name='{sel_name}' ({len(opts)} seçenek)")
    for j, opt in enumerate(opts[:10]):
        print(f"    [{j}] value='{opt.get_attribute('value')[:30]}' text='{opt.text.strip()[:40]}'")
    if len(opts) > 10:
        print(f"    ... ve {len(opts)-10} daha")

# Geçmiş tarihlere link var mı?
print("\n🔍 TARİH LİNKLERİ:")
print("="*60)
links = driver.find_elements(By.TAG_NAME, "a")
for link in links:
    href = link.get_attribute("href") or ""
    txt = link.text.strip()
    if "Iddaa" in href and ("Date" in href or "date" in href or "hafta" in href or "202" in href):
        print(f"  '{txt[:30]}' → {href[:80]}")

# URL pattern testi - geçmiş tarihler
print("\n🌐 GEÇMİŞ TARİH URL TESTİ:")
print("="*60)
test_urls = [
    "https://arsiv.mackolik.com/Iddaa-Programi?date=2026-04-28",
    "https://arsiv.mackolik.com/Iddaa-Programi?date=28.04.2026",
    "https://arsiv.mackolik.com/Iddaa-Programi/28.04.2026",
    "https://arsiv.mackolik.com/Iddaa-Programi?Date=2026-04-28",
]

for url in test_urls:
    try:
        driver.get(url)
        time.sleep(4)
        title = driver.title
        rows = len(driver.find_elements(By.TAG_NAME, "tr"))
        print(f"  {url}")
        print(f"    Başlık: {title[:60]}")
        print(f"    Satır: {rows}")
        if "404" not in title:
            body = driver.find_element(By.TAG_NAME, "body")
            text = body.text[200:400]
            print(f"    İçerik: {text[:150]}")
        print()
    except:
        print(f"  {url} → HATA\n")

print("="*60)
input("⏸️ Enter'a basın...")
driver.quit()