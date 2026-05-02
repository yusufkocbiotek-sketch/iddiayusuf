import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.spordb.com/iddaa-programi/")
time.sleep(10)

# Sayfadaki her şeyi göster
body = driver.find_element(By.TAG_NAME, "body")
print("📄 Sayfa içeriği:")
print(body.text[:2000])

# Butonları kontrol et
buttons = driver.find_elements(By.TAG_NAME, "button")
print(f"\n🔘 {len(buttons)} buton bulundu")
for i, btn in enumerate(buttons[:10]):
    print(f"   [{i}] '{btn.text.strip()}'")

input("Enter...")
driver.quit()
