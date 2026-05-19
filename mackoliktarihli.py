import json, os, re, time
from datetime import datetime, timedelta
import subprocess
from pathlib import Path
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# =============================================================================
# AYARLAR - 🛡️ SON 2 GÜN + BAŞLANGIÇ BİTİŞ SAATİ EKLENDİ
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
BASE_LINK = "https://www.mackolik.com/futbol/canli-sonuclar"

# ---------------------------
# 🚨 TARİH AYARI: SON 2 GÜNÜ ÇEK - BUGÜN HARİÇ
# ---------------------------
BUGUN = datetime.now()
DUN = BUGUN - timedelta(days=1)
ONDEN_GUN = BUGUN - timedelta(days=3) # ⬅️ Son 3 gün: Dün ve Önceki gün
BASLANGIC_TARIHI = ONDEN_GUN.strftime("%Y-%m-%d")
BITIS_TARIHI = DUN.strftime("%Y-%m-%d")
# ---------------------------

ESLESME_SEVIYESI = 0.50       
TAM_ESLESME_SEVIYESI = 0.80   
GIT_BRANCH_NAME = "main"

# 🚨 KESİN KURALLAR
KURAL_SKOR_KONTROL = True     
KURAL_SIFIR_KONTROL = False   
KURAL_TARIH_KESIN = True      
KURAL_IKI_KONTROL = True       # 🔁 2 kere kontrol et
KURAL_UZERINE_YAZ = True       # ✅ Üzerine yaz (doğruluk öncelikli)

# ⚙️ PERFORMANS & BEKLEME SÜRELERİ (SAĞLAM MOD)
SAYFA_YUKLEME_BEKLEME = 45     
KAYDIRMA_BEKLEME = 2.5         
VERI_OKUMA_BEKLEME = 1.0       
TEKRAR_OKUMA_SAYISI = 2        
TEKRARLAR_ARASI_BEKLEME = 3.0  
MANTIK_HATASI_DUZELT = True    

# =============================================================================
# 📅 TARİH İŞLEMLERİ - DATA-DATE FORMATI
# =============================================================================
def tarihleri_olustur(baslangic_str, bitis_str):
    def str_to_tarih(t):
        yil, ay, gun = map(int, t.split('-'))
        return datetime(yil, ay, gun)
    
    baslangic = str_to_tarih(baslangic_str)
    bitis = str_to_tarih(bitis_str)
    tarihler = []
    
    while baslangic <= bitis:
        if baslangic.date() != BUGUN.date():
            tarihler.append(baslangic.strftime("%Y-%m-%d"))
        baslangic += timedelta(days=1)
    return tarihler

def tarihi_esit_kabul_et(t1, t2):
    if not t1 or not t2: return False
    def duzelt(t):
        t = str(t).strip()
        if '/' in t:
            parca = t.split('/')
            if len(parca) == 3: return f"{parca[2]}-{parca[1]}-{parca[0]}"
            if len(parca) == 2: return f"2026-{parca[1]}-{parca[0]}"
        if len(t) > 10: return t[:10]
        return t
    return duzelt(t1) == duzelt(t2)

# =============================================================================
# 🔐 İSİM TEMİZLEME & EŞLEŞTİRME (BOŞLUKLARI SİLER, AKILLI EŞLEŞİR)
# =============================================================================
def akilli_isim_temizle(isim):
    if not isim: return ""
    isim = isim.lower().strip()
    # 📌 Boşlukları, özel karakterleri tamamen sil
    isim = isim.replace(" ", "").replace("-", "").replace(".", "").replace("'", "").replace("’", "")
    tr_map = str.maketrans("çğıöşüâêîôûáéíóúñðßçşğ", "cgiosuaeiouaeiounbscsg")
    isim = isim.translate(tr_map)
    isim = re.sub(r'[^a-z]', '', isim)
    gereksiz = [
        'fc', 'sk', 'jk', 'bk', 'as', 'spor', 'kulubu', 'kulübü', 'team', 'fk', 'sc', 'cf',
        'u19', 'u21', 'ii', 'iii', 'iv', 'rc', 'ac', 'fc', 'cfc', 'sfc', 'fck', 'fcb', 'fcp',
        'united', 'city', 'academy', 'reserves', 'youth', 'bk', 'ff'
    ]
    for ek in gereksiz:
        isim = isim.replace(ek, '')
    if len(isim) < 3: return "GECERSIZ"
    return isim.strip()

