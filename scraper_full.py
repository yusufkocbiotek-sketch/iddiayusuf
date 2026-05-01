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
    options.add_argument("--disable-gpu")
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
    aylar_list = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
                  "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    current_market = ""
    while i < len(lines):
        line = lines[i]
        if line in dur:
            break
        if any(ay in line for ay in aylar_list) and any(c.isdigit() for c in line):
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
    """Tümü görünene kadar bekle"""
    for _ in range(max_sure):
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            if "Tümü" in body.text:
                return True
        except:
            pass
        time.sleep(1)
    return False

def sayfa_yukle(driver, url):
    """Sayfayı yükle ve maçların yüklenmesini bekle"""
    driver.get(url)
    time.sleep(5)
    for _ in range(30):
        try:
            maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
            if len(maclar) > 0:
                time.sleep(3)
                return len(maclar)
        except:
            pass
        time.sleep(1)
    return 0

def temel_oranlari_oku(driver):
    """Sayfadaki maçların temel oranlarını oku"""
    temel_maclar = []
    body = driver.find_element(By.TAG_NAME, "body")
    lines = [l.strip() for l in body.text.split("\n") if l.strip()]
    i = 0
    while i < len(lines) - 15:
        saat = lines[i + 1] if i + 1 < len(lines) else ""
        if not saat_mi(saat):
            i += 1
            continue
        tarih_text = lines[i]
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
                "saat": saat, "ev": ev, "dep": dep,
                "mac_kodu": mac_kodu, "temel": temel
            })
            i = oran_start + 15
        except:
            i += 1
    return temel_maclar

def tarihleri_al(driver):
    """Tarih dropdown'ından günleri al"""
    bugun = datetime.date.today()
    tarihler = []
    
    # Bugünü ekle
    tarihler.append({
        "adi": "Bugün",
        "url_tarih": bugun.strftime("%d.%m.%Y"),
        "iso_tarih": bugun.isoformat()
    })
    
    sboxes = driver.find_elements(By.CSS_SELECTOR, ".style_selectBox__mo_KX")
    for sb in sboxes:
        try:
            if sb.text.strip().split("\n")[0] == "Tarih":
                driver.execute_script("arguments[0].click();", sb)
                time.sleep(3)
                try:
                    dropdown = sb.find_element(By.CSS_SELECTOR, "div[class*='absolute']")
                    labels = dropdown.find_elements(By.TAG_NAME, "i")
                except:
                    labels = sb.find_elements(By.TAG_NAME, "i")
                
                aylar = {"Ocak":1,"Şubat":2,"Mart":3,"Nisan":4,"Mayıs":5,"Haziran":6,
                         "Temmuz":7,"Ağustos":8,"Eylül":9,"Ekim":10,"Kasım":11,"Aralık":12}
                
                for label in labels:
                    try:
                        txt = label.text.strip()
                        if not txt or txt == "Bugün":
                            continue
                        if txt == "Yarın":
                            yarin = bugun + datetime.timedelta(days=1)
                            tarihler.append({
                                "adi": txt,
                                "url_tarih": yarin.strftime("%d.%m.%Y"),
                                "iso_tarih": yarin.isoformat()
                            })
                        else:
                            parcalar = txt.replace(",", "").split()
                            if len(parcalar) >= 2:
                                gun = int(parcalar[0])
                                ay = aylar.get(parcalar[1], 0)
                                if ay > 0:
                                    tarih_obj = datetime.date(bugun.year, ay, gun)
                                    tarihler.append({
                                        "adi": txt,
                                        "url_tarih": tarih_obj.strftime("%d.%m.%Y"),
                                        "iso_tarih": tarih_obj.isoformat()
                                    })
                    except:
                        continue
                
                driver.find_element(By.TAG_NAME, "body").click()
                time.sleep(2)
                break
        except:
            continue
    return tarihler

