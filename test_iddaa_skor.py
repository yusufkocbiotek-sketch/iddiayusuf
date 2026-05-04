import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

print("📡 iddaa.com sonuçlar sayfası açılıyor...")
driver.get("https://www.iddaa.com/iddaa-sonuclari")
time.sleep(15)

print("\n📜 Sayfa aşağı kaydırılıyor...")
for s in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
driver.execute_script("window.scrollTo(0, 0);")
time.sleep(2)

print("\n📄 SAYFA İÇERİĞİ PARSE EDİLİYOR:")
print("="*60)
try:
    body = driver.find_element(By.TAG_NAME, "body")
    lines = [line.strip() for line in body.text.split("\n") if line.strip() != ""]
    
    print(f"📄 Toplam {len(lines)} satır okundu.")
    
    # "Biten" kelimesini veya skor formatını (örn "MS", "İY", ":") arayalım
    skor_sayaci = 0
    for i, line in enumerate(lines):
        if "Bitti" in line or "MS" in line or (len(line) == 5 and line[2] == ":"):
            print(f"\n   [Bulunan Kesit Satır {i}]")
            for j in range(max(0, i-2), min(len(lines), i+8)):
                print(f"     {j}: {lines[j][:80]}")
            skor_sayaci += 1
            if skor_sayaci >= 10:
                break

    if skor_sayaci == 0:
        print("\n   ⚠️ Skorlar bulunamadı. İlk 50 satırı gösteriyorum:")
        for k in range(min(50, len(lines))):
            print(f"   {k}: {lines[k][:80]}")

except Exception as e:
    print(f"❌ Hata: {e}")

input("\n⏸️ Enter'a basın Chrome kapansın...")
driver.quit()