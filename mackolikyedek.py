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
from selenium.common.exceptions import *

# =============================================================================
# AYARLAR - 🚀 KESİNLİKLE GÜNCELLE | DOĞRU VERİ | OTOMATİK GİT ✅
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
BASE_LINK = "https://www.mackolik.com/futbol/canli-sonuclar"

# ---------------------------
# TARİH ARALIĞI - GG/AA/YYYY
# ---------------------------
BASLANGIC_TARIHI = "01/05/2026"
BITIS_TARIHI = "23/05/2026"
# ---------------------------

# 📌 EŞLEŞTİRME ORANI DÜŞÜRÜLDÜ: Artık isimler biraz farklı olsa da bulup eşleştirir
ESLESME_SEVIYESI = 0.25       
GIT_BRANCH_NAME = "main"      

# 🚨 KURALLAR
KURAL_SKOR_KONTROL = True     
KURAL_SIFIR_KONTROL = False   
KURAL_TARIH_KESIN = True      
MANTIK_HATASI_DUZELT = True   

# ⚙️ PERFORMANS
SAYFA_YUKLEME_BEKLEME = 20    
ADIM_KAYDIRMA_MIKTARI = 600   
ADIMLAR_ARASI_BEKLEME = 0.7   
GENEL_HATA_BEKLEME = 2        

# =============================================================================
# 📅 TARİH İŞLEMLERİ
# =============================================================================
def tarihleri_olustur(baslangic_str, bitis_str):
    def str_to_tarih(t):
        t = str(t).strip()
        if "/" in t:
            g, a, y = map(int, t.split('/'))
            return datetime.date(y, a, g)
        return None

    baslangic = str_to_tarih(baslangic_str)
    bitis = str_to_tarih(bitis_str)
    
    if not baslangic or not bitis:
        print("❌ Tarih formatı: 14/05/2026")
        return []

    tarihler = []
    while baslangic <= bitis:
        tarihler.append(baslangic.strftime("%Y-%m-%d"))
        baslangic += datetime.timedelta(days=1)
    return tarihler

def tarihi_esit_kabul_et(t1, t2):
    if not t1 or not t2: return False
    return str(t1).strip() == str(t2).strip()

# =============================================================================
# 🔐 İSİM TEMİZLEME - DAHA SADE HALE GETİRİLDİ
# =============================================================================
def akilli_isim_temizle(isim):
    if not isim: return ""
    isim = isim.lower().strip()
    # Türkçe karakterleri ve noktalama işaretlerini kaldır
    tr_map = str.maketrans("çğıöşüâêîôûáéíóúñðßçşğ()1234567890", "cgiosuaeiouaeiounbscsg         ")
    isim = isim.translate(tr_map)
    isim = re.sub(r'[^a-z\s]', '', isim) # Sadece harf ve boşluk kalsın
    isim = re.sub(r'\s+', ' ', isim).strip()
    
    # Gereksiz eklemeleri tamamen sil
    gereksiz = ['fk', 'sk', 'jk', 'bk', 'fc', 'as', 'spor', 'kulubu', 'kulübü', 'şportif', 'sport', 'clube', 'il', 'gk', 'üni', 'gençler']
    for ek in gereksiz:
        if isim.endswith(ek): isim = isim[:-len(ek)].strip()
        if isim.startswith(ek): isim = isim[len(ek):].strip()

    if len(isim) < 2: return ""
    return isim

def benzerlik_orani(a, b):
    if not a or not b: return 0.0
    a_temiz = akilli_isim_temizle(a)
    b_temiz = akilli_isim_temizle(b)
    
    # Tam eşleşme
    if a_temiz == b_temiz: return 1.0
    # Birinin içinde geçiyor mu?
    if a_temiz in b_temiz or b_temiz in a_temiz: return 0.85
    # İlk 3 harf eşleşiyor mu? (Çok önemli)
    if len(a_temiz) > 2 and len(b_temiz) > 2 and a_temiz[:3] == b_temiz[:3]: return 0.6
    
    return round(SequenceMatcher(None, a_temiz, b_temiz).ratio(), 2)

