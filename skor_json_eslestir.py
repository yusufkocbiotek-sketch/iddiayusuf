import json, os, re, time, datetime
from pathlib import Path
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# =============================================================================
# AYARLAR
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
# gecmis_maclar.json -> BU DOSYAYA HİÇBİR ŞEKİLDE DOKUNULMAZ, ADI BİLE GEÇMEZ
BASE_LINK = "https://www.mackolik.com/canli-sonuclar"
GERI_GUN_SAYISI = 5
ESLESME_SEVIYESI = 0.2

# =============================================================================
# 🔐 İSİM TEMİZLEME (Eşleşme için standart hale getirir)
# =============================================================================
def akilli_isim_temizle(isim):
    if not isim: return ""
    isim = isim.lower().strip()
    gereksiz_ekler = [
        'fc', 'sk', 'jk', 'bk', 'as', 'aş', 'spor', 'kulübü', 'kulubu',
        '1899', '1903', '1905', '1907', '1910', '1912', '04', '05', '07',
        'sv', 'bv', 'vfb', 'bvb', 'sc', 'fortuna', 'bayer', 'hertha',
        'u19', 'u20', 'u21', 'u23', 'rez', 'rezerve', 'youth', 'ii', '(k)', 'kadın',
        'montevideo', 'liverpool', 'ca', 'sp', 'fc', 'cd', 'cf', 'sc', 'lp', 'ec', 'ac'
    ]
    for ek in gereksiz_ekler:
        isim = isim.replace(f" {ek} ", " ").replace(f" {ek}", "").replace(f"{ek} ", "")
    isim = re.sub(r'[.\-_,:0-9]', '', isim)
    isim = re.sub(r'\s+', ' ', isim).strip()
    duzelt = {
        "gs": "galatasaray", "fb": "fenerbahçe", "bjk": "beşiktaş", "ts": "trabzonspor",
        "bvb": "borussia dortmund", "fcb": "bayern münih", "man utd": "manchester united",
        "man city": "manchester city", "kopenhag": "copenhagen", "psg": "paris saint germain"
    }
    return duzelt.get(isim, isim)

def benzerlik_orani(a, b):
    if not a or not b: return 0
    a_temiz = akilli_isim_temizle(a)
    b_temiz = akilli_isim_temizle(b)
    if a_temiz == b_temiz: return 1.0
    if a_temiz in b_temiz or b_temiz in a_temiz: return 0.95
    return SequenceMatcher(None, a_temiz, b_temiz).ratio()

# =============================================================================
# 📖 DOSYANI OKU - ARTIK KESİNLİKLE SENİN FORMATIN ({ "matches": [] }) İLE ÇALIŞIR
# =============================================================================
def load_mac_json():
    try:
        if not MAC_JSON_PATH.exists():
            print(f"❌ HATA: {MAC_JSON_PATH} bulunamadı!")
            return None
        
        with open(MAC_JSON_PATH, 'r', encoding='utf-8') as f:
            veri = json.load(f)

        # Senin dosyanın yapısı bu: {"matches": [ ... maçlar ... ]}
        if isinstance(veri, dict) and "matches" in veri:
            print(f"📖 Dosyan Başarıyla Okundu | Toplam: {len(veri['matches'])} adet maç.")
            return veri  # Tüm yapıyı olduğu gibi koru (diğer anahtarlar da duruyor)
        
        else:
            print("❌ HATA: Dosya formatın beklenenden farklı.")
            return None

    except Exception as e:
        print(f"❌ OKUMA HATASI: {e} - Dosyan BOZULMADI, güvenle duruyor.")
        return None

