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
    print(f"   💾 {len(yeni_liste)} maç kaydedildi")

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

def detay_parse(driver):
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
    sekmeler = ["Kim Kazanır","Alt/Üst","Goller","Skor","Diğer",
                "Oyuncu","Özel","Kombo","Korner/Kart","Korner",
                "Kart","Handikap","Yarı","Dakika","Asist",
                "Toplam","İstatistik","Kombine"]
    while i < len(lines) and lines[i] in sekmeler:
        i += 1
    dur = ["Bugün","Yarın","Yardım","Hakkımızda","İletişim",
           "Gizlilik","Popüler Bahisler","Kolay Kuponlar","Spor Toto",
           "Bülten","Canlı Sonuçlar","Yazar Yorumları"]
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
             "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    current_market = ""
    while i < len(lines):
        line = lines[i]
        if line in dur:
            break
        if any(ay in line for ay in aylar) and any(c.isdigit() for c in line):
            break
        if saat_mi(line):
            break
        if line.isupper() and len(line) > 2:
            i += 1
            continue
        if i + 1 < len(lines):
            sonraki = lines[i + 1]
            if nokta_var_mi(sonraki):
                outcome = line
                oran = float(sonraki)
                key = f"{current_market}_{outcome}" if current_market else outcome
                oranlar[key] = oran
                i += 2
                continue
        if not nokta_var_mi(line):
            current_market = line
        i += 1
    return oranlar

def tumu_bekle(driver, max_sure=20):
    for _ in range(max_sure):
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            if "Tümü" in body.text:
                return True
        except:
            pass
        time.sleep(1)
    return False

def tum_maclari_yukle(driver, url):
    """Sayfayı aç, butonlara tıkla, TÜM maçları yükle"""
    driver.get(url)
    time.sleep(10)
    
    print("   📜 Tüm maçlar yükleniyor...")
    onceki = 0
    
    degismedi = 0
    for tur in range(200):
        # Devamını gör + Daha fazla göster butonlarına bas
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                try:
                    txt = btn.text.strip()
                    if "Devamını gör" in txt or "Daha fazla" in txt or "devamını" in txt.lower():
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(5)
                except:
                    continue
        except:
            pass
        
        # Scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
        sayi = len(maclar)
        
        if tur % 10 == 0:
            print(f"   📜 Tur {tur}: {sayi} maç")
        
        if sayi == onceki:
            degismedi += 1
            if degismedi >= 5:
                break
        else:
            degismedi = 0
        onceki = sayi
    
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    
    maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
    print(f"   ✅ Toplam {len(maclar)} maç yüklendi!")
    return len(maclar)