# =============================================================================
# 🚨 SKOR KONTROLÜ
# =============================================================================
def skor_mantikli_mi(ev, dep, iy_ev, iy_dep, durum, ev_isim="", dep_isim=""):
    if iy_ev > ev or iy_dep > dep:
        if MANTIK_HATASI_DUZELT:
            return True, f"ℹ️ {ev_isim}-{dep_isim} | Veri geç geldi, kısmi kaydedildi", False
        else:
            return False, f"❌ HATA | {ev_isim}-{dep_isim} | İmkansız Skor", False

    # ✅ ARTIK 0-0 OLANLARI DA KAYDETSİN, ATLAMASIN
    return True, "✅ Geçerli Veri", True

# =============================================================================
# 📖 DOSYA İŞLEMLERİ
# =============================================================================
def load_mac_json():
    try:
        if not MAC_JSON_PATH.exists(): return None
        with open(MAC_JSON_PATH, 'r', encoding='utf-8') as f:
            veri = json.load(f)
        if isinstance(veri, dict) and "matches" in veri:
            print(f"📖 Mevcut Dosya Okundu | Toplam: {len(veri['matches'])} maç.")
            return veri 
        return None
    except Exception as e:
        print(f"❌ OKUMA HATASI: {e}")
        return None

def save_mac_json(veri):
    try:
        yedek = MAC_JSON_PATH.with_name("mac_json_yedek.json")
        with open(yedek, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        with open(MAC_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2, default=str)
        print("💾 GÜNCEL DOSYA KAYDEDİLDİ ✅")
    except Exception as e:
        print(f"❌ KAYDETME HATASI: {e}")

def git_islemlerini_yap():
    try:
        print("\n🔄 GİT İŞLEMLERİ BAŞLATILIYOR...")
        os.chdir(BASE_DIR) 

        subprocess.run(["git", "add", "."], check=True)
        print("✅ git add .")

        tarih_saat = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        commit_mesaji = f"[OTOMATİK] | {tarih_saat} | Maç Sonuçları Güncellendi"
        subprocess.run(["git", "commit", "-m", commit_mesaji], check=True)
        print("✅ git commit")

        subprocess.run(["git", "push", "origin", GIT_BRANCH_NAME], check=True)
        print("✅ git push origin " + GIT_BRANCH_NAME)
        print("🚀 Tüm Git işlemleri tamamlandı!")

    except subprocess.CalledProcessError as e:
        if "nothing to commit" in str(e.output):
            print("ℹ️ Git: Değişiklik yok, gönderilecek bir şey yok.")
        else:
            print(f"⚠️ GİT HATA: {e}")
    except Exception as e:
        print(f"⚠️ GİT GENEL HATA: {e}")

# =============================================================================
# 🛠️ YARDIMCI FONKSİYONLAR
# =============================================================================
def rakam_bul(text):
    if not text: return 0
    rakamlar = re.findall(r'\d+', str(text))
    return int(rakamlar[0]) if rakamlar else 0

# =============================================================================
# 🌐 ÇEKİM - 🐢 ADIM ADIM KAYDIR | ✅ DOĞRU SINIFLAR
# =============================================================================
def get_skorlar_tek_gun(driver, hedef_tarih_iso):
    print(f"\n📅 İŞLENİYOR: {hedef_tarih_iso} | 🐢 ADIM ADIM KAYDIR")
    skor_listesi = []
    gorulen = set()
    gecerli_sayisi = 0
    atlanan_sayisi = 0

    try:
        # 📅 TAKVİM
        print("🔧 Takvim butonu: widget-dateslider__datepicker-toggle")
        try:
            takvim_buton = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "widget-dateslider__datepicker-toggle"))
            )
            driver.execute_script("arguments[0].click();", takvim_buton)
            print("✅ Takvim Açıldı")
            time.sleep(2)
        except Exception as e:
            print(f"❌ TAKVİM HATA: {e}")
            return []

        print(f"🔧 Tarih Seçiliyor: {hedef_tarih_iso}")
        try:
            secici = f'td.widget-datepicker__calendar-body-cell[data-date="{hedef_tarih_iso}"]'
            tarih_elemani = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, secici)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tarih_elemani)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", tarih_elemani)
            print(f"✅ TARİH SEÇİLDİ: {hedef_tarih_iso}")
            time.sleep(12)
        except Exception as e:
            print(f"❌ TARİH SEÇİLEMEDİ: {e}")
            return []

        # 📜 SAYFAYI ADIM ADIM KAYDIR
        print("📜 Sayfa adım adım taranıyor...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # 🔽 ADIM ADIM KAYDIRMA DÖNGÜSÜ
        for adim in range(150):
            driver.execute_script(f"window.scrollBy(0, {ADIM_KAYDIRMA_MIKTARI});")
            time.sleep(ADIMLAR_ARASI_BEKLEME)

            mac_satirlari = driver.find_elements(By.CSS_SELECTOR, "div.match-row")
            if not mac_satirlari: continue

            for satir in mac_satirlari:
                try:
                    # 📝 1. TAKIM İSİMLERİ
                    isimler = satir.find_elements(By.CSS_SELECTOR, "span.match-row__team-name-text")
                    if len(isimler) < 2: continue
                    ev_isim = isimler[0].text.strip()
                    dep_isim = isimler[1].text.strip()

                    kimlik = f"{akilli_isim_temizle(ev_isim)}-{akilli_isim_temizle(dep_isim)}"
                    if kimlik in gorulen or kimlik == "-": continue
                    gorulen.add(kimlik)

                    # 📊 2. ANA SKOR - Senin verdiğin sınıflar
                    s_ev = 0
                    s_dep = 0
                    try:
                        ev_skor_el = satir.find_element(By.CSS_SELECTOR, "span.match-row__score-home")
                        s_ev = rakam_bul(ev_skor_el.get_attribute("innerHTML"))
                    except: pass

                    try:
                        dep_skor_el = satir.find_element(By.CSS_SELECTOR, "span.match-row__score-away")
                        s_dep = rakam_bul(dep_skor_el.get_attribute("innerHTML"))
                    except: pass

                    # ⚽ 3. İLK YARI SKORU - Senin verdiğin sınıf
                    iy_ev = 0
                    iy_dep = 0
                    try:
                        iy_el = satir.find_element(By.CSS_SELECTOR, "div.match-row__half-time-score")
                        iy_metin = iy_el.text.strip()
                        rakamlar_iy = re.findall(r'\d+', iy_metin)
                        if len(rakamlar_iy) == 2:
                            iy_ev = int(rakamlar_iy[0])
                            iy_dep = int(rakamlar_iy[1])
                    except: pass

                    # 🟢 4. DURUM
                    durum = "baslamadi"
                    if s_ev > 0 or s_dep > 0:
                        durum = "bitti"
                    elif iy_ev > 0 or iy_dep > 0:
                        durum = "devam ediyor"

                    # ✅ KAYIT
                    skor_listesi.append({
                        "tarih": hedef_tarih_iso,
                        "ev_sahibi": ev_isim,
                        "deplasman": dep_isim,
                        "skor_ev": s_ev,
                        "skor_dep": s_dep,
                        "skor_1y_ev": iy_ev,
                        "skor_1y_dep": iy_dep,
                        "durum": durum
                    })
                    gecerli_sayisi += 1
                    print(f"✅ VERİ ALINDI | {gecerli_sayisi}. | {ev_isim} - {dep_isim} | MS:{s_ev}-{s_dep} | İY:{iy_ev}-{iy_dep}")

                except Exception:
                    continue

            # 🛑 SONA GELDİK Mİ?
            son_durum = driver.execute_script("return window.innerHeight + window.scrollY >= document.body.scrollHeight - 500;")
            if son_durum:
                print(f"🏁 Sayfa sonuna ulaşıldı. Adım: {adim+1}")
                break

    except Exception as ana_hata:
        print(f"❌ ÇEKİM HATASI: {ana_hata}")

    print(f"📅 {hedef_tarih_iso} Özeti: Alınan Veri: {gecerli_sayisi}")
    return skor_listesi

# =============================================================================
# 🧠 GÜNCELLEME MOTORU - ✅ ARTIK KESİNLİKLE GÜNCELLEME YAPAR
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

        en_uygun_eslesme = None
        en_yuksek_oran = 0

        # Mevcut listedeki her maçı kontrol et
        for i, mac in enumerate(mac_listesi):
            if i in eslesen_indexler: continue # Daha önce eşleşeni atla
            if not tarihi_esit_kabul_et(mac.get("tarih",""), y_tarih): continue # Tarih aynı değilse atla

            # İki ihtimali hesapla: Normal sıra / Ters sıra
            oran_normal = benzerlik_orani(mac["ev_sahibi"], y_ev) + benzerlik_orani(mac["deplasman"], y_dep)
            oran_ters = benzerlik_orani(mac["ev_sahibi"], y_dep) + benzerlik_orani(mac["deplasman"], y_ev)

            toplam_oran = max(oran_normal, oran_ters)

            # Eşleşme oranı yeterli ve şimdiki en iyisiyse kaydet
            if toplam_oran >= ESLESME_SEVIYESI * 2 and toplam_oran > en_yuksek_oran:
                en_yuksek_oran = toplam_oran
                en_uygun_eslesme = (i, (oran_ters > oran_normal)) # index, ters mi?

        # Eşleşme bulunduysa güncelle
        if en_uygun_eslesme:
            index, ters_mi = en_uygun_eslesme
            eslesen_indexler.add(index)

            mac = mac_listesi[index]

            # Verileri yerleştir (ters maçsa ev/deplasman değiştir)
            s_ev, s_dep = (y_veri["skor_ev"], y_veri["skor_dep"]) if not ters_mi else (y_veri["skor_dep"], y_veri["skor_ev"])
            iy_ev, iy_dep = (y_veri["skor_1y_ev"], y_veri["skor_1y_dep"]) if not ters_mi else (y_veri["skor_1y_dep"], y_veri["skor_1y_ev"])

            # ✅ ARTIK SKOR 0 BİLE OLSA GÜNCELLE - Önceki durum ne olursa olsun
            mac["skor_ev"] = s_ev
            mac["skor_dep"] = s_dep
            mac["skor_1y_ev"] = iy_ev
            mac["skor_1y_dep"] = iy_dep
            mac["durum"] = y_veri["durum"]

            guncelleme_sayisi += 1
            print(f"🔄 GÜNCELLEME BAŞARILI | DB: {mac['ev_sahibi']}-{mac['deplasman']} | Yeni: MS:{s_ev}-{s_dep} İY:{iy_ev}-{iy_dep}")

    return guncelleme_sayisi

# =============================================================================
# 🚀 ANA ÇALIŞTIRICI
# =============================================================================
if __name__ == "__main__":
    print("="*70)
    print("⚽ SON DÜZELTME | ✅ ARTIK KESİNLİKLE JSON GÜNCELLENİR | 🚀 OTOMATİK GİT")
    print("="*70)

    mevcut_yapi = load_mac_json()
    if not mevcut_yapi:
        print("❌ mac.json bulunamadı veya bozuk.")
        input("Çık...")
        exit()

    tarihler = tarihleri_olustur(BASLANGIC_TARIHI, BITIS_TARIHI)
    print(f"📅 İşlenecek Tarihler: {tarihler}")

    # Tarayıcı Ayarları
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

    tum_veriler = []

    try:
        # 🔄 Tüm tarihlerde döngü
        for gun_iso in tarihler:
            print(f"\n===================== {gun_iso} =====================")
            driver.get(BASE_LINK)
            time.sleep(SAYFA_YUKLEME_BEKLEME)
            gunluk_veri = get_skorlar_tek_gun(driver, gun_iso)
            tum_veriler.extend(gunluk_veri)

    except Exception as genel_hata:
        print(f"❌ GENEL HATA: {genel_hata}")
    finally:
        if driver:
            driver.quit()

    if not tum_veriler:
        print("❌ Hiç veri çekilemedi.")
        input("Çık...")
        exit()

    # 🧠 Eşleştir ve Güncelle
    print("\n🧠 EŞLEŞTİRME VE GÜNCELLEME BAŞLIYOR...")
    guncellenen = skorlari_eslestir_ve_guncelle(mevcut_yapi, tum_veriler)

    if guncellenen > 0:
        print(f"\n✅ TOPLAM {guncellenen} MAÇ BAŞARIYLA GÜNCELLENDİ.")
        save_mac_json(mevcut_yapi) # Dosyayı KESİNLİKLE kaydet
        git_islemlerini_yap()      # Git işlemlerini yap
    else:
        print("\n❌ HİÇBİR MAÇ GÜNCELLENEMEDİ! (Eşleşme bulunamadı)")
        print("ℹ️ Bu durum genellikle takım isimleri çok farklı yazıldığında olur. İsimleri manuel kontrol et.")

    input("🔚 Çıkmak için Enter...")