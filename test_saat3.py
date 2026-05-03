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

# Sayfadaki tüm div ve span'ları tara
all_els = driver.find_elements(By.CSS_SELECTOR, "div, span")
saat_els = []

for el in all_els:
    try:
        txt = el.text.strip()
        if len(txt) == 5 and ":" in txt and txt[:2].isdigit():
            saat_els.append(el)
    except:
        continue

print(f"\nBulunan saat elementleri: {len(saat_els)}")

# Her saat grubundaki maçları say
for el in saat_els:
    try:
        saat = el.text.strip()
        
        # Parent elementi bul
        parent = el.find_element(By.XPATH, "..")
        
        # Grandparent
        grandparent = parent.find_element(By.XPATH, "..")
        
        # Great-grandparent
        great_grandparent = grandparent.find_element(By.XPATH, "..")
        
        # Maçları bul
        maclar = great_grandparent.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
        
        print(f"\n  Saat {saat}:")
        print(f"    Parent class: {parent.get_attribute('class')[:40]}")
        print(f"    Grandparent class: {grandparent.get_attribute('class')[:40]}")
        print(f"    Great-grandparent class: {great_grandparent.get_attribute('class')[:40]}")
        print(f"    Great-grandparent içinde {len(maclar)} maç bulundu")
        
        for i, m in enumerate(maclar[:3]):
            print(f"      {i+1}. {m.text.strip()[:40]}")
            
    except:
        continue

input("Enter...")
driver.quit()