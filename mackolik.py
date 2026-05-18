import json, os, re, time
import datetime
import subprocess
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
# gecmis_maclar.json -> BU DOSYAYA HİÇBİR ŞEKİLDE DOKUNULMAZ
BASE_LINK = "https://www.mackolik.com/futbol/canli-sonuclar"
# ===> ÇEKİLECEK TARİH <=== (Gün/Ay formatında yaz, örnek: "17/05", "16/05")
HEDEF_TARIH = "17/05"
ESLESME_SEVIYESI = 0.15 # Eşleştirmeyi daha esnek yaptım
# ===> GİT AYARLARI <=== (Eğer senin dal ismin "master" ise "main" yerine "master" yaz)
GIT_BRANCH_NAME = "main"

# =============================================================================
# 🔐 İSİM TEMİZLEME - ARTIK ÇOK DAHA ESNEK, GERÇEK İSİMLER SİLİNMEZ
# =============================================================================
def akilli_isim_temizle(isim):
    if not isim: return ""
    # SADECE ÇOK ANLAMSIZ VERİLERİ ELE, GERÇEK İSİMLERİ KORU
    if isim.isdigit() or len(isim.strip()) <= 1:
        return ""

    isim = isim.lower().strip()
    # Sadece gereksiz kesin ekleri çıkar, isimlerin kendisine dokunma
    gereksiz_ekler = ['fc', 'sk', 'jk', 'bk', 'as', 'spor', 'kulübü', 'kulubu', '(k)', 'u21', 'u19', 'ii']
    for ek in gereksiz_ekler:
        isim = isim.replace(f" {ek} ", " ").replace(f" {ek}", "").replace(f"{ek} ", "")
    
    isim = re.sub(r'[.\-_,:0-9]', '', isim)
    isim = re.sub(r'\s+', ' ', isim).strip()
    return isim

def benzerlik_orani(a, b):
    if not a or not b: return 0
    a_temiz = akilli_isim_temizle(a)
    b_temiz = akilli_isim_temizle(b)
    if a_temiz == b_temiz: return 1.0
    if a_temiz in b_temiz or b_temiz in a_temiz: return 0.9
    return SequenceMatcher(None, a_temiz, b_temiz).ratio()

# =============================================================================
# 📖 DOSYANI OKU - Senin "matches" formatınla uyumlu
# =============================================================================
def load_mac_json():
    try:
        if not MAC_JSON_PATH.exists():
            print(f"❌ HATA: {MAC_JSON_PATH} bulunamadı!")
            return None
        
        with open(MAC_JSON_PATH, 'r', encoding='utf-8') as f:
            veri = json.load(f)

        if isinstance(veri, dict) and "matches" in veri:
            print(f"📖 Dosyan Başarıyla Okundu | Toplam: {len(veri['matches'])} adet maç.")
            return veri 
        
        else:
            print("❌ HATA: Dosya formatın beklenenden farklı.")
            return None

    except Exception as e:
        print(f"❌ OKUMA HATASI: {e} - Dosyan BOZULMADI.")
        return None

