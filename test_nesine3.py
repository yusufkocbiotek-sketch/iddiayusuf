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

url = "https://www.nesine.com/iddaa/canli-skor/futbol"
print(f"📡 {url}")
driver.get(url)
time.sleep(15)

body = driver.find_element(By.TAG_NAME, "body")
text = body.text[:4000]
print("\n📄 İlk 3000 karakter:")
print(text)

# Tarihlere bak
print("\n📅 Tarihler:")
for line in text.split("\n"):
    if "2026" in line or "2025" in line:
        print(f"   {line.strip()[:60]}")

# Select'ları
selects = driver.find_elements(By.TAG_NAME, "select")
print(f"\n📅 {len(selects)} select bulundu")

for i, sel in enumerate(selects[:10]):
    opts = sel.find_elements(By.TAG_NAME, "option")
    print(f"\n   Select {i}: {len(opts)} seçenek")
    for j, opt in enumerate(opts[:10]):
        txt = opt.text.strip()
        if txt:
            print(f"      [{j}] '{txt[:40]}'")

# Butonları
buttons = driver.find_elements(By.TAG_NAME, "button")
print(f"\n🔘 {len(buttons)} buton bulundu (ilk 15):")
for i, btn in enumerate(buttons[:15]):
    txt = btn.text.strip()
    if txt:
        print(f"   [{i}] '{txt[:40]}'")

# Linkleri
links = driver.find_elements(By.TAG_NAME, "a")
print(f"\n🔗 {len(links)} link (ilk 20):")
for i, link in enumerate(links[:20]):
    txt = link.text.strip()
    if txt and len(txt) > 2 and len(txt) < 50:
        print(f"   [{i}] '{txt[:40]}'")

input("\nEnter...")
driver.quit()