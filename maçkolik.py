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
from selenium.common.exceptions import *

# =============================================================================
# & AYARLAR
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
BASE_LINK = "https://www.mackolik.com/futbol/canli-sonuclar"

# Tarih aralığı
BASLANGIC_TARIHI = "10/05/2026"
BITIS_TARIHI = "01/06/2026"

# Eşleştirme ayarları
ESLESME_SEVIYESI = 0.25
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

# Debug modu (True yaparsan HTML kaydeder)
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
    
    # Türkçe karakter dönüşümü
    tr_map = str.maketrans(
        "çğıöşüâêîôûáéíóúñðßçşğ",
        "cgiosuaeiouaeiounbscsg"
    )
    isim = isim.translate(tr_map)
    
    # Sadece harf ve boşluk bırak
    isim = re.sub(r'[^a-z\s]', '', isim)
    isim = re.sub(r'\s+', ' ', isim).strip()
    
    # Gereksiz ekleri temizle
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
    
    # Tam eşleşme
    if a_temiz == b_temiz:
        return 1.0
    
    # Biri diğerinin içinde mi?
    if a_temiz in b_temiz or b_temiz in a_temiz:
        return 0.85
    
    # İlk 3 harf eşleşiyor mu?
    if len(a_temiz) > 2 and len(b_temiz) > 2:
        if a_temiz[:3] == b_temiz[:3]:
            return 0.6
    
    # Genel benzerlik
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
        # Yedek oluştur
        yedek = MAC_JSON_PATH.with_name("mac_json_yedek.json")
        with open(yedek, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        
        # Ana dosyayı kaydet
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
        
        # Değişiklikleri ekle
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        print("✅ git add .")
        
        # Commit
        tarih_saat = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        commit_mesaji = f"[OTOMATİK] | {tarih_saat} | Maç Sonuçları Güncellendi"
        subprocess.run(["git", "commit", "-m", commit_mesaji], check=True, capture_output=True)
        print("✅ git commit")
        
        # Push
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
    """Debug için sayfa yapısını kaydeder"""
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
    """
    Maç satırlarını bulmak için birkaç farklı yöntem dener
    Returns: list of WebElement
    """
    satirlar = []
    
    # Yöntem 1: match-row class'ı
    try:
        satirlar = driver.find_elements(By.CSS_SELECTOR, "div.match-row")
        if satirlar:
            print(f"✅ Yöntem 1: {len(satirlar)} match-row bulundu")
            return satirlar
    except:
        pass
    
    # Yöntem 2: match içeren class'lar
    try:
        satirlar = driver.find_elements(By.CSS_SELECTOR, "div[class*='match']")
        if satirlar:
            print(f"✅ Yöntem 2: {len(satirlar)} 'match' içeren div bulundu")
            return satirlar
    except:
        pass
    
    # Yöntem 3: Takım ismi içeren yapıyı bul
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
    
    # Yöntem 4: data-testid veya benzeri attribute'lar
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
        # 1️⃣ TAKVİM AÇMA
        # ═══════════════════════════════════════════════════════════
        print("🔧 [1/5] Takvim açılıyor...")
        
        try:
            takvim_buton = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "widget-dateslider__datepicker-toggle"))
            )
            driver.execute_script("arguments[0].click();", takvim_buton)
            print("✅ Takvim açıldı")
            time.sleep(2)
        except Exception as e:
            print(f"❌ TAKVİM HATA: {e}")
            return []
        
        # ═══════════════════════════════════════════════════════════
        # 2️⃣ TARİH SEÇME
        # ═══════════════════════════════════════════════════════════
        print(f"🔧 [2/5] Tarih seçiliyor: {hedef_tarih_iso}")
        
        try:
            secici = f'td.widget-datepicker__calendar-body-cell[data-date="{hedef_tarih_iso}"]'
            tarih_elemani = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, secici))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tarih_elemani)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", tarih_elemani)
            print(f"✅ TARİH SEÇİLDİ: {hedef_tarih_iso}")
            time.sleep(15)  # Sayfanın yüklenmesi için uzun bekle
        except Exception as e:
            print(f"❌ TARİH SEÇİLEMEDİ: {e}")
            return []
        
        # Debug kaydet
        debug_sayfa_kaydet(driver, hedef_tarih_iso)
        
        # ═══════════════════════════════════════════════════════════
        # 3️⃣ SAYFAYI KAYDIRMA VE VERİ TOPLAMA
        # ═══════════════════════════════════════════════════════════
        print("🔧 [3/5] Sayfa kaydırılıyor ve veri toplanıyor...")
        
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(3)
        
        # Toplam kaç adım kaydıracağız
        max_adim = 200
        
        for adim in range(max_adim):
            # Kaydır
            driver.execute_script(f"window.scrollBy(0, {ADIM_KAYDIRMA_MIKTARI});")
            time.sleep(ADIMLAR_ARASI_BEKLEME)
            
            # Maç satırlarını bul
            mac_satirlari = maç_satirlarini_bul(driver)
            
            if not mac_satirlari:
                if adim % 20 == 0:  # Her 20 adımda bir durum yazdır
                    print(f"   📍 Adım {adim+1}/{max_adim} - Henüz maç yok...")
                continue
            
            # Her 20 adımda bir bilgi ver
            if adim % 20 == 0:
                print(f"   📍 Adım {adim+1}/{max_adim} - {len(mac_satirlari)} satır bulundu")
            
            # Her satırı işle
            for satir in mac_satirlari:
                try:
                    # ─── TAKIM İSİMLERİ ───
                    isimler = satir.find_elements(By.CSS_SELECTOR, "span.match-row__team-name-text")
                    
                    if len(isimler) < 2:
                        # Alternatif selector dene
                        try:
                            isimler = satir.find_elements(By.CSS_SELECTOR, "span[class*='team-name']")
                        except:
                            continue
                    
                    if len(isimler) < 2:
                        continue
                    
                    ev_isim = isimler[0].text.strip()
                    dep_isim = isimler[1].text.strip()
                    
                    # Boş isim kontrolü
                    if not ev_isim or not dep_isim or ev_isim == dep_isim:
                        continue
                    
                    # Daha önce görüldü mü?
                    kimlik = f"{akilli_isim_temizle(ev_isim)}-{akilli_isim_temizle(dep_isim)}"
                    if kimlik in gorulen or kimlik == "-":
                        continue
                    gorulen.add(kimlik)
                    
                    # ─── ANA SKOR ───
                    s_ev, s_dep = 0, 0
                    
                    # Yöntem 1: Direct span selector
                    try:
                        ev_skor = satir.find_element(By.CSS_SELECTOR, "span.match-row__score-home")
                        s_ev = rakam_bul(ev_skor.get_attribute("innerHTML"))
                    except: pass
                    
                    try:
                        dep_skor = satir.find_element(By.CSS_SELECTOR, "span.match-row__score-away")
                        s_dep = rakam_bul(dep_skor.get_attribute("innerHTML"))
                    except: pass
                    
                    # Yöntem 2: Link içindeki span'ler
                    if s_ev == 0 or s_dep == 0:
                        try:
                            skor_linki = satir.find_element(By.CSS_SELECTOR, "a.match-row__score")
                            tum_spanlar = skor_linki.find_elements(By.TAG_NAME, "span")
                            if len(tum_spanlar) >= 2:
                                s_ev = rakam_bul(tum_spanlar[0].get_attribute("innerHTML"))
                                s_dep = rakam_bul(tum_spanlar[1].get_attribute("innerHTML"))
                        except: pass
                    
                    # Yöntem 3: Genel score span'leri
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
                    # Hata olsa bile devam et
                    continue
            
            # ─── SON KONTROL: Sayfa sonuna geldik mi? ───
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
# 🧠 GÜNCELLEME MOTORU
# =============================================================================
def skorlari_eslestir_ve_guncelle(mevcut_yapi, tum_veriler):
    mac_listesi = mevcut_yapi.get("matches", [])
    
    if not mac_listesi:
        print("⚠️ Mevcut yapıda maç bulunamadı!")
        return 0
    
    if not tum_veriler:
        print("⚠️ Güncellenecek veri bulunamadı!")
        return 0
    
    print(f"\n🧠 EŞLEŞTİRME BAŞLIYOR...")
    print(f"   • Mevcut maç sayısı: {len(mac_listesi)}")
    print(f"   • Yeni veri sayısı: {len(tum_veriler)}")
    
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
            # Daha önce eşleşeni atla
            if i in eslesen_indexler:
                continue
            
            # Tarih aynı mı?
            if not tarihi_esit_kabul_et(mac.get("tarih", ""), y_tarih):
                continue
            
            # Benzerlik hesapla (normal ve ters sıra)
            oran_normal = (
                benzerlik_orani(mac["ev_sahibi"], y_ev) + 
                benzerlik_orani(mac["deplasman"], y_dep)
            )
            
            oran_ters = (
                benzerlik_orani(mac["ev_sahibi"], y_dep) + 
                benzerlik_orani(mac["deplasman"], y_ev)
            )
            
            toplam_oran = max(oran_normal, oran_ters)
            
            # Eşleşme yeterli mi?
            if toplam_oran >= ESLESME_SEVIYESI * 2 and toplam_oran > en_yuksek_oran:
                en_yuksek_oran = toplam_oran
                en_uygun_eslesme = (i, oran_ters > oran_normal)
        
        # Eşleşme bulunduysa güncelle
        if en_uygun_eslesme:
            index, ters_mi = en_uygun_eslesme
            eslesen_indexler.add(index)
            
            mac = mac_listesi[index]
            
            # Verileri yerleştir (ters maçsa ev/deplasman değiştir)
            if not ters_mi:
                s_ev, s_dep = y_veri["skor_ev"], y_veri["skor_dep"]
                iy_ev, iy_dep = y_veri["skor_1y_ev"], y_veri["skor_1y_dep"]
            else:
                s_ev, s_dep = y_veri["skor_dep"], y_veri["skor_ev"]
                iy_ev, iy_dep = y_veri["skor_1y_dep"], y_veri["skor_1y_ev"]
            
            # ✅ SKOR 0 BİLE OLSA GÜNCELLE
            mac["skor_ev"] = s_ev
            mac["skor_dep"] = s_dep
            mac["skor_1y_ev"] = iy_ev
            mac["skor_1y_dep"] = iy_dep
            mac["durum"] = y_veri["durum"]
            
            guncelleme_sayisi += 1
            print(f"   🔄 [{guncelleme_sayisi}] {mac['ev_sahibi']} - {mac['deplasman']}")
            print(f"      Yeni: MS:{s_ev}-{s_dep} | İY:{iy_ev}-{iy_dep} | {y_veri['durum']}")
    
    print(f"\n✅ TOPLAM {guncelleme_sayisi} MAÇ GÜNCELLENDİ")
    return guncelleme_sayisi

