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

print("📡 mackolik açılıyor...")
driver.get("https://arsiv.mackolik.com/Iddaa-Programi")
time.sleep(10)

# Cookie kapat
try:
    for btn in driver.find_elements(By.TAG_NAME, "button"):
        if "Kabul" in btn.text:
            btn.click()
            time.sleep(2)
            break
except:
    pass

# 1. Sol/Sağ ok butonlarını bul
print("🔍 OK BUTONLARI ARANIYOR:")
print("="*60)

# Tüm tıklanabilir elementleri tara
clickables = driver.find_elements(By.CSS_SELECTOR, "a, button, input[type=button], input[type=submit], [onclick], [class*='arrow'], [class*='prev'], [class*='next'], [class*='left'], [class*='right'], [class*='nav'], img[onclick]")

for i, el in enumerate(clickables):
    tag = el.tag_name
    cls = el.get_attribute("class") or ""
    txt = el.text.strip()[:30]
    href = el.get_attribute("href") or ""
    onclick = el.get_attribute("onclick") or ""
    title = el.get_attribute("title") or ""
    src = el.get_attribute("src") or ""
    
    if any(k in (cls+txt+onclick+title+href+src).lower() for k in ["prev","next","left","right","arrow","sol","sag","geri","ileri","<",">","«","»","nav","date","tarih"]):
        print(f"  [{i}] <{tag}> class='{cls[:40]}' text='{txt}' onclick='{onclick[:50]}' title='{title}' href='{href[:50]}'")

# 2. Tarih yazısının etrafındaki elementleri bul
print("\n🔍 TARİH ALANI ANALİZİ:")
print("="*60)

# Tarihi içeren elementi bul
all_els = driver.find_elements(By.CSS_SELECTOR, "*")
for el in all_els:
    try:
        txt = el.text.strip()
        if "2026" in txt and "/" in txt and len(txt) < 20:
            tag = el.tag_name
            cls = el.get_attribute("class") or ""
            el_id = el.get_attribute("id") or ""
            print(f"  Tarih elementi: <{tag}> id='{el_id}' class='{cls[:40]}' text='{txt}'")
            
            # Parent element
            parent = el.find_element(By.XPATH, "..")
            pcls = parent.get_attribute("class") or ""
            print(f"  Parent: <{parent.tag_name}> class='{pcls[:40]}'")
            
            # Parent'ın çocukları (sol-tarih-sağ sıralı olabilir)
            siblings = parent.find_elements(By.CSS_SELECTOR, "*")
            print(f"  Parent'ın {len(siblings)} çocuğu:")
            for j, sib in enumerate(siblings[:15]):
                stag = sib.tag_name
                scls = sib.get_attribute("class") or ""
                stxt = sib.text.strip()[:20]
                sonclick = sib.get_attribute("onclick") or ""
                shref = sib.get_attribute("href") or ""
                if stxt or sonclick or shref:
                    print(f"    [{j}] <{stag}> cls='{scls[:30]}' text='{stxt}' onclick='{sonclick[:40]}' href='{shref[:40]}'")
            break
    except:
        continue

# 3. Sayfadaki tüm img etiketlerini kontrol et (ok resmi olabilir)
print("\n🔍 RESIM BUTONLARI:")
print("="*60)

imgs = driver.find_elements(By.TAG_NAME, "img")
for img in imgs:
    src = img.get_attribute("src") or ""
    onclick = img.get_attribute("onclick") or ""
    alt = img.get_attribute("alt") or ""
    cls = img.get_attribute("class") or ""
    if any(k in (src+onclick+alt+cls).lower() for k in ["arrow","prev","next","left","right","sol","sag","nav","ok","back","forward"]):
        print(f"  src='{src[:50]}' onclick='{onclick[:50]}' alt='{alt}'")

# 4. JavaScript fonksiyonlarını ara
print("\n🔍 JAVASCRIPT FONKSİYONLARI:")
print("="*60)

try:
    scripts = driver.find_elements(By.TAG_NAME, "script")
    for script in scripts:
        src = script.get_attribute("src") or ""
        txt = script.get_attribute("innerHTML") or ""
        if any(k in txt.lower() for k in ["datechange","changdate","prevdate","nextdate","dateclick","tarih","amamackolik"]):
            # İlgili kısımları yazdır
            for line in txt.split("\n"):
                if any(k in line.lower() for k in ["date","tarih","prev","next"]):
                    print(f"  {line.strip()[:80]}")
except:
    pass

# 5. Sol oka tıklama denemesi
print("\n🖱️ SOL OK TIKLAMA DENEMESİ:")
print("="*60)

# Mevcut sayfadaki maç sayısını say
body = driver.find_element(By.TAG_NAME, "body")
onceki_text = body.text
onceki_mac = onceki_text.count(" - ")
print(f"  Şu anki maç sayısı (tahmini): {onceki_mac}")

# Tüm tıklanabilir şeylere tek tek tıklayıp değişen var mı bak
try:
    # Önce < veya « veya ◄ gibi karakterleri ara
    for el in driver.find_elements(By.CSS_SELECTOR, "a, span, div, button, i, img"):
        try:
            txt = el.text.strip()
            onclick = el.get_attribute("onclick") or ""
            cls = el.get_attribute("class") or ""
            
            if txt in ["<", "«", "◄", "‹", "←", "Önceki", "Geri"] or "prev" in cls.lower() or "left" in cls.lower() or "prev" in onclick.lower():
                print(f"  BULUNDU: <{el.tag_name}> text='{txt}' class='{cls[:30]}' onclick='{onclick[:40]}'")
                
                driver.execute_script("arguments[0].click();", el)
                time.sleep(8)
                
                body = driver.find_element(By.TAG_NAME, "body")
                yeni_text = body.text
                yeni_mac = yeni_text.count(" - ")
                print(f"  Tıkladıktan sonra maç: {yeni_mac}")
                print(f"  URL: {driver.current_url}")
                
                # Tarih değişti mi?
                for line in yeni_text.split("\n"):
                    if "2026" in line and "/" in line and len(line.strip()) < 20:
                        print(f"  Yeni tarih: {line.strip()}")
                        break
                break
        except:
            continue
except Exception as e:
    print(f"  ❌ {e}")

print("\n" + "="*60)
input("⏸️ Enter'a basın...")
driver.quit()