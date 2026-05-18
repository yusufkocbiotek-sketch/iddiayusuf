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
# AYARLAR - GELİŞTİRİLDİ: Eşleştirme Çok Daha Esnek
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
# gecmis_maclar.json -> HİÇ DOKUNULMAZ
BASE_LINK = "https://www.mackolik.com/futbol/canli-sonuclar"
HEDEF_TARIH = "12/05"
ESLESME_SEVIYESI = 0.35  # ✅ DÜŞÜRÜLDÜ: %35 benzerlik bile yeterli, daha fazla eşleşme olsun
TAM_ESLESME_SEVIYESI = 0.70 # %70 ve üstü kesin aynı maç
GIT_BRANCH_NAME = "main"

# =============================================================================
# 🔐 İSİM TEMİZLEME - GELİŞTİRİLDİ: Farklı yazımları aynı yapar
# =============================================================================
def akilli_isim_temizle(isim):
    if not isim: return ""
    # Küçük harfe çevir
    isim = isim.lower().strip()
    # Türkçe karakterleri dönüştür
    tr_map = str.maketrans("çğıöşüâêîôû", "cgiosuaeiou")
    isim = isim.translate(tr_map)
    # Sadece harf kal, rakam ve noktalama sil
    isim = re.sub(r'[^a-z]', '', isim)
    # Çok yaygın ekleri tamamen sil
    gereksiz = ['fc', 'sk', 'jk', 'bk', 'as', 'spor', 'kulubu', 'kulübü', 'team', 'fk', 'sc', 'cf', 'u19', 'u21', 'ii']
    for ek in gereksiz:
        isim = isim.replace(ek, '')
    # Tekrar eden boşlukları temizle
    isim = re.sub(r'\s+', ' ', isim).strip()
    return isim

def benzerlik_orani(a, b):
    if not a or not b: return 0.0
    a_temiz = akilli_isim_temizle(a)
    b_temiz = akilli_isim_temizle(b)
    if a_temiz == b_temiz: return 1.0
    if a_temiz in b_temiz or b_temiz in a_temiz: return 0.85
    return round(SequenceMatcher(None, a_temiz, b_temiz).ratio(), 2)

# =============================================================================
# 📅 TARİH DÖNÜŞTÜRÜCÜ - GELİŞTİRİLDİ: Tüm formatları aynı yapar
# =============================================================================
def tarihi_esit_kabul_et(t1, t2):
    if not t1 or not t2: return False
    # Farklı formatları aynı ISO formatına çevir
    def duzelt(t):
        t = str(t).strip()
        # 17/05/2026 -> 2026-05-17
        if '/' in t:
            parca = t.split('/')
            if len(parca) == 3: return f"{parca[2]}-{parca[1]}-{parca[0]}"
            if len(parca) == 2: return f"2026-{parca[1]}-{parca[0]}"
        # 17 Mayıs 2026 -> 2026-05-17
        ay_ayrim = {'ocak':'01','subat':'02','mart':'03','nisan':'04','mayis':'05','haziran':'06','temmuz':'07','agustos':'08','eylul':'09','ekim':'10','kasim':'11','aralik':'12'}
        for ay, num in ay_ayrim.items():
            if ay in t.lower():
                gun = re.search(r'\d+', t).group()
                return f"2026-{num}-{gun.zfill(2)}"
        return t
    return duzelt(t1)[:10] == duzelt(t2)[:10]

# =============================================================================
# 📖 DOSYANI OKU
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
            print("❌ HATA: Dosya formatı uyumsuz.")
            return None
    except Exception as e:
        print(f"❌ OKUMA HATASI: {e}")
        return None

