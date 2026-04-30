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

url = "https://www.iddaa.com/program/futbol"
print("📡 iddaa.com açılıyor...")
driver.get(url)
time.sleep(10)

maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
print(f"📋 Başlangıç: {len(maclar)} maç")

# Tarih dropdown'ını aç
print("\n🖱️ Tarih dropdown açılıyor...")
sboxes = driver.find_elements(By.CSS_SELECTOR, ".style_selectBox__mo_KX")
tarih_sb = None
for sb in sboxes:
    if sb.text.strip().split("\n")[0] == "Tarih":
        tarih_sb = sb
        break

if tarih_sb:
    driver.execute_script("arguments[0].click();", tarih_sb)
    time.sleep(3)
    
    # Dropdown içindeki label'ları bul
    dropdown = tarih_sb.find_element(By.CSS_SELECTOR, "div[class*='absolute']")
    labels = dropdown.find_elements(By.TAG_NAME, "label")
    print(f"   📋 {len(labels)} tarih seçeneği bulundu:")
    for i, label in enumerate(labels):
        txt = label.text.strip()
        print(f"      [{i}] '{txt}'")
    
    # Yarın'a tıkla
    print("\n🖱️ 'Yarın' seçiliyor...")
    for label in labels:
        if label.text.strip() == "Yarın":
            print(f"   Label bulundu: '{label.text.strip()}'")
            
            # Farklı tıklama yöntemlerini dene
            print("\n   === YÖNTEM A: label.click() ===")
            try:
                label.click()
                time.sleep(8)
                maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
                print(f"   📋 Sonuç: {len(maclar)} maç")
                print(f"   URL: {driver.current_url}")
                
                if len(maclar) > 0:
                    eg = driver.find_element(By.CSS_SELECTOR, ".event-group")
                    lines = eg.text.split("\n")[:10]
                    print("   İlk 10 satır:")
                    for l in lines:
                        print(f"      | {l.strip()}")
            except Exception as e:
                print(f"   ❌ {e}")
            
            break
    
    # Sayfayı yenile ve tekrar dene
    print("\n   === YÖNTEM B: checkbox input ===")
    driver.get(url)
    time.sleep(10)
    
    sboxes = driver.find_elements(By.CSS_SELECTOR, ".style_selectBox__mo_KX")
    for sb in sboxes:
        if sb.text.strip().split("\n")[0] == "Tarih":
            driver.execute_script("arguments[0].click();", sb)
            time.sleep(3)
            
            # input[type=checkbox] veya input[type=radio] ara
            inputs = sb.find_elements(By.TAG_NAME, "input")
            print(f"   📋 {len(inputs)} input bulundu")
            for i, inp in enumerate(inputs):
                inp_type = inp.get_attribute("type") or ""
                inp_id = inp.get_attribute("id") or ""
                inp_name = inp.get_attribute("name") or ""
                inp_value = inp.get_attribute("value") or ""
                checked = inp.get_attribute("checked")
                print(f"      [{i}] type={inp_type} id={inp_id} name={inp_name} value={inp_value} checked={checked}")
            
            # İkinci input'a (Yarın) tıkla
            if len(inputs) >= 2:
                print(f"\n   🖱️ input[1] (Yarın) tıklanıyor...")
                driver.execute_script("arguments[0].click();", inputs[1])
                time.sleep(8)
                maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
                print(f"   📋 Sonuç: {len(maclar)} maç")
                print(f"   URL: {driver.current_url}")
                
                if len(maclar) > 0:
                    eg = driver.find_element(By.CSS_SELECTOR, ".event-group")
                    lines = eg.text.split("\n")[:10]
                    print("   İlk 10 satır:")
                    for l in lines:
                        print(f"      | {l.strip()}")
            
            break

print("\n" + "="*60)
input("⏸️ Enter'a basın...")
driver.quit()