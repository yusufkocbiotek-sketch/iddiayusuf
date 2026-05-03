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

url = f"https://www.iddaa.com/program/futbol?date=03.05.2026"
driver.get(url)
time.sleep(15)

print("1. Başlangıç:", len(driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")))

# Sayfadaki tüm saatleri bul
saatler = []
try:
    # Saatler genelde belirli bir class içinde olur
    saat_els = driver.find_elements(By.CSS_SELECTOR, "[class*='saat'], [class*='time'], [class*='hour']")
    for el in saat_els:
        txt = el.text.strip()
        if len(txt) == 5 and ":" in txt:
            if txt not in saatler:
                saatler.append(txt)
except:
    pass

# Eğer class ile bulamazsak, body text'ten bul
if not saatler:
    body = driver.find_element(By.TAG_NAME, "body")
    lines = body.text.split("\n")
    for line in lines:
        txt = line.strip()
        if len(txt) == 5 and ":" in txt and txt[:2].isdigit():
            if txt not in saatler:
                saatler.append(txt)

print(f"\nBulunan saatler: {saatler}")

# Her saat grubundaki maçları say
for saat in saatler:
    mac_sayisi = 0
    body = driver.find_element(By.TAG_NAME, "body")
    lines = body.text.split("\n")
    
    for i, line in enumerate(lines):
        if line.strip() == saat:
            # Bu saatten sonraki maçları say
            for j in range(i + 1, len(lines)):
                # Bir sonraki saate veya gün sonuna kadar
                next_line = lines[j].strip()
                if len(next_line) == 5 and ":" in next_line and next_line[:2].isdigit():
                    break
                
                # Takım adı formatı
                if " - " in next_line and len(next_line) > 5:
                    mac_sayisi += 1
    
    print(f"  Saat {saat}: ~{mac_sayisi} maç")

input("Enter...")
driver.quit()