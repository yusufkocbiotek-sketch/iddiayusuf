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

print("Once:", len(driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")))

for btn in driver.find_elements(By.TAG_NAME, "button"):
    if "Bülteni" in btn.text or "Tüm" in btn.text:
        print("Tiklaniyor:", btn.text.strip())
        driver.execute_script("arguments[0].click()", btn)
        break

time.sleep(15)
print("Sonra:", len(driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")))

input("Enter...")
driver.quit()