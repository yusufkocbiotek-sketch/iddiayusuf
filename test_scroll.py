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
time.sleep(10)

maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
print(f"Baslangic: {len(maclar)} mac")

# Sadece butonlara tıkla, scroll yapma
for tur in range(30):
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        tiklandi = False
        for btn in buttons:
            try:
                txt = btn.text.strip()
                if "Devamını gör" in txt or "Daha fazla" in txt:
                    print(f"  Tur {tur}: '{txt}' tıklanıyor...")
                    driver.execute_script("arguments[0].click();", btn)
                    tiklandi = True
                    time.sleep(5)
                    break
            except:
                continue
        
        if not tiklandi:
            print(f"  Tur {tur}: Buton bulunamadı")
            break
        
        maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
        print(f"  Sonuc: {len(maclar)} mac")
        
    except:
        break

maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
print(f"\nFinal: {len(maclar)} mac")

# İlk ve son maç adı
if maclar:
    print(f"Ilk: {maclar[0].text.strip()[:40]}")
    print(f"Son: {maclar[-1].text.strip()[:40]}")

input("Enter...")
driver.quit()