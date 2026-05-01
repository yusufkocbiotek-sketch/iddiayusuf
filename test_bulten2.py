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

driver.get("https://www.iddaa.com/program/futbol?date=01.05.2026")
time.sleep(12)

print("1. Baslangic:", len(driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")))

# Adim 1: Tüm Bülteni Göster
for btn in driver.find_elements(By.TAG_NAME, "button"):
    if "Bülteni" in btn.text:
        print("   -> Tum Bulteni Goster tiklandi")
        driver.execute_script("arguments[0].click()", btn)
        break
time.sleep(10)
print("2. Bulten sonrasi:", len(driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")))

# Adim 2: Devamini gor + Daha fazla goster (tekrarlı)
for tur in range(30):
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
    if tur % 5 == 0 or not tiklandi:
        print(f"   Tur {tur}: {sayi} mac (tiklandi={tiklandi})")
    
    if not tiklandi:
        break

print("3. Final:", len(driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")))

input("Enter...")
driver.quit()