def iddaa_cek(driver):
    bugun = datetime.date.today()
    url = f"https://www.iddaa.com/program/futbol?date={bugun.strftime('%d.%m.%Y')}"
    
    # 1. Sayfayı aç ve TÜM maçları yükle
    print(f"📡 {url}")
    toplam = tum_maclari_yukle(driver, url)
    
    if toplam == 0:
        print("   ❌ Maç bulunamadı!")
        return []
    
    # 2. Tüm maç isimlerini topla
    print(f"\n🔍 Maç isimleri toplanıyor...")
    takim_adlari = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
    
    mac_listesi = []
    for ta in takim_adlari:
        try:
            txt = ta.text.strip()
            parcalar = txt.split("\n")
            ev = ""
            dep = ""
            for p in parcalar:
                p = p.strip()
                if p and p != "-":
                    if not ev:
                        ev = p
                    elif not dep:
                        dep = p
            if ev and dep:
                mac_listesi.append({"ev": ev, "dep": dep})
        except:
            continue
    
    print(f"   📋 {len(mac_listesi)} maç bulundu:")
    for i, m in enumerate(mac_listesi):
        print(f"      {i+1}. {m['ev']} vs {m['dep']}")
    
    # 3. Her maç için: sayfa yükle → maça tıkla → oranları çek
    print(f"\n🔽 Maçlar tek tek açılıyor...\n")
    maclar = []
    basarili = 0
    basarisiz = 0
    
    for idx, mac in enumerate(mac_listesi):
        print(f"   [{idx+1}/{len(mac_listesi)}] {mac['ev']} vs {mac['dep']}")
        
        # Sayfayı yeniden yükle (504 koruması)
        time.sleep(10)
        driver.get(url)
        time.sleep(12)
        
        # 504 kontrolü
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            if "504" in body_text or "Gateway" in body_text or "didn't respond" in body_text:
                print(f"      ⏳ 504 hatası! 3 dakika bekleniyor...")
                time.sleep(180)
                driver.get(url)
                time.sleep(15)
        except:
            pass
        
        # Devamını gör / Daha fazla göster butonlarına bas
        for _ in range(20):
            try:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                tiklandi = False
                for btn in buttons:
                    try:
                        txt = btn.text.strip()
                        if "Devamını gör" in txt or "Daha fazla" in txt:
                            driver.execute_script("arguments[0].click();", btn)
                            tiklandi = True
                            time.sleep(3)
                            break
                    except:
                        continue
                if not tiklandi:
                    break
            except:
                break
        
        # Scroll yaparak tüm maçları yükle
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # Temel oranları body text'ten oku
        body = driver.find_element(By.TAG_NAME, "body")
        lines = [l.strip() for l in body.text.split("\n") if l.strip()]
        
        temel_oranlar = {}
        mac_saat = ""
        mac_kodu = ""
        
        # Maçı bul
        for li in range(len(lines) - 15):
            if lines[li + 2] == mac['ev'] and lines[li + 4] == mac['dep'] and lines[li + 3] == "-":
                mac_saat = lines[li + 1] if saat_mi(lines[li + 1]) else ""
                oran_start = li + 5
                if lines[oran_start] == "Kral Oran":
                    oran_start = li + 7
                if nokta_var_mi(lines[oran_start]):
                    try:
                        temel_oranlar = {
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
                    except:
                        pass
                break
        
        # Maça tıkla
        detay_oranlar = {}
        try:
            takim_els = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
            for ta in takim_els:
                ta_text = ta.text.strip()
                if mac['ev'] in ta_text and mac['dep'] in ta_text:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ta)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", ta)
                    
                    # Tümü görünene kadar bekle
                    bulundu = tumu_bekle(driver, 20)
                    
                    if bulundu:
                        # Scroll ile tüm oranları yükle
                        driver.execute_script("window.scrollTo(0, 500);")
                        time.sleep(2)
                        driver.execute_script("window.scrollTo(0, 1000);")
                        time.sleep(2)
                        driver.execute_script("window.scrollTo(0, 1500);")
                        time.sleep(2)
                        driver.execute_script("window.scrollTo(0, 2000);")
                        time.sleep(2)
                        driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(2)
                        
                        detay_oranlar = detay_parse(driver)
                        basarili += 1
                        print(f"      ✅ {len(detay_oranlar)} detay oran")
                    else:
                        basarisiz += 1
                        print(f"      ❌ Detay yüklenemedi")
                    break
        except Exception as e:
            basarisiz += 1
            print(f"      ❌ Hata: {str(e)[:40]}")
        
        # Birleştir
        tum_oranlar = {**temel_oranlar, **detay_oranlar}
        
        maclar.append({
            "index": 0,
            "mac_kodu": mac_kodu,
            "ev_sahibi": mac['ev'],
            "deplasman": mac['dep'],
            "saat": mac_saat,
            "lig": "",
            "tarih": bugun.isoformat(),
            "cekme_zamani": datetime.datetime.now().isoformat(),
            "durum": "baslamadi",
            "skor_ev": 0,
            "skor_dep": 0,
            "skor_1y_ev": 0,
            "skor_1y_dep": 0,
            "kaynak": "iddaa.com",
            "oranlar": tum_oranlar
        })
        
        print(f"      📊 Toplam {len(tum_oranlar)} oran")
        
        # Her 10 maçta kaydet
        if (idx + 1) % 10 == 0:
            veri_kaydet(maclar)
            print(f"   💾 {len(maclar)} maç kaydedildi (✅{basarili} ❌{basarisiz})")
    
    return maclar

def mac_cek():
    driver = None
    baslangic = datetime.datetime.now()
    try:
        driver = tarayici_baslat()
        maclar = iddaa_cek(driver)
        bitis = datetime.datetime.now()
        sure = bitis - baslangic

        print(f"\n{'='*60}")
        print(f"📊 FİNAL SONUÇ")
        print(f"   ⚽ Toplam maç: {len(maclar)}")
        if maclar:
            toplam_oran = sum(len(m["oranlar"]) for m in maclar)
            basarili = sum(1 for m in maclar if len(m["oranlar"]) > 14)
            print(f"   📊 Toplam oran: {toplam_oran}")
            print(f"   📊 Ortalama: {toplam_oran // len(maclar)} oran/maç")
            print(f"   ✅ Detaylı: {basarili}")
        print(f"   ⏱️ Süre: {sure}")
        print(f"{'='*60}")

        if maclar:
            veri_kaydet(maclar)
            print("\n🎉 İşlem tamamlandı!")
            print(f"\n📌 GitHub'a yükleyin:")
            print(f"   git add -A")
            print(f'   git commit -m "Oranlar guncellendi"')
            print(f"   git push")
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print("⚽ İddaa Oran Çekici - BUGÜNÜN TÜM MAÇLARI")
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)
    mac_cek()