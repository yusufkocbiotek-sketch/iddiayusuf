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

print("📡 spordb.com açılıyor...")
driver.get("https://www.spordb.com/iddaa-programi/")
time.sleep(10)

print("🔍 Select'ları arıyorum...")
selects = driver.find_elements(By.TAG_NAME, "select")
print(f"   {len(selects)} select bulundu")

for i, sel in enumerate(selects):
    opts = sel.find_elements(By.TAG_NAME, "option")
    print(f"\n   Select {i}: {len(opts)} seçenek")
    for j, opt in enumerate(opts[:5]):
        print(f"      [{j}] '{opt.text.strip()[:30]}' value='{opt.get_attribute('value')}'")

input("Enter...")
driver.quit()