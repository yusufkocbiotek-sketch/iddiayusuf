import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

print("📡 mackolik açılıyor...")
driver.get("https://arsiv.mackolik.com/Iddaa-Programi")
time.sleep(8)

# Cookie kapat
try:
    for btn in driver.find_elements(By.TAG_NAME, "button"):
        if "Kabul" in btn.text:
            btn.click()
            time.sleep(2)
            break
except:
    pass

# 1. Geçmiş tarih seç (28 Nisan - dün veya önceki gün)
print("🖱️ Geçmiş tarih seçiliyor...")
try:
    date_sel = Select(driver.find_element(By.ID, "IddaaDateCmb"))
    opts = date_sel.options
    print(f"  {len(opts)} tarih seçeneği var:")
    for o in opts:
        print(f"    '{o.text.strip()}' value='{o.get_attribute('value')}'")
    
    # İlk geçmiş tarihi seç (bugünden önceki)
    gecmis_tarih = None
    for o in opts:
        val = o.get_attribute("value")
        txt = o.text.strip()
        if val != "-1" and ("28.04" in val or "29.04" in val or "30.04" in val):
            gecmis_tarih = val
            print(f"\n  📅 Seçilen: {txt}")
            date_sel.select_by_value(val)
            time.sleep(8)
            break
except Exception as e:
    print(f"  ❌ {e}")

# 2. Sayfadaki maç verilerini oku
print("\n📋 MAÇLAR (seçilen tarih):")
print("="*60)

tables = driver.find_elements(By.TAG_NAME, "table")
for table in tables:
    rows = table.find_elements(By.TAG_NAME, "tr")
    if len(rows) < 5:
        continue
    
    mac_sayisi = 0
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, "td")
        if len(cells) < 15:
            # Lig başlığı satırı
            if len(cells) == 1 and cells[0].text.strip():
                txt = cells[0].text.strip()
                if len(txt) > 3 and not txt[0].isdigit():
                    print(f"\n  🏆 {txt}")
            continue
        
        hucre = [c.text.strip() for c in cells]
        saat = hucre[0] if hucre[0] else ""
        
        if ":" not in saat:
            continue
        
        mac_sayisi += 1
        if mac_sayisi <= 15:
            print(f"  [{mac_sayisi}] Saat:{hucre[0]}")
            for j, h in enumerate(hucre):
                if h:
                    print(f"      [{j}] {h}")
    
    print(f"\n  📊 Toplam {mac_sayisi} maç")
    break

# 3. Oyun Türü dropdown'ını değiştir
print("\n\n🔄 OYUN TÜRÜ DEĞİŞTİRME:")
print("="*60)

game_types = {
    "7": "MS - Alt Üst - ÇŞ",
    "8": "İY Sonucu - KG - Toplam Gol",
    "4": "İY/MS",
    "11": "1.5 - 2.5 - 3.5 Gol"
}

for gt_value, gt_name in game_types.items():
    try:
        print(f"\n  📊 Oyun Türü: {gt_name} (value={gt_value})")
        gt_sel = Select(driver.find_element(By.ID, "GameTypecmb"))
        gt_sel.select_by_value(gt_value)
        time.sleep(5)
        
        # Header satırını oku
        tables = driver.find_elements(By.TAG_NAME, "table")
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            if len(rows) < 5:
                continue
            
            # Header
            for row in rows[:3]:
                cells = row.find_elements(By.CSS_SELECTOR, "td, th")
                if len(cells) > 5:
                    header = [c.text.strip()[:15] for c in cells if c.text.strip()]
                    print(f"    Header: {' | '.join(header)}")
            
            # İlk maç
            for row in rows[3:]:
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                if len(cells) >= 15:
                    hucre = [c.text.strip() for c in cells]
                    print(f"    İlk maç:")
                    for j, h in enumerate(hucre):
                        if h:
                            print(f"      [{j}] {h}")
                    break
            break
    except Exception as e:
        print(f"    ❌ {e}")

print("\n" + "="*60)
input("⏸️ Enter'a basın...")
driver.quit()