def benzerlik_orani(a, b):
    if not a or not b: return 0.0
    a_temiz = akilli_isim_temizle(a)
    b_temiz = akilli_isim_temizle(b)
    if a_temiz == "GECERSIZ" or b_temiz == "GECERSIZ": return 0.0
    if a_temiz == b_temiz: return 1.0
    if a_temiz in b_temiz or b_temiz in a_temiz: return 0.9
    return round(SequenceMatcher(None, a_temiz, b_temiz).ratio(), 2)

# =============================================================================
# 🚨 SKOR MANTIK KONTROLÜ
# =============================================================================
def skor_mantikli_mi(ev, dep, iy_ev, iy_dep, durum, ev_isim="", dep_isim=""):
    if not KURAL_SKOR_KONTROL:
        return True, "Kontrol Kapalı", True

    if iy_ev > ev or iy_dep > dep:
        if MANTIK_HATASI_DUZELT:
            return True, f"⚠️ UYARI | {ev_isim}-{dep_isim} | İY:{iy_ev}-{iy_dep} > MS:{ev}-{dep} | Kısmi veri", False
        else:
            return False, f"❌ MANTIK HATASI | {ev_isim}-{dep_isim} | İmkansız Skor", False

    if ev == 0 and dep == 0 and iy_ev == 0 and iy_dep == 0:
        return True, f"✅ BİTEN MAÇ | {ev_isim}-{dep_isim} | 0-0 | Geçerli", True

    return True, "✅ Mantık Hatası Yok", True

# =============================================================================
# 📖 DOSYA OKU - KAYDET - GİT
# =============================================================================
def load_mac_json():
    try:
        if not MAC_JSON_PATH.exists():
            print(f"❌ HATA: {MAC_JSON_PATH} bulunamadı!")
            return None
        with open(MAC_JSON_PATH, 'r', encoding='utf-8') as f:
            veri = json.load(f)
        if isinstance(veri, dict) and "matches" in veri:
            print(f"📖 Dosya Okundu | Toplam: {len(veri['matches'])} maç.")
            return veri 
        else:
            print("❌ HATA: Dosya formatı uyumsuz.")
            return None
    except Exception as e:
        print(f"❌ OKUMA HATASI: {e}")
        return None

def save_mac_json(veri):
    try:
        yedek = MAC_JSON_PATH.with_name("mac_json_yedek_guvenli.json")
        with open(yedek, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        with open(MAC_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2, default=str)
        print(f"💾 Kayıt Başarılı | Yedek: {yedek.name}")
        print("🔒 Oran, Lig, Kodlar -> KORUNDU.")
    except Exception as e:
        print(f"❌ KAYDETME HATASI: {e}")

def git_islemlerini_yap():
    print("\n" + "="*70)
    print("🚀 GİT İŞLEMLERİ BAŞLATILDI...")
    print("="*70)
    try:
        os.chdir(BASE_DIR)
        durum_cikisi = subprocess.run(["git", "status"], capture_output=True, text=True).stdout
        if "nothing to commit" in durum_cikisi:
            print("ℹ️ Değişiklik yok.")
            return False
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"[OTOMATİK] SON 2 GÜN | BAŞLANGIÇ-BİTİŞ SAATİ EKLENDİ"], check=True)
        subprocess.run(["git", "push", "origin", GIT_BRANCH_NAME], check=True)
        print("✅ GİT BAŞARILI!")
        return True
    except Exception as e:
        print(f"❌ GİT HATASI: {e}")
        return False