# =============================================================================
# 🚀 ANA ÇALIŞTIRICI
# =============================================================================
if __name__ == "__main__":
    print("="*70)
    print("⚽ MACKOLİK SCORE SCRAPER - TAM OTOMATİK")
    print("="*70)
    print(f"📅 Tarih Aralığı: {BASLANGIC_TARIHI} - {BITIS_TARIHI}")
    print(f"🔄 Eşleşme Seviyesi: {ESLESME_SEVIYESI}")
    print(f"📦 JSON Dosyası: {MAC_JSON_PATH}")
    print("="*70)
    
    # Mevcut JSON'u yükle
    mevcut_yapi = load_mac_json()
    if not mevcut_yapi:
        print("❌ mac.json bulunamadı veya bozuk!")
        input("Çıkmak için Enter'a basın...")
        exit()
    
    # Tarihleri oluştur
    tarihler = tarihleri_olustur(BASLANGIC_TARIHI, BITIS_TARIHI)
    if not tarihler:
        print("❌ Geçersiz tarih aralığı!")
        input("Çıkmak için Enter'a basın...")
        exit()
    
    print(f"\n📅 İşlenecek {len(tarihler)} gün:")
    for t in tarihler:
        print(f"   • {t}")
    
    # Chrome ayarları
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # ⚠️ DEBUG MODU: Headless'ı kapat (tarayıcıyı görmek istiyorsan)
    # chrome_options.add_argument("--headless=new")  # YORUM SATIRI YAP
    
    try:
        print("\n🚀 TARAYICI BAŞLATILIYOR...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✅ Tarayıcı hazır!")
        
        tum_veriler = []
        
        # Her gün için döngü
        for gun_iso in tarihler:
            try:
                print(f"\n{'#'*70}")
                print(f"# 📅 GÜN: {gun_iso}")
                print(f"{'#'*70}")
                
                # Ana sayfaya git
                driver.get(BASE_LINK)
                time.sleep(SAYFA_YUKLEME_BEKLEME)
                
                # Sayfa yapısını kontrol et
                sayfa_kaynagi = driver.page_source
                if "match-row" in sayfa_kaynagi:
                    print("✅ match-row sınıfı sayfada bulundu")
                else:
                    print("⚠️ UYARI: match-row sınıfı bulunamadı!")
                    print("   Sayfa yapısı değişmiş olabilir.")
                
                # Verileri çek
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
    
    # Sonuçları işle
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
    
    # Eşleştir ve güncelle
    print("\n🧠 GÜNCELLEME BAŞLIYOR...")
    guncellenen = skorlari_eslestir_ve_guncelle(mevcut_yapi, tum_veriler)
    
    if guncellenen > 0:
        print(f"\n✅ {guncellenen} MAÇ BAŞARIYLA GÜNCELLENDİ!")
        
        # JSON'u kaydet
        if save_mac_json(mevcut_yapi):
            # Git işlemleri
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