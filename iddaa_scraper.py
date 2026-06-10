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
# ⚙️ AYARLAR
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
BASE_LINK = "https://www.iddaa.com/canli-skor/futbol"

BASLANGIC_TARIHI = "14/05/2026"
BITIS_TARIHI = "14/05/2026"

ESLESME_SEVIYESI = 0.25
GIT_BRANCH_NAME = "main"

KURAL_SKOR_KONTROL = True
MANTIK_HATASI_DUZELT = True

SAYFA_YUKLEME_BEKLEME = 30
ADIM_KAYDIRMA_MIKTARI = 600
GENEL_HATA_BEKLEME = 2

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

def aylar_arasi_fark(hedef_ay, mevcut_ay):
    fark = mevcut_ay - hedef_ay
    if fark < 0:
        fark += 12
    return fark

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
            print(f"⚠️ {MAC_JSON_PATH} bulunamadı")
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
        dosya_adi = f"debug_iddaa_{gun_iso}.html"
        with open(dosya_adi, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"🔍 DEBUG: {dosya_adi} kaydedildi")
    except:
        pass

# =============================================================================
# 📅 TAKVİM NAVİGASYONU - İDDAA.COM
# =============================================================================
def iddaa_takvimde_gezin(driver, hedef_tarih_iso):
    """
    İddaa.com takviminde hedef tarihe gider
    1. Sayfanın tam yüklenmesini bekle
    2. span.truncate butonuna tıkla (takvimi açar)
    3. Previous/Next ile doğru aya git
    4. Gün numarasına tıkla
    """
    print(f"   🔧 İddaa Takvim navigasyonu: {hedef_tarih_iso}")
    
    try:
        hedef_yil, hedef_ay, hedef_gun = map(int, hedef_tarih_iso.split('-'))
        
        # ═══════════════════════════════════════════
        # 0️⃣ SAYFANIN TAM YÜKLENMESİNİ BEKLE
        # ═══════════════════════════════════════════
        print("   📍 Sayfa yüklenmesi bekleniyor...")
        
        # YÖNTEM 1: Lig başlığı görünene kadar bekle
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h3[data-testid="tournament-name-link"]'))
            )
            print("   ✅ Lig başlıkları yüklendi")
        except:
            print("   ⚠️ Lig başlığı bulunamadı, devam ediliyor...")
        
        # Ekstra bekleme
        time.sleep(3)
        
        # ═══════════════════════════════════════════
        # 1️⃣ TARİH BUTONUNA TIKLA
        # ═══════════════════════════════════════════
        print("   📍 Tarih butonu aranıyor...")
        
        takvim_acildi = False
        
        # YÖNTEM 1: CSS Selector ile
        try:
            tarih_buton = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span.truncate"))
            )
            
            buton_metni = tarih_buton.text.strip()
            print(f"   📍 Buton metni: '{buton_metni}'")
            
            driver.execute_script("arguments[0].click();", tarih_buton)
            print("   ✅ Takvim açıldı (Yöntem 1)")
            takvim_acildi = True
        except Exception as e1:
            print(f"   ⚠️ Yöntem 1 başarısız: {str(e1)[:80]}")
        
        # YÖNTEM 2: XPath ile - tüm span.truncate'ları bul
        if not takvim_acildi:
            try:
                print("   📍 Yöntem 2 deneniyor...")
                tum_truncate = driver.find_elements(By.CSS_SELECTOR, "span.truncate")
                print(f"   📍 {len(tum_truncate)} adet span.truncate bulundu")
                
                for btn in tum_truncate:
                    metin = btn.text.strip()
                    print(f"      - '{metin}'")
                    
                    if metin:  # Boş olmayan ilk butona tıkla
                        driver.execute_script("arguments[0].click();", btn)
                        print(f"   ✅ '{metin}' butonuna tıklandı (Yöntem 2)")
                        takvim_acildi = True
                        break
                        
            except Exception as e2:
                print(f"   ⚠️ Yöntem 2 başarısız: {str(e2)[:80]}")
        
        # YÖNTEM 3: JavaScript ile zorla tıkla
        if not takvim_acildi:
            try:
                print("   📍 Yöntem 3 (JavaScript) deneniyor...")
                js_result = driver.execute_script("""
                    var buttons = document.querySelectorAll('span.truncate');
                    if (buttons.length > 0) {
                        buttons[0].click();
                        return buttons[0].innerText;
                    }
                    return null;
                """)
                
                if js_result:
                    print(f"   ✅ JavaScript ile tıklandı: '{js_result}' (Yöntem 3)")
                    takvim_acildi = True
                else:
                    print("   ⚠️ JavaScript ile buton bulunamadı")
                    
            except Exception as e3:
                print(f"   ⚠️ Yöntem 3 başarısız: {str(e3)[:80]}")
        
        # YÖNTEM 4: Button elementini ara (span değil button olabilir)
        if not takvim_acildi:
            try:
                print("   📍 Yöntem 4 (button element) deneniyor...")
                
                # aria-label'da tarih olan button'ları ara
                tum_buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in tum_buttons:
                    aria = btn.get_attribute("aria-label") or ""
                    text = btn.text.strip()
                    
                    # Tarih içeren veya "Bugün" yazan buton
                    if any(x in aria or x in text for x in ["Bugün", "Today", "Haz", "May", "June", "Oca", "Şub"]):
                        driver.execute_script("arguments[0].click();", btn)
                        print(f"   ✅ Button tıklandı: aria='{aria}', text='{text}' (Yöntem 4)")
                        takvim_acildi = True
                        break
                        
            except Exception as e4:
                print(f"   ⚠️ Yöntem 4 başarısız: {str(e4)[:80]}")
        
        if not takvim_acildi:
            print("   ❌ Takvim açılamadı!")
            
            # DEBUG: Sayfada ne var?
            try:
                tum_spanlar = driver.find_elements(By.TAG_NAME, "span")
                print(f"   🔍 Sayfada {len(tum_spanlar)} span var, ilk 20'si:")
                for s in tum_spanlar[:20]:
                    txt = s.text.strip()
                    cls = s.get_attribute("class") or ""
                    if txt or "truncate" in cls:
                        print(f"      - class='{cls}' | text='{txt[:50]}'")
            except:
                pass
            
            return False
        
        time.sleep(2)
        
        # ═══════════════════════════════════════════
        # 2️⃣ MEVCUT AYI TESPİT ET
        # ═══════════════════════════════════════════
        try:
            secili_gun = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    "button[aria-selected='true']"
                ))
            )
            aria_label = secili_gun.get_attribute("aria-label")
            print(f"   📍 Seçili gün: {aria_label}")
            
            ay_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)', aria_label)
            if ay_match:
                ay_isimleri = {
                    "January": 1, "February": 2, "March": 3, "April": 4, 
                    "May": 5, "June": 6, "July": 7, "August": 8,
                    "September": 9, "October": 10, "November": 11, "December": 12
                }
                mevcut_ay_metni = ay_match.group(1)
                mevcut_ay = ay_isimleri[mevcut_ay_metni]
                print(f"   📍 Mevcut ay: {mevcut_ay_metni} ({mevcut_ay})")
            else:
                mevcut_ay = 6
                print(f"   ⚠️ Ay tespit edilemedi, varsayılan: Haziran")
                
        except Exception as e:
            print(f"   ⚠️ Seçili gün bulunamadı: {e}")
            mevcut_ay = 6
        
        # ═══════════════════════════════════════════
        # 3️⃣ KAÇ KERE PREVIOUS'A BASILMALI?
        # ═══════════════════════════════════════════
        tiklama_sayisi = aylar_arasi_fark(hedef_ay, mevcut_ay)
        
        print(f"   📍 Previous butonuna {tiklama_sayisi} kere basılacak")
        
        if tiklama_sayisi == 0:
            print(f"   ✅ Zaten hedef aydayız")
        else:
            for i in range(tiklama_sayisi):
                try:
                    previous_buton = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((
                            By.CSS_SELECTOR,
                            "button[aria-label='Go to the Previous Month']"
                        ))
                    )
                    driver.execute_script("arguments[0].click();", previous_buton)
                    print(f"   📍 Previous [{i+1}/{tiklama_sayisi}] - Tıklandı")
                    time.sleep(1.5)
                    
                    try:
                        secili_gun = driver.find_element(By.CSS_SELECTOR, "button[aria-selected='true']")
                        aria_label = secili_gun.get_attribute("aria-label")
                        ay_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)', aria_label)
                        if ay_match:
                            ay_isimleri = {
                                "January": 1, "February": 2, "March": 3, "April": 4, 
                                "May": 5, "June": 6, "July": 7, "August": 8,
                                "September": 9, "October": 10, "November": 11, "December": 12
                            }
                            mevcut_ay = ay_isimleri[ay_match.group(1)]
                            print(f"      Yeni ay: {ay_match.group(1)} ({mevcut_ay})")
                    except:
                        pass
                        
                except NoSuchElementException:
                    print(f"   ⚠️ Previous butonu bulunamadı (deneme {i+1})")
                    break
                except Exception as e:
                    print(f"   ⚠️ Previous butonu tıklanamadı (deneme {i+1}): {e}")
                    break
        
        # ═══════════════════════════════════════════
        # 4️⃣ HEDEF GÜN NUMARASINA TIKLA
        # ═══════════════════════════════════════════
        print(f"   📍 Hedef gün seçiliyor: {hedef_gun} ({hedef_tarih_iso})")
        
        try:
            ay_ingilizce = {
                1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"
            }
            
            ay_adi = ay_ingilizce[hedef_ay]
            
            tum_gunler = driver.find_elements(By.CSS_SELECTOR, "button[aria-label]")
            bulundu = False
            
            for gun_btn in tum_gunler:
                aria = gun_btn.get_attribute("aria-label") or ""
                if ay_adi in aria and str(hedef_yil) in aria:
                    gun_match = re.search(r',\s*(\d+)(?:st|nd|rd|th)?', aria)
                    if gun_match and int(gun_match.group(1)) == hedef_gun:
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", gun_btn)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", gun_btn)
                        print(f"   ✅ TARİH SEÇİLDİ: {hedef_tarih_iso} | Aria: {aria}")
                        bulundu = True
                        break
            
            if not bulundu:
                print(f"   ❌ Hedef tarih takvimde bulunamadı!")
                print(f"      Aranan: {ay_adi} {hedef_gun}, {hedef_yil}")
                
                print(f"      Takvimdeki günler:")
                for gun_btn in tum_gunler[:31]:
                    aria = gun_btn.get_attribute("aria-label") or ""
                    text = gun_btn.text.strip()
                    if aria:
                        print(f"         - {text} | {aria}")
                
                return False
            
            time.sleep(12)
            return True
            
        except Exception as e:
            print(f"   ❌ TARİH SEÇİLEMEDİ: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"   ❌ TAKVİM HATASI: {e}")
        import traceback
        traceback.print_exc()
        return False
# =============================================================================
# 🌐 MAÇ SATIRLARINI BUL - İDDAA.COM
# =============================================================================
def iddaa_mac_satirlarini_bul(driver):
    """
    İddaa.com'daki maç satırlarını bulur
    Lig başlığı + maç listesi yapısını kullanır
    """
    mac_gruplari = []
    
    try:
        lig_basliklari = driver.find_elements(By.CSS_SELECTOR, 'h3[data-testid="tournament-name-link"]')
        
        if not lig_basliklari:
            print("⚠️ Hiç lig başlığı bulunamadı!")
            return []
        
        print(f"✅ {len(lig_basliklari)} lig başlığı bulundu")
        
        for lig_baslik in lig_basliklari:
            try:
                # ── LİG ADINI ÇEK ──
                lig_link = lig_baslik.find_element(By.CSS_SELECTOR, "a[href*='tournament']")
                lig_adi = lig_link.text.strip()
                
                # ── ÜLKE ADINI ÇEK ──
                ulke_adi = ""
                try:
                    tum_truncate = lig_baslik.find_elements(By.CSS_SELECTOR, "div.truncate")
                    for div in tum_truncate:
                        txt = div.text.strip()
                        if txt and txt != lig_adi and len(txt) < 20:
                            ulke_adi = txt
                            break
                except:
                    pass
                
                # ── BU LİGİN MAÇLARINI BUL ──
                mac_satirlari = []
                
                try:
                    parent_container = lig_baslik.find_element(By.XPATH, "./ancestor::div[contains(@class, 'match-list') or contains(@class, 'tournament')]")
                    mac_divler = parent_container.find_elements(By.CSS_SELECTOR, "div[role='row'], div[class*='match-row'], div[class*='MatchRow']")
                except:
                    mac_divler = lig_baslik.find_elements(By.XPATH, 
                        "./following-sibling::div[contains(@class, 'match') or contains(@class, 'row') or @role='row']")
                
                for mac_div in mac_divler:
                    try:
                        truncate_divler = mac_div.find_elements(By.CSS_SELECTOR, "div.truncate")
                        
                        if len(truncate_divler) < 2:
                            continue
                        
                        ev_isim = truncate_divler[0].text.strip()
                        dep_isim = truncate_divler[1].text.strip()
                        
                        if not ev_isim or not dep_isim:
                            continue
                        
                        mac_satirlari.append({
                            "element": mac_div,
                            "ev_sahibi": ev_isim,
                            "deplasman": dep_isim,
                            "lig": lig_adi,
                            "ulke": ulke_adi
                        })
                        
                    except Exception as e:
                        continue
                
                if mac_satirlari:
                    print(f"   📍 {lig_adi} ({ulke_adi}) → {len(mac_satirlari)} maç")
                    mac_gruplari.extend(mac_satirlari)
                    
            except Exception as e:
                continue
        
        print(f"✅ Toplam {len(mac_gruplari)} maç satırı bulundu")
        return mac_gruplari
        
    except Exception as e:
        print(f"❌ Maç satırları bulunurken hata: {e}")
        return []

# =============================================================================
# 🌐 ANA ÇEKİM FONKSİYONU - İDDAA.COM
# =============================================================================
def iddaa_get_skorlar_tek_gun(driver, hedef_tarih_iso):
    print(f"\n{'='*70}")
    print(f"📅 İDDAA İŞLENİYOR: {hedef_tarih_iso}")
    print(f"{'='*70}")
    
    skor_listesi = []
    gorulen = {}
    gecerli_sayisi = 0
    
    try:
        print("🔧 [1/4] Takvim navigasyonu yapılıyor...")
        basarili = iddaa_takvimde_gezin(driver, hedef_tarih_iso)
        if not basarili:
            print("❌ Takvim navigasyonu başarısız, bu gün atlanıyor")
            return []
        
        debug_sayfa_kaydet(driver, hedef_tarih_iso)
        
        print("🔧 [2/4] Sayfa kaydırılıyor ve veri toplanıyor...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(3)
        
        max_adim = 200
        
        for adim in range(max_adim):
            driver.execute_script(f"window.scrollBy(0, {ADIM_KAYDIRMA_MIKTARI});")
            time.sleep(1.2)
            
            mac_gruplari = iddaa_mac_satirlarini_bul(driver)
            
            if not mac_gruplari:
                if adim % 20 == 0:
                    print(f"   📍 Adım {adim+1}/{max_adim} - Henüz maç yok...")
                continue
            
            if adim % 20 == 0:
                print(f"   📍 Adım {adim+1}/{max_adim} - {len(mac_gruplari)} satır bulundu")
            
            for mac_info in mac_gruplari:
                try:
                    satir = mac_info["element"]
                    ev_isim = mac_info["ev_sahibi"]
                    dep_isim = mac_info["deplasman"]
                    lig_adi = mac_info.get("lig", "")
                    ulke_adi = mac_info.get("ulke", "")
                    
                    if not ev_isim or not dep_isim or ev_isim == dep_isim:
                        continue
                    
                    kimlik = f"{akilli_isim_temizle(ev_isim)}-{akilli_isim_temizle(dep_isim)}"
                    
                    # ═══════════════════════════════════════════
                    # 🎯 SKOR ÇEKME - İDDAA.COM SELECTOR'LARI
                    # ═══════════════════════════════════════════
                    s_ev, s_dep = 0, 0
                    iy_ev, iy_dep = 0, 0
                    
                    # ── MAÇ SONUCU SKORLARI ──
                    try:
                        tum_score_divler = satir.find_elements(By.CSS_SELECTOR, 
                            "div.rounded-match__score, div.relative.flex.h-\\[1\\.125rem\\].justify-center.w-6")
                        
                        if len(tum_score_divler) >= 4:
                            s_ev = rakam_bul(tum_score_divler[0].text)
                            s_dep = rakam_bul(tum_score_divler[1].text)
                            iy_ev = rakam_bul(tum_score_divler[2].text)
                            iy_dep = rakam_bul(tum_score_divler[3].text)
                    except: pass
                    
                    if s_ev == 0 and s_dep == 0:
                        try:
                            font_medium_scores = satir.find_elements(By.CSS_SELECTOR, 
                                "div.rounded-match__score.font-medium, div.relative.flex.h-\\[1\\.125rem\\].justify-center.w-6.font-medium")
                            font_normal_scores = satir.find_elements(By.CSS_SELECTOR, 
                                "div.rounded-match__score.font-normal, div.relative.flex.h-\\[1\\.125rem\\].justify-center.w-6.font-normal")
                            
                            if len(font_medium_scores) >= 1 and len(font_normal_scores) >= 1:
                                s_dep = rakam_bul(font_medium_scores[0].text)
                                s_ev = rakam_bul(font_normal_scores[0].text)
                        except: pass
                    
                    if s_ev == 0 and s_dep == 0:
                        try:
                            tum_w6 = satir.find_elements(By.CSS_SELECTOR, "div.w-6")
                            sayilar = []
                            for div in tum_w6:
                                txt = div.text.strip()
                                if txt.isdigit():
                                    sayilar.append(int(txt))
                            
                            if len(sayilar) >= 4:
                                s_ev = sayilar[0]
                                s_dep = sayilar[1]
                                iy_ev = sayilar[2]
                                iy_dep = sayilar[3]
                            elif len(sayilar) >= 2:
                                s_ev = sayilar[0]
                                s_dep = sayilar[1]
                        except: pass
                    
                    # ═══════════════════════════════════════════
                    # 🔄 DUPLICATE KONTROLÜ
                    # ═══════════════════════════════════════════
                    if kimlik in gorulen:
                        eski_veri = gorulen[kimlik]
                        
                        if (eski_veri["skor_ev"] == s_ev and 
                            eski_veri["skor_dep"] == s_dep and
                            eski_veri["skor_1y_ev"] == iy_ev and
                            eski_veri["skor_1y_dep"] == iy_dep):
                            continue
                        
                        print(f"   ⚠️ DUPLICATE FARKLI SKOR: {ev_isim} - {dep_isim}")
                        print(f"      İlk: MS:{eski_veri['skor_ev']}-{eski_veri['skor_dep']} | İY:{eski_veri['skor_1y_ev']}-{eski_veri['skor_1y_dep']}")
                        print(f"      Yeni: MS:{s_ev}-{s_dep} | İY:{iy_ev}-{iy_dep}")
                        print(f"      → İlk kayıt korunuyor")
                        continue
                    
                    # ═══════════════════════════════════════════
                    # 🚨 DURUM BELİRLEME
                    # ═══════════════════════════════════════════
                    durum = "baslamadi"
                    if s_ev > 0 or s_dep > 0:
                        durum = "bitti"
                    elif iy_ev > 0 or iy_dep > 0:
                        durum = "devam ediyor"
                    
                    # ═══════════════════════════════════════════
                    # 💾 KAYIT ET
                    # ═══════════════════════════════════════════
                    yeni_veri = {
                        "tarih": hedef_tarih_iso,
                        "ev_sahibi": ev_isim,
                        "deplasman": dep_isim,
                        "skor_ev": s_ev,
                        "skor_dep": s_dep,
                        "skor_1y_ev": iy_ev,
                        "skor_1y_dep": iy_dep,
                        "durum": durum,
                        "lig": lig_adi,
                        "ulke": ulke_adi,
                        "kaynak": "iddaa.com"
                    }
                    
                    gorulen[kimlik] = yeni_veri
                    skor_listesi.append(yeni_veri)
                    
                    gecerli_sayisi += 1
                    print(f"   ✅ [{gecerli_sayisi}] {ev_isim} - {dep_isim} | MS:{s_ev}-{s_dep} | İY:{iy_ev}-{iy_dep} | {lig_adi} | {durum}")
                    
                except Exception as e:
                    continue
            
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
# 🧠 GÜNCELLEME MOTORU - ±2 GÜN TOLERANSLI
# =============================================================================
def skorlari_eslestir_ve_guncelle(mevcut_yapi, tum_veriler):
    mac_listesi = mevcut_yapi.get("matches", [])
    
    if not mac_listesi:
        print("⚠️ Mevcut yapıda maç bulunamadı!")
        return 0
    
    if not tum_veriler:
        print("⚠️ Güncellenecek veri bulunamadı!")
        return 0
    
    print(f"\n🧠 EŞLEŞTİRME BAŞLIYOR (±2 GÜN TARİH TOLERANSLI)...")
    print(f"   • Mevcut JSON maç sayısı: {len(mac_listesi)}")
    print(f"   • Siteden Çekilen Yeni maç sayısı: {len(tum_veriler)}")
    
    guncelleme_sayisi = 0
    atlanan_sayisi = 0
    kullanilan_json_indeksleri = set()
    
    def tarih_farki_gun(tarih1_str, tarih2_str):
        try:
            t1 = datetime.datetime.strptime(str(tarih1_str).strip(), "%Y-%m-%d").date()
            t2 = datetime.datetime.strptime(str(tarih2_str).strip(), "%Y-%m-%d").date()
            return abs((t1 - t2).days)
        except:
            return 999
    
    for y_veri in tum_veriler:
        y_ev = y_veri["ev_sahibi"]
        y_dep = y_veri["deplasman"]
        y_tarih = str(y_veri["tarih"]).strip()
        
        en_yuksek_oran = 0
        en_iyi_mac_index = -1
        en_iyi_ters_mi = False
        
        for idx, mac in enumerate(mac_listesi):
            if idx in kullanilan_json_indeksleri:
                continue
            
            mac_tarih = str(mac.get("tarih", "")).strip()
            
            # ±2 GÜN DIŞINDAKİLERİ ATLA
            if mac_tarih and y_tarih:
                fark = tarih_farki_gun(mac_tarih, y_tarih)
                if fark > 2:
                    continue
            
            oran_normal = (benzerlik_orani(mac["ev_sahibi"], y_ev) + 
                          benzerlik_orani(mac["deplasman"], y_dep))
            oran_ters = (benzerlik_orani(mac["ev_sahibi"], y_dep) + 
                        benzerlik_orani(mac["deplasman"], y_ev))
            
            # TARİH BONUSU
            tarih_bonus = 0.0
            if mac_tarih and y_tarih:
                fark = tarih_farki_gun(mac_tarih, y_tarih)
                if fark == 0:
                    tarih_bonus = 2.0
                elif fark == 1:
                    tarih_bonus = 1.5
                elif fark == 2:
                    tarih_bonus = 1.0
            
            toplam_normal = oran_normal + tarih_bonus
            toplam_ters = oran_ters + tarih_bonus
            toplam_oran = max(toplam_normal, toplam_ters)
            
            if toplam_oran > en_yuksek_oran:
                en_yuksek_oran = toplam_oran
                en_iyi_mac_index = idx
                en_iyi_ters_mi = toplam_ters > toplam_normal
        
        min_gerekli = ESLESME_SEVIYESI * 2
        
        if en_yuksek_oran >= min_gerekli and en_iyi_mac_index != -1:
            mac = mac_listesi[en_iyi_mac_index]
            
            mac_tarih = str(mac.get("tarih", "")).strip()
            fark_bilgi = ""
            if mac_tarih and y_tarih:
                fark = tarih_farki_gun(mac_tarih, y_tarih)
                if fark == 0:
                    fark_bilgi = "✅ AYNI TARİH"
                else:
                    fark_bilgi = f"⚠️ ±{fark} GÜN FARK"
            
            if not en_iyi_ters_mi:
                s_ev, s_dep = y_veri["skor_ev"], y_veri["skor_dep"]
                iy_ev, iy_dep = y_veri["skor_1y_ev"], y_veri["skor_1y_dep"]
            else:
                s_ev, s_dep = y_veri["skor_dep"], y_veri["skor_ev"]
                iy_ev, iy_dep = y_veri["skor_1y_dep"], y_veri["skor_1y_ev"]
            
            mac["skor_ev"] = s_ev
            mac["skor_dep"] = s_dep
            mac["skor_1y_ev"] = iy_ev
            mac["skor_1y_dep"] = iy_dep
            mac["durum"] = y_veri["durum"]
            
            kullanilan_json_indeksleri.add(en_iyi_mac_index)
            guncelleme_sayisi += 1
            
            print(f"   ✅ [{guncelleme_sayisi}] {mac['ev_sahibi']} - {mac['deplasman']} | {fark_bilgi}")
            print(f"      JSON Tarihi: {mac_tarih} | Çekilen Tarih: {y_tarih}")
            print(f"      MS:{s_ev}-{s_dep} | İY:{iy_ev}-{iy_dep}")
        else:
            atlanan_sayisi += 1
            if en_yuksek_oran > 0:
                print(f"   ⏭️ ATLADI: {y_ev} - {y_dep} ({y_tarih}) | Oran: {en_yuksek_oran:.2f}")
            else:
                print(f"   ⏭️ ATLADI: {y_ev} - {y_dep} ({y_tarih}) | Eşleşme bulunamadı")
    
    print(f"\n✅ GÜNCELLENEN: {guncelleme_sayisi}")
    print(f"⏭️ ATLANAN: {atlanan_sayisi}")
    return guncelleme_sayisi

# =============================================================================
# 🚀 ANA ÇALIŞTIRICI
# =============================================================================
if __name__ == "__main__":
    print("="*70)
    print("⚽ İDDAA.COM SCORE SCRAPER - TAM OTOMATİK")
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
    
    driver = None
    
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
                
                gunluk_veri = iddaa_get_skorlar_tek_gun(driver, gun_iso)
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
        if driver is not None:
            try:
                driver.quit()
                print("\n✅ Tarayıcı kapatıldı")
            except:
                pass
    
    if not tum_veriler:
        print("\n" + "="*70)
        print("❌ HİÇ VERİ ÇEKİLEMEDİ!")
        print("="*70)
        print("\n💡 DEBUG_MODU = True yapıp tekrar deneyin")
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
        print("\n💡 ESLESME_SEVIYESI değerini değiştirin (0.1 - 0.5 arası)")
        print("💡 DEBUG_MODU = True yapıp debug dosyalarını inceleyin")
    
    print("\n" + "="*70)
    input("✅ İŞLEM TAMAMLANDI - Çıkmak için Enter'a basın...")