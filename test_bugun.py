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

# Test 1: Ana sayfa
print("1️⃣ ANA SAYFA:")
driver.get("https://www.iddaa.com/program/futbol")
time.sleep(10)
maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
print(f"   {len(maclar)} mac")

# Test 2: Bugün URL
print("\n2️⃣ BUGUN URL (?date=01.05.2026):")
driver.get("https://www.iddaa.com/program/futbol?date=01.05.2026")
time.sleep(15)
maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
print(f"   {len(maclar)} mac")

# body text'te kaç maç var?
body = driver.find_element(By.TAG_NAME, "body")
text = body.text
mac_sayisi = text.count(" - ")
print(f"   Body text'te {mac_sayisi} tire")

# Sayfada ÖNE ÇIKANLAR var mı?
if "ÖNE ÇIKAN" in text:
    print("   ⚠️ ÖNE ÇIKANLAR aktif!")
else:
    print("   ✅ ÖNE ÇIKANLAR yok")

# Daha fazla göster butonu var mı?
buttons = driver.find_elements(By.TAG_NAME, "button")
for btn in buttons:
    txt = btn.text.strip()
    if "Daha fazla" in txt or "Devamını" in txt or "daha" in txt.lower():
        print(f"   🔘 Buton: '{txt}'")

# Test 3: Yarın URL
print("\n3️⃣ YARIN URL (?date=02.05.2026):")
driver.get("https://www.iddaa.com/program/futbol?date=02.05.2026")
time.sleep(15)
maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
print(f"   {len(maclar)} mac")

# Test 4: Ana sayfa + Daha fazla göster
print("\n4️⃣ ANA SAYFA + DAHA FAZLA GÖSTER:")
driver.get("https://www.iddaa.com/program/futbol")
time.sleep(10)

for tur in range(20):
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        clicked = False
        for btn in buttons:
            try:
                txt = btn.text.strip()
                if "Daha fazla" in txt or "Devamını" in txt:
                    driver.execute_script("arguments[0].click();", btn)
                    clicked = True
                    time.sleep(3)
                    break
            except:
                continue
        if not clicked:
            break
    except:
        break
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
print(f"   {len(maclar)} mac (scroll+buton sonrası)")

# İlk 10 maç adı
for i, m in enumerate(maclar[:10]):
    print(f"   {i+1}. {m.text.strip()[:40]}")

print("\n" + "="*60)
input("Enter...")
driver.quit()