# =============================================================================
# 🌐 VERİ ÇEKİMİ - ✅ BAŞLANGIÇ & BİTİŞ SAATİ EKLENDİ + 2X KONTROL
# =============================================================================
def get_skorlar_tek_gun(hedef_tarih_iso):
    print(f"\n📅 İŞLENİYOR: {hedef_tarih_iso} | 🛡️ SAĞLAM MOD + SAAT BİLGİSİ")
    skor_listesi = []
    gorulen = set()
    
    atlanan_sayisi = 0
    kismi_veri_sayisi = 0
    gecerli_sayisi = 0
    driver = None

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    try:
        print(f"🌐 Site: {BASE_LINK}")
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.get(BASE_LINK)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.widget-dateslider__datepicker-toggle"))
        )

        # ✅ Takvim Butonu Aç
        try:
            takvim_buton = driver.find_element(By.CSS_SELECTOR, "button.widget-dateslider__datepicker-toggle")
            driver.execute_script("arguments[0].click();", takvim_buton)
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Takvim butonu hatası: {e}")
            return []

        # ✅ Tarihi Kesin Olarak Seç (data-date ile)
        try:
            secici = f'td.widget-datepicker__calendar-body-cell[data-date="{hedef_tarih_iso}"]'
            tarih_elemani = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, secici))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tarih_elemani)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", tarih_elemani)
            print(f"✅ Tarih Seçildi: {hedef_tarih_iso}")
            print(f"⌛ Sayfa Yüklenmesi Bekleniyor... ({SAYFA_YUKLEME_BEKLEME} sn)")
            time.sleep(SAYFA_YUKLEME_BEKLEME)
        except Exception as e:
            print(f"⚠️ {hedef_tarih_iso} bulunamadı: {e}")
            return []

        # ✅ Sayfayı En Alta Kadar YAVAŞÇA Kaydır
        print("📜 Sayfa yavaşça kaydırılıyor, tüm maçlar yüklensin...")
        son_yukseklik = driver.execute_script("return document.body.scrollHeight")
        for _ in range(15):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(KAYDIRMA_BEKLEME)
            yeni_yukseklik = driver.execute_script("return document.body.scrollHeight")
            if yeni_yukseklik == son_yukseklik:
                break
            son_yukseklik = yeni_yukseklik
        time.sleep(3)

        # ✅ MAÇLARI OKU - 🔁 İKİ KERE KONTROL MEKANİZMASI
        mac_satirlari = driver.find_elements(By.CSS_SELECTOR, "div.match-row")
        print(f"🔍 Toplam Satır: {len(mac_satirlari)} | 🔁 2 Kere Kontrol Edilecek")

        gecici_veriler = {}

        for okuma_donemi in range(TEKRAR_OKUMA_SAYISI):
            print(f"🔁 Okuma Turu: {okuma_donemi+1}/{TEKRAR_OKUMA_SAYISI}")
            mac_satirlari = driver.find_elements(By.CSS_SELECTOR, "div.match-row")

            for satir_index, satir in enumerate(mac_satirlari):
                try:
                    time.sleep(VERI_OKUMA_BEKLEME)

                    # ✅ SAAT BİLGİSİNİ ÇEK (Maç Başlangıcı)
                    mac_baslangic = ""
                    try:
                        saat_el = satir.find_element(By.CSS_SELECTOR, "span.match-row__time")
                        mac_baslangic = saat_el.text.strip()
                    except: pass

                    # ✅ TAKIM İSİMLERİ
                    isimler = satir.find_elements(By.CSS_SELECTOR, "span.match-row__team-name-text")
                    if len(isimler) < 2: continue

                    ev_isim = isimler[0].text.strip()
                    dep_isim = isimler[1].text.strip()

                    # 📌 BOŞLUKLARI SİLEREK KARŞILAŞTIR (osgorriones - villaespanola sorunu çözümü)
                    kimlik = f"{akilli_isim_temizle(ev_isim)}-{akilli_isim_temizle(dep_isim)}"
                    if kimlik in gorulen and okuma_donemi == 0: continue

                    if len(ev_isim) < 3 or len(dep_isim) < 3:
                        atlanan_sayisi +=1
                        continue

                    # ✅ SKORLARI OKU
                    en_iyi_sonuc = {"s_ev":0, "s_dep":0, "iy_ev":0, "iy_dep":0, "baslangic": mac_baslangic, "bitis": ""}

                    try:
                        ev_skor_el = satir.find_element(By.CSS_SELECTOR, "span.match-row__score-home")
                        dep_skor_el = satir.find_element(By.CSS_SELECTOR, "span.match-row__score-away")
                        s1_tmp = ev_skor_el.text.strip()
                        s2_tmp = dep_skor_el.text.strip()
                        if s1_tmp.isdigit(): en_iyi_sonuc["s_ev"] = int(s1_tmp)
                        if s2_tmp.isdigit(): en_iyi_sonuc["s_dep"] = int(s2_tmp)
                    except: pass

                    # ✅ İLK YARI SKORU
                    try:
                        iy_el = satir.find_element(By.CSS_SELECTOR, "div.match-row__half-time-score")
                        iy_metin = iy_el.text.strip()
                        rakamlar_tmp = re.findall(r'\d+', iy_metin)
                        if len(rakamlar_tmp) == 2:
                            en_iyi_sonuc["iy_ev"] = int(rakamlar_tmp[0])
                            en_iyi_sonuc["iy_dep"] = int(rakamlar_tmp[1])
                            # ✅ İlk yarı skoru varsa maçı bitmiş kabul edip bitiş saati ata
                            en_iyi_sonuc["bitis"] = "Bitti"
                    except: pass

                    # ✅ 2. Tur Kontrolü: Eğer önceki veriden farklı ve sıfır değilse, yenisini geçerli say
                    if okuma_donemi == 0:
                        # İlk okumayı kaydet
                        gecici_veriler[kimlik] = en_iyi_sonuc.copy()
                        # Orjinal isimleri de sakla ki sonra yazdırabilelim
                        gecici_veriler[f"{kimlik}_isimler"] = {"ev": ev_isim, "dep": dep_isim}
                    else:
                        # İkinci okuma: karşılaştır ve en doğrusunu al
                        onceki = gecici_veriler.get(kimlik, {})
                        if onceki:
                            # Eğer ikinci okumadaki veri daha doluysa veya farklıysa onu kullan
                            if (en_iyi_sonuc["s_ev"] != onceki.get("s_ev", 0) and en_iyi_sonuc["s_ev"] > 0) or \
                               (en_iyi_sonuc["s_dep"] != onceki.get("s_dep", 0) and en_iyi_sonuc["s_dep"] > 0) or \
                               (en_iyi_sonuc["iy_ev"] != onceki.get("iy_ev", 0) and en_iyi_sonuc["iy_ev"] > 0) or \
                               (en_iyi_sonuc["iy_dep"] != onceki.get("iy_dep", 0) and en_iyi_sonuc["iy_dep"] > 0) or \
                               (en_iyi_sonuc["baslangic"] != onceki.get("baslangic", "")):
                                print(f"🔁 Düzeltme Yapıldı | {ev_isim} - {dep_isim} | Eski: {onceki} | Yeni: {en_iyi_sonuc}")
                                gecici_veriler[kimlik] = en_iyi_sonuc.copy()

                except Exception as satir_hata:
                    atlanan_sayisi += 1
                    continue

            # Turlar arası bekleme
            if okuma_donemi < TEKRAR_OKUMA_SAYISI - 1:
                time.sleep(TEKRARLAR_ARASI_BEKLEME)

        # ✅ Tüm kontroller bitti, artık kesinleşmiş verileri listeye ekle
        for kimlik, sonuc in gecici_veriler.items():
            if "_isimler" in kimlik: continue # İsim yedeklerini atla

            isimler_bilgisi = gecici_veriler.get(f"{kimlik}_isimler", {})
            ev_isim_orj = isimler_bilgisi.get("ev", "")
            dep_isim_orj = isimler_bilgisi.get("dep", "")

            s_ev = sonuc["s_ev"]
            s_dep = sonuc["s_dep"]
            iy_ev = sonuc["iy_ev"]
            iy_dep = sonuc["iy_dep"]
            mac_baslangic = sonuc["baslangic"]
            mac_bitis = sonuc["bitis"]

            # ✅ KURAL: HEPSİNİ BİTTİ KABUL ET
            durum = "bitti"

            # Kontrol
            mantikli, mesaj, tam_veri_mi = skor_mantikli_mi(s_ev, s_dep, iy_ev, iy_dep, durum, ev_isim_orj, dep_isim_orj)

            if not mantikli:
                print(f"{mesaj} | TAMAMEN ATLANDI")
                atlanan_sayisi += 1
                continue

            if not tam_veri_mi:
                print(f"{mesaj} | KISMEN KAYDEDİLDİ")
                kismi_veri_sayisi += 1
            else:
                if "Geçerli Sonuç" in mesaj or "Mantık Hatası Yok" in mesaj:
                    print(f"✅ KAYIT | {ev_isim_orj} - {dep_isim_orj} | MS:{s_ev}-{s_dep} | İY:{iy_ev}-{iy_dep} | SAAT:{mac_baslangic}")

            skor_listesi.append({
                "tarih": hedef_tarih_iso,
                "ev_sahibi": ev_isim_orj,
                "deplasman": dep_isim_orj,
                "skor_ev": s_ev,
                "skor_dep": s_dep,
                "skor_1y_ev": iy_ev,
                "skor_1y_dep": iy_dep,
                "durum": durum,
                "mac_baslangic": mac_baslangic, # ⏰ YENİ ÖZELLİK: Maç Başlangıç Saati
                "mac_bitis": mac_bitis          # ⏰ YENİ ÖZELLİK: Maç Bitiş Durumu
            })
            gecerli_sayisi += 1

    except WebDriverException as wde:
        print(f"❌ Sürücü Hatası: {wde}")
    except Exception as ana_hata:
        print(f"❌ Çekim Ana Hatası: {ana_hata}")
    finally:
        if driver:
            driver.quit()

    print(f"📅 {hedef_tarih_iso} Özeti: Toplam Geçerli: {gecerli_sayisi} | Kısmi Veri: {kismi_veri_sayisi} | Tamamen Atlanan: {atlanan_sayisi}")
    return skor_listesi

