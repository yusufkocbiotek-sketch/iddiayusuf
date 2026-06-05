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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *

# =============================================================================
# & AYARLAR
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
BASE_LINK = "https://www.mackolik.com/futbol/canli-sonuclar"

# Tarih aralığı
BASLANGIC_TARIHI = "13/05/2026"
BITIS_TARIHI = "13/05/2026"

# Eşleştirme ayarları
ESLESME_SEVIYESI = 0.5  # %50 benzerlik yeterli
GIT_BRANCH_NAME = "main"

# Kurallar
KURAL_SKOR_KONTROL = True
KURAL_SIFIR_KONTROL = False
KURAL_TARIH_KESIN = True
MANTIK_HATASI_DUZELT = True

# Performans ayarları
SAYFA_YUKLEME_BEKLEME = 30
ADIM_KAYDIRMA_MIKTARI = 600
ADIMLAR_ARASI_BEKLEME = 1.5
GENEL_HATA_BEKLEME = 2

# Debug modu
DEBUG_MODU = False

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
        print("❌ Tarih formatı: GG/AA/YYYY (örn: 01/06/2026)")
        return []

    tarihler = []
    while baslangic <= bitis:
        tarihler.append(baslangic.strftime("%Y-%m-%d"))
        baslangic += datetime.timedelta(days=1)
    return tarihler

def tarihi_esit_kabul_et(t1, t2):
    if not t1 or not t2: 
        return False
    return str(t1).strip() == str(t2).strip()

# =============================================================================
# 🔐 İSİM TEMİZLEME VE BENZERLİK
# =============================================================================
def akilli_isim_temizle(isim):
    if not isim: 
        return ""
    
    isim = isim.lower().strip()
    
    tr_map = str.maketrans(
        "çğıöşüâêîôûáéíóúñðßçşğ",
        "cgiosuaeiouaeiounbscsg"
    )
    isim = isim.translate(tr_map)
    isim = re.sub(r'[^a-z\s]', '', isim)
    isim = re.sub(r'\s+', ' ', isim).strip()
    
    gereksiz = [
        'fk', 'sk', 'jk', 'bk', 'fc', 'as', 'spor', 'kulubu', 
        'kulübü', 'şportif', 'sport', 'clube', 'il', 'gk', 
        'üni', 'gençler', 'takımı'
    ]
    
    for ek in gereksiz:
        if isim.endswith(ek):
            isim = isim[:-len(ek)].strip()
        if isim.startswith(ek):
            isim = isim[len(ek):].strip()
    
    if len(isim) < 2:
        return ""
    
    return isim

def benzerlik_orani(a, b):
    if not a or not b:
        return 0.0
    
    a_temiz = akilli_isim_temizle(a)
    b_temiz = akilli_isim_temizle(b)
    
    if not a_temiz or not b_temiz:
        return 0.0
    
    if a_temiz == b_temiz:
        return 1.0
    
    if a_temiz in b_temiz or b_temiz in a_temiz:
        return 0.85
    
    if len(a_temiz) > 2 and len(b_temiz) > 2:
        if a_temiz[:3] == b_temiz[:3]:
            return 0.6
    
    return round(SequenceMatcher(None, a_temiz, b_temiz).ratio(), 2)

# =============================================================================
# 🚨 SKOR KONTROLÜ
# =============================================================================
def skor_mantikli_mi(ev, dep, iy_ev, iy_dep, durum, ev_isim="", dep_isim=""):
    if iy_ev > ev or iy_dep > dep:
        if MANTIK_HATASI_DUZELT:
            return True, f"! {ev_isim}-{dep_isim} | Veri geç geldi, kısmi kaydedildi", False
        else:
            return False, f"❌ HATA | {ev_isim}-{dep_isim} | İmkansız Skor", False
    
    return True, "✅ Geçerli Veri", True