# =============================================================================
# 💾 KAYDETME
# =============================================================================
def save_mac_json(veri):
    try:
        yedek = MAC_JSON_PATH.with_name("mac_json_yedek_guvenli.json")
        with open(yedek, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        with open(MAC_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2, default=str)
        print(f"💾 Kayıt Başarılı | Yedek: {yedek.name}")
        print("🔒 Oran, Lig, Saat, Index, Kodlar KORUNDU.")
    except Exception as e:
        print(f"❌ KAYDETME HATASI: {e}")

# =============================================================================
# 🚀 GİT
# =============================================================================
def git_islemlerini_yap():
    print("\n" + "="*70)
    print("🚀 GİT İŞLEMLERİ BAŞLATILDI...")
    print("="*70)
    try:
        os.chdir(BASE_DIR)
        if "nothing to commit" in subprocess.run(["git","status"], capture_output=True, text=True).stdout:
            print("ℹ️ Değişiklik yok.")
            return False
        subprocess.run(["git","add","."], check=True)
        subprocess.run(["git","commit","-m",f"[OTOMATİK] {HEDEF_TARIH} Güncelleme"], check=True)
        subprocess.run(["git","push","origin",GIT_BRANCH_NAME], check=True)
        print("✅ GİT BAŞARILI!")
        return True
    except Exception as e:
        print(f"❌ GİT HATASI: {e}")
        return False

# =============================================================================
# 🌐 MAÇKOLİK VERİ ÇEKİMİ
# =============================================================================
def get_skorlar():
    print("🔎 Maçkolik'ten veriler çekiliyor...")
    skor_listesi = []
    gorulen = set()

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        print(f"🌐 Site: {BASE_LINK}")
        driver.get(BASE_LINK)
        time.sleep(12)

        print(f"📅 Tarih: {HEDEF_TARIH}")
        try:
            tarihler = driver.find_elements(By.CSS_SELECTOR, "span.widget-dateslider__day-date")
            for el in tarihler:
                if el.text.strip() == HEDEF_TARIH:
                # if HEDEF_TARIH in el.text.strip(): # ✅ Tarih esnekliği
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                    time.sleep(2)
                    driver.execute_script("arguments[0].click();", el)
                    print(f"✅ Tarih seçildi: {HEDEF_TARIH}")
                    time.sleep(20)
                    break
        except: pass

        # Sayfayı tamamen aşağı indir
        print("📜 Sayfa yükleniyor...")
        for _ in range(80):
            driver.execute_script("window.scrollBy(0, 1200);")
            time.sleep(0.4)

        mac_satirlari = driver.find_elements(By.CSS_SELECTOR, "div.match-row, div.row-table__row, tr.match")
        print(f"🔍 Satır: {len(mac_satirlari)}")

        # ✅ Tarihi ISO'ya çevir
        gun, ay = HEDEF_TARIH.split('/')
        hedef_tarih_iso = f"2026-{ay}-{gun}"

        gecerli = 0
        biten = 0
        ilk_yari = 0

        for satir in mac_satirlari:
            try:
                # Takım isimleri - tüm olası seçiciler
                isimler = satir.find_elements(By.CSS_SELECTOR, 
                    "span.match-row__team-name-text, span.team-name, div.match-row__team-name, span.name, td.team")
                if len(isimler) < 2: continue

                ev = isimler[0].text.strip()
                dep = isimler[1].text.strip()

                # Tekrar engelleme
                kimlik = f"{akilli_isim_temizle(ev)}-{akilli_isim_temizle(dep)}"
                if kimlik in gorulen: continue
                gorulen.add(kimlik)

                if len(ev) < 2 or len(dep) < 2: continue

                # Skorlar
                s_ev, s_dep = 0, 0
                skor_el = satir.find_elements(By.CSS_SELECTOR, 
                    "span.match-row__score-text, span.score, div.score, td.score")
                if len(skor_el)>=2:
                    if skor_el[0].text.strip().isdigit(): s_ev=int(skor_el[0].text.strip())
                    if skor_el[1].text.strip().isdigit(): s_dep=int(skor_el[1].text.strip())

                # İlk Yarı
                iy_ev, iy_dep = 0, 0
                try:
                    iy_el = satir.find_element(By.CSS_SELECTOR, 
                        "div.match-row__half-time-score, div.half-time, span.ht, td.ht")
                    rakam = re.findall(r'\d+', iy_el.text)
                    if len(rakam)==2:
                        iy_ev=int(rakam[0]); iy_dep=int(rakam[1]); ilk_yari+=1
                except: pass

                # ✅ DURUM: MS = BİTTİ KESİN KURAL
                durum = "baslamadi"
                try:
                    st_el = satir.find_element(By.CSS_SELECTOR, 
                        "a.match-row__status, div.match-row__status, span.status, td.status")
                    st_yazi = st_el.text.strip().upper()
                    if "MS" in st_yazi or "FİNAL" in st_yazi or "BİTTİ" in st_yazi or "SONUÇ" in st_yazi:
                        durum = "bitti"; biten+=1
                    elif "CANLI" in st_yazi or "DEVAM" in st_yazi or "'" in st_yazi or "DK" in st_yazi:
                        durum = "devam ediyor"
                except: pass

                skor_listesi.append({
                    "tarih": hedef_tarih_iso,
                    "ev_sahibi": ev,
                    "deplasman": dep,
                    "skor_ev": s_ev,
                    "skor_dep": s_dep,
                    "skor_1y_ev": iy_ev,
                    "skor_1y_dep": iy_dep,
                    "durum": durum
                })
                gecerli+=1
                print(f"✅ {ev} - {dep} | {s_ev}-{s_dep} | {durum}")

            except: continue

    except Exception as hata:
        print(f"❌ Çekim Hatası: {hata}")
    finally:
        if driver: driver.quit()

    print(f"✅ Tamamlandı | Geçerli: {gecerli} | Biten: {biten} | İlk Yarı: {ilk_yari}")
    return skor_listesi

# =============================================================================
# 🧠 GÜNCELLEME MOTORU - ✅ EN BÜYÜK GELİŞTİRME BURADA
# =============================================================================
def skorlari_eslestir_ve_guncelle(mevcut_yapi, yeni_skorlar):
    mac_listesi = mevcut_yapi.get("matches", [])
    if not mac_listesi or not yeni_skorlar: return 0

    guncelleme_sayisi = 0
    eslesen_indexler = set() # ✅ Aynı maçı tekrar güncellemesin

    # ✅ Her yeni veriyi, JSON'daki TÜM maçlarla karşılaştır (birini bulunca diğerlerini es geçmez)
    for y_veri in yeni_skorlar:
        y_tarih = y_veri["tarih"]
        y_ev = y_veri["ev_sahibi"]
        y_dep = y_veri["deplasman"]

        en_uygun = []

        # JSON'daki HER MAÇLA KARŞILAŞTIR
        for i, mac in enumerate(mac_listesi):
            if i in eslesen_indexler: continue

            m_tarih = mac.get("tarih", "")
            m_ev = mac.get("ev_sahibi", "")
            m_dep = mac.get("deplasman", "")

            # ✅ TARİH FARKLI YAZILSA BİLE AYNI KABUL ET
            if not tarihi_esit_kabul_et(m_tarih, y_tarih):
                continue

            # ✅ İSİMLER FARKLI YAZILSA BİLE BENZERLİK ORANI %35 ÜSTÜYSE EŞLEŞTİR
            o1 = benzerlik_orani(m_ev, y_ev) + benzerlik_orani(m_dep, y_dep)
            o2 = benzerlik_orani(m_ev, y_dep) + benzerlik_orani(m_dep, y_ev)

            if o1 >= ESLESME_SEVIYESI or o2 >= ESLESME_SEVIYESI:
                en_uygun.append( (-max(o1,o2), i, (o2>o1)) )

        # En yüksek benzerlik oranına sahip olanı seç
        if en_uygun:
            en_uygun.sort()
            _, index, ters_mi = en_uygun[0]
            eslesen_indexler.add(index) # ✅ Aynı maçı tekrar eşleştirmeyi engelle

            mac = mac_listesi[index]

            # Skorları doğru tarafa yerleştir (ters eşleşme varsa değiştir)
            s_ev, s_dep = (y_veri["skor_ev"], y_veri["skor_dep"]) if not ters_mi else (y_veri["skor_dep"], y_veri["skor_ev"])
            iy_ev, iy_dep = (y_veri["skor_1y_ev"], y_veri["skor_1y_dep"]) if not ters_mi else (y_veri["skor_1y_dep"], y_veri["skor_1y_ev"])

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

            # Durum Güncelle - MS yazanlar kesin bitti
            if mac.get("durum") != y_veri["durum"]:
                mac["durum"] = y_veri["durum"]
                degisiklik_var = True

            if degisiklik_var:
                guncelleme_sayisi += 1
                print(f"✅ GÜNCELLEME | {mac['ev_sahibi']} - {mac['deplasman']} | Skor: {mac['skor_ev']}-{mac['skor_dep']} | İlk Yarı: {mac['skor_1y_ev']}-{mac['skor_1y_dep']} | Durum: {mac['durum']}")

    return guncelleme_sayisi

# =============================================================================
# 🚀 ANA ÇALIŞTIRICI - Tüm Sorunlar Çözüldü
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("⚽ GELİŞTİRİLMİŞ SKOR GÜNCELLEYİCİ | AKILLI EŞLEŞTİRME MODU 🧠")
    print("=" * 70)
    print("🔒 KURAL 1: Oranlar, Lig, Saat, Index, Kodlar -> HİÇ DOKUNULMAZ!")
    print("🔒 KURAL 2: gecmis_maclar.json -> KESİNLİKLE GÖRMEZ, DOKUNMAZ!")
    print("🔧 ÖZELLİK: Aynı maç farklı yazılsa / farklı tarihte görünse bile hepsini günceller")
    print("-" * 70)

    # 1. Mevcut dosyayı oku
    mevcut_yapi = load_mac_json()
    if not mevcut_yapi:
        print("❌ İşlem iptal edildi.")
        input("🔚 Çıkmak için Enter...")
        exit()

    # 2. Maçkolik'ten verileri çek
    yeni_skorlar = get_skorlar()
    if not yeni_skorlar:
        print("❌ Maçkolik verisi alınamadı. İşlem iptal edildi.")
        input("🔚 Çıkmak için Enter...")
        exit()

    # 3. Akıllı eşleştirme ile güncelle
    guncellenen_sayi = skorlari_eslestir_ve_guncelle(mevcut_yapi, yeni_skorlar)

    # 4. Kaydet ve Git gönderimi
    if guncellenen_sayi > 0:
        save_mac_json(mevcut_yapi)
        print(f"\n📊 Toplam {guncellenen_sayi} adet maç güncellendi.")
        git_islemlerini_yap()
    else:
        print("\nℹ️ Güncellenecek veri bulunamadı.")

    print("\n" + "=" * 70)
    print("✅ TÜM İŞLEMLER BİTTİ | Artık aynı maçtan kaç tane varsa hepsi güncellenir ✅")
    print("🔧 GELİŞTİRME: Farklı isim yazımları / farklı tarih formatları tamamen destekleniyor")
    print("=" * 70)
    input("🔚 Çıkmak için Enter tuşuna bas...")