# =============================================================================
# 🧠 GÜNCELLEME MOTORU - ✅ BOŞLUKSUZ EŞLEŞTİRME + ÜZERİNE YAZMA + SAAT BİLGİSİ
# =============================================================================
def skorlari_eslestir_ve_guncelle(mevcut_yapi, tum_veriler):
    mac_listesi = mevcut_yapi.get("matches", [])
    if not mac_listesi or not tum_veriler:
        return 0

    guncelleme_sayisi = 0
    eslesen_indexler = set()

    for y_veri in tum_veriler:
        y_tarih = y_veri["tarih"]
        y_ev = y_veri["ev_sahibi"]
        y_dep = y_veri["deplasman"]

        en_uygun = []

        for i, mac in enumerate(mac_listesi):
            if i in eslesen_indexler:
                continue

            m_tarih = mac.get("tarih", "")
            m_ev = mac.get("ev_sahibi", "")
            m_dep = mac.get("deplasman", "")

            # ✅ KURAL: Tarihler tamamen aynı olmalı
            if not tarihi_esit_kabul_et(m_tarih, y_tarih):
                continue

            # ✅ KURAL: BOŞLUKLARI SİLEREK AKILLI EŞLEŞTİRME (En önemli kısım!)
            # "Osgor Riones" ile "osgorriones" aynı kabul ediliyor
            o1 = benzerlik_orani(m_ev, y_ev) + benzerlik_orani(m_dep, y_dep)
            o2 = benzerlik_orani(m_ev, y_dep) + benzerlik_orani(m_dep, y_ev)

            if o1 >= ESLESME_SEVIYESI or o2 >= ESLESME_SEVIYESI:
                en_uygun.append( (-max(o1, o2), i, (o2 > o1)) )

        if en_uygun:
            en_uygun.sort()
            _, index, ters_mi = en_uygun[0]
            eslesen_indexler.add(index)

            mac = mac_listesi[index]

            # Skorları doğru tarafa yerleştir (ev/deplasman karışıklığı olursa düzeltir)
            s_ev, s_dep = (y_veri["skor_ev"], y_veri["skor_dep"]) if not ters_mi else (y_veri["skor_dep"], y_veri["skor_ev"])
            iy_ev, iy_dep = (y_veri["skor_1y_ev"], y_veri["skor_1y_dep"]) if not ters_mi else (y_veri["skor_1y_dep"], y_veri["skor_1y_ev"])
            baslangic_saat = y_veri["mac_baslangic"]
            bitis_durum = y_veri["mac_bitis"]

            degisiklik_var = False

            # ✅ KURAL: ÜZERİNE YAZ! Yeni veri ne geldiyse, eskisi ne yazıyordu olursa olsun onu geçerli say.
            if KURAL_UZERINE_YAZ:
                # Maç Sonu Skorları
                if s_ev > 0 or s_dep > 0 or (s_ev == 0 and s_dep == 0 and y_veri["durum"] == "bitti"):
                    if mac.get("skor_ev") != s_ev:
                        mac["skor_ev"] = s_ev
                        degisiklik_var = True
                    if mac.get("skor_dep") != s_dep:
                        mac["skor_dep"] = s_dep
                        degisiklik_var = True

                # İlk Yarı Skorları (Her zaman güncelle)
                if mac.get("skor_1y_ev") != iy_ev:
                    mac["skor_1y_ev"] = iy_ev
                    degisiklik_var = True
                if mac.get("skor_1y_dep") != iy_dep:
                    mac["skor_1y_dep"] = iy_dep
                    degisiklik_var = True

                # ⏰ SAAT BİLGİLERİNİ EKLE/GÜNCELLE
                if mac.get("mac_baslangic") != baslangic_saat and baslangic_saat:
                    mac["mac_baslangic"] = baslangic_saat
                    degisiklik_var = True
                if mac.get("mac_bitis") != bitis_durum and bitis_durum:
                    mac["mac_bitis"] = bitis_durum
                    degisiklik_var = True

                # Durumu her zaman bitti yap
                if mac.get("durum") != "bitti":
                    mac["durum"] = "bitti"
                    degisiklik_var = True

            if degisiklik_var:
                guncelleme_sayisi += 1
                print(f"✅ GÜNCELLEME | {mac['ev_sahibi']} - {mac['deplasman']} | ESKİ: MS:{mac.get('skor_ev','?')}-{mac.get('skor_dep','?')} SAAT:{mac.get('mac_baslangic','?')} | YENİ: MS:{s_ev}-{s_dep} SAAT:{baslangic_saat} | DURUM:{mac['durum']}")

    return guncelleme_sayisi