# =============================================================================
# 📖 DOSYA İŞLEMLERİ
# =============================================================================
def load_mac_json():
    try:
        if not MAC_JSON_PATH.exists():
            print(f"⚠️ {MAC_JSON_PATH} bulunamadı, yeni dosya oluşturulacak")
            return {"matches": []}
        
        with open(MAC_JSON_PATH, 'r', encoding='utf-8') as f:
            veri = json.load(f)
        
        if isinstance(veri, dict) and "matches" in veri:
            print(f"📖 Mevcut Dosya Okundu | Toplam: {len(veri['matches'])} maç")
            return veri
        
        return {"matches": []}
    
    except Exception as e:
        print(f"❌ OKUMA HATASI: {e}")
        return {"matches": []}

def save_mac_json(veri):
    try:
        yedek = MAC_JSON_PATH.with_name("mac_json_yedek.json")
        with open(yedek, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        
        with open(MAC_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2, default=str)
        
        print("💾 GÜNCEL DOSYA KAYDEDİLDİ ✅")
        return True
    
    except Exception as e:
        print(f"❌ KAYDETME HATASI: {e}")
        return False

def git_islemlerini_yap():
    try:
        print("\n🔄 GİT İŞLEMLERİ BAŞLATILIYOR...")
        os.chdir(BASE_DIR)
        
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        print("✅ git add .")
        
        tarih_saat = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        commit_mesaji = f"[OTOMATİK] | {tarih_saat} | Maç Sonuçları Güncellendi"
        subprocess.run(["git", "commit", "-m", commit_mesaji], check=True, capture_output=True)
        print("✅ git commit")
        
        subprocess.run(["git", "push", "origin", GIT_BRANCH_NAME], check=True, capture_output=True)
        print(f"✅ git push origin {GIT_BRANCH_NAME}")
        print("🚀 Tüm Git işlemleri tamamlandı!")
        return True
        
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in str(e.stderr):
            print("! Git: Değişiklik yok, gönderilecek bir şey yok")
        else:
            print(f"⚠️ GİT HATA: {e}")
        return False
    
    except Exception as e:
        print(f"⚠️ GİT GENEL HATA: {e}")
        return False

# =============================================================================
# 🛠️ YARDIMCI FONKSİYONLAR
# =============================================================================
def rakam_bul(text):
    if not text:
        return 0
    rakamlar = re.findall(r'\d+', str(text))
    return int(rakamlar[0]) if rakamlar else 0

def debug_sayfa_kaydet(driver, gun_iso):
    if not DEBUG_MODU:
        return
    
    try:
        dosya_adi = f"debug_{gun_iso}.html"
        with open(dosya_adi, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"🔍 DEBUG: {dosya_adi} kaydedildi")
    except:
        pass

def maç_satirlarini_bul(driver):
    """Maç satırlarını bulmak için birkaç farklı yöntem dener"""
    satirlar = []
    
    try:
        satirlar = driver.find_elements(By.CSS_SELECTOR, "div.match-row")
        if satirlar:
            print(f"✅ Yöntem 1: {len(satirlar)} match-row bulundu")
            return satirlar
    except:
        pass
    
    try:
        satirlar = driver.find_elements(By.CSS_SELECTOR, "div[class*='match']")
        if satirlar:
            print(f"✅ Yöntem 2: {len(satirlar)} 'match' içeren div bulundu")
            return satirlar
    except:
        pass
    
    try:
        tum_divler = driver.find_elements(By.TAG_NAME, "div")
        for div in tum_divler:
            try:
                isimler = div.find_elements(By.CSS_SELECTOR, "span.match-row__team-name-text")
                if len(isimler) >= 2:
                    satirlar.append(div)
            except:
                continue
        
        if satirlar:
            print(f"✅ Yöntem 3: {len(satirlar)} potansiyel maç satırı bulundu")
            return satirlar
    except:
        pass
    
    try:
        satirlar = driver.find_elements(By.XPATH, "//div[contains(@class, 'match') or contains(@data-testid, 'match')]")
        if satirlar:
            print(f"✅ Yöntem 4: {len(satirlar)} data attribute ile bulundu")
            return satirlar
    except:
        pass
    
    print("⚠️ Hiçbir yöntemle maç satırı bulunamadı!")
    return []

# =============================================================================
# 📅 TAKVİM NAVİGASYONU - AY GÖSTERGESİNE TIKLAMA
# =============================================================================
def takvimde_gezin(driver, hedef_tarih_iso):
    """
    Takvimde hedef tarihe gider
    1. Takvimi aç
    2. widget-datepicker__value elementine tıklayarak aylara git
    3. Hedef tarihi seç
    """
    print(f"   🔧 Takvim navigasyonu: {hedef_tarih_iso}")
    
    try:
        # 1️⃣ TAKVİMİ AÇ
        print("   📍 Takvim butonu aranıyor...")
        takvim_buton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "widget-dateslider__datepicker-toggle"))
        )
        driver.execute_script("arguments[0].click();", takvim_buton)
        print("   ✅ Takvim açıldı")
        time.sleep(2)
        
        # 2️⃣ AY GÖSTERGESİNE TIKLA (widget-datepicker__value)
        print("   📍 Ay göstergesine tıklanıyor...")
        
        ay_gostergesi = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "widget-datepicker__value"))
        )
        
        # Mevcut ayı oku
        mevcut_ay_metni = ay_gostergesi.text.strip()
        print(f"   📍 Mevcut ay: {mevcut_ay_metni}")
        
        # Hedef ayı hesapla
        hedef_yil, hedef_ay, hedef_gun = map(int, hedef_tarih_iso.split('-'))
        
        # Ay isimleri (İngilizce)
        ay_isimleri = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        hedef_ay_ismi = ay_isimleri[hedef_ay - 1]
        
        # Mevcut ayın index'ini bul
        mevcut_ay_index = -1
        for i, ay in enumerate(ay_isimleri):
            if mevcut_ay_metni == ay:
                mevcut_ay_index = i
                break
        
        hedef_ay_index = hedef_ay - 1
        print(f"   📍 Hedef ay: {hedef_ay_ismi} (index: {hedef_ay_index})")
        
        # Hedef aya ulaşana kadar tıkla
        tiklama_sayisi = 0
        max_tiklama = 12
        
        while tiklama_sayisi < max_tiklama:
            # Mevcut ay hedef ay mı?
            if mevcut_ay_metni == hedef_ay_ismi:
                print(f"   ✅ Hedef aya ulaşıldı: {mevcut_ay_metni} (tiklama: {tiklama_sayisi})")
                break
            
            # Tıkla
            ay_gostergesi = driver.find_element(By.CLASS_NAME, "widget-datepicker__value")
            driver.execute_script("arguments[0].click();", ay_gostergesi)
            tiklama_sayisi += 1
            time.sleep(1.5)
            
            # Yeni ayı oku
            ay_gostergesi = driver.find_element(By.CLASS_NAME, "widget-datepicker__value")
            mevcut_ay_metni = ay_gostergesi.text.strip()
            print(f"   📍 Tıklama {tiklama_sayisi}: {mevcut_ay_metni}")
        else:
            print(f"   ⚠️ Hedef aya ulaşılamadı (max {max_tiklama} tıklama)")
            print(f"      Mevcut: {mevcut_ay_metni}, Hedef: {hedef_ay_ismi}")
            return False
        
        # 3️⃣ HEDEF TARİHİ SEÇ
        print(f"   📍 Hedef tarih seçiliyor: {hedef_tarih_iso}")
        
        try:
            tarih_secici = f'td.widget-datepicker__calendar-body-cell[data-date="{hedef_tarih_iso}"]'
            tarih_elemani = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, tarih_secici))
            )
            
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tarih_elemani)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", tarih_elemani)
            
            print(f"   ✅ TARİH SEÇİLDİ: {hedef_tarih_iso}")
            time.sleep(12)
            
            return True
            
        except Exception as e:
            print(f"   ❌ TARİH SEÇİLEMEDİ: {e}")
            print(f"      Aranan: {tarih_secici}")
            
            try:
                tum_tarihler = driver.find_elements(By.CSS_SELECTOR, "td.widget-datepicker__calendar-body-cell")
                print(f"      Takvimde bulunan tarihler ({len(tum_tarihler)} tane):")
                for t in tum_tarihler[:15]:
                    date_attr = t.get_attribute("data-date")
                    text = t.text.strip()
                    if date_attr:
                        print(f"         - {date_attr} (görünen: {text})")
            except:
                pass
            
            return False
            
    except Exception as e:
        print(f"   ❌ TAKVİM HATASI: {e}")
        import traceback
        traceback.print_exc()
        return False

