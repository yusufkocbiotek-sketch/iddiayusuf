import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

print("📡 iddaa.com açılıyor...")
driver.get("https://www.iddaa.com/program/futbol")
time.sleep(10)

print(f"📋 Sayfa: {driver.title}")
print("="*60)

# event-group içeriğini al
print("🔍 EVENT-GROUP İÇERİĞİ:")
print("="*60)
try:
    eg = driver.find_element(By.CSS_SELECTOR, ".event-group")
    text = eg.text
    lines = text.split("\n")
    for i, line in enumerate(lines[:80]):
        if line.strip():
            print(f"  {i}: {line.strip()}")
except:
    print("  event-group bulunamadı")

print("\n" + "="*60)

# flex-row içeriklerini al (ilk 10 tane)
print("🔍 İLK 10 FLEX-ROW İÇERİĞİ:")
print("="*60)
try:
    rows = driver.find_elements(By.CSS_SELECTOR, ".flex-row")
    for i, row in enumerate(rows[:10]):
        text = row.text.strip()
        if text:
            print(f"\n  --- FLEX-ROW {i} ---")
            print(f"  {text[:200]}")
except:
    print("  flex-row bulunamadı")

print("\n" + "="*60)

# Sayfanın tüm metnini al (ilk 80 satır)
print("📄 SAYFA METNİ (İLK 80 SATIR):")
print("="*60)
try:
    body = driver.find_element(By.TAG_NAME, "body")
    text = body.text
    lines = text.split("\n")
    for i, line in enumerate(lines[:80]):
        if line.strip():
            print(f"  {i}: {line.strip()}")
except:
    print("  body bulunamadı")

print("\n" + "="*60)
input("⏸️ Enter'a basın Chrome kapansın...")
driver.quit()