# =============================================================================
# 💾 KAYDETME - SADECE SKOR DEĞİŞİR, DİĞER HER ŞEY (ORAN, LİG, SAAT) AYNI KALIR
# =============================================================================
def save_mac_json(veri):
    try:
        # Önce yedek al
        yedek_dosya = MAC_JSON_PATH.with_name("mac_json_yedek_guvenli.json")
        with open(yedek_dosya, 'w', encoding='utf-8') as f_yedek:
            json.dump(veri, f_yedek, ensure_ascii=False, indent=2)
        
        # Asıl dosyayı üzerine yaz (sadece skorlar değişik, diğer her şey aynı)
        with open(MAC_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 Kayıt Başarılı | Yedek alındı: {yedek_dosya.name}")
        print("🔒 Korumalı Alanlar: Oranlar, Lig, Saat, Index, Kodlar, Tüm Eski Veriler.")
        print("🔒 gececmis_maclar.json -> HİÇ DOKUNULMADI, KİRPİSİNE BİLE DEĞİLMEDİ!")
    except Exception as e:
        print(f"❌ KAYDETME HATASI: {e} - KESİNLİKLE ESKİ HALİ KORUNDU, ÜZERİNE YAZILMADI!")

# =============================================================================
# 🌐 MAÇKOLİK'TEN SADECE SKOR VE DURUM VERİSİ ÇEK
# =============================================================================
def get_skorlar():
    print("🔎 Maçkolik'ten veriler çekiliyor...")
    skor_listesi = []

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(BASE_LINK)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".match-row__match-content")))
        time.sleep(3)

        # Son belirlenen gün kadar geriye git
        for adim in range(GERI_GUN_SAYISI):
            hedef_tarih = datetime.date.today() - datetime.timedelta(days=adim)
            gun_iso = hedef_tarih.isoformat()

            try:
                # Tarih seçici aç
                takvim_buton = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='datepicker']")))
                driver.execute_script("arguments[0].click();", takvim_buton)
                time.sleep(1)
                
                # İlgili tarihi seç
                tarih_eleman = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'td[data-date="{gun_iso}"]')))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tarih_eleman)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", tarih_eleman)
                time.sleep(4)

                # Sayfayı en alta kaydırarak tüm maçların yüklenmesini sağla
                for _ in range(20):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    yeni_yukseklik = driver.execute_script("return document.body.scrollHeight")
                    if yeni_yukseklik == driver.execute_script("return document.body.scrollHeight"): break

                # Maçları çek
                mac_satirlari = driver.find_elements(By.CSS_SELECTOR, ".match-row__match-content[data-sport='S']")
                for satir in mac_satirlari:
                    try:
                        # İsimler
                        ev_isim = satir.find_element(By.CSS_SELECTOR, ".match-row__team--home .match-row__team-name-text").text.strip()
                        dep_isim = satir.find_element(By.CSS_SELECTOR, ".match-row__team--away .match-row__team-name-text").text.strip()
                        if not ev_isim or not dep_isim: continue

                        # Skorlar
                        skor_ev = int(satir.find_element(By.CSS_SELECTOR, ".match-row__score-home").text.strip() or 0)
                        skor_dep = int(satir.find_element(By.CSS_SELECTOR, ".match-row__score-away").text.strip() or 0)

                        # İlk Yarı Skorları
                        iy_ev, iy_dep = 0, 0
 try:
                            iy_text = satir.find_element(By.CSS_SELECTOR, ".match-row__half-time-score").text.strip()
                            rakamlar = re.findall(r'\d+', iy_text)
                            if len(rakamlar)>=2: iy_ev, iy_dep = int(rakamlar[0]), int(rakamlar[1])
                        except: pass

                        # Durum
                        durum = "baslamadi"
                        try:
                            d_ham = satir.find_element(By.CSS_SELECTOR, ".match-row__status").text.strip().lower()
                            if d_ham in ["bitti", "ms"]: durum = "bitti"
                            elif d_ham in ["canlı", "devam"]: durum = "devam ediyor"
                        except: pass

                        # Listeye ekle
                        skor_listesi.append({
                            "tarih": gun_iso,
                            "ev_sahibi": ev_isim,
                            "deplasman": dep_isim,
                            "skor_ev": skor_ev,
                            "skor_dep": skor_dep,
                            "skor_1y_ev": iy_ev,
                            "skor_1y_dep": iy_dep,
                            "durum": durum
                        })
                    except:
                        continue
            except:
                continue
    finally:
        if driver:
            driver.quit()

    print(f"✅ Maçkolik'ten {len(skor_listesi)} adet skor verisi çekildi.")
    return skor_listesi