# =============================================================================
# 🌐 ANA ÇEKİM FONKSİYONU
# =============================================================================
def get_skorlar_tek_gun(driver, hedef_tarih_iso):
    print(f"\n{'='*70}")
    print(f"📅 İŞLENİYOR: {hedef_tarih_iso}")
    print(f"{'='*70}")
    
    skor_listesi = []
    gorulen = set()
    gecerli_sayisi = 0
    
    try:
        # ═══════════════════════════════════════════════════════════
        # 1️⃣ TAKVİM NAVİGASYONU
        # ═══════════════════════════════════════════════════════════
        print("🔧 [1/4] Takvim navigasyonu yapılıyor...")
        
        basarili = takvimde_gezin(driver, hedef_tarih_iso)
        if not basarili:
            print("❌ Takvim navigasyonu başarısız, bu gün atlanıyor")
            return []
        
        # Debug kaydet
        debug_sayfa_kaydet(driver, hedef_tarih_iso)
        
        # ═══════════════════════════════════════════════════════════
        # 2️⃣ SAYFAYI KAYDIRMA VE VERİ TOPLAMA
        # ═══════════════════════════════════════════════════════════
        print("🔧 [2/4] Sayfa kaydırılıyor ve veri toplanıyor...")
        
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(3)
        
        max_adim = 200
        
        for adim in range(max_adim):
            driver.execute_script(f"window.scrollBy(0, {ADIM_KAYDIRMA_MIKTARI});")
            time.sleep(ADIMLAR_ARASI_BEKLEME)
            
            mac_satirlari = maç_satirlarini_bul(driver)
            
            if not mac_satirlari:
                if adim % 20 == 0:
                    print(f"   📍 Adım {adim+1}/{max_adim} - Henüz maç yok...")
                continue
            
            if adim % 20 == 0:
                print(f"   📍 Adım {adim+1}/{max_adim} - {len(mac_satirlari)} satır bulundu")
            
            for satir in mac_satirlari:
                try:
                    # ─── TAKIM İSİMLERİ ───
                    isimler = satir.find_elements(By.CSS_SELECTOR, "span.match-row__team-name-text")
                    
                    if len(isimler) < 2:
                        try:
                            isimler = satir.find_elements(By.CSS_SELECTOR, "span[class*='team-name']")
                        except:
                            continue
                    
                    if len(isimler) < 2:
                        continue
                    
                    ev_isim = isimler[0].text.strip()
                    dep_isim = isimler[1].text.strip()
                    
                    if not ev_isim or not dep_isim or ev_isim == dep_isim:
                        continue
                    
                    kimlik = f"{akilli_isim_temizle(ev_isim)}-{akilli_isim_temizle(dep_isim)}"
                    if kimlik in gorulen or kimlik == "-":
                        continue
                    gorulen.add(kimlik)
                    
                    # ─── ANA SKOR ───
                    s_ev, s_dep = 0, 0
                    
                    try:
                        ev_skor = satir.find_element(By.CSS_SELECTOR, "span.match-row__score-home")
                        s_ev = rakam_bul(ev_skor.get_attribute("innerHTML"))
                    except: pass
                    
                    try:
                        dep_skor = satir.find_element(By.CSS_SELECTOR, "span.match-row__score-away")
                        s_dep = rakam_bul(dep_skor.get_attribute("innerHTML"))
                    except: pass
                    
                    if s_ev == 0 or s_dep == 0:
                        try:
                            skor_linki = satir.find_element(By.CSS_SELECTOR, "a.match-row__score")
                            tum_spanlar = skor_linki.find_elements(By.TAG_NAME, "span")
                            if len(tum_spanlar) >= 2:
                                s_ev = rakam_bul(tum_spanlar[0].get_attribute("innerHTML"))
                                s_dep = rakam_bul(tum_spanlar[1].get_attribute("innerHTML"))
                        except: pass
                    
                    if s_ev == 0 or s_dep == 0:
                        try:
                            tum_skorlar = satir.find_elements(By.CSS_SELECTOR, "span[class*='score']")
                            if len(tum_skorlar) >= 2:
                                s_ev = rakam_bul(tum_skorlar[0].text)
                                s_dep = rakam_bul(tum_skorlar[1].text)
                        except: pass
                    
                    # ─── İLK YARI SKORU ───
                    iy_ev, iy_dep = 0, 0
                    
                    try:
                        iy_el = satir.find_element(By.CSS_SELECTOR, "div.match-row__half-time-score")
                        iy_metin = iy_el.text.strip()
                        rakamlar_iy = re.findall(r'\d+', iy_metin)
                        if len(rakamlar_iy) == 2:
                            iy_ev = int(rakamlar_iy[0])
                            iy_dep = int(rakamlar_iy[1])
                    except: pass
                    
                    # ─── DURUM ───
                    durum = "baslamadi"
                    if s_ev > 0 or s_dep > 0:
                        durum = "bitti"
                    elif iy_ev > 0 or iy_dep > 0:
                        durum = "devam ediyor"
                    
                    # ─── SKOR KONTROLÜ ───
                    mantik_ok, mesaj, skor_gecerli = skor_mantikli_mi(
                        s_ev, s_dep, iy_ev, iy_dep, durum, ev_isim, dep_isim
                    )
                    
                    if not skor_gecerli and KURAL_SKOR_KONTROL:
                        print(f"⚠️ {mesaj}")
                        continue
                    
                    # ─── KAYIT ───
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
                    print(f"   ✅ [{gecerli_sayisi}] {ev_isim} - {dep_isim} | MS:{s_ev}-{s_dep} | İY:{iy_ev}-{iy_dep} | {durum}")
                    
                except Exception as e:
                    continue
            
            # ─── SON KONTROL ───
            try:
                son_durum = driver.execute_script(
                    "return window.innerHeight + window.scrollY >= document.body.scrollHeight - 500;"
                )
                if son_durum:
                    print(f"🏁 Sayfa sonuna ulaşıldı! (Adım: {adim+1})")
                    break
            except:
                pass
        
        print(f"\n📊 {hedef_tarih_iso} ÖZET:")
        print(f"   • Toplam veri: {len(skor_listesi)}")
        print(f"   • Geçerli veri: {gecerli_sayisi}")
        
    except Exception as e:
        print(f"❌ ÇEKİM HATASI: {e}")
        import traceback
        traceback.print_exc()
    
    return skor_listesi

