import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

print("🚀 İddaa.com açılıyor ve gizli veri (Next Data) aranıyor...")

options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get("https://www.iddaa.com/sonuclar")
    print("⏳ Sayfa yükleniyor (10 saniye bekleniyor)...")
    time.sleep(10) 
    
    # Sayfanın tüm HTML kaynağını al
    html = driver.page_source
    driver.quit()
    
    # BeautifulSoup ile HTML'i analiz et
    soup = BeautifulSoup(html, "html.parser")
    
    # İddaa'nın verileri sakladığı gizli etiketi bul
    next_data_script = soup.find("script", {"id": "__NEXT_DATA__"})
    
    if next_data_script and next_data_script.string:
        print("\n🎉 BAŞARILI! Sayfada __NEXT_DATA__ (Gizli Veri) bulundu!")
        
        # Bu devasa veriyi JSON formatında kaydet
        with open("next_data.json", "w", encoding="utf-8") as f:
            f.write(next_data_script.string)
            
        print("💾 Tüm veriler 'next_data.json' dosyasına kaydedildi.")
        print("👉 Lütfen 'next_data.json' dosyasını aç, içinde 'AS Roma' veya dünkü maçlardan birini bul ve o maçın etrafındaki 20 satırı bana gönder!")
        
    else:
        print("\n⚠️ __NEXT_DATA__ bulunamadı. İddaa verileri dinamik olarak yüklüyor olabilir.")
        print("Bunun için sitede manuel olarak bir tarihe tıklamamız gerekecek. Önce bu sonucu bana bildir.")

except Exception as e:
    print(f"❌ Hata oluştu: {e}")