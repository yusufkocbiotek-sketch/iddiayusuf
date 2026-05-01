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

print("📡 spordb.com açılıyor...")
driver.get("https://www.spordb.com/iddaa-programi/")
time.sleep(10)

print(f"📋 Sayfa: {driver.title}")
print(f"🌐 URL: {driver.current_url}")
print("="*60)

# Sayfadaki tüm metni al
body = driver.find_element(By.TAG_NAME, "body")
text = body.text
lines = text.split("\n")

print(f"📄 Toplam {len(lines)} satır")
print("\n📄 İLK 80 SATIR:")
print("="*60)
for i, line in enumerate(lines[:80]):
    if line.strip():
        print(f"  {i}: {line.strip()}")

# Tablo var mı?
print("\n🔍 TABLO ANALİZİ:")
print("="*60)
tables = driver.find_elements(By.TAG_NAME, "table")
print(f"  {len(tables)} tablo bulundu")

for idx, table in enumerate(tables[:3]):
    rows = table.find_elements(By.TAG_NAME, "tr")
    print(f"\n  Tablo {idx}: {len(rows)} satır")
    for i, row in enumerate(rows[:5]):
        cells = row.find_elements(By.CSS_SELECTOR, "td, th")
        txt = " | ".join([c.text.strip()[:20] for c in cells])
        print(f"    [{i}] {txt}")

# Link analizi - geçmiş sonuçlar var mı?
print("\n🔍 GEÇMİŞ SONUÇLAR LİNKLERİ:")
print("="*60)
links = driver.find_elements(By.TAG_NAME, "a")
for link in links:
    href = link.get_attribute("href") or ""
    txt = link.text.strip()
    if any(k in href.lower() or k in txt.lower() for k in ["sonuc", "gecmis", "arsiv", "tarih", "result", "history", "biten"]):
        print(f"  '{txt}' → {href}")

# Class analizi
print("\n🔍 İLGİLİ CLASS'LAR:")
print("="*60)
all_els = driver.find_elements(By.CSS_SELECTOR, "div[class], table[class], tr[class]")
classes = set()
for el in all_els[:500]:
    cls = el.get_attribute("class") or ""
    for c in cls.split():
        lo = c.lower()
        if any(k in lo for k in ["match","mac","game","oran","odds","score","skor","event","fixture","row","list","table","result","sonuc"]):
            classes.add(c)

for cn in sorted(classes):
    count = len(driver.find_elements(By.CSS_SELECTOR, f".{cn}"))
    print(f"  .{cn} → {count}")

print("\n" + "="*60)
input("⏸️ Enter'a basın...")
driver.quit()