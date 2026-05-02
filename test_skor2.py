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

driver.get("https://www.spordb.com/iddaa-programi/")
time.sleep(15)

print("📋 Sayfa başlığı:", driver.title)
print("\n📄 Body text ilk 500 karakter:")
body = driver.find_element(By.TAG_NAME, "body")
print(body.text[:500])

print("\n🔍 Seçilebilir elementler:")
elements = driver.find_elements(By.CSS_SELECTOR, "select, [id*=date], [id*=hafta], [name*=date], [name*=hafta], [class*=date], [class*=hafta]")
print(f"   {len(elements)} element bulundu")
for i, el in enumerate(elements[:10]):
    tag = el.tag_name
    id_ = el.get_attribute("id") or ""
    name = el.get_attribute("name") or ""
    cls = el.get_attribute("class") or ""
    print(f"   [{i}] <{tag}> id='{id_}' name='{name}' class='{cls[:30]}'")

input("Enter...")
driver.quit()