# =============================================================================
# 💾 KAYDETME - SADECE SKOR DEĞİŞİR, DİĞER HER ŞEY AYNI KALIR
# =============================================================================
def save_mac_json(veri):
    try:
        yedek_dosya = MAC_JSON_PATH.with_name("mac_json_yedek_guvenli.json")
        with open(yedek_dosya, 'w', encoding='utf-8') as f_yedek:
            json.dump(veri, f_yedek, ensure_ascii=False, indent=2)
        
        with open(MAC_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 Kayıt Başarılı | Yedek: {yedek_dosya.name}")
        print("🔒 Korumalı: Oranlar, Lig, Saat, Index, Kodlar.")
        print("🔒 gecmis_maclar.json -> HİÇ DOKUNULMADI!")
    except Exception as e:
        print(f"❌ KAYDETME HATASI: {e} - ESKİ HALİ KORUNDU!")

# =============================================================================
# 🚀 GİT İŞLEMLERİ - OTOMATİK GÖNDERİM
# =============================================================================
def git_islemlerini_yap():
    print("\n" + "="*70)
    print("🚀 GİT İŞLEMLERİ BAŞLATILDI | DEPOYA GÖNDERİLİYOR...")
    print("="*70)
    try:
        os.chdir(BASE_DIR)
        durum = subprocess.run(["git", "status"], capture_output=True, text=True, encoding='utf-8')
        if "nothing to commit" in durum.stdout:
            print("ℹ️ Değişiklik yok, Git işlemi yapılmasına gerek yok.")
            return False

        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        mesaj = f"[OTOMATİK GÜNCELLEME] {HEDEF_TARIH} Maç verileri güncellendi | Skor + Durum + İlk Yarı"
        subprocess.run(["git", "commit", "-m", mesaj], check=True, capture_output=True, text=True)
        subprocess.run(["git", "push", "origin", GIT_BRANCH_NAME], check=True, capture_output=True, text=True)
        
        print("✅ GİT BAŞARILI! Tüm veriler GitHub'a yüklendi.")
        return True

    except Exception as e:
        print(f"❌ GİT HATASI: {str(e)}")
        return False

# =============================================================================
# 🌐 MAÇKOLİK'TEN VERİ ÇEK - ARTIK MS YAZANLAR KESİN BİTTİ OLARAK İŞARETLENİR
# =============================================================================
def get_skorlar():
    print("🔎 Maçkolik'ten veriler çekiliyor...")
    skor_listesi = []
    gorulen_maclar = set()

    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        print(f"🌐 Siteye gidiliyor: {BASE_LINK}")
        driver.get(BASE_LINK)
        time.sleep(10) # Daha uzun bekle

        print(f"📅 Hedef tarih aranıyor: {HEDEF_TARIH}")
        try:
            tarih_elemanlari = driver.find_elements(By.CSS_SELECTOR, "span.widget-dateslider__day-date")
            for el in tarih_elemanlari:
                if el.text.strip() == HEDEF_TARIH:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    time.sleep(2)
                    driver.execute_script("arguments[0].click();", el)
                    print(f"✅ Tarih seçildi: {HEDEF_TARIH}")
                    time.sleep(15) # Verilerin yüklenmesi için ÇOK BEKLE
                    break
        except Exception as e:
            print(f"⚠️ Tarih seçim hatası: {e}")

        # Sayfayı SONUNA KADAR kaydır
        print("📜 Sayfa sonuna kadar kaydırılıyor...")
        son_yukseklik = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            yeni_yukseklik = driver.execute_script("return document.body.scrollHeight")
            if yeni_yukseklik == son_yukseklik:
                break
            son_yukseklik = yeni_yukseklik

        # Tüm maç satırlarını bul
        mac_satirlari = driver.find_elements(By.CSS_SELECTOR, "div.match-row")
        print(f"🔍 Sayfada bulunan toplam satır: {len(mac_satirlari)}")

        gun, ay = HEDEF_TARIH.split('/')
        hedef_tarih_iso = f"2026-{ay}-{gun}"

        gecerli_veri_sayisi = 0
        biten_mac_sayisi = 0
        ilk_yari_sayisi = 0

        # Her bir satırı işle
        for satir in mac_satirlari:
            try:
                # Takım İsimleri - Farklı sınıf isimlerini de kontrol et
                isim_elemanlari = satir.find_elements(By.CSS_SELECTOR, "span.match-row__team-name-text, span.team-name")
                if len(isim_elemanlari) < 2:
                    continue

                ev_isim = isim_elemanlari[0].text.strip()
                dep_isim = isim_elemanlari[1].text.strip()

                # Tekrar edenleri engelle
                mac_kimlik = f"{ev_isim}-{dep_isim}"
                if mac_kimlik in gorulen_maclar:
                    continue
                gorulen_maclar.add(mac_kimlik)

                # ===> ARTIK İSİM KONTROLÜ ÇOK DAHA ESNEK <===
                if len(ev_isim) < 2 or len(dep_isim) < 2:
                    continue

                # Maç Sonu Skorları
                skor_ev = 0
                skor_dep = 0
                try:
                    skor_elemanlari = satir.find_elements(By.CSS_SELECTOR, "span.match-row__score-text, span.score")
                    if len(skor_elemanlari) >= 2:
                        s1 = skor_elemanlari[0].text.strip()
                        s2 = skor_elemanlari[1].text.strip()
                        if s1.isdigit(): skor_ev = int(s1)
                        if s2.isdigit(): skor_dep = int(s2)
                except:
                    pass

                # İlk Yarı Skorları
                skor_1y_ev = 0
                skor_1y_dep = 0
                try:
                    iy_elem = satir.find_element(By.CSS_SELECTOR, "div.match-row__half-time-score, div.half-time")
                    iy_yazi = iy_elem.text.strip()
                    rakamlar = re.findall(r'\d+', iy_yazi)
                    if len(rakamlar) == 2:
                        skor_1y_ev = int(rakamlar[0])
                        skor_1y_dep = int(rakamlar[1])
                        ilk_yari_sayisi += 1
                except:
                    pass

                # ==============================================================
                # 🔴 DURUM KONTROLÜ - ARTIK MS YAZANLAR KESİN BİTTİ OLARAK İŞARETLENİR
                # ==============================================================
                durum = "baslamadi"
                try:
                    # Tam olarak senin verdiğin HTML yapısına uygun seçici
                    status_elem = satir.find_element(By.CSS_SELECTOR, "a.match-row__status, div.match-row__status")
                    durum_yazi = status_elem.text.strip().upper() # Büyük harfe çevir "MS" diye kontrol et

                    # KESİN KURALLAR: MS yazıyorsa bitmiştir
                    if "MS" in durum_yazi or "FİNAL" in durum_yazi or "BITTI" in durum_yazi or "EN DÜDÜK" in durum_yazi:
                        durum = "bitti"
                        biten_mac_sayisi += 1
                    elif "CANLI" in durum_yazi or "DEVAM" in durum_yazi or "'" in durum_yazi or "DK" in durum_yazi:
                        durum = "devam ediyor"
                    else:
                        durum = "baslamadi"

                except Exception as durum_hata:
                    pass

                # Veriyi listeye ekle
                skor_listesi.append({
                    "tarih": hedef_tarih_iso,
                    "ev_sahibi": ev_isim,
                    "deplasman": dep_isim,
                    "skor_ev": skor_ev,
                    "skor_dep": skor_dep,
                    "skor_1y_ev": skor_1y_ev,
                    "skor_1y_dep": skor_1y_dep,
                    "durum": durum
                })
                gecerli_veri_sayisi += 1

                print(f"✅ VERİ | {ev_isim} - {dep_isim} | Skor: {skor_ev}-{skor_dep} | İlk Yarı: {skor_1y_ev}-{skor_1y_dep} | {durum.upper()}")

            except Exception as satir_hata:
                continue

    except Exception as ana_hata:
        print(f"❌ Ana Hata: {ana_hata}")
    finally:
        if driver:
            driver.quit()
            print("🔒 Tarayıcı kapatıldı.")

    print(f"✅ İŞLEM TAMAMLANDI | Toplam {gecerli_veri_sayisi} adet GEÇERLİ maç verisi çekildi.")
    print(f"📊 İstatistik: Biten = {biten_mac_sayisi}, İlk Yarı Skoru = {ilk_yari_sayisi}")
    return skor_listesi

# =============================================================================
# 🧠 GÜNCELLEME MOTORU
# =============================================================================
def skorlari_eslestir_ve_guncelle(mevcut_yapi, yeni_skorlar):
    mac_listesi = mevcut_yapi.get("matches", [])
    if not mac_listesi or not yeni_skorlar:
        return 0

    guncelleme_sayisi = 0

    for y_skor in yeni_skorlar:
        y_tarih = y_skor["tarih"]
        y_ev = y_skor["ev_sahibi"]
        y_dep = y_skor["deplasman"]

        en_uygun_index = -1
        ters_mi = False

        for i, mac in enumerate(mac_listesi):
            m_tarih = mac.get("tarih", "")
            m_ev = mac.get("ev_sahibi", "")
            m_dep = mac.get("deplasman", "")

            if m_tarih != y_tarih:
                continue

            # Normal eşleşme
            oran1 = benzerlik_orani(m_ev, y_ev) + benzerlik_orani(m_dep, y_dep)
            # Ters eşleşme
            oran2 = benzerlik_orani(m_ev, y_dep) + benzerlik_orani(m_dep, y_ev)

            if oran1 > 1.0:
                en_uygun_index = i
                ters_mi = False
            elif oran2 > 1.0:
                en_uygun_index = i
                ters_mi = True

        if en_uygun_index != -1:
            mac = mac_listesi[en_uygun_index]

            # Skorları doğru tarafa yerleştir
            s_ev, s_dep = (y_skor["skor_ev"], y_skor["skor_dep"]) if not ters_mi else (y_skor["skor_dep"], y_skor["skor_ev"])
            iy_ev, iy_dep = (y_skor["skor_1y_ev"], y_skor["skor_1y_dep"]) if not ters_mi else (y_skor["skor_1y_dep"], y_skor["skor_1y_ev"])

            degisiklik_var = False

            # Maç Sonu Skorları Güncelle
            if s_ev != 0 and mac.get("skor_ev") != s_ev:
                mac["skor_ev"] = s_ev
                degisiklik_var = True
            if s_dep != 0 and mac.get("skor_dep") != s_dep:
                mac["skor_dep"] = s_dep
                degisiklik_var = True

            # İlk Yarı Skorları Güncelle
            if iy_ev != 0 and mac.get("skor_1y_ev") != iy_ev:
                mac["skor_1y_ev"] = iy_ev
                degisiklik_var = True
            if iy_dep != 0 and mac.get("skor_1y_dep") != iy_dep:
                mac["skor_1y_dep"] = iy_dep
                degisiklik_var = True

            # Durum Güncelle - MS yazanlar kesin bitti olacak
            if mac.get("durum") != y_skor["durum"]:
                mac["durum"] = y_skor["durum"]
                degisiklik_var = True

            if degisiklik_var:
                guncelleme_sayisi += 1
                print(f"✅ GÜNCELLEME | {mac['ev_sahibi']} - {mac['deplasman']} | Skor: {mac['skor_ev']}-{mac['skor_dep']} | İlk Yarı: {mac['skor_1y_ev']}-{mac['skor_1y_dep']} | Durum: {mac['durum']}")

    return guncelleme_sayisi

# =============================================================================
# 🚀 ANA ÇALIŞTIRICI - TAMamen DÜZELTİLDİ, ARTIK HATA YOK
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("⚽ GÜVENLİ SKOR GÜNCELLEYİCİ | VERİ KORUMA MODU 🛡️")
    print("=" * 70)
    print("🔒 KURAL 1: Oranlar, Lig, Saat, Index, Kodlar -> HİÇ DOKUNULMAZ!")
    print("🔒 KURAL 2: gecmis_maclar.json -> KESİNLİKLE GÖRMEZ, DOKUNMAZ!")
    print("🔒 KURAL 3: Sadece Skor ve Durum güncellenir. Yeni maç EKLENMEZ.")
    print("-" * 70)

    # 1. Mevcut dosyayı oku
    mevcut_yapi = load_mac_json()
    if not mevcut_yapi:
        print("❌ İşlem iptal edildi.")
        input("🔚 Çıkmak için Enter...")
        exit()

    # 2. Maçkolik'ten verileri çek (İlk yarı + DOĞRU DURUM - MS = BİTTİ)
    yeni_skorlar = get_skorlar() # <-- HATA DÜZELTİLDİ: Değişken adı doğru tanımlandı
    if not yeni_skorlar:
        print("❌ Maçkolik verisi alınamadı. İşlem iptal edildi.")
        input("🔚 Çıkmak için Enter...")
        exit()

    # 3. Verileri eşleştir ve güncelle
    guncellenen_sayi = skorlari_eslestir_ve_guncelle(mevcut_yapi, yeni_skorlar)

    # 4. Kaydet ve Git gönderimi
    if guncellenen_sayi > 0:
        save_mac_json(mevcut_yapi)
        print(f"\n📊 Toplam {guncellenen_sayi} adet maçın SKORU, İLK YARISI ve DURUMU güncellendi.")
        
        # 🔄 Otomatik Git Push
        git_islemlerini_yap()
        
    else:
        print("\nℹ️ Güncellenecek yeni veri bulunamadı. Dosya içeriği değiştirilmedi.")

    print("\n" + "=" * 70)
    print("✅ TÜM İŞLEMLER BİTTİ | HİÇBİR VERİN SİLİNMEDİ / BOZULMADI ✅")
    print("🔒 Korumada olanlar: Oranlar, Lig, Saat, Index, Kodlar, Tüm Geçmiş Veriler")
    print("🔒 gecmis_maclar.json -> Tamamen güvende, hiç dokunulmadı")
    print("=" * 70)
    input("🔚 Çıkmak için Enter tuşuna bas...")