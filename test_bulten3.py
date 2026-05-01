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

# Test 1: Date ile
print("1️⃣ DATE ILE (?date=01.05.2026):")
driver.get("https://www.iddaa.com/program/futbol?date=01.05.2026")
time.sleep(12)
print(f"   Baslangic: {len(driver.find_elements(By.CSS_SELECTOR, '.i_tnw__t8AmC'))} mac")

# Tüm Bülteni Göster tıkla
for btn in driver.find_elements(By.TAG_NAME, "button"):
    if "Bülteni" in btn.text:
        driver.execute_script("arguments[0].click()", btn)
        print("   Tum Bulteni tiklandi")
        break
time.sleep(10)
print(f"   Sonra: {len(driver.find_elements(By.CSS_SELECTOR, '.i_tnw__t8AmC'))} mac")
print(f"   URL: {driver.current_url}")

# Test 2: Date olmadan
print("\n2️⃣ DATE OLMADAN (ana sayfa):")
driver.get("https://www.iddaa.com/program/futbol")
time.sleep(12)
print(f"   Baslangic: {len(driver.find_elements(By.CSS_SELECTOR, '.i_tnw__t8AmC'))} mac")

for btn in driver.find_elements(By.TAG_NAME, "button"):
    if "Bülteni" in btn.text:
        driver.execute_script("arguments[0].click()", btn)
        print("   Tum Bulteni tiklandi")
        break
time.sleep(10)

sayi = len(driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC"))
print(f"   Sonra: {sayi} mac")
print(f"   URL: {driver.current_url}")

# Devamını gör + Daha fazla tekrarla
for tur in range(50):
    tiklandi = False
    for btn in driver.find_elements(By.TAG_NAME, "button"):
        try:
            txt = btn.text.strip()
            if "Devamını gör" in txt or "Daha fazla" in txt:
                driver.execute_script("arguments[0].click()", btn)
                tiklandi = True
                time.sleep(5)
                break
        except:
            continue
    
    sayi = len(driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC"))
    if tur % 5 == 0:
        print(f"   Tur {tur}: {sayi} mac")
    if not tiklandi:
        break

print(f"\n   Final: {len(driver.find_elements(By.CSS_SELECTOR, '.i_tnw__t8AmC'))} mac")

# Test 3: Tüm Bülteni tıkladıktan sonra URL ne oldu?
print(f"\n3️⃣ URL ANALİZİ:")
print(f"   URL: {driver.current_url}")

# Sayfadaki FUTBOL sayısını bul
body = driver.find_element(By.TAG_NAME, "body")
text = body.text
for line in text.split("\n"):
    line = line.strip()
    if "FUTBOL" in line and any(c.isdigit() for c in line):
        print(f"   {line}")

input("\nEnter...")
driver.quit()