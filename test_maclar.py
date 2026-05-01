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

url = "https://www.iddaa.com/program/futbol?date=01.05.2026"
print(f"📡 {url}")
driver.get(url)
time.sleep(15)

# Body text'teki tüm maçları say
body = driver.find_element(By.TAG_NAME, "body")
text = body.text
lines = text.split("\n")

# Saat formatında satırları say (HH:MM)
saat_sayisi = 0
mac_isimleri = []
for i, line in enumerate(lines):
    line = line.strip()
    if len(line) == 5 and line[2] == ":" and line[:2].isdigit() and line[3:5].isdigit():
        # Sonraki satırda takım adı olmalı
        if i + 2 < len(lines) and " - " not in lines[i+1] and lines[i+1].strip() != "-":
            saat_sayisi += 1

# Takım elementleri
takim_els = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
print(f"📋 Takım elementleri: {takim_els and len(takim_els)}")

# Tüm maç satırları
mac_satirlari = driver.find_elements(By.CSS_SELECTOR, ".i_mc__MDEbN")
print(f"📋 Maç satırları: {len(mac_satirlari)}")

# ÖNE ÇIKANLAR var mı?
if "ÖNE ÇIKAN" in text:
    print("⚠️ ÖNE ÇIKANLAR aktif!")
else:
    print("✅ ÖNE ÇIKANLAR yok")

# Sayfadaki toplam maç sayısını bul
# "FUTBOL" yanında yazan sayı
for line in lines[:20]:
    if "FUTBOL" in line:
        print(f"📊 {line.strip()}")

# Butonlar
buttons = driver.find_elements(By.TAG_NAME, "button")
for btn in buttons:
    txt = btn.text.strip()
    if txt and len(txt) < 30:
        cls = btn.get_attribute("class") or ""
        visible = btn.is_displayed()
        print(f"🔘 '{txt}' visible={visible}")

print(f"\n📄 Sayfa satır sayısı: {len(lines)}")
print(f"📄 Sayfadaki toplam metin: {len(text)} karakter")

# Ekranın altındaki "Daha fazla" butonunu JavaScript ile bul
print("\n🔍 JavaScript ile maç sayısı:")
try:
    count = driver.execute_script("return document.querySelectorAll('.i_mc__MDEbN').length")
    print(f"   .i_mc__MDEbN: {count}")
    count2 = driver.execute_script("return document.querySelectorAll('.i_tnw__t8AmC').length")
    print(f"   .i_tnw__t8AmC: {count2}")
    count3 = driver.execute_script("return document.querySelectorAll('[class*=match]').length")
    print(f"   [class*=match]: {count3}")
except:
    pass

# 504 kontrolü
if "504" in text or "Gateway" in text:
    print("🛑 504 HATASI!")

input("\nEnter...")
driver.quit()