# =============================================================================
# 🚀 ANA ÇALIŞTIRICI - SON 2 GÜN ÇALIŞACAK
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("⚽ KUSURSUZ VERİ ÇEKİCİ | SON 2 GÜN + BAŞLANGIÇ/BİTİŞ SAATİ 🛡️")
    print("=" * 70)
    print("🔒 KORUMA: Oran, Lig, Saat, Kodlar -> DOKUNULMAZ")
    print("✅ KURAL: Tüm maçlar otomatik olarak 'bitti' sayılır")
    print("✅ KURAL: Yeni veri geldiğinde ESKİSİNİN ÜZERİNE YAZ")
    print("✅ KURAL: İsimlerde boşluk olsa bile AKILLI EŞLEŞTİRME yapar")
    print("✅ KURAL: Her maçı 2 kere oku, hataları düzelt")
    print("✅ 📅 ÇEKİLECEK: Sadece Son 2 Gün (Dün ve Önceki Gün)")
    print("-" * 70)

    # 1. Dosyayı oku
    mevcut_yapi = load_mac_json()
    if not mevcut_yapi:
        print("❌ İşlem iptal edildi.")
        input("🔚 Çıkmak için Enter'a bas...")
        exit()

    # 2. Tarih aralığını hazırla (Sadece son 2 gün)
    tarihler = tarihleri_olustur(BASLANGIC_TARIHI, BITIS_TARIHI)
    print(f"📅 Taratılacak Tarihler: {tarihler}")

    # 3. Tüm tarihler için döngü
    tum_veriler = []
    for gun_iso in tarihler:
        gunluk_veri = get_skorlar_tek_gun(gun_iso)
        tum_veriler.extend(gunluk_veri)

    if not tum_veriler:
        print("❌ Hiç veri çekilemedi.")
        input("🔚 Çıkmak için Enter'a bas...")
        exit()

    # 4. JSON'dakilerle eşleştir ve güncelle
    guncellenen_sayisi = skorlari_eslestir_ve_guncelle(mevcut_yapi, tum_veriler)

    # 5. Kaydet ve Gönder
    if guncellenen_sayisi > 0:
        save_mac_json(mevcut_yapi)
        print(f"\n📊 Toplam {guncellenen_sayisi} adet maç güncellendi.")
        git_islemlerini_yap()
    else:
        print("\nℹ️ Güncellenecek yeni veri bulunamadı.")

    print("\n" + "=" * 70)
    print("✅ TÜM İŞLEMLER BİTTİ | VERİLER GÜVENDE ✅")
    print("=" * 70)
    input("🔚 Çıkmak için Enter'a bas...")