# =============================================================================
# 🧠 AKILLI GÜNCELLEME MOTORU - ÜZERİNE YAZMA
# =============================================================================
def skorlari_eslestir_ve_guncelle(mevcut_yapi, tum_veriler):
    """
    Yeni verileri mevcut verilerle eşleştirir ve GÜNCELLER
    
    Strateji:
    1. Önce TAM EŞLEŞME dene (tarih + takım ismi aynı)
    2. Sonra BENZER EŞLEŞME dene (tarih aynı, takım benzer)
    3. Hala bulamazsa YENİ EKLE
    """
    mac_listesi = mevcut_yapi.get("matches", [])
    
    if not mac_listesi:
        print("⚠️ Mevcut yapıda maç bulunamadı! Hepsi yeni eklenecek")
        mevcut_yapi["matches"] = tum_veriler
        return len(tum_veriler)
    
    if not tum_veriler:
        print("⚠️ Güncellenecek veri bulunamadı!")
        return 0
    
    print(f"\n🧠 AKILLI GÜNCELLEME BAŞLIYOR...")
    print(f"   • Mevcut maç sayısı: {len(mac_listesi)}")
    print(f"   • Yeni veri sayısı: {len(tum_veriler)}")
    
    guncellenen = 0
    eklenen = 0
    atlanan = 0
    
    # Her yeni veri için en iyi eşleşmeyi bul
    for y_veri in tum_veriler:
        y_tarih = y_veri["tarih"]
        y_ev = y_veri["ev_sahibi"]
        y_dep = y_veri["deplasman"]
        
        en_uygun_eslesme = None
        en_yuksek_oran = 0
        eslesme_tipi = ""
        
        # ═══════════════════════════════════════════════════
        # 1️⃣ ÖNCE TAM EŞLEŞME DENE
        # ═══════════════════════════════════════════════════
        for i, mac in enumerate(mac_listesi):
            if mac is None:
                continue
            
            m_tarih = mac.get("tarih", "")
            m_ev = mac.get("ev_sahibi", "")
            m_dep = mac.get("deplasman", "")
            
            # Tarih aynı mı?
            if not tarihi_esit_kabul_et(m_tarih, y_tarih):
                continue
            
            # Takım isimleri TAM AYNI mi?
            akilli_y_ev = akilli_isim_temizle(y_ev)
            akilli_y_dep = akilli_isim_temizle(y_dep)
            akilli_m_ev = akilli_isim_temizle(m_ev)
            akilli_m_dep = akilli_isim_temizle(m_dep)
            
            if akilli_y_ev == akilli_m_ev and akilli_y_dep == akilli_m_dep:
                en_uygun_eslesme = (i, False)
                en_yuksek_oran = 1.0
                eslesme_tipi = "tam"
                break
            
            # Ters eşleşme kontrolü
            if akilli_y_ev == akilli_m_dep and akilli_y_dep == akilli_m_ev:
                en_uygun_eslesme = (i, True)
                en_yuksek_oran = 1.0
                eslesme_tipi = "tam_ters"
                break
        
        # ═══════════════════════════════════════════════════
        # 2️⃣ TAM BULUNAMADI → BENZER EŞLEŞME DENE
        # ═══════════════════════════════════════════════════
        if not en_uygun_eslesme:
            for i, mac in enumerate(mac_listesi):
                if mac is None:
                    continue
                
                m_tarih = mac.get("tarih", "")
                if not tarihi_esit_kabul_et(m_tarih, y_tarih):
                    continue
                
                akilli_m_ev = akilli_isim_temizle(mac.get("ev_sahibi", ""))
                akilli_m_dep = akilli_isim_temizle(mac.get("deplasman", ""))
                
                oran_normal = (
                    benzerlik_orani(akilli_m_ev, akilli_isim_temizle(y_ev)) + 
                    benzerlik_orani(akilli_m_dep, akilli_isim_temizle(y_dep))
                )
                
                oran_ters = (
                    benzerlik_orani(akilli_m_ev, akilli_isim_temizle(y_dep)) + 
                    benzerlik_orani(akilli_m_dep, akilli_isim_temizle(y_ev))
                )
                
                toplam_oran = max(oran_normal, oran_ters)
                
                if toplam_oran >= ESLESME_SEVIYESI and toplam_oran > en_yuksek_oran:
                    en_yuksek_oran = toplam_oran
                    en_uygun_eslesme = (i, oran_ters > oran_normal)
                    eslesme_tipi = f"benzer_{toplam_oran:.2f}"
        
        # ═══════════════════════════════════════════════════
        # 3️⃣ HALA BULUNAMADI → SADECE TARİH İLE EŞLEŞTİR
        # ═══════════════════════════════════════════════════
        if not en_uygun_eslesme:
            ayni_tarih_maclari = [
                i for i, mac in enumerate(mac_listesi) 
                if mac and tarihi_esit_kabul_et(mac.get("tarih", ""), y_tarih)
            ]
            
            if len(ayni_tarih_maclari) == 1:
                en_uygun_eslesme = (ayni_tarih_maclari[0], False)
                en_yuksek_oran = 0.3
                eslesme_tipi = "tarih_only"
        
        # ═══════════════════════════════════════════════════
        # 4️⃣ EŞLEŞME BULUNDU → GÜNCELLE (ÜZERİNE YAZ!)
        # ═══════════════════════════════════════════════════
        if en_uygun_eslesme:
            index, ters_mi = en_uygun_eslesme
            mac = mac_listesi[index]
            
            if not ters_mi:
                s_ev, s_dep = y_veri["skor_ev"], y_veri["skor_dep"]
                iy_ev, iy_dep = y_veri["skor_1y_ev"], y_veri["skor_1y_dep"]
            else:
                s_ev, s_dep = y_veri["skor_dep"], y_veri["skor_ev"]
                iy_ev, iy_dep = y_veri["skor_1y_dep"], y_veri["skor_1y_ev"]
            
            # Eski verileri göster
            eski_ms = f"{mac.get('skor_ev', 0)}-{mac.get('skor_dep', 0)}"
            eski_iy = f"{mac.get('skor_1y_ev', 0)}-{mac.get('skor_1y_dep', 0)}"
            
            # ✅ ÜZERİNE YAZ!
            mac["skor_ev"] = s_ev
            mac["skor_dep"] = s_dep
            mac["skor_1y_ev"] = iy_ev
            mac["skor_1y_dep"] = iy_dep
            mac["durum"] = y_veri["durum"]
            
            guncellenen += 1
            
            if eslesme_tipi == "tam":
                print(f"   ✅ [GÜNCELLEME] {mac['ev_sahibi'][:25]:25s} - {mac['deplasman'][:25]:25s}")
                print(f"      MS: {eski_ms} → {s_ev}-{s_dep} | İY: {eski_iy} → {iy_ev}-{iy_dep}")
            elif eslesme_tipi == "benzer":
                print(f"   🔄 [BENZER] {mac['ev_sahibi'][:25]:25s} - {mac['deplasman'][:25]:25s} (oran:{en_yuksek_oran:.2f})")
                print(f"      MS: {eski_ms} → {s_ev}-{s_dep} | İY: {eski_iy} → {iy_ev}-{iy_dep}")
            else:
                print(f"   📝 [{eslesme_tipi}] {mac['ev_sahibi'][:25]:25s} - {mac['deplasman'][:25]:25s}")
                print(f"      MS: {eski_ms} → {s_ev}-{s_dep} | İY: {eski_iy} → {iy_ev}-{iy_dep}")
        
        # ═══════════════════════════════════════════════════
        # 5️⃣ EŞLEŞME BULUNAMADI → YENİ EKLE
        # ═══════════════════════════════════════════════════
        else:
            mac_listesi.append(y_veri)
            eklenen += 1
            print(f"   ➕ [YENİ] {y_ev[:25]:25s} - {y_dep[:25]:25s} | MS:{y_veri['skor_ev']}-{y_veri['skor_dep']}")
    
    print(f"\n📊 GÜNCELLEME SONUÇLARI:")
    print(f"   ✅ Güncellenen: {guncellenen}")
    print(f"   ➕ Eklenen: {eklenen}")
    print(f"   📦 Toplam maç: {len(mac_listesi)}")
    
    return guncellenen

