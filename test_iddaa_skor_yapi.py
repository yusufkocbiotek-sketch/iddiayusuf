import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.iddaa.com/canli-skor/futbol"

print(f"📡 Açılıyor: {url}")
driver.get(url)
time.sleep(15)

print("\n============================================================")
print("📋 SAYFA BİLGİSİ")
print("============================================================")
print("Başlık:", driver.title)
print("URL:", driver.current_url)

# HTML kaydet
try:
    with open("debug_iddaa_skor.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("💾 HTML kaydedildi: debug_iddaa_skor.html")
except Exception as e:
    print("HTML kaydedilemedi:", e)

# Body text
try:
    body = driver.find_element(By.TAG_NAME, "body")
    lines = [x.strip() for x in body.text.split("\n") if x.strip()]
except Exception as e:
    print("Body okunamadı:", e)
    lines = []

print("\n============================================================")
print(f"📄 İLK 200 SATIR - Toplam satır: {len(lines)}")
print("============================================================")
for i, line in enumerate(lines[:200]):
    print(f"{i}: {line}")

print("\n============================================================")
print("🔘 BUTON / LİNK / TAB METİNLERİ")
print("============================================================")

elements = driver.find_elements(By.CSS_SELECTOR, "button, a, span, div")
seen = set()
count = 0

keywords = [
    "biten", "bitti", "sonuç", "sonuc", "canlı", "canli",
    "başlamadı", "baslamadi", "bugün", "dün", "yarın",
    "tüm", "hepsi", "futbol", "skor", "program"
]

for el in elements:
    try:
        txt = el.text.strip()
        if not txt:
            continue
        if len(txt) > 80:
            continue

        low = txt.lower()
        if any(k in low for k in keywords):
            key = txt
            if key in seen:
                continue
            seen.add(key)

            tag = el.tag_name
            cls = el.get_attribute("class") or ""
            href = el.get_attribute("href") or ""
            onclick = el.get_attribute("onclick") or ""

            print(f"[{count}] <{tag}> text='{txt}' class='{cls[:60]}' href='{href[:80]}' onclick='{onclick[:80]}'")
            count += 1
    except:
        continue

print("\n============================================================")
print("🔍 SKOR GİBİ GÖRÜNEN SATIRLAR")
print("============================================================")

skor_count = 0
for i, line in enumerate(lines):
    # 2-1, 0 - 0, 3:2 gibi skor benzeri satırları yakala
    compact = line.replace(" ", "")
    if (
        "-" in compact and
        len(compact) <= 7 and
        any(c.isdigit() for c in compact)
    ) or (
        ":" in compact and
        len(compact) <= 7 and
        any(c.isdigit() for c in compact)
    ):
        print("\n--- SKOR ADAYI ---")
        for j in range(max(0, i-4), min(len(lines), i+6)):
            print(f"{j}: {lines[j]}")
        skor_count += 1
        if skor_count >= 20:
            break

print(f"\nToplam skor adayı gösterildi: {skor_count}")

print("\n============================================================")
input("⏸️ Enter'a basın Chrome kapansın...")
driver.quit()