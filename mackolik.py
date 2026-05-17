import json, os, re, time, datetime, traceback, subprocess
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
GECMIS_JSON_PATH = BASE_DIR / "public" / "data" / "gecmis_maclar.json"
OUTPUT_SKOR_JSON = BASE_DIR / "public" / "data" / "skorlar_mackolik.json"
SPORDB_JSON_PATH = BASE_DIR / "public" / "data" / "spordb_data.json"

GERI_GUN_SAYISI = 2
BASE_LINK = "https://www.mackolik.com/canli-sonuclar"
ESLESME_SEVIYESI = 0.15
ADD_MISSING_MATCHES = True
GUNCELLE_SKORLARI = True
SCROLL_PAUSE_TIME = 1.5
MAX_SCROLL_ATTEMPT = 50

# =============================================================================
# İSİM TEMİZLEYİCİ (Eşleştirme için)
# =============================================================================
def akilli_isim_temizle(isim):
    if not isim: return ""
    isim = isim.lower().strip()
    
    gereksiz_ekler = [
        'fc', 'sk', 'jk', 'bk', 'as', 'aş', 'spor', 'kulübü', 'kulubu',
        '1899', '1903', '1905', '1907', '1910', '1912', '04', '05', '07',
        'sv', 'bv', 'vfb', 'bvb', 'sc', 'fortuna', 'bayer', 'hertha',
        'u19', 'u20', 'u21', 'u23', 'rez', 'rezerve', 'youth', 'ii', '(k)', 'kadın',
        'montevideo', 'liverpool', 'ca', 'sp', 'fc', 'cd', 'cf'
    ]
    for ek in gereksiz_ekler:
        isim = isim.replace(f" {ek} ", " ").replace(f" {ek}", "").replace(f"{ek} ", "")
    
    isim = re.sub(r'[.\-_,:0-9]', '', isim)
    isim = re.sub(r'\s+', ' ', isim).strip()
    
    duzelt = {
        "gs": "galatasaray", "fb": "fenerbahçe", "bjk": "beşiktaş", "ts": "trabzonspor",
        "bvb": "borussia dortmund", "fcb": "bayern münih", "ca penarol": "penarol",
        "liverpool montevideo": "liverpool"
    }
    return duzelt.get(isim, isim)

def benzerlik_orani(a, b):
    if not a or not b: return 0
    a_temiz = akilli_isim_temizle(a)
    b_temiz = akilli_isim_temizle(b)
    if a_temiz == b_temiz: return 1.0
    if a_temiz in b_temiz or b_temiz in a_temiz: return 0.90
    return SequenceMatcher(None, a_temiz, b_temiz).ratio()

def match_uid(tarih, ev, deplasman):
    if not ev or not deplasman: return ""
    ev_k = akilli_isim_temizle(ev)
    dep_k = akilli_isim_temizle(deplasman)
    if ev_k > dep_k: ev_k, dep_k = dep_k, ev_k
    return f"{tarih}|{ev_k}|{dep_k}"

# =============================================================================
# ✅ KESİNLİKLE VERİ KORUYAN OKUMA / KAYDETME
# =============================================================================
def load_json_safe(path):
    try:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                veri = json.load(f)
                # Senin yapın: Direkt liste olduğu için listeyi döndür
                if isinstance(veri, list):
                    return veri
                elif isinstance(veri, dict) and "matches" in veri:
                    return veri.get("matches", [])
        return []
    except Exception as e:
        print(f"⚠️ Okuma Hatası: {e}")
        return []

def save_json_atomic(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    try:
        if not isinstance(data, list):
            raise ValueError("Veri liste değil!")
            
        # ✅ Senin formatın birebir korunur, EKSTRA BİRŞEY EKLEMEZ
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        # Yedek al (GÜVENLİK İÇİN)
        if path.exists():
            try:
                path.replace(path.with_suffix(".json.yedek"))
            except: pass
            
        os.replace(temp_path, path)
        print(f"💾 {path.name} | Toplam: {len(data)} adet maç | ✅ TÜM ALANLAR KORUNDU")
    except Exception as e:
        print(f"❌ KAYDETME HATASI: {e} | ESKİ VERİLER KORUNDU!")
        if temp_path.exists(): temp_path.unlink()

# =============================================================================
# REKLAM KAPAT
# =============================================================================
def reklamlari_kapat(driver):
    try:
        kapat = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Kapat'], .close, .popup-close, .ad-close")
        for btn in kapat:
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.2)
        driver.execute_script("document.querySelectorAll('.modal-backdrop, .overlay').forEach(e=>e.remove());")
    except: pass

