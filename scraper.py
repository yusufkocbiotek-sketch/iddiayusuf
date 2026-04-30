import json
import os
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

CIKTI_DOSYA = "public/data/mac.json"

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome başlatıldı!")
    return driver

def veri_kaydet(maclar):
    data = {"version": 2, "updated": "", "matches": []}
    if os.path.exists(CIKTI_DOSYA):
        try:
            with open(CIKTI_DOSYA, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            pass
    data["updated"] = datetime.datetime.now().isoformat()
    guncel_dict = {f"{m['tarih']}_{m['ev_sahibi']}_{m['deplasman']}": m for m in data.get("matches", [])}
    for ym in maclar:
        guncel_dict[f"{ym['tarih']}_{ym['ev_sahibi']}_{ym['deplasman']}"] = ym
    yeni_liste = sorted(guncel_dict.values(), key=lambda x: (x["tarih"], x["saat"]))
    for i, m in enumerate(yeni_liste, 1):
        m["index"] = i
    data["matches"] = yeni_liste
    os.makedirs(os.path.dirname(CIKTI_DOSYA), exist_ok=True)
    with open(CIKTI_DOSYA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Toplam {len(yeni_liste)} maç kaydedildi → {CIKTI_DOSYA}")

def tarih_cevir(tarih_text):
    bugun = datetime.date.today()
    if tarih_text == "Bugün":
        return bugun.isoformat()
    elif tarih_text == "Yarın":
        return (bugun + datetime.timedelta(days=1)).isoformat()
    else:
        try:
            aylar = {"Ocak":1,"Şubat":2,"Mart":3,"Nisan":4,"Mayıs":5,"Haziran":6,
                     "Temmuz":7,"Ağustos":8,"Eylül":9,"Ekim":10,"Kasım":11,"Aralık":12}
            parcalar = tarih_text.split()
            if len(parcalar) >= 2:
                gun = int(parcalar[0])
                ay = aylar.get(parcalar[1], 0)
                if ay > 0:
                    return datetime.date(bugun.year, ay, gun).isoformat()
        except:
            pass
        return bugun.isoformat()

def saat_mi(text):
    if len(text) == 5 and text[2] == ":":
        try:
            s, d = text.split(":")
            if 0 <= int(s) <= 23 and 0 <= int(d) <= 59:
                return True
        except:
            pass
    return False

def nokta_var_mi(text):
    try:
        if "." not in text:
            return False
        val = float(text)
        return 1.01 <= val <= 99.99
    except:
        return False

def one_cikanlari_kapat(driver):
    """ÖNE ÇIKANLAR filtresini kapatıp TÜM MAÇLARI göster"""
    try:
        # "Tarihe Göre Sırala" butonuna tıkla
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            txt = btn.text.strip()
            if "Tarihe Göre Sırala" in txt:
                driver.execute_script("arguments[0].click();", btn)
                print("   ✅ 'Tarihe Göre Sırala' tıklandı")
                time.sleep(5)
                return True
    except:
        pass
    
    # Alternatif: ÖNE ÇIKANLAR yazısını veya filtreyi kaldır
    try:
        # Filter dropdown'larını kontrol et
        dropdowns = driver.find_elements(By.CSS_SELECTOR, "select, [class*='filter'], [class*='dropdown']")
        for dd in dropdowns:
            txt = dd.text.strip()
            if "ÖNE ÇIKAN" in txt or "Öne Çıkan" in txt:
                # Tüm maçları seç
                options = dd.find_elements(By.TAG_NAME, "option")
                for opt in options:
                    if "Tüm" in opt.text or "Hepsi" in opt.text:
                        opt.click()
                        time.sleep(5)
                        return True
    except:
        pass
    
    return False

def tam_sayfa_yukle(driver, url):
    """Sayfayı yükle, filtreyi kaldır, tüm maçları kaydır"""
    driver.get(url)
    time.sleep(8)
    
    # ÖNE ÇIKANLARI kapat, tüm maçları göster
    print("   🔍 Tüm maçlar yüklenmeye çalışılıyor...")
    
    # "Tarihe Göre Sırala" butonunu bul ve tıkla
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        if "ÖNE ÇIKANLAR" in body_text:
            print("   ⚠️ Şu an sadece ÖNE ÇIKANLAR gösteriliyor")
            one_cikanlari_kapat(driver)
            time.sleep(3)
    except:
        pass
    
    # Sayfayı kaydır
    print("   📜 Sayfa kaydırılıyor...")
    son = driver.execute_script("return document.body.scrollHeight")
    mac_sayisi_onceki = 0
    
    for s in range(100):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Kaç maç yüklendi kontrol et
        maclar_now = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
        mac_sayisi = len(maclar_now)
        
        yeni = driver.execute_script("return document.body.scrollHeight")
        
        if s % 5 == 0:
            print(f"   📜 Scroll {s+1} - {mac_sayisi} maç yüklendi")
        
        # Hem yükseklik hemde maç sayısı değişmiyorsa dur
        if yeni == son and mac_sayisi == mac_sayisi_onceki:
            print(f"   📜 Scroll {s+1} - Sayfa sonu ({mac_sayisi} maç)")
            break
        
        son = yeni
        mac_sayisi_onceki = mac_sayisi
    
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    
    maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
    print(f"   📋 Toplam {len(maclar)} maç yüklendi!")
    return len(maclar)

def detay_sayfa_yukle(driver, detay_url):
    """Detay sayfasını yükle - 5 deneme"""
    for deneme in range(5):
        driver.get(detay_url)
        bekleme = 8 + (deneme * 4)
        print(f"      ⏳ Sayfa yükleniyor ({bekleme}sn)...")
        time.sleep(bekleme)
        
        # Sayfayı kaydır
        driver.execute_script("window.scrollTo(0, 400);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 1200);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        body = driver.find_element(By.TAG_NAME, "body")
        if "Tümü" in body.text:
            return True
        
        print(f"      ⚠️ 'Tümü' bulunamadı ({deneme+1}/5)")
    
    # Son çare: tıklama yöntemi
    print(f"      🔄 Tıklama yöntemi deneniyor...")
    try:
        base_url = "https://www.iddaa.com/program/futbol"
        hd = detay_url.split("hd=")[1].split("&")[0]
        
        driver.get(base_url)
        time.sleep(8)
        
        # Sayfayı kaydır
        for s in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # JavaScript ile URL'i değiştir (SPA navigasyonu)
        driver.execute_script(f"window.history.pushState(null, null, '?hd={hd}');")
        driver.execute_script("window.dispatchEvent(new PopStateEvent('popstate'));")
        time.sleep(5)
        
        body = driver.find_element(By.TAG_NAME, "body")
        if "Tümü" in body.text:
            print(f"      ✅ Tıklama yöntemi çalıştı!")
            return True
        
        # Takim adina tıklama yöntemi
        takim_adlari = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
        for ta in takim_adlari:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ta)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", ta)
                time.sleep(5)
                
                if "hd=" in driver.current_url:
                    current_hd = driver.current_url.split("hd=")[1].split("&")[0]
                    if current_hd == hd:
                        body = driver.find_element(By.TAG_NAME, "body")
                        if "Tümü" in body.text:
                            print(f"      ✅ Tıklama ile bulundu!")
                            return True
                
                # Yanlış maça tıkladık, geri git
                driver.back()
                time.sleep(3)
            except:
                continue
    except:
        pass
    
    return False

def detay_parse(driver):
    """Detay sayfasındaki TÜM oranları çeker"""
    oranlar = {}
    body = driver.find_element(By.TAG_NAME, "body")
    text = body.text
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    tumu_idx = -1
    for i, line in enumerate(lines):
        if line == "Tümü":
            tumu_idx = i
            break
    if tumu_idx == -1:
        return oranlar

    i = tumu_idx + 1
    sekmeler = [
        "Kim Kazanır", "Alt/Üst", "Goller", "Skor", "Diğer",
        "Oyuncu", "Özel", "Kombo", "Korner/Kart", "Korner",
        "Kart", "Handikap", "Yarı", "Dakika", "Asist",
        "Toplam", "İstatistik", "Kombine"
    ]
    while i < len(lines) and lines[i] in sekmeler:
        i += 1

    dur_kelimeleri = [
        "Bugün", "Yarın", "Yardım", "Hakkımızda", "İletişim",
        "Gizlilik", "Popüler Bahisler", "Kolay Kuponlar", "Spor Toto",
        "Bülten", "Canlı Sonuçlar", "Yazar Yorumları"
    ]
    ay_isimleri = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
                   "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]

    current_market = ""
    while i < len(lines):
        line = lines[i]
        if line in dur_kelimeleri:
            break
        if any(ay in line for ay in ay_isimleri) and any(c.isdigit() for c in line):
            break
        if saat_mi(line):
            break
        if line.isupper() and len(line) > 2:
            i += 1
            continue
        if i + 1 < len(lines):
            sonraki = lines[i + 1]
            if nokta_var_mi(sonraki):
                outcome_adi = line
                oran_degeri = float(sonraki)
                if current_market:
                    key = f"{current_market}_{outcome_adi}"
                else:
                    key = outcome_adi
                oranlar[key] = oran_degeri
                i += 2
                continue
        if not nokta_var_mi(line):
            current_market = line
        i += 1
    return oranlar

def iddaa_cek(driver):
    url = "https://www.iddaa.com/program/futbol"

    # 1. ADIM: Sayfayı yükle ve TÜM maçları yükle
    print(f"📡 {url} açılıyor...")
    toplam_mac = tam_sayfa_yukle(driver, url)

    # 2. ADIM: Temel oranları topla
    print(f"\n🔍 Temel oranlar okunuyor...")
    eg = driver.find_element(By.CSS_SELECTOR, ".event-group")
    tum_text = eg.text
    lines = [l.strip() for l in tum_text.split("\n") if l.strip()]

    temel_maclar = []
    i = 0
    while i < len(lines) - 15:
        tarih_text = lines[i]
        saat = lines[i + 1]
        if not saat_mi(saat):
            i += 1
            continue
        ev = lines[i + 2]
        ayrac = lines[i + 3]
        dep = lines[i + 4]
        if ayrac != "-":
            i += 1
            continue
        oran_start = i + 5
        if lines[oran_start] == "Kral Oran":
            oran_start = i + 7
        if not nokta_var_mi(lines[oran_start]):
            i += 1
            continue
        try:
            temel = {
                "Maç Sonucu_1": float(lines[oran_start]),
                "Maç Sonucu_0": float(lines[oran_start + 1]),
                "Maç Sonucu_2": float(lines[oran_start + 2]),
                "İY Sonuç_1": float(lines[oran_start + 3]),
                "İY Sonuç_0": float(lines[oran_start + 4]),
                "İY Sonuç_2": float(lines[oran_start + 5]),
                "Handikap": lines[oran_start + 6],
                "Handikap_1": float(lines[oran_start + 7]),
                "Handikap_0": float(lines[oran_start + 8]),
                "Handikap_2": float(lines[oran_start + 9]),
                "Alt/Üst 2.5_Alt": float(lines[oran_start + 10]),
                "Alt/Üst 2.5_Üst": float(lines[oran_start + 11]),
                "Karşılıklı Gol_Var": float(lines[oran_start + 12]),
                "Karşılıklı Gol_Yok": float(lines[oran_start + 13]),
            }
            mac_kodu = lines[oran_start + 14]
            temel_maclar.append({
                "tarih_text": tarih_text, "saat": saat,
                "ev": ev, "dep": dep,
                "mac_kodu": mac_kodu, "temel": temel
            })
            print(f"   📋 {ev} vs {dep} ({saat}) - Kod: {mac_kodu}")
            i = oran_start + 15
        except:
            i += 1

    print(f"   📋 Toplam {len(temel_maclar)} maç bulundu")

    # 3. ADIM: hd linkleri topla
    print(f"\n🔗 Maç linkleri toplanıyor...")
    mac_linkleri = []

    for idx in range(len(temel_maclar)):
        tm = temel_maclar[idx]
        try:
            driver.get(url)
            time.sleep(5)
            # Scroll
            for s in range(20):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                yeni = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            takim_adlari = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
            tiklandi = False
            for ta in takim_adlari:
                ta_text = ta.text.strip()
                if tm["ev"] in ta_text and tm["dep"] in ta_text:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ta)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", ta)
                    time.sleep(3)
                    current_url = driver.current_url
                    if "hd=" in current_url:
                        hd = current_url.split("hd=")[1].split("&")[0]
                        mac_linkleri.append({
                            "ev": tm["ev"], "dep": tm["dep"],
                            "hd": hd, "url": current_url
                        })
                        print(f"   ✅ [{idx+1}/{len(temel_maclar)}] {tm['ev']} vs {tm['dep']} → hd={hd}")
                        tiklandi = True
                    break
            if not tiklandi:
                print(f"   ⚠️ [{idx+1}/{len(temel_maclar)}] {tm['ev']} vs {tm['dep']} → Bulunamadı")
        except Exception as e:
            print(f"   ⚠️ [{idx+1}/{len(temel_maclar)}] Hata: {str(e)[:60]}")

    print(f"\n📋 {len(mac_linkleri)} maç linki toplandı!")

    # 4. ADIM: Detay oranlarını çek
    print(f"\n🔽 Detaylı oranlar çekiliyor...\n")
    maclar = []

    for idx, tm in enumerate(temel_maclar):
        print(f"   [{idx+1}/{len(temel_maclar)}] {tm['ev']} vs {tm['dep']} ({tm['saat']})")
        detay_oranlar = {}

        hd_link = None
        for ml in mac_linkleri:
            if ml["ev"] == tm["ev"] and ml["dep"] == tm["dep"]:
                hd_link = ml
                break

        if hd_link:
            try:
                print(f"      🌐 Detay açılıyor... (hd={hd_link['hd']})")
                yuklendi = detay_sayfa_yukle(driver, hd_link["url"])
                
                if yuklendi:
                    # Oranların tam yüklenmesi için ekstra scroll
                    driver.execute_script("window.scrollTo(0, 2000);")
                    time.sleep(3)
                    driver.execute_script("window.scrollTo(0, 4000);")
                    time.sleep(3)
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(2)
                    
                    detay_oranlar = detay_parse(driver)
                    print(f"      📊 {len(detay_oranlar)} detay oranı çekildi")
                    if detay_oranlar:
                        for k, v in list(detay_oranlar.items())[:5]:
                            print(f"         • {k}: {v}")
                        if len(detay_oranlar) > 5:
                            print(f"         ... ve {len(detay_oranlar) - 5} oran daha")
                else:
                    print(f"      ❌ Detay yüklenemedi!")
            except Exception as e:
                print(f"      ⚠️ Hata: {e}")
        else:
            print(f"      ⚠️ hd linki yok")

        tum_oranlar = {**tm["temel"], **detay_oranlar}
        maclar.append({
            "index": 0,
            "mac_kodu": tm["mac_kodu"],
            "ev_sahibi": tm["ev"],
            "deplasman": tm["dep"],
            "saat": tm["saat"],
            "lig": "",
            "tarih": tarih_cevir(tm["tarih_text"]),
            "cekme_zamani": datetime.datetime.now().isoformat(),
            "durum": "baslamadi",
            "skor_ev": 0,
            "skor_dep": 0,
            "skor_1y_ev": 0,
            "skor_1y_dep": 0,
            "kaynak": "iddaa.com",
            "oranlar": tum_oranlar
        })
        print(f"      ✅ Toplam {len(tum_oranlar)} oran\n")

    return maclar

def mac_cek():
    driver = None
    try:
        driver = tarayici_baslat()
        maclar = iddaa_cek(driver)

        print(f"\n{'='*60}")
        print(f"📊 SONUÇ")
        print(f"   ⚽ Toplam maç: {len(maclar)}")
        if maclar:
            toplam_oran = sum(len(m["oranlar"]) for m in maclar)
            print(f"   📊 Toplam oran: {toplam_oran}")
            print(f"   📊 Ortalama: {toplam_oran // len(maclar)} oran/maç")
        print(f"{'='*60}")

        if maclar:
            veri_kaydet(maclar)
            print("\n🎉 İşlem tamamlandı!")
            print(f"📁 Dosya: {os.path.abspath(CIKTI_DOSYA)}")
            print(f"\n📌 GitHub'a yükleyin:")
            print(f"   git add -A")
            print(f'   git commit -m "Oranlar güncellendi"')
            print(f"   git push")
        else:
            print("\n❌ Maç bulunamadı!")
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            input("\n⏸️ Enter'a basın Chrome kapansın...")
            driver.quit()
            print("🌐 Chrome kapatıldı.")

if __name__ == "__main__":
    print("⚽ İddaa Oran Çekici - iddaa.com DETAYLI v9.0")
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)
    mac_cek()