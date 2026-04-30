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

# İlk maçın takım adına tıkla
print("🖱️ İlk maça tıklanıyor...")
takim_adlari = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
print(f"  Bulunan takım adı: {len(takim_adlari)}")

if takim_adlari:
    driver.execute_script("arguments[0].click();", takim_adlari[0])
    time.sleep(6)
    
    print(f"  URL: {driver.current_url}")
    
    # Sayfayı aşağı kaydır
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(2)
    
    body = driver.find_element(By.TAG_NAME, "body")
    text = body.text
    lines = text.split("\n")
    
    # Tümü'nün indexini bul
    tumu_index = -1
    for i, line in enumerate(lines):
        if line.strip() == "Tümü":
            tumu_index = i
            print(f"\n✅ 'Tümü' bulundu! Satır: {i}")
            break
    
    if tumu_index == -1:
        print("\n❌ 'Tümü' BULUNAMADI!")
        print("📄 TÜM SATIRLAR:")
        for i, line in enumerate(lines):
            if line.strip():
                print(f"  {i}: [{line.strip()}]")
    else:
        # Tümü'nden sonraki 80 satırı göster
        print(f"\n📄 'Tümü' SONRASI 80 SATIR:")
        print("="*60)
        for i in range(tumu_index, min(tumu_index + 80, len(lines))):
            line = lines[i].strip()
            if line:
                # Ondalıklı sayı mı?
                has_dot = "." in line
                print(f"  {i}: [{line}] {'← ORAN' if has_dot and len(line) < 6 else ''}")

input("\n⏸️ Enter'a basın...")
driver.quit()