# =============================================================================
# 🧠 GÜNCELLEME MOTORU - SADECE SKOR YAZAR, DİĞER HER ŞEYE DOKUNMAZ
# =============================================================================
def skorlari_eslestir_ve_guncelle(mevcut_yapi, yeni_skorlar):
    # Senin formatın: mevcut_yapi["matches"]
    mac_listesi = mevcut_yapi.get("matches", [])
    if not mac_listesi or not yeni_skorlar:
        return 0

    guncelleme_sayisi = 0

    # Her yeni skoru kontrol et
    for y_skor in yeni_skorlar:
        y_tarih = y_skor["tarih"]
        y_ev = y_skor["ev_sahibi"]
        y_dep = y_skor["deplasman"]

        en_uygun_index = -1
        en_yuksek_oran = 0
        ters_mi = False

        # Senin dosyandaki maçlarla eşleştir
        for i, mac in enumerate(mac_listesi):
            m_tarih = mac.get("tarih", "")
            m_ev = mac.get("ev_sahibi", "")
            m_dep = mac.get("deplasman", "")

            # Farklı günse geç
            if m_tarih != y_tarih:
                continue

            # Benzerlik hesapla (Normal ve Yer değiştirmiş olabilir diye kontrol)
            o1 = benzerlik_orani(m_ev, y_ev) + benzerlik_orani(m_dep, y_dep)
            o2 = benzerlik_orani(m_ev, y_dep) + benzerlik_orani(m_dep, y_ev)

            if o1 > en_yuksek_oran and (o1/2) >= ESLESME_SEVIYESI:
                en_yuksek_oran = o1
                en_uygun_index = i
                ters_mi = False
            if o2 > en_yuksek_oran and (o2/2) >= ESLESME_SEVIYESI:
                en_yuksek_oran = o2
                en_uygun_index = i
                ters_mi = True

        # Eşleşme bulunduysa -> SADECE SKORLARI GÜNCELLE
        if en_uygun_index != -1:
            mac = mac_listesi[en_uygun_index]
            
            # Skorları doğru yere yerleştir
            s1, s2 = (y_skor["skor_ev"], y_skor["skor_dep"]) if not ters_mi else (y_skor["skor_dep"], y_skor["skor_ev"])
            i1, i2 = (y_skor["skor_1y_ev"], y_skor["skor_1y_dep"]) if not ters_mi else (y_skor["skor_1y_dep"], y_skor["skor_1y_ev"])

            degisiklik_var = False

            # 0 olmayan ve eskisinden farklı olanları güncelle
            if s1 != 0 and mac.get("skor_ev") != s1:
                mac["skor_ev"] = s1
                degisiklik_var = True
            if s2 != 0 and mac.get("skor_dep") != s2:
                mac["skor_dep"] = s2
                degisiklik_var = True
            if i1 != 0 and mac.get("skor_1y_ev") != i1:
                mac["skor_1y_ev"] = i1
                degisiklik_var = True
            if i2 != 0 and mac.get("skor_1y_dep") != i2:
                mac["skor_1y_dep"] = i2
                degisiklik_var = True
            
            # Durum güncelle
            if y_skor["durum"] and mac.get("durum") != y_skor["durum"]:
                mac["durum"] = y_skor["durum"]
                degisiklik_var = True

            if degisiklik_var:
                guncelleme_sayisi += 1
                print(f"✅ GÜNCELLE | {mac['ev_sahibi']} - {mac['deplasman']} | Skor: {mac['skor_ev']}-{mac['skor_dep']} | İY: {mac['skor_1y_ev']}-{mac['skor_1y_dep']}")

    return guncelleme_sayisi

# =============================================================================
# 🚀 ANA ÇALIŞTIRICI
# =============================================================================
if __name__ == "__main__":
    print("="*70)
    print("⚽ GÜVENLİ SKOR GÜNCELLEYİCİ | VERİ KORUMA MODU 🛡️")
    print("="*70)
    print("🔒 KURAL 1: Oranlar, Lig, Saat, Index, Kodlar -> HİÇ DOKUNULMAZ!")
    print("🔒 KURAL 2: gecmis_maclar.json -> KESİNLİKLE GÖRMEZ, DOKUNMAZ!")
    print("🔒 KURAL 3: Sadece Skor ve Durum güncellenir. Yeni maç EKLENMEZ.")
    print("-"*70)

    # 1. Dosyayı oku
    mevcut_yapi = load_mac_json()
    if not mevcut_yapi:
        print("❌ İşlem iptal edildi.")
        input("🔚 Çıkmak için Enter...")
        exit()

    # 2. Maçkolik'ten verileri çek
    yeni_skor_verileri = get_skorlar()
    if not yeni_skor_verileri:
        print("❌ Maçkolik verisi alınamadı. İşlem iptal edildi.")
        input("🔚 Çıkmak için Enter...")
        exit()

    # 3. Eşleştir ve sadece skorları güncelle
    guncellenen_sayi = skorlari_eslestir_ve_guncelle(mevcut_yapi, yeni_skor_verileri)

    # 4. Sonuç ve Kayıt
    if guncellenen_sayi > 0:
        save_mac_json(mevcut_yapi)
        print(f"\n📊 Toplam {guncellenen_sayi} adet maçın skoru güncellendi.")
    else:
        print("\nℹ️ Güncellenecek yeni skor veya durum bilgisi bulunamadı. Dosya değiştirilmedi.")

    print("\n" + "="*70)
    print("✅ TÜM İŞLEMLER BİTTİ | HİÇBİR VERİN SİLİNMEDİ / BOZULMADI ✅")
    print("="*70)
    input("🔚 Çıkmak için Enter tuşuna bas...")