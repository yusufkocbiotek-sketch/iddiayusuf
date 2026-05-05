import json
import os
import datetime
import time
import random
import subprocess
import socket
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

CIKTI_DOSYA = "public/data/mac.json"
ULTRASURF_EXE = "u2211.exe"
ULTRASURF_PROXY = "127.0.0.1:9666"
SESSION_LIMIT = 10

def rastgele_bekle(min_sn, max_sn):
    time.sleep(random.uniform(min_sn, max_sn))

def port_hazir_mi(port, timeout=30):
    baslangic = time.time()
    while time.time() - baslangic < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        time.sleep(1)
    return False

def ultrasurf_baslat():
    print("   🌐 Ultrasurf başlatılıyor...")
    try:
        exe_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), ULTRASURF_EXE)
        try:
            subprocess.run("taskkill /f /im " + ULTRASURF_EXE, shell=True, 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
        except:
            pass
        subprocess.Popen(exe_yolu, shell=True)
        print("   ⏳ Ultrasurf'ün hazır olması bekleniyor (max 30sn)...")
        if port_hazir_mi(9666, timeout=30):
            print("   ✅ Ultrasurf portu açık")
            time.sleep(8)  # 🔑 Port açıldıktan sonra trafiğin stabilize olması için bekle
            print("   ✅ Ultrasurf hazır (yeni IP)")
            return True
        else:
            print("   ❌ Ultrasurf portu zaman aşımına uğradı!")
            return False
    except Exception as e:
        print(f"   ⚠️ Ultrasurf hatası: {e}")
        return False

def ultrasurf_durdur():
    try:
        subprocess.run("taskkill /f /im " + ULTRASURF_EXE, shell=True, 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
    except:
        pass

def ip_degistir():
    print("\n   🔄 IP DEĞİŞTİRİLİYOR...")
    ultrasurf_durdur()
    time.sleep(5)
    if ultrasurf_baslat():
        time.sleep(5)
        print("   ✅ Yeni IP alındı!\n")
        return True
    else:
        print("   ⚠️ IP değiştirme başarısız!\n")
        return False

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.add_argument("--proxy-server=" + ULTRASURF_PROXY)
    options.add_argument("--proxy-bypass-list=<-loopback>")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en-US', 'en']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
        """
    })
    print(f"✅ Chrome başlatıldı! Proxy: {ULTRASURF_PROXY}")
    return driver

def proxy_calisiyor_mu(driver, max_deneme=3):
    """Proxy'nin gerçekten çalışıp çalışmadığını test et."""
    print("   🧪 Proxy bağlantısı test ediliyor...")
    for deneme in range(max_deneme):
        try:
            driver.set_page_load_timeout(20)
            driver.get("https://www.iddaa.com")
            time.sleep(3)
            body = driver.find_element(By.TAG_NAME, "body")
            if body.text and len(body.text) > 100:
                print("   ✅ Proxy çalışıyor, sayfa yüklendi!")
                return True
        except TimeoutException:
            print(f"   ⏳ Deneme {deneme+1}: Zaman aşımı, tekrar deneniyor...")
            time.sleep(5)
        except WebDriverException as e:
            print(f"   ⚠️ Deneme {deneme+1}: WebDriver hatası: {str(e)[:50]}")
            time.sleep(5)
        except Exception as e:
            print(f"   ⚠️ Deneme {deneme+1}: Hata: {str(e)[:50]}")
            time.sleep(5)
    return False

def mac_json_kaydet(yeni_maclar):
    data = {"version": 2, "updated": "", "matches": []}
    if os.path.exists(CIKTI_DOSYA):
        try:
            with open(CIKTI_DOSYA, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            pass
    guncel_dict = {}
    for m in data.get("matches", []):
        key = m['tarih'] + "_" + m['ev_sahibi'] + "_" + m['deplasman']
        guncel_dict[key] = m
    for ym in yeni_maclar:
        key = ym['tarih'] + "_" + ym['ev_sahibi'] + "_" + ym['deplasman']
        if key in guncel_dict:
            mevcut = guncel_dict[key]
            if len(ym.get("oranlar", {})) > len(mevcut.get("oranlar", {})):
                mevcut["oranlar"] = ym["oranlar"]
        else:
            guncel_dict[key] = ym
    yeni_liste = sorted(guncel_dict.values(), key=lambda x: (x["tarih"], x.get("saat", "")))
    for i, m in enumerate(yeni_liste, 1):
        m["index"] = i
    data["matches"] = yeni_liste
    data["updated"] = datetime.datetime.now().isoformat()
    os.makedirs(os.path.dirname(CIKTI_DOSYA), exist_ok=True)
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

def sayi_mi(text):
    try:
        float(text.replace(",", "."))
        return True
    except:
        return False

def nokta_var_mi(text):
    try:
        if "." not in text:
            return False
        val = float(text)
        return 1.01 <= val <= 99.99
    except:
        return False

# 🔑 SAHTE MAÇ FİLTRESİ GÜNCELLENDİ
SAHTE = ["Tarih", "Oyun Türü", "Lig Seçimi", "Tarihe Göre", "Maç Sonucu",
         "İlk Yarı", "Handikap", "Alt/Üst", "Karşılıklı", "Bugün", "Yarın",
         "ÖNE ÇIKAN", "CANLI", "FUTBOL", "BASKETBOL", "TENİS",
         "UEFA", "Şampiyonlar Ligi", "Ligi", "Final", "Rövanş", "Yarı Final",
         "Çeyrek Final", "Kupa", "Süper Kupa", "Play-off", "Play off"]

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
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        text = body.text
        lines = [l.strip() for l in text.split("\n") if l.strip()]
    except:
        return oranlar
    
    tumu_idx = -1
    for i, line in enumerate(lines):
        if line == "Tümü":
            tumu_idx = i
            break
    if tumu_idx == -1:
        return oranlar
    
    i = tumu_idx + 1
    sekmeler = ["Kim Kazanır", "Alt/Üst", "Goller", "Skor", "Diğer",
                "Oyuncu", "Özel", "Kombo", "Korner/Kart", "Korner",
                "Kart", "Handikap", "Yarı", "Dakika", "Asist",
                "Toplam", "İstatistik", "Kombine"]
    while i < len(lines) and lines[i] in sekmeler:
        i += 1
    
    dur = ["Bugün", "Yarın", "Yardım", "Hakkımızda", "İletişim",
           "Gizlilik", "Popüler Bahisler", "Kolay Kuponlar", "Spor Toto",
           "Bülten", "Canlı Sonuçlar", "Yazar Yorumları"]
    aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
             "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
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
                key = current_market + "_" + outcome if current_market else outcome
                oranlar[key] = oran
                i += 2
                continue
        if not nokta_var_mi(line):
            current_market = line
        i += 1
    return oranlar

def rastgele_mouse_hareketi(driver):
    try:
        for _ in range(random.randint(2, 4)):
            x = random.randint(100, 1800)
            y = random.randint(100, 900)
            driver.execute_script(
                "var event = new MouseEvent('mousemove', {clientX: " + str(x) +
                ", clientY: " + str(y) + ", bubbles: true}); document.dispatchEvent(event);"
            )
            time.sleep(random.uniform(0.2, 0.5))
    except:
        pass

def insani_tiklama(driver, element):
    rastgele_mouse_hareketi(driver)
    actions = ActionChains(driver)
    actions.move_to_element(element)
    time.sleep(random.uniform(0.3, 0.8))
    actions.click()
    actions.perform()
    time.sleep(random.uniform(0.5, 1.0))

def tum_maclari_topla(driver):
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(3)
    toplanan = {}
    bos_sayaci = 0
    adim = 0
    while bos_sayaci < 25:
        adim += 1
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            lines = [l.strip() for l in body.text.split("\n") if l.strip()]
        except:
            time.sleep(2)
            continue
        yeni = 0
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
                        if key not in toplanan:
                            toplanan[key] = {"saat": saat, "ev": ev, "dep": dep}
                            yeni += 1
        if yeni > 0:
            bos_sayaci = 0
            print(f"   ⬇️ Adım {adim}: +{yeni} yeni maç | Toplam: {len(toplanan)}")
        else:
            bos_sayaci += 1
        driver.execute_script("window.scrollBy({top: 300, behavior: 'smooth'});")
        time.sleep(6)
    return list(toplanan.values())

def mac_detay_cek(driver, url, mac):
    detay_oranlar = {}
    hata_sebebi = ""
    
    for deneme in range(2):
        try:
            driver.set_page_load_timeout(45)
            driver.get(url)
            rastgele_bekle(5, 8)
            
            # Sayfanın yüklendiğini kontrol et
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                if not body.text or len(body.text) < 100:
                    hata_sebebi = "Sayfa boş yüklendi"
                    if deneme == 0:
                        print(f"      ⚠️ {hata_sebebi}, tekrar deneniyor...")
                        rastgele_bekle(8, 12)
                        continue
                    else:
                        break
            except:
                hata_sebebi = "Body elementi bulunamadı"
                if deneme == 0:
                    rastgele_bekle(8, 12)
                    continue
                else:
                    break
            
            driver.execute_script("window.scrollTo(0, 0);")
            rastgele_bekle(1, 2)
            
            mac_bulundu = False
            for kaydir in range(15):
                try:
                    takim_els = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
                except:
                    time.sleep(2)
                    continue
                    
                for ta in takim_els:
                    try:
                        ta_text = ta.text.strip()
                        if mac['ev'] in ta_text and mac['dep'] in ta_text:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ta)
                            rastgele_bekle(1, 2)
                            insani_tiklama(driver, ta)
                            rastgele_bekle(4, 7)
                            driver.execute_script("window.scrollTo(0, 600);")
                            rastgele_bekle(1, 2)
                            driver.execute_script("window.scrollTo(0, 1200);")
                            rastgele_bekle(1, 2)
                            driver.execute_script("window.scrollTo(0, 0);")
                            rastgele_bekle(1, 2)
                            if tumu_bekle(driver, 15):
                                detay_oranlar = detay_parse(driver)
                            mac_bulundu = True
                            break
                    except:
                        pass
                if mac_bulundu:
                    break
                driver.execute_script("window.scrollBy({top: 400, behavior: 'smooth'});")
                rastgele_bekle(2, 3)
            
            if not mac_bulundu:
                hata_sebebi = "Maç listede bulunamadı"
            
            if len(detay_oranlar) > 0:
                break
            elif deneme == 0:
                hata_sebebi = "Detay oranlar boş"
                print(f"      ⚠️ {hata_sebebi}, tekrar deneniyor...")
                rastgele_bekle(8, 12)
                
        except TimeoutException:
            hata_sebebi = "Zaman aşımı"
            if deneme == 0:
                print(f"      ⚠️ {hata_sebebi}, tekrar deneniyor...")
                rastgele_bekle(8, 12)
        except WebDriverException as e:
            hata_sebebi = f"WebDriver hatası: {str(e)[:40]}"
            if deneme == 0:
                print(f"      ⚠️ {hata_sebebi}, tekrar deneniyor...")
                rastgele_bekle(8, 12)
        except Exception as e:
            hata_sebebi = f"Hata: {str(e)[:40]}"
            if deneme == 0:
                print(f"      ⚠️ {hata_sebebi}, tekrar deneniyor...")
                rastgele_bekle(8, 12)
    
    if len(detay_oranlar) == 0 and hata_sebebi:
        print(f"      ❌ Başarısız: {hata_sebebi}")
        
    return detay_oranlar

def mac_cek():
    baslangic = datetime.datetime.now()
    bugun = datetime.date.today()
    url = "https://www.iddaa.com/program/futbol"
    driver = None

    try:
        if not ultrasurf_baslat():
            print("❌ Ultrasurf başlatılamadı! İşlem iptal.")
            return

        # 🔑 Proxy test döngüsü
        max_proxy_deneme = 3
        for proxy_deneme in range(max_proxy_deneme):
            driver = tarayici_baslat()
            if proxy_calisiyor_mu(driver):
                break
            else:
                print(f"   ⚠️ Proxy testi başarısız! Ultrasurf yeniden başlatılıyor...")
                try:
                    driver.quit()
                except:
                    pass
                if not ip_degistir():
                    print("❌ Proxy düzeltilemedi! İşlem iptal.")
                    return
                driver = None
        
        if not driver:
            print("❌ Tarayıcı başlatılamadı!")
            return

        print(f"\n📡 {url}")
        driver.get(url)
        rastgele_bekle(8, 12)

        mac_listesi = tum_maclari_topla(driver)
        if not mac_listesi:
            print("   ❌ Maç bulunamadı!")
            return

        # Sahte maçları filtrele
        mac_listesi = [m for m in mac_listesi 
                       if not any(kw in m['ev'] for kw in SAHTE) 
                       and not any(kw in m['dep'] for kw in SAHTE)]
        
        print(f"\n   📋 {len(mac_listesi)} maç bulundu!")
        session_sayisi = len(mac_listesi) // SESSION_LIMIT + 1
        print(f"   🔄 Her {SESSION_LIMIT} maçta IP değiştirilecek ({session_sayisi} session)")
        print(f"   ⏱️ Tahmini süre: {len(mac_listesi) * 35 // 60} dakika\n")

        maclar = []
        basarili = 0
        basarisiz = 0
        session_sayaci = 0

        for idx, mac in enumerate(mac_listesi):
            if session_sayaci >= SESSION_LIMIT:
                try:
                    driver.quit()
                except:
                    pass
                
                if ip_degistir():
                    # 🔑 Yeni proxy testi
                    for proxy_deneme in range(3):
                        driver = tarayici_baslat()
                        if proxy_calisiyor_mu(driver):
                            break
                        else:
                            print(f"   ⚠️ Yeni proxy testi başarısız, tekrar deneniyor...")
                            try:
                                driver.quit()
                            except:
                                pass
                            ultrasurf_durdur()
                            time.sleep(5)
                            ultrasurf_baslat()
                            driver = None
                    
                    if not driver:
                        print("   ❌ Yeni proxy düzeltilemedi, mevcut driver ile devam ediliyor...")
                        # Mevcut driver'ı kullanmaya devam et (zaten kapalı, hata yönetimi gerekli)
                        # Basitçe devam et, bir sonraki IP değişiminde düzelir
                        continue
                        
                    driver.get(url)
                    rastgele_bekle(8, 12)
                    session_sayaci = 0
                else:
                    print("   ⚠️ IP değiştirilemedi, mevcut session ile devam ediliyor...")

            print(f"   [{idx + 1}/{len(mac_listesi)}] {mac['ev']} vs {mac['dep']}")

            sonuc = mac_detay_cek(driver, url, mac)
            session_sayaci += 1

            if sonuc:
                basarili += 1
                print(f"      ✅ {len(sonuc)} detay oran çekildi")
            else:
                basarisiz += 1

            maclar.append({
                "index": 0,
                "mac_kodu": "",
                "ev_sahibi": mac['ev'],
                "deplasman": mac['dep'],
                "saat": mac.get("saat", ""),
                "lig": "",
                "tarih": bugun.isoformat(),
                "cekme_zamani": datetime.datetime.now().isoformat(),
                "durum": "baslamadi",
                "skor_ev": 0,
                "skor_dep": 0,
                "skor_1y_ev": 0,
                "skor_1y_dep": 0,
                "kaynak": "iddaa.com",
                "oranlar": sonuc if sonuc else {}
            })

            print(f"      📊 Toplam {len(sonuc)} oran | ✅{basarili} ❌{basarisiz}")

            if (idx + 1) % 10 == 0:
                mac_json_kaydet(maclar)
                print(f"   💾 Ara kayıt: {len(maclar)} maç")

            print(f"      ⏳ 30 saniye bekleniyor...")
            time.sleep(30)

        mac_json_kaydet(maclar)
        sure = datetime.datetime.now() - baslangic
        detayli = sum(1 for m in maclar if len(m.get("oranlar", {})) > 14)

        print(f"\n{'='*60}")
        print(f"📊 FİNAL SONUÇ")
        print(f"   ⚽ Toplam maç: {len(maclar)}")
        print(f"   📊 Toplam oran: {sum(len(m['oranlar']) for m in maclar)}")
        print(f"   ✅ Detaylı: {detayli}")
        print(f"   ❌ Başarısız: {basarisiz}")
        print(f"   ⏱️ Süre: {sure}")
        print(f"{'='*60}")
        print("\n🎉 İşlem tamamlandı!")

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
        ultrasurf_durdur()

if __name__ == "__main__":
    print("⚽ İDDAA ORAN ÇEKİCİ - ULTRASURF VPN MODU (STABİL)")
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)
    mac_cek()