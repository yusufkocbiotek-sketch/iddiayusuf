import json
import os
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

CIKTI_DOSYA = "public/data/mac_test.json"

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("✅ Chrome başlatıldı!")
    return driver

def saat_mi(text):
    if len(text) == 5 and text[2] == ":":
        try:
            s, d = text.split(":")
            if 0 <= int(s) <= 23 and 0 <= int(d) <= 59:
                return True
        except:
            pass
    return False

def sayi_mi(text):
    try:
        float(text.replace(",", "."))
        return True
    except:
        return False

SAHTE = ["Tarih", "Oyun Türü", "Lig Seçimi", "Tarihe Göre", "Maç Sonucu",
         "İlk Yarı", "Handikap", "Alt/Üst", "Karşılıklı", "Bugün", "Yarın",
         "ÖNE ÇIKAN", "CANLI", "FUTBOL", "BASKETBOL", "TENİS"]

def mac_bul(body_text):
    lines = [l.strip() for l in body_text.split("\n") if l.strip()]
    bulunan = []
    for i in range(len(lines)):
        line = lines[i].strip()
        if line in ["-", "–", "—"]:
            if i >= 2 and i + 1 < len(lines):
                ev = lines[i - 1].strip()
                dep = lines[i + 1].strip()
                if (len(ev) >= 2 and len(dep) >= 2 and
                    not sayi_mi(ev) and not sayi_mi(dep) and
                    not any(kw in ev for kw in SAHTE) and
                    not any(kw in dep for kw in SAHTE)):
                    saat = ""
                    for j in range(max(0, i - 3), i):
                        if saat_mi(lines[j].strip()):
                            saat = lines[j].strip()
                            break
                    key = ev.lower().strip() + "_vs_" + dep.lower().strip()
                    bulunan.append({"key": key, "saat": saat, "ev": ev, "dep": dep})
    return bulunan, len(lines)

def test_cek():
    driver = None
    baslangic = datetime.datetime.now()

    try:
        driver = tarayici_baslat()
        url = "https://www.iddaa.com/program/futbol"

        print(f"\n📡 {url}")
        driver.get(url)
        time.sleep(8)

        # Sayfayı en üste çek
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        toplanan = {}
        bos_sayaci = 0
        adim = 0
        en_buyuk_satir = 0

        print(f"\n📜 WINDOW SCROLL ile maçlar toplanıyor...")
        print(f"   (Her adımda 300px kaydır, 4sn bekle)\n")

        # 🔑 100 kez kaydır (toplam ~30.000px, bol bol yeterli)
        while bos_sayaci < 20:
            adim += 1

            # Body text'i oku
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                maclar, satir_sayisi = mac_bul(body.text)
                
                if satir_sayisi > en_buyuk_satir:
                    en_buyuk_satir = satir_sayisi
            except:
                time.sleep(2)
                continue

            # Yeni maçları ekle
            yeni = 0
            for m in maclar:
                if m["key"] not in toplanan:
                    toplanan[m["key"]] = m
                    yeni += 1

            if yeni > 0:
                bos_sayaci = 0
                print(f"   ⬇️ Adım {adim}: +{yeni} yeni maç | Toplam: {len(toplanan)} | Satır: {satir_sayisi}")
            else:
                bos_sayaci += 1

            # 🔑 WINDOW SCROLL (300px aşağı, smooth)
            driver.execute_script("window.scrollBy({top: 300, behavior: 'smooth'});")
            
            # 🔑 4 saniye bekle (site yeni verileri yüklesin)
            time.sleep(4)
            
            # 🔑 Ekranda maç olup olmadığını kontrol et
            try:
                kontrol = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
                if len(kontrol) == 0:
                    # Maç elementleri kayboldu, biraz daha bekle
                    time.sleep(2)
            except:
                pass

        # Sonuçlar
        sonuc = list(toplanan.values())
        sure = datetime.datetime.now() - baslangic

        print(f"\n{'='*60}")
        print(f"📊 TEST SONUÇ")
        print(f"   ⚽ Toplam farklı maç: {len(sonuc)}")
        print(f"   📄 En büyük satır sayısı: {en_buyuk_satir}")
        print(f"   ⏱️ Süre: {sure}")
        print(f"{'='*60}")

        if sonuc:
            print(f"\n📋 Bulunan maçlar (İlk 30):")
            for i, m in enumerate(sonuc[:30]):
                print(f"   {i+1}. [{m['saat']}] {m['ev']} vs {m['dep']}")
            if len(sonuc) > 30:
                print(f"   ... ve {len(sonuc) - 30} maç daha")

            os.makedirs(os.path.dirname(CIKTI_DOSYA), exist_ok=True)
            veri = {"version": 2, "updated": datetime.datetime.now().isoformat(), "matches": []}
            for i, m in enumerate(sonuc):
                veri["matches"].append({
                    "index": i + 1,
                    "ev_sahibi": m["ev"],
                    "deplasman": m["dep"],
                    "saat": m["saat"],
                    "tarih": datetime.date.today().isoformat(),
                    "durum": "baslamadi"
                })
            with open(CIKTI_DOSYA, "w", encoding="utf-8") as f:
                json.dump(veri, f, ensure_ascii=False, indent=2)
            print(f"\n💾 '{CIKTI_DOSYA}' dosyasına kaydedildi!")

        print("\n🎉 Test tamamlandı!")

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 SCRAPER TEST - WINDOW SCROLL (UZUN)")
    print("=" * 60)
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)
    test_cek()