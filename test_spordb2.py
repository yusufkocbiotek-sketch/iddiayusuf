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

print("📡 spordb.com açılıyor...")
driver.get("https://www.spordb.com/iddaa-programi/")
time.sleep(10)

# Tabloyu bul
table = driver.find_element(By.CSS_SELECTOR, "table")
rows = table.find_elements(By.TAG_NAME, "tr")
print(f"📋 {len(rows)} satır bulundu")

# İlk 20 satırı detaylı incele
print("\n📋 İLK 20 SATIR DETAYLI:")
print("="*80)

for i, row in enumerate(rows[:20]):
    cells = row.find_elements(By.CSS_SELECTOR, "td, th")
    print(f"\n--- SATIR {i} ({len(cells)} hücre) ---")
    for j, cell in enumerate(cells):
        txt = cell.text.strip()[:60]
        cls = cell.get_attribute("class") or ""
        if txt:
            print(f"  [{j}] class='{cls[:30]}' → '{txt}'")

# Şimdi maç satırlarını parse edelim
print("\n\n📊 MAÇ VERİLERİ PARSE:")
print("="*80)

mac_sayisi = 0
for i, row in enumerate(rows):
    cells = row.find_elements(By.CSS_SELECTOR, "td")
    if len(cells) < 10:
        continue
    
    try:
        # Tüm hücre metinlerini al
        hucre = [c.text.strip() for c in cells]
        
        # Skor içeren satırları bul (X-X formatı)
        full_text = " ".join(hucre)
        
        if "-" in full_text and any(c.isdigit() for c in full_text):
            # Bu bir maç satırı olabilir
            mac_sayisi += 1
            if mac_sayisi <= 10:
                print(f"\n  MAÇ {mac_sayisi}:")
                for j, h in enumerate(hucre):
                    if h:
                        print(f"    [{j}] {h}")
    except:
        continue

print(f"\n📊 Toplam {mac_sayisi} maç satırı bulundu")

# Hafta dropdown'ını incele
print("\n\n📅 HAFTA SEÇENEKLERİ:")
print("="*80)

try:
    selects = driver.find_elements(By.TAG_NAME, "select")
    print(f"  {len(selects)} select bulundu")
    for idx, sel in enumerate(selects):
        opts = sel.find_elements(By.TAG_NAME, "option")
        if len(opts) > 3:
            print(f"\n  Select {idx}: {len(opts)} seçenek")
            for j, opt in enumerate(opts[:10]):
                print(f"    [{j}] value='{opt.get_attribute('value')[:30]}' text='{opt.text.strip()[:40]}'")
            if len(opts) > 10:
                print(f"    ... ve {len(opts)-10} seçenek daha")
except:
    pass

# Geçmiş hafta linklerini bul
print("\n\n🔗 GEÇMİŞ HAFTA LİNKLERİ:")
print("="*80)

try:
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute("href") or ""
        txt = link.text.strip()
        if "hafta" in href.lower() or "week" in href.lower() or ("202" in txt and "-" in txt):
            print(f"  '{txt}' → {href}")
except:
    pass

# URL pattern testi
print("\n\n🌐 URL PATTERN TESTİ:")
print("="*80)

test_urls = [
    "https://www.spordb.com/iddaa-programi/?hafta=1",
    "https://www.spordb.com/iddaa-programi/?week=1",
    "https://www.spordb.com/iddaa-sonuclari/",
]

for url in test_urls:
    try:
        driver.get(url)
        time.sleep(3)
        print(f"  {url}")
        print(f"    → {driver.current_url}")
        print(f"    → {driver.title[:50]}")
    except:
        print(f"  {url} → HATA")

print("\n" + "="*80)
input("⏸️ Enter'a basın...")
driver.quit()