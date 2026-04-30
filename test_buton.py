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

print("📡 iddaa.com açılıyor...")
driver.get("https://www.iddaa.com/program/futbol")
time.sleep(10)

maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
print(f"📋 Başlangıç: {len(maclar)} maç")

# YÖNTEM 1: "Tarihe Göre Sırala" tıkla
print("\n🖱️ YÖNTEM 1: Tarihe Göre Sırala...")
try:
    spans = driver.find_elements(By.TAG_NAME, "span")
    for sp in spans:
        try:
            if "Tarihe Göre Sırala" in sp.text:
                driver.execute_script("arguments[0].click();", sp)
                print("   Tıklandı! 10sn bekleniyor...")
                time.sleep(10)
                # Scroll
                for s in range(10):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
                print(f"   📋 Şimdi: {len(maclar)} maç")
                break
        except:
            continue
except Exception as e:
    print(f"   ❌ {e}")

# YÖNTEM 2: "Devamını gör" tıkla
print("\n🖱️ YÖNTEM 2: Devamını gör...")
try:
    driver.get("https://www.iddaa.com/program/futbol")
    time.sleep(10)
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        try:
            if "Devamını gör" in btn.text:
                driver.execute_script("arguments[0].click();", btn)
                print("   Tıklandı! 10sn bekleniyor...")
                time.sleep(10)
                for s in range(10):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
                print(f"   📋 Şimdi: {len(maclar)} maç")
                break
        except:
            continue
except Exception as e:
    print(f"   ❌ {e}")

# YÖNTEM 3: Filtre dropdown - Oyun Türü / Lig Seçimi
print("\n🖱️ YÖNTEM 3: Filtre alanları...")
try:
    driver.get("https://www.iddaa.com/program/futbol")
    time.sleep(10)
    
    # selectBox elementlerini bul
    selectboxes = driver.find_elements(By.CSS_SELECTOR, "[class*='selectBox']")
    print(f"   📋 {len(selectboxes)} selectBox bulundu")
    for i, sb in enumerate(selectboxes):
        txt = sb.text.strip()[:50]
        print(f"   [{i}] '{txt}'")
    
    # Her birine tıklamayı dene
    for i, sb in enumerate(selectboxes):
        try:
            txt = sb.text.strip()
            print(f"\n   🖱️ SelectBox {i} tıklanıyor: '{txt[:30]}'...")
            driver.execute_script("arguments[0].click();", sb)
            time.sleep(3)
            
            # Açılan dropdown seçeneklerini oku
            dropdown_items = driver.find_elements(By.CSS_SELECTOR, "[class*='option'], [class*='item'], [class*='menu'] li, [class*='dropdown'] div")
            if dropdown_items:
                print(f"   📋 {len(dropdown_items)} seçenek bulundu:")
                for j, item in enumerate(dropdown_items[:15]):
                    try:
                        print(f"      {j}: '{item.text.strip()[:50]}'")
                    except:
                        pass
            
            # Sayfaya tıklayarak dropdown'u kapat
            driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(2)
        except:
            pass

except Exception as e:
    print(f"   ❌ {e}")

# YÖNTEM 4: ÖNE ÇIKANLAR başlığına tıkla (belki kapatır)
print("\n🖱️ YÖNTEM 4: ÖNE ÇIKANLAR tıkla...")
try:
    driver.get("https://www.iddaa.com/program/futbol")
    time.sleep(10)
    
    one_cikan = driver.find_elements(By.CSS_SELECTOR, "[class*='mh']")
    for el in one_cikan:
        try:
            txt = el.text.strip()
            if "ÖNE ÇIKAN" in txt:
                print(f"   Bulundu: '{txt[:40]}'")
                driver.execute_script("arguments[0].click();", el)
                time.sleep(5)
                maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
                print(f"   📋 Tıkladıktan sonra: {len(maclar)} maç")
                break
        except:
            continue
except Exception as e:
    print(f"   ❌ {e}")

# YÖNTEM 5: Body text'te sayfanın altında ne var?
print("\n📄 YÖNTEM 5: Sayfanın alt kısmı...")
try:
    driver.get("https://www.iddaa.com/program/futbol")
    time.sleep(10)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    
    body = driver.find_element(By.TAG_NAME, "body")
    text = body.text
    lines = text.split("\n")
    
    # Son 30 satır
    print("   Son 30 satır:")
    for line in lines[-30:]:
        if line.strip():
            print(f"   | {line.strip()[:60]}")
except Exception as e:
    print(f"   ❌ {e}")

print("\n" + "="*60)
input("⏸️ Enter'a basın...")
driver.quit()