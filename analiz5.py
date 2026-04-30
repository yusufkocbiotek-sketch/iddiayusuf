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

print("✅ Sayfa yüklendi!")
print("="*60)

# TÜM butonları listele
print("🔍 SAYFADAKİ TÜM BUTONLAR:")
print("="*60)
buttons = driver.find_elements(By.TAG_NAME, "button")
for i, btn in enumerate(buttons):
    txt = btn.text.strip()
    cls = btn.get_attribute("class") or ""
    if txt:
        print(f"  [{i}] text='{txt[:60]}' class='{cls[:60]}'")

print("\n" + "="*60)

# "ÖNE ÇIKANLAR" ile ilgili elementleri bul
print("🔍 ÖNE ÇIKANLAR İLE İLGİLİ ELEMENTLER:")
print("="*60)
all_els = driver.find_elements(By.CSS_SELECTOR, "*")
for el in all_els[:2000]:
    txt = el.text.strip()
    if "ÖNE ÇIKAN" in txt and len(txt) < 100:
        tag = el.tag_name
        cls = el.get_attribute("class") or ""
        print(f"  <{tag}> class='{cls[:60]}' text='{txt[:80]}'")

print("\n" + "="*60)

# Tarihe Göre Sırala butonunu bul
print("🔍 'TARİHE GÖRE SIRALA' BUTONU:")
print("="*60)
for el in driver.find_elements(By.CSS_SELECTOR, "*"):
    txt = el.text.strip()
    if "Tarihe" in txt and len(txt) < 50:
        tag = el.tag_name
        cls = el.get_attribute("class") or ""
        clickable = el.get_attribute("onclick") or ""
        print(f"  <{tag}> class='{cls[:60]}' text='{txt}'")

# Tarihe Göre Sırala'ya tıkla
print("\n🖱️ 'Tarihe Göre Sırala' tıklanıyor...")
for btn in buttons:
    txt = btn.text.strip()
    if "Tarihe" in txt:
        print(f"  Buton bulundu: '{txt}'")
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(8)
        
        # Scroll yap
        for s in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        
        maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
        print(f"  📋 Tıkladıktan sonra {len(maclar)} maç görünüyor")
        
        # İlk 5 maçın adını yazdır
        for j, m in enumerate(maclar[:5]):
            print(f"    {j+1}. {m.text.strip()[:50]}")
        
        break

# Dropdown/Select elementleri
print("\n" + "="*60)
print("🔍 DROPDOWN / SELECT ELEMENTLER:")
print("="*60)
selects = driver.find_elements(By.CSS_SELECTOR, "select, [role='listbox'], [role='combobox']")
print(f"  {len(selects)} select bulundu")
for s in selects:
    print(f"  text='{s.text[:100]}'")

# Filtre alanını incele
print("\n" + "="*60)
print("🔍 FİLTRE ALANI:")
print("="*60)
filters = driver.find_elements(By.CSS_SELECTOR, "[class*='filter'], [class*='Filter']")
for f in filters[:10]:
    txt = f.text.strip()[:200]
    cls = f.get_attribute("class") or ""
    print(f"  class='{cls[:60]}'")
    print(f"  text='{txt}'")
    print()

print("\n" + "="*60)
input("⏸️ Enter'a basın...")
driver.quit()