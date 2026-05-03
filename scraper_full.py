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
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome başlatıldı!")
    return driver

def mac_json_kaydet(yeni_maclar):
    data = {"version": 2, "updated": "", "matches": []}
    if os.path.exists(CIKTI_DOSYA):
        try:
            with open(CIKTI_DOSYA, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            pass
    
    guncel_dict = {f"{m['tarih']}_{m['ev_sahibi']}_{m['deplasman']}": m for m in data.get("matches", [])}
    for ym in yeni_maclar:
        guncel_dict[f"{ym['tarih']}_{ym['ev_sahibi']}_{ym['deplasman']}"] = ym
    
    yeni_liste = sorted(guncel_dict.values(), key=lambda x: (x["tarih"], x["saat"]))
    for i, m in enumerate(yeni_liste, 1):
        m["index"] = i
    
    data["matches"] = yeni_liste
    data["updated"] = datetime.datetime.now().isoformat()
    
    with open(CIKTI_DOSYA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"   💾 Toplam {len(yeni_liste)} maç kaydedildi")

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

def tum_maclari_yukle(driver, url):
    driver.get(url)
    print("   ⏳ Maçlar yükleniyor (max 30sn)...")
    for _ in range(30):
        maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
        if len(maclar) > 0:
            print(f"   ✅ {len(maclar)} maç bulundu")
            return len(maclar)
        time.sleep(1)
    print("   ⚠️ Maç bulunamadı (timeout)")
    return 0

def iddaa_cek(driver):
    bugun = datetime.date.today()
    url = f"https://www.iddaa.com/program/futbol?date={bugun.strftime('%d.%m.%Y')}"
    
    print(f"📡 {url}")
    toplam = tum_maclari_yukle(driver, url)
    
    if toplam == 0:
        print("   ❌ Maç bulunamadı!")
        return []
    
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
    
    print(f"\n🔽 Maçlar tek tek açılıyor...\n")
    maclar = []
    basarili = 0
    basarisiz = 0
    
    for idx, mac in enumerate(mac_listesi):
        print(f"   [{idx+1}/{len(mac_listesi)}] {mac['ev']} vs {mac['dep']}")
        
        temel_oranlar = {}
        detay_oranlar = {}
        mac_saat = ""
        mac_kodu = ""
        
        for deneme in range(3):
            try:
                driver.get(url)
                time.sleep(10)
                
                body = driver.find_element(By.TAG_NAME, "body")
                lines = [l.strip() for l in body.text.split("\n") if l.strip()]
                
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
                
                takim_els = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
                for ta in takim_els:
                    ta_text = ta.text.strip()
                    if mac['ev'] in ta_text and mac['dep'] in ta_text:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ta)
                        time.sleep(2)
                        driver.execute_script("arguments[0].click();", ta)
                        time.sleep(6)
                        
                        if tumu_bekle(driver, 25):
                            driver.execute_script("window.scrollTo(0, 800);")
                            time.sleep(2)
                            driver.execute_script("window.scrollTo(0, 1600);")
                            time.sleep(2)
                            driver.execute_script("window.scrollTo(0, 0);")
                            time.sleep(2)
                            detay_oranlar = detay_parse(driver)
                        break
                
                if len(detay_oranlar) > 0:
                    print(f"      ✅ {len(detay_oranlar)} detay oran çekildi")
                    break
                
                if deneme < 2:
                    print(f"      ⏳ Deneme {deneme+1} başarısız, 30sn sonra tekrar...")
                    time.sleep(30)
                else:
                    print("      ❌ 3 deneme de başarısız oldu")
                    
            except Exception as e:
                print(f"      ⚠️ Hata: {str(e)[:60]}")
                if deneme < 2:
                    print(f"      ⏳ Hata sonrası 30sn bekleniyor...")
                    time.sleep(30)
        
        if len(detay_oranlar) > 0:
            basarili += 1
        else:
            basarisiz += 1
        
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
        
        if (idx + 1) % 10 == 0:
            mac_json_kaydet(maclar)
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
            mac_json_kaydet(maclar)
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