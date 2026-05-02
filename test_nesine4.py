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

# Farklı URL'leri deneyelim
urls = [
    "https://www.nesine.com/iddaa/programi/futbol",
    "https://www.nesine.com/iddaa/sonuclar",
    "https://www.nesine.com/iddaa/sonuclar/1",
]

for url in urls:
    print(f"\n{'='*60}")
    print(f"📡 {url}")
    print('='*60)
    driver.get(url)
    time.sleep(12)
    
    body = driver.find_element(By.TAG_NAME, "body")
    text = body.text[:5000]
    
    # Maç isimlerini ara
    maclar = []
    for line in text.split("\n"):
        line = line.strip()
        if any(x in line for x in ["vs", "-", "MAÇ", "Süper Lig", "Premier"]):
            if len(line) > 5 and len(line) < 100:
                maclar.append(line)
    
    print(f"\n📋 Maçlar bulundu: {len(maclar)}")
    for m in maclar[:15]:
        print(f"   {m}")
    
    # Select'ları kontrol et
    selects = driver.find_elements(By.TAG_NAME, "select")
    if selects:
        print(f"\n📅 {len(selects)} select var")
        for i, sel in enumerate(selects):
            opts = sel.find_elements(By.TAG_NAME, "option")
            for j, opt in enumerate(opts):
                txt = opt.text.strip()
                if txt and "2026" in txt or "2025" in txt or "Hepsi" in txt or "Hafta" in txt:
                    print(f"   Select {i} -> '{txt}'")

input("\nEnter...")
driver.quit()