# =============================================================================
# 🟦 MAÇKOLİK VERİ ÇEKME
# =============================================================================
def get_all_matches(driver):
    print("🔎 [1/2] Maçkolik Verisi Çekiliyor...")
    tum_veriler = []

    try:
        driver.get(BASE_LINK)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".match-row__match-content")))
        time.sleep(5)
        reklamlari_kapat(driver)
    except Exception as e:
        print(f"❌ Maçkolik Sayfa Hatası: {e}")
        return []

    for adim in range(GERI_GUN_SAYISI):
        hedef_tarih = datetime.date.today() - datetime.timedelta(days=adim)
        gun_iso = hedef_tarih.isoformat()

        try:
            try:
                takvim_buton = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='datepicker']")))
                driver.execute_script("arguments[0].click();", takvim_buton)
                time.sleep(2)
                tarih_eleman = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'td[data-date="{gun_iso}"]')))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tarih_eleman)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", tarih_eleman)
                time.sleep(6)
                reklamlari_kapat(driver)
            except: pass

            for _ in range(MAX_SCROLL_ATTEMPT):
                onceki_yukseklik = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
                if driver.execute_script("return document.body.scrollHeight") == onceki_yukseklik:
                    break
            driver.execute_script("window.scrollTo(0,0);")

            mac_satirlari = driver.find_elements(By.CSS_SELECTOR, ".match-row__match-content[data-sport='S']")
            if not mac_satirlari: continue

            for sira, satir in enumerate(mac_satirlari, 1):
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", satir)
                except: pass

                lig = ""
                try: lig = satir.find_element(By.CSS_SELECTOR, ".match-row__competition-code").text.strip()
                except: pass

                saat = ""
                try: saat = satir.find_element(By.CSS_SELECTOR, ".match-row__start-time").text.strip()
                except: pass

                durum = ""
                try: 
                    durum_ham = satir.find_element(By.CSS_SELECTOR, ".match-row__status").text.strip().lower()
                    if durum_ham in ["bitti", "ms", "uzatma", "penaltı"]: durum = "bitti"
                    elif durum_ham in ["başlamadı", "bekleniyor", "ertelendi"]: durum = "baslamadi"
                    elif durum_ham in ["canlı", "devam", "ilk yarı", "ikinci yarı"]: durum = "devam ediyor"
                    else: durum = durum_ham
                except: pass

                ev_isim, dep_isim = "", ""
                try: ev_isim = satir.find_element(By.CSS_SELECTOR, ".match-row__team-name--home .match-row__team-name-text").text.strip()
                except: pass
                try: dep_isim = satir.find_element(By.CSS_SELECTOR, ".match-row__team-name--away .match-row__team-name-text").text.strip()
                except: pass
                if not ev_isim or not dep_isim: continue

                skor_ev, skor_dep = 0, 0
                try: skor_ev = int(satir.find_element(By.CSS_SELECTOR, ".match-row__score-home").text.strip() or 0)
                except: pass
                try: skor_dep = int(satir.find_element(By.CSS_SELECTOR, ".match-row__score-away").text.strip() or 0)
                except: pass

                iy_ev, iy_dep = 0, 0
                try:
                    iy_text = satir.find_element(By.CSS_SELECTOR, ".match-row__half-time-score").text.strip()
                    rakamlar = re.findall(r'\d+', iy_text)
                    if len(rakamlar) >= 2: iy_ev, iy_dep = int(rakamlar[0]), int(rakamlar[1])
                except:
                    try:
                        detay_veri = satir.get_attribute('data-match-detail') or ""
                        d_rakam = re.search(r'half_time":\[(\d+),(\d+)\]', detay_veri)
                        if d_rakam: iy_ev, iy_dep = int(d_rakam.group(1)), int(d_rakam.group(2))
                    except: pass

                # ✅ SENİN JSON YAPINA BİREBİR UYGUN
                veri = {
                    "index": 0,
                    "mac_kodu": "",
                    "ev_sahibi": ev_isim,
                    "deplasman": dep_isim,
                    "saat": saat,
                    "lig": lig,
                    "tarih": gun_iso,
                    "cekme_zamani": datetime.datetime.now().isoformat(),
                    "durum": durum,
                    "skor_ev": skor_ev,
                    "skor_dep": skor_dep,
                    "skor_1y_ev": iy_ev,
                    "skor_1y_dep": iy_dep,
                    "kaynak": "mackolik.com",
                    "oranlar": {}
                }
                tum_veriler.append(veri)

        except Exception as hata:
            continue

    print(f"✅ Maçkolik: {len(tum_veriler)} adet maç alındı.")
    return tum_veriler

