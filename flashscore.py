import json
import os
import datetime
import time
import re
import difflib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

MAC_JSON = "public/data/mac.json"

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Gerçekçi tarayıcı profili
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("✅ Chrome başlatıldı!")
    return driver

def mac_json_oku():
    if os.path.exists(MAC_JSON):
        try:
            with open(MAC_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ mac.json dosyası bozuk, yeni dosya oluşturuluyor.")
    return {"version": 2, "updated": "", "matches": []}

def mac_json_kaydet(data):
    data["updated"] = datetime.datetime.now().isoformat()
    os.makedirs(os.path.dirname(MAC_JSON), exist_ok=True)
    with open(MAC_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("💾 mac.json güncellendi!")

def ismi_temizle(ad):
    if not ad:
        return ""
    ad = ad.lower().strip()
    
    karakter_map = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'i': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u', 'æ': 'ae', 'œ': 'oe',
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n', 'ã': 'a',
        'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u', 'ý': 'y', 'å': 'a', 'ø': 'o',
        '-': '', '_': '', '.': '', '(': '', ')': '', '/': '', '\\': '', "'": '', '"': '', ' ': ''
    }
    for eski, yeni in karakter_map.items():
        ad = ad.replace(eski, yeni)
    
    # Genişletilmiş gereksiz ekler listesi
    gereksiz_ekler = [
        "fc", "sk", "bk", "as", "ac", "spor", "kulubu", "takimi", "kulübü", 
        "team", "fussball", "genclik", "k", "k.", "sc", "fk", "nk", "cs", "cd", 
        "u21", "u19", "u18", "u17", "ii", "iii", "iv", "v", "fc.", "sk.", "jk",
        "s", "r", "sport", "klub", "united", "city", "sc",
        "al", "el", "ahli", "ittihad", "nasr", "hilal", "shabab", "okhdood", "ettifaq",
        "maccabi", "hapoel", "fc", "utd", "cf", "rcd", "cd", "ca", "cs", "as",
        "uniao", "nacional", "deportivo", "racing", "newells", "central",
        "provincial", "municipal", "olympic", "sporting", "melaka", "johor",
        "united", "city", "rover", "rangers", "wanderers", "warriors", "lion",
        "navy", "army", "police", "railway", "airforce", "port", "harbour"
    ]
    for ek in gereksiz_ekler:
        if ad.startswith(ek):
            ad = ad[len(ek):]
        if ad.endswith(ek):
            ad = ad[:-len(ek)]
    
    ad = re.sub(r'[^a-z0-9]', '', ad)
    return ad if len(ad) >= 2 else ""

def takim_eslesme_kontrol(ad1, ad2):
    t1 = ismi_temizle(ad1)
    t2 = ismi_temizle(ad2)
    
    if not t1 or not t2:
        return False
    
    if t1 == t2:
        return True
    
    if len(t1) > 2 and len(t2) > 2 and (t1 in t2 or t2 in t1):
        return True
    
    benzerlik = difflib.SequenceMatcher(None, t1, t2).ratio()
    if benzerlik >= 0.50:  # Çok düşük eşik - tüm varyantları yakala
        return True
    
    return False

# ✅ FLASHSCORE - EN KAPSAMLI VE ENGELSİZ KAYNAK
def flashscore_veri_cek(driver, tarih):
    """Flashscore'dan tüm maç verilerini çeker - tüm ülkeler/tüm ligler"""
    skorlar = []
    try:
        gun, ay, yil = tarih.split(".")
        iso_tarih = f"{yil}-{ay}-{gun}"
        
        # Flashscore tarih URL yapısı
        url = f"https://www.flashscore.com/matches/{yil}-{ay}-{gun}/"
        print(f"      🔗 Flashscore adresi: {url}")
        
        driver.get(url)
        time.sleep(6)  # Sayfanın tam yüklenmesi için bekle
        
        # Tüm maç elemanlarını bul
        mac_satirlari = []
        
        # Farklı sınıf adları ile dene
        siniflar = [
            "event__match", "g_1", "event__row", "match-row", 
            "sportName_soccer", "event__match--withRowLink"
        ]
        
        for sinif in siniflar:
            try:
                elemanlar = driver.find_elements(By.CLASS_NAME, sinif)
                if elemanlar:
                    mac_satirlari.extend(elemanlar)
            except:
                pass
        
        # Eğer eleman bulunamazsa XPath ile dene
        if not mac_satirlari:
            try:
                mac_satirlari = driver.find_elements(By.XPATH, "//div[contains(@class, 'event__match') or contains(@class, 'g_1') or contains(@class, 'match')]")
            except:
                pass
        
        # Elemanlardan veri çek
        for satir in mac_satirlari:
            try:
                # Ev sahibi takım
                ev_elem = None
                for secici in [".//div[contains(@class, 'home')]", ".//div[contains(@class, 'event__home')]", ".//span[contains(@class, 'home')]"]:
                    try:
                        ev_elem = satir.find_element(By.XPATH, secici)
                        break
                    except:
                        continue
                
                # Deplasman takımı
                dep_elem = None
                for secici in [".//div[contains(@class, 'away')]", ".//div[contains(@class, 'event__away')]", ".//span[contains(@class, 'away')]"]:
                    try:
                        dep_elem = satir.find_element(By.XPATH, secici)
                        break
                    except:
                        continue
                
                # Skor
                skor_elem = None
                for secici in [".//div[contains(@class, 'score')]", ".//div[contains(@class, 'event__score')]", ".//span[contains(@class, 'score')]"]:
                    try:
                        skor_elem = satir.find_element(By.XPATH, secici)
                        break
                    except:
                        continue
                
                if ev_elem and dep_elem and skor_elem:
                    ev = ev_elem.text.strip()
                    dep = dep_elem.text.strip()
                    skor_metin = skor_elem.text.strip()
                    
                    # Skoru ayıkla
                    skor_eslesme = re.search(r'(\d+)\s*-\s*(\d+)', skor_metin)
                    if skor_eslesme:
                        ev_gol = int(skor_eslesme.group(1))
                        dep_gol = int(skor_eslesme.group(2))
                        
                        if len(ev) > 1 and len(dep) > 1:
                            skorlar.append({
                                "ev": ev,
                                "dep": dep,
                                "tarih": iso_tarih,
                                "skor_ev": ev_gol,
                                "skor_dep": dep_gol,
                                "skor_1y_ev": 0,
                                "skor_1y_dep": 0
                            })
            except:
                continue
        
        # Eğer eleman yöntemi başarısız olursa METİN ANALİZİ yap
        if len(skorlar) < 5:
            tum_metin = driver.find_element(By.TAG_NAME, "body").text
            
            # Genişletilmiş maç kalıbı - tüm formatları yakala
            mac_kalibi = re.compile(
                r'([^\-\d\n\r\t•·]+?)\s*-\s*([^\-\d\n\r\t•·]+?)\s+(\d+)\s*-\s*(\d+)|'
                r'([^\-\d\n\r\t•·]+?)\s+(\d+)\s*-\s*(\d+)\s+([^\-\d\n\r\t•·]+)|'
                r'([^\-\d\n\r\t•·]+?)\s*-\s*([^\-\d\n\r\t•·]+?)\s+(\d+):(\d+)'
            )
            
            eslesmeler = mac_kalibi.findall(tum_metin)
            
            for eslesme in eslesmeler:
                ev, dep, ev_gol, dep_gol = None, None, None, None
                
                if eslesme[0] and eslesme[1]:
                    ev = eslesme[0].strip()
                    dep = eslesme[1].strip()
                    ev_gol = int(eslesme[2])
                    dep_gol = int(eslesme[3])
                elif eslesme[4] and eslesme[7]:
                    ev = eslesme[4].strip()
                    dep = eslesme[7].strip()
                    ev_gol = int(eslesme[5])
                    dep_gol = int(eslesme[6])
                elif eslesme[8] and eslesme[9]:
                    ev = eslesme[8].strip()
                    dep = eslesme[9].strip()
                    ev_gol = int(eslesme[10])
                    dep_gol = int(eslesme[11])
                
                if ev and dep and len(ev) > 1 and len(dep) > 1:
                    # Tekrarı engelle
                    var_mi = False
                    for mevcut in skorlar:
                        if (takim_eslesme_kontrol(mevcut["ev"], ev) and 
                            takim_eslesme_kontrol(mevcut["dep"], dep)):
                            var_mi = True
                            break
                    if not var_mi:
                        skorlar.append({
                            "ev": ev,
                            "dep": dep,
                            "tarih": iso_tarih,
                            "skor_ev": ev_gol,
                            "skor_dep": dep_gol,
                            "skor_1y_ev": 0,
                            "skor_1y_dep": 0
                        })
        
        print(f"      ✅ {tarih} -> {len(skorlar)} maç verisi bulundu")
        
    except Exception as hata:
        print(f"      ❌ Veri çekme hatası: {str(hata)[:60]}...")
    
    return skorlar

def tum_verileri_cek(driver, tarihler):
    tum_skorlar = []
    for tarih in tarihler:
        print(f"\n   📅 {tarih} tarihi işleniyor...")
        gunun_skorlari = flashscore_veri_cek(driver, tarih)
        tum_skorlar.extend(gunun_skorlari)
    
    print(f"\n✅ Toplam {len(tum_skorlar)} maç verisi Flashscore.com'dan alındı!")
    return tum_skorlar

def skorlari_guncelle(data, skorlar):
    guncellenen = 0
    bulunamayan = 0
    eslesemeyen_liste = []
    mac_listesi = data.get("matches", [])
    bugun = datetime.date.today().isoformat()

    if not mac_listesi:
        print("❌ JSON dosyasında maç verisi bulunamadı!")
        return 0, 0, []

    print("\n🔎 EŞLEŞTİRME SONUÇLARI:")
    print("-" * 70)

    for mac in mac_listesi:
        if mac.get("durum", "baslamadi") != "baslamadi":
            continue
        
        mac_tarih = mac.get("tarih", "")
        mac_ev = mac.get("ev_sahibi", "")
        mac_dep = mac.get("deplasman", "")
        eslesti = False

        for skor in skorlar:
            if mac_tarih != skor["tarih"]:
                continue
            
            if (takim_eslesme_kontrol(mac_ev, skor["ev"]) and 
                takim_eslesme_kontrol(mac_dep, skor["dep"])):
                
                mac["durum"] = "bitti"
                mac["skor_ev"] = skor["skor_ev"]
                mac["skor_dep"] = skor["skor_dep"]
                mac["skor_1y_ev"] = skor["skor_1y_ev"]
                mac["skor_1y_dep"] = skor["skor_1y_dep"]
                guncellenen += 1
                eslesti = True
                print(f"✅ BAŞARILI: {mac_ev} - {mac_dep} | Tarih: {mac_tarih} | Skor: {skor['skor_ev']}-{skor['skor_dep']}")
                break
        
        if not eslesti:
            bulunamayan += 1
            if mac_tarih < bugun:
                eslesemeyen_liste.append(f"{mac_ev} vs {mac_dep} ({mac_tarih})")

    print("-" * 70)
    return guncellenen, bulunamayan, eslesemeyen_liste

def main():
    print("============================================================")
    print("⚽ FLASHSCORE MAÇ SKORU GÜNCELLEYİCİ - KESİN ÇÖZÜM")
    print("============================================================")
    
    veri = mac_json_oku()
    
    kontrol_edilecek_gunler = [
        "28.04.2026",
        "29.04.2026", 
        "30.04.2026",
        "01.05.2026",
        "02.05.2026",
        "03.05.2026",
        "04.05.2026"
    ]

    tarayici = None
    try:
        tarayici = tarayici_baslat()
        print(f"   📅 Kontrol edilecek tarihler: {', '.join(kontrol_edilecek_gunler)}")
        
        tum_skorlar = tum_verileri_cek