def iddaa_full_cek(driver):
    base_url = "https://www.iddaa.com/program/futbol"
    
    # 1. Tarihleri al
    print(f"📡 {base_url} açılıyor...")
    driver.get(base_url)
    time.sleep(10)
    tarihler = tarihleri_al(driver)
    
    print(f"\n📅 {len(tarihler)} gün bulundu:")
    for t in tarihler:
        print(f"   • {t['adi']} → {t['url_tarih']}")
    
    tum_maclar = []
    
    for gun_idx, gun in enumerate(tarihler):
        print(f"\n{'='*60}")
        print(f"📅 [{gun_idx+1}/{len(tarihler)}] {gun['adi']} ({gun['url_tarih']})")
        print(f"{'='*60}")
        
        gun_url = base_url if gun['adi'] == "Bugün" else f"{base_url}?date={gun['url_tarih']}"
        
        # Sayfayı yükle
        mac_sayisi = sayfa_yukle(driver, gun_url)
        print(f"   📋 {mac_sayisi} maç yüklendi")
        
        if mac_sayisi == 0:
            print(f"   ⚠️ Maç yok, atlanıyor")
            continue
        
        # Temel oranları oku
        temel_maclar = temel_oranlari_oku(driver)
        print(f"   📋 {len(temel_maclar)} maçın temel oranları okundu")
        
        if not temel_maclar:
            continue
        
        basarili = 0
        basarisiz = 0
        
        for idx, tm in enumerate(temel_maclar):
            detay_oranlar = {}
            
            try:
                # Her maç için sayfayı yeniden yükle
                sayfa_yukle(driver, gun_url)
                
                # Scroll (tüm maçlar görünsün)
                for _ in range(5):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(2)
                
                # Doğru maçı bul ve tıkla
                takim_adlari = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
                
                for ta in takim_adlari:
                    try:
                        ta_text = ta.text.strip()
                        if tm["ev"] in ta_text and tm["dep"] in ta_text:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ta)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", ta)
                            
                            # SPA navigasyonu - Tümü görünene kadar bekle
                            bulundu = tumu_bekle(driver, 20)
                            
                            if bulundu:
                                # Tüm oranlar yüklensin diye scroll
                                driver.execute_script("window.scrollTo(0, 500);")
                                time.sleep(2)
                                driver.execute_script("window.scrollTo(0, 1000);")
                                time.sleep(2)
                                driver.execute_script("window.scrollTo(0, 1500);")
                                time.sleep(2)
                                driver.execute_script("window.scrollTo(0, 2000);")
                                time.sleep(2)
                                driver.execute_script("window.scrollTo(0, 3000);")
                                time.sleep(2)
                                driver.execute_script("window.scrollTo(0, 0);")
                                time.sleep(2)
                                
                                detay_oranlar = detay_parse(driver)
                                basarili += 1
                            else:
                                basarisiz += 1
                            break
                    except:
                        continue
                        
            except Exception as e:
                basarisiz += 1
            
            tum_oranlar = {**tm["temel"], **detay_oranlar}
            
            tum_maclar.append({
                "index": 0, "mac_kodu": tm["mac_kodu"],
                "ev_sahibi": tm["ev"], "deplasman": tm["dep"],
                "saat": tm["saat"], "lig": "",
                "tarih": gun["iso_tarih"],
                "cekme_zamani": datetime.datetime.now().isoformat(),
                "durum": "baslamadi",
                "skor_ev": 0, "skor_dep": 0,
                "skor_1y_ev": 0, "skor_1y_dep": 0,
                "kaynak": "iddaa.com",
                "oranlar": tum_oranlar
            })
            
            if (idx + 1) % 5 == 0 or idx == 0 or idx == len(temel_maclar) - 1:
                print(f"      [{idx+1}/{len(temel_maclar)}] {tm['ev']} vs {tm['dep']} → {len(tum_oranlar)} oran")
        
        gun_maclar = tum_maclar[-len(temel_maclar):]
        gun_oran = sum(len(m["oranlar"]) for m in gun_maclar)
        print(f"   📊 {gun['adi']}: {len(temel_maclar)} maç | ✅{basarili} ❌{basarisiz} | {gun_oran} oran")
        veri_kaydet(tum_maclar)
        print(f"   💾 Toplam: {len(tum_maclar)} maç")
    
    return tum_maclar

def mac_cek():
    driver = None
    baslangic = datetime.datetime.now()
    try:
        driver = tarayici_baslat()
        maclar = iddaa_full_cek(driver)
        bitis = datetime.datetime.now()
        sure = bitis - baslangic
        print(f"\n{'='*60}")
        print(f"📊 FİNAL SONUÇ")
        print(f"   ⚽ Toplam maç: {len(maclar)}")
        if maclar:
            toplam_oran = sum(len(m["oranlar"]) for m in maclar)
            print(f"   📊 Toplam oran: {toplam_oran}")
            print(f"   📊 Ortalama: {toplam_oran // len(maclar)} oran/maç")
        print(f"   ⏱️ Süre: {sure}")
        print(f"{'='*60}")
        if maclar:
            veri_kaydet(maclar)
            print("\n🎉 İşlem tamamlandı!")
            print(f"\n📌 GitHub'a yükleyin:")
            print(f"   git add -A")
            print(f'   git commit -m "Tum oranlar guncellendi"')
            print(f"   git push")
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            input("\n⏸️ Enter'a basın Chrome kapansın...")
            driver.quit()

if __name__ == "__main__":
    print("⚽ İddaa FULL Oran Çekici v5.0 - TÜM GÜNLER")
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"⚠️ Bu işlem birkaç saat sürebilir!")
    print("=" * 60)
    mac_cek()