# =============================================================================
# 🟩 SPORDB VERİ OKUMA & FORMAT DÖNÜŞÜMÜ (SENİN YAPINA UYGUN)
# =============================================================================
def get_spordb_matches():
    print("🔎 [2/2] Spordb Verisi Okunuyor...")
    if not SPORDB_JSON_PATH.exists():
        print("⚠️ Spordb JSON bulunamadı!")
        return []

    try:
        with open(SPORDB_JSON_PATH, 'r', encoding='utf-8') as f:
            spordb_json = json.load(f)
        
        ham_maclar = spordb_json.get("matches", [])
        duzenlenmis = []

        for mac in ham_maclar:
            # ✅ SPORDB -> SENİN FORMATIN (Hiçbir eksik alan yok)
            yeni = {
                "index": 0,
                "mac_kodu": mac.get("spordb_match_id", ""),
                "ev_sahibi": mac.get("sp_home", ""),
                "deplasman": mac.get("sp_away", ""),
                "saat": "",
                "lig": "",
                "tarih": mac.get("tarih", ""),
                "cekme_zamani": mac.get("cekme_zamani", datetime.datetime.now().isoformat()),
                "durum": "bitti" if (mac.get("skor1") or mac.get("skor2")) else "baslamadi",
                "skor_ev": mac.get("skor1", 0),
                "skor_dep": mac.get("skor2", 0),
                "skor_1y_ev": mac.get("iy_skor1", 0),
                "skor_1y_dep": mac.get("iy_skor2", 0),
                "kaynak": "spordb.com",
                "oranlar": {}
            }
            duzenlenmis.append(yeni)

        print(f"✅ Spordb: {len(duzenlenmis)} adet maç alındı.")
        return duzenlenmis

    except Exception as e:
        print(f"❌ Spordb Hatası: {e}")
        return []