# =============================================================================
# 🚀 ANA ÇALIŞTIRICI
# =============================================================================
if __name__ == "__main__":
    print("="*70)
    print("⚽ MACKOLİK SCORE SCRAPER - AKILLI GÜNCELLEME MOTORU")
    print("="*70)
    print(f"📅 Tarih Aralığı: {BASLANGIC_TARIHI} - {BITIS_TARIHI}")
    print(f"🔄 Eşleşme Seviyesi: {ESLESME_SEVIYESI}")
    print(f"📦 JSON Dosyası: {MAC_JSON_PATH}")
    print("="*70)
    
    mevcut_yapi = load_mac_json()
    if not mevcut_yapi:
        print("❌ mac.json bulunamadı veya bozuk!")
        input("Çıkmak için Enter'a basın...")
        exit()
    
    tarihler = tarihleri_olustur(BASLANGIC_TARIHI, BITIS_TARIHI)
    if not tarihler:
        print("❌ Geçersiz tarih aralığı!")
        input("Çıkmak için Enter'a basın...")
        exit()
    
    print(f"\n📅 İşlenecek {len(tarihler)} gün:")
    for t in tarihler:
        print(f"   • {t}")
    
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    try:
        print("\n🚀 TARAYICI BAŞLATILIYOR...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✅ Tarayıcı hazır!")
        
        tum_veriler = []
        
        for gun_iso in tarihler:
            try:
                print(f"\n{'#'*70}")
                print(f"# 📅 GÜN: {gun_iso}")
                print(f"{'#'*70}")
                
                driver.get(BASE_LINK)
                time.sleep(SAYFA_YUKLEME_BEKLEME)
                
                sayfa_kaynagi = driver.page_source
                if "match-row" in sayfa_kaynagi:
                    print("✅ match-row sınıfı sayfada bulundu")
                else:
                    print("⚠️ UYARI: match-row sınıfı bulunamadı!")
                
                gunluk_veri = get_skorlar_tek_gun(driver, gun_iso)
                tum_veriler.extend(gunluk_veri)
                
                print(f"\n📊 {gun_iso} SONUÇ: {len(gunluk_veri)} veri çekildi")
                
            except Exception as gun_hatasi:
                print(f"❌ {gun_iso} işlenirken hata: {gun_hatasi}")
                import traceback
                traceback.print_exc()
                continue
        
    except Exception as genel_hata:
        print(f"❌ GENEL HATA: {genel_hata}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'driver' in locals():
            try:
                driver.quit()
                print("\n✅ Tarayıcı kapatıldı")
            except:
                pass
    
    if not tum_veriler:
        print("\n" + "="*70)
        print("❌ HİÇ VERİ ÇEKİLEMEDİ!")
        print("="*70)
        print("\n⚠️ Olası nedenler:")
        print("   1. İnternet bağlantısı sorunu")
        print("   2. mackolik.com engelledi")
        print("   3. Sayfa yapısı tamamen değişti")
        print("   4. Tarih aralığında maç yok")
        print("\n💡 Çözüm önerileri:")
        print("   • DEBUG_MODU = True yapıp tekrar deneyin")
        print("   • Tarayıcıyı manuel açıp siteye girin")
        print("   • Chrome sürümünüzü güncelleyin")
        input("\nÇıkmak için Enter'a basın...")
        exit()
    
    print("\n" + "="*70)
    print(f"📊 TOPLAM VERİ: {len(tum_veriler)} maç çekildi")
    print("="*70)
    
    print("\n🧠 GÜNCELLEME BAŞLIYOR...")
    guncellenen = skorlari_eslestir_ve_guncelle(mevcut_yapi, tum_veriler)
    
    if guncellenen > 0:
        print(f"\n✅ {guncellenen} MAÇ BAŞARIYLA GÜNCELLENDİ!")
        
        if save_mac_json(mevcut_yapi):
            git_islemlerini_yap()
        else:
            print("⚠️ JSON kaydedilemedi, Git atlandı")
    else:
        print("\n❌ HİÇBİR MAÇ GÜNCELLENEMEDİ!")
        print("\n💡 Olası nedenler:")
        print("   • Takım isimleri çok farklı yazılmış")
        print("   • Tarih formatı uyuşmuyor")
        print("   • Eşleşme seviyesi çok düşük/yüksek")
        print("\n💡 Çözüm:")
        print("   • ESLESME_SEVIYESI değerini değiştirin (0.1 - 0.5 arası)")
        print("   • DEBUG_MODU = True yapıp debug dosyalarını inceleyin")
    
    print("\n" + "="*70)
    input("✅ İŞLEM TAMAMLANDI - Çıkmak için Enter'a basın...")