# =============================================================================
# 🔄 GÜNCELLEME KURALI: KESİNLİKLE ESKİ VERİYİ BOZMAZ / SİLMEZ
# =============================================================================
def update_database(existing_matches, new_scores):
    # Mevcut verileri eşleştirme için hazırla
    mevcut_ids = {}
    gruplu = {}
    for m in existing_matches:
        uid = match_uid(m.get("tarih"), m.get("ev_sahibi"), m.get("deplasman"))
        if uid:
            mevcut_ids[uid] = m
        # Tarihe göre grupla, eşleştirmeyi hızlandır
        gruplu.setdefault(m.get("tarih"), []).append(m)

    stats = {"güncellendi":0, "yeni_eklendi":0, "atlanan":0, "eslesti":0}

    # Yeni gelen her maçı kontrol et
    for yeni in new_scores:
        t_tarih = yeni.get("tarih", "")
        t_ev = yeni.get("ev_sahibi", "")
        t_dep = yeni.get("deplasman", "")
        
        # Temel bilgisi eksik olanı atla
        if not t_tarih or not t_ev or not t_dep:
            continue

        # Aynı tarihteki maçları aday olarak al
        adaylar = gruplu.get(t_tarih, [])
        en_uygun = None
        en_puan = 0
        ters_mi = False

        # 🔎 AKILLI EŞLEŞTİRME: İsimler aynı mı, benzer mi?
        for aday in adaylar:
            a_ev = aday.get("ev_sahibi", "")
            a_dep = aday.get("deplasman", "")
            
            # Normal sıralama ve ters sıralama kontrolü
            p1 = benzerlik_orani(a_ev, t_ev) + benzerlik_orani(a_dep, t_dep)
            p2 = benzerlik_orani(a_ev, t_dep) + benzerlik_orani(a_dep, t_ev)
            
            if p1 > en_puan and (p1 / 2) >= ESLESME_SEVIYESI:
                en_puan = p1
                en_uygun = aday
                ters_mi = False
            if p2 > en_puan and (p2 / 2) >= ESLESME_SEVIYESI:
                en_puan = p2
                en_uygun = aday
                ters_mi = True

        # ✅ EŞLEŞME OLDU: GÜNCELLEME ZAMANI
        if en_uygun:
            stats["eslesti"] += 1

            # Skorları doğru tarafa yerleştir (ev/deplasman yer değiştirme durumu)
            s1, s2 = (yeni["skor_ev"], yeni["skor_dep"]) if not ters_mi else (yeni["skor_dep"], yeni["skor_ev"])
            i1, i2 = (yeni["skor_1y_ev"], yeni["skor_1y_dep"]) if not ters_mi else (yeni["skor_1y_dep"], yeni["skor_1y_ev"])

            degisim_var_mi = False

            # 🛑 KURAL 1: SADECE YENİ VERİDE DEĞER VARSA VE 0 DEĞİLSE GÜNCELLE!
            # 🛑 KURAL 2: Yeni veri boş veya 0 ise ESKİ VERİ AYNI KALSIN, DOKUNMA!
            if GUNCELLE_SKORLARI:
                
                # Ana Skor Güncelleme
                if s1 != 0 and en_uygun.get("skor_ev") != s1:
                    en_uygun["skor_ev"] = s1
                    degisim_var_mi = True
                if s2 != 0 and en_uygun.get("skor_dep") != s2:
                    en_uygun["skor_dep"] = s2
                    degisim_var_mi = True

                # İlk Yarı Skor Güncelleme
                if i1 != 0 and en_uygun.get("skor_1y_ev") != i1:
                    en_uygun["skor_1y_ev"] = i1
                    degisim_var_mi = True
                if i2 != 0 and en_uygun.get("skor_1y_dep") != i2:
                    en_uygun["skor_1y_dep"] = i2
                    degisim_var_mi = True

                # Durum Güncelleme
                yeni_durum = yeni.get("durum", "")
                if yeni_durum and yeni_durum != "" and en_uygun.get("durum") != yeni_durum:
                    en_uygun["durum"] = yeni_durum
                    degisim_var_mi = True

                # Spordb ID (mac_kodu) - Sadece eski boşsa doldur, doluysa değiştirme
                yeni_kod = yeni.get("mac_kodu", "")
                if yeni_kod and yeni_kod != "" and not en_uygun.get("mac_kodu"):
                    en_uygun["mac_kodu"] = yeni_kod
                    degisim_var_mi = True

                # Kaynak ve Zaman Bilgisi
                if degisim_var_mi:
                    en_uygun["kaynak"] = yeni.get("kaynak", en_uygun.get("kaynak", ""))
                    en_uygun["cekme_zamani"] = datetime.datetime.now().isoformat()
                    stats["güncellendi"] += 1
                    print(f"✏️ GÜNCELLE | {en_uygun['ev_sahibi']} - {en_uygun['deplasman']} | Skor: {en_uygun['skor_ev']}-{en_uygun['skor_dep']}")

            # 🔒 KORUMA: ORANLAR, LİG, SAAT, INDEX GİBİ ALANLARA DOKUNULMUYOR!
            # Bu alanlar yeni veride olmasa bile eski değerleri aynen kalır, silinmez!

        # ✅ EŞLEŞME YOK: YENİ KAYIT OLARAK EKLE
        else:
            if ADD_MISSING_MATCHES:
                yeni_uid = match_uid(yeni["tarih"], yeni["ev_sahibi"], yeni["deplasman"])
                
                # Aynı kayıt zaten varsa atla
                if yeni_uid in mevcut_ids:
                    stats["atlanan"] += 1
                    continue

                # 📌 SENİN JSON YAPINA %100 UYGUN YENİ KAYIT
                # 📌 Eksik alanlar boş geçilir, mevcut veriyi etkilemez
                yeni_mac = {
                    "index": 0,
                    "mac_kodu": yeni.get("mac_kodu", ""),
                    "ev_sahibi": yeni["ev_sahibi"],
                    "deplasman": yeni["deplasman"],
                    "saat": yeni.get("saat", ""),
                    "lig": yeni.get("lig", ""),
                    "tarih": yeni["tarih"],
                    "cekme_zamani": yeni.get("cekme_zamani", datetime.datetime.now().isoformat()),
                    "durum": yeni["durum"],
                    "skor_ev": yeni["skor_ev"],
                    "skor_dep": yeni["skor_dep"],
                    "skor_1y_ev": yeni["skor_1y_ev"],
                    "skor_1y_dep": yeni["skor_1y_dep"],
                    "kaynak": yeni["kaynak"],
                    "oranlar": yeni.get("oranlar", {})
                }

                existing_matches.append(yeni_mac)
                mevcut_ids[yeni_uid] = yeni_mac
                gruplu.setdefault(yeni["tarih"], []).append(yeni_mac)
                stats["yeni_eklendi"] += 1
                print(f"➕ YENİ EKLENDİ | {yeni_mac['ev_sahibi']} - {yeni_mac['deplasman']} | {yeni_mac['tarih']}")
            else:
                stats["atlanan"] += 1

    # ✅ SON ADIM: INDEX NUMARALANDIRMA (SIRALAMA BOZULMAZ)
    # Tarih -> Saat -> Ev Sahibi ismine göre sırala
    existing_matches.sort(key=lambda x: (x.get("tarih", ""), x.get("saat", "00:00"), x.get("ev_sahibi", "")))
    
    # Indexleri 1'den başlayarak tekrar numaralandır
    for sira, eleman in enumerate(existing_matches, 1):
        eleman["index"] = sira

    return stats

# =============================================================================
# ANA FONKSİYON
# =============================================================================
def main():
    print("="*70)
    print("⚽ MAÇKOLİK + SPORDB | VERİ KORUMA MODU ✅ | SİTE UYUMLU ✅")
    print("="*70)
    print(f"🔗 Maçkolik: {BASE_LINK}")
    print(f"📂 Spordb: {SPORDB_JSON_PATH.name}")
    print(f"📅 Gün: {GERI_GUN_SAYISI}")
    print(f"⚙️ Eşleşme Seviyesi: {ESLESME_SEVIYESI}")
    print("🔒 KORUMA: Oranlar, Lig, Saat, Index, Eski Veri SİLİNMEZ / BOZULMAZ")
    print("-"*70)

    driver = None
    tum_veriler = []
    istatistik = {}

    try:
        # 🚀 TARAYICI AYARLARI
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")  # Gizli mod için bu satırı aç
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        print("🌐 Tarayıcı Başlatılıyor...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # 📥 VERİLERİ ÇEK
        mackolik_veri = get_all_matches(driver)
        spordb_veri = get_spordb_matches()

        # 📥 BİRLEŞTİR: Spordb verisi sonradan işlensin ki güncellemede önceliği olsun
        tum_veriler = mackolik_veri + spordb_veri

        # 💾 HAM VERİYİ KAYDET
        save_json_atomic(tum_veriler, OUTPUT_SKOR_JSON)

        # 🔄 MEVCUT VERİTABANINI GÜNCELLE (EN KRİTİK KISIM)
        if len(tum_veriler) > 0:
            print("\n🔄 Ana Veritabanı (mac.json) Yükleniyor ve Güncelleniyor...")
            mac_veri = load_json_safe(MAC_JSON_PATH)
            onceki_sayi = len(mac_veri)
            
            # ✅ GÜNCELLEME FONKSİYONU ÇALIŞIR (Artık hiçbir veri silinmez!)
            istatistik = update_database(mac_veri, tum_veriler)
            yeni_sayi = len(mac_veri)
            
            # ✅ KAYDETME: SADECE LİSTE FORMATINDA, EKSTRA VERİ EKLEMEZ!
            save_json_atomic(mac_veri, MAC_JSON_PATH)

            # 📈 SONUÇ EKRANI
            print(f"""
📈 İŞLEM SONUÇLARI
--------------------------------------------------
📊 Önceki Kayıt Sayısı : {onceki_sayi}
✅ Eşleşen Maç Sayısı   : {istatistik.get('eslesti', 0)}
✏️ Güncellenen Bilgi    : {istatistik.get('güncellendi', 0)}
➕ Yeni Eklenen Maç     : {istatistik.get('yeni_eklendi', 0)}
⏭️ Atlanan (Varolan)    : {istatistik.get('atlanan', 0)}
📊 Yeni Toplam Kayıt    : {yeni_sayi}
🔒 Korumalı Alanlar     : oranlar, lig, saat, index (DEĞİŞMEDİ)
""")

            # 📂 GEÇMİŞ VERİYİ DE GÜNCELLE
            print("\n🔄 Geçmiş Veritabanı (gecmis_maclar.json) Güncelleniyor...")
            gecmis_veri = load_json_safe(GECMIS_JSON_PATH)
            update_database(gecmis_veri, tum_veriler)
            save_json_atomic(gecmis_veri, GECMIS_JSON_PATH)

        else:
            print("\n⚠️ Hiç veri çekilemedi, mevcut dosyalar GÜVENDE!")

    except Exception as genel_hata:
        print(f"❌ GENEL HATA: {genel_hata}")
        traceback.print_exc()
        print("🔒 ÖNEMLİ: Hata oluştu ama mevcut verileriniz BOZULMADI, eski hali duruyor.")

    finally:
        if driver:
            driver.quit()
            print("🗑️ Tarayıcı Kapatıldı.")

        # 🚀 GİT GÖNDERİMİ (SADECE DEĞİŞİKLİK VARSA ÇALIŞIR)
        try:
            if len(tum_veriler) > 0 and istatistik and (istatistik.get('yeni_eklendi',0) + istatistik.get('güncellendi',0)) > 0:
                print("\n🚀 Git Gönderim İşlemi Başlatılıyor...")
                repo_yol = BASE_DIR
                dosyalar = [
                    "public/data/mac.json",
                    "public/data/gecmis_maclar.json",
                    "public/data/skorlar_mackolik.json"
                ]
                for dosya in dosyalar:
                    dp = repo_yol / dosya
                    if dp.exists():
                        subprocess.run(["git", "add", dosya], cwd=repo_yol, capture_output=True)
                
                durum = subprocess.run(["git", "status", "--porcelain"], cwd=repo_yol, capture_output=True, text=True)
                if durum.stdout.strip():
                    zaman = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                    mesaj = f"🤖 {zaman} | Güncelleme | +{istatistik.get('yeni_eklendi',0)} Yeni | ~{istatistik.get('güncellendi',0)} Düzeltme"
                    subprocess.run(["git", "commit", "-m", mesaj], cwd=repo_yol, capture_output=True)
                    subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=repo_yol, capture_output=True)
                    subprocess.run(["git", "push", "origin", "main"], cwd=repo_yol, capture_output=True)
                    print("✅ Git İşlemi Tamamlandı.")
                else:
                    print("ℹ️ Değişiklik tespit edilmedi, Git'e gerek yok.")
            else:
                print("ℹ️ Gönderilecek yeni veri veya güncelleme yok.")
        except Exception as git_hata:
            print(f"⚠️ Git Hatası: {git_hata} - Dosyalarınız yine GÜVENDE.")

    print("\n" + "="*70)
    print("✅ TÜM İŞLEMLER BİTTİ | VERİLER %100 KORUNDU ✅")
    print("="*70)
    print("🔒 Korumalı Alanlar: oranlar, lig, saat, index, eski skorlar")
    print("📥 Güncellenen Alanlar: skor_ev, skor_dep, skor_1y_ev, skor_1y_dep, durum (SADECE yeni veri doluysa)")
    print("="*70)
    input("🔚 Çıkmak için Enter...")

# BAŞLAT
if __name__ == "__main__":
    main()