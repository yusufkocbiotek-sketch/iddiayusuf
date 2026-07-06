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

BASLANGIC_TARIHI = "09/05/2026"
BITIS_TARIHI = "10/05/2026"

ESLESME_SEVIYESI = 0.25
GIT_BRANCH_NAME = "main"

KURAL_SKOR_KONTROL = True
MANTIK_HATASI_DUZELT = True

SAYFA_YUKLEME_BEKLEME = 15
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
        print("❌ Tarih formatı: GG/AA/YYYY")
        return []

    tarihler = []
    while baslangic <= bitis:
        tarihler.append(baslangic.strftime("%Y-%m-%d"))
        baslangic += datetime.timedelta(days=1)
    return tarihler

# =============================================================================
# 🔐 İSİM TEMİZLEME VE BENZERLİK
# =============================================================================
def akilli_isim_temizle(isim):
    if not isim: 
        return ""
    isim = isim.lower().strip()
    tr_map = str.maketrans("çğıöşüâêîôûáéíóúñðßçşğ", "cgiosuaeiouaeiounbscsg")
    isim = isim.translate(tr_map)
    isim = re.sub(r'[^a-z\s]', '', isim)
    isim = re.sub(r'\s+', ' ', isim).strip()
    gereksiz = ['fk', 'sk', 'jk', 'bk', 'fc', 'as', 'spor', 'kulubu', 'kulübü', 'şportif', 'sport', 'clube', 'il', 'gk', 'üni', 'gençler', 'takımı']
    for ek in gereksiz:
        if isim.endswith(ek):
            isim = isim[:-len(ek)].strip()
        if isim.startswith(ek):
            isim = isim[len(ek):].strip()
    return isim if len(isim) >= 2 else ""

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
    if len(a_temiz) > 2 and len(b_temiz) > 2 and a_temiz[:3] == b_temiz[:3]:
        return 0.6
    return round(SequenceMatcher(None, a_temiz, b_temiz).ratio(), 2)

# =============================================================================
# 🚨 SKOR KONTROLÜ
# =============================================================================
def skor_mantikli_mi(ev, dep, iy_ev, iy_dep, durum, ev_isim="", dep_isim=""):
    if iy_ev > ev or iy_dep > dep:
        if MANTIK_HATASI_DUZELT:
            return True, f"ℹ️ {ev_isim}-{dep_isim} | Veri geç geldi", False
        else:
            return False, f"❌ HATA | İmkansız Skor", False
    return True, "✅ Geçerli", True

# =============================================================================
# 📖 DOSYA İŞLEMLERİ
# =============================================================================
def load_mac_json():
    try:
        if not MAC_JSON_PATH.exists():
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
        return True
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in str(e.stderr):
            print("! Git: Değişiklik yok")
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
# 📅 TAKVİM - JS AY DEĞİŞTİRME MOTORLU KESİN ÇÖZÜM
# =============================================================================
def iddaa_takvimde_gezin(driver, hedef_tarih_iso):
    print(f"   🔧 İddaa Tarih navigasyonu: {hedef_tarih_iso}")
    
    try:
        hedef_yil, hedef_ay, hedef_gun = map(int, hedef_tarih_iso.split('-'))
        
        # Çok uzun bekle (React yükleme için)
        time.sleep(5)
        
        # Popup kapat (kesin)
        try:
            driver.execute_script("""
                document.querySelectorAll("button[aria-label='Kapat'], button[aria-label='Close'], .modal-close").forEach(b => b.click());
            """)
            time.sleep(1)
        except:
            pass
        
        print("   🔍 Takvim butonu aranıyor (Agresif mod)...")
        
        # STRATEJİ 1: WebDriverWait + data-testid (En stabil)
        try:
            wait = WebDriverWait(driver, 10)
            # data-testid="icon-use" içeren ve dates href'li olanın parent button'u
            takvim_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//*[contains(@href, 'dates') or contains(@href, 'calendar')]]"))
            )
            print("   ✅ Bulundu (WebDriverWait + SVG href)")
        except:
            takvim_btn = None
        
        # STRATEJİ 2: JavaScript ile DOM tarama
        if not takvim_btn:
            takvim_btn = driver.execute_script("""
                // Tüm butonları tar
                const buttons = Array.from(document.querySelectorAll('button'));
                
                // 1. İçinde dates/calendar SVG'si olan
                for (let btn of buttons) {
                    if (btn.innerHTML.includes('dates-') || btn.innerHTML.includes('calendar')) return btn;
                }
                
                // 2. İçinde truncate span olan ve metni sayı içeren (2 Tem 26 vb)
                for (let btn of buttons) {
                    const span = btn.querySelector('span.truncate');
                    if (span && /\\d/.test(span.textContent)) return btn;
                }
                
                // 3. Aria-label'ı takvim/calendar olan
                for (let btn of buttons) {
                    const aria = btn.getAttribute('aria-label');
                    if (aria && (aria.toLowerCase().includes('takvim') || aria.toLowerCase().includes('calendar'))) return btn;
                }
                
                return null;
            """)
            if takvim_btn:
                print("   ✅ Bulundu (JavaScript DOM tarama)")
        
        # STRATEJİ 3: Manuel debug tarama (Son çare)
        if not takvim_btn:
            print("   ⚠️ Normal yöntemler başarısız, debug taraması yapılıyor...")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"   Toplam {len(buttons)} buton var.")
            
            for i, btn in enumerate(buttons[:20]):  # İlk 20'sini kontrol et
                try:
                    html = btn.get_attribute("innerHTML")
                    text = btn.text.strip()
                    # Eğer içinde 'dates' veya tarih formatı varsa
                    if "dates" in html or (text and any(c.isdigit() for c in text)):
                        print(f"   [Aday {i}] Text: '{text[:20]}' | HTML: {html[:80]}...")
                        if not takvim_btn:  # İlk bulduğunu al
                            takvim_btn = btn
                except:
                    continue
            
            if takvim_btn:
                print("   ✅ Debug taramasıyla bulundu")
        
        if not takvim_btn:
            print("   ❌ Takvim butonu bulunamadı! Sayfa yapısı değişmiş olabilir.")
            # Ekran görüntüsü al
            try:
                driver.save_screenshot("takvim_hata.png")
                print("   📸 Ekran görüntüsü kaydedildi: takvim_hata.png")
            except:
                pass
            return False
        
        # TIKLA (JavaScript ile kesin tıklama)
        print("   👆 Takvime tıklanıyor...")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", takvim_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", takvim_btn)
        print("   ✅ Takvim açıldı")
        time.sleep(4)  # Animasyon için bekle
        
        # HEDEF TARİH SEÇİMİ (Önceki ay navigasyonu ile)
        print(f"   🔍 Hedef tarih aranıyor: {hedef_tarih_iso}")
        max_attempts = 36
        
        for attempt in range(max_attempts):
            # data-day attribute'u ile direkt bul
            try:
                gun_btn = driver.find_element(By.CSS_SELECTOR, f'td[data-day="{hedef_tarih_iso}"] button')
                
                if gun_btn.get_attribute("disabled") != "true":
                    driver.execute_script("arguments[0].click();", gun_btn)
                    time.sleep(3)
                    print(f"   ✅ TARİH SEÇİLDİ: {hedef_tarih_iso}")
                    return True
                else:
                    print("   ⚠️ Tarih pasif (disabled)")
                    return False
            except NoSuchElementException:
                pass
            
            # Önceki ay butonu (Nav bar içindeki ilk buton - arrow-left SVG'si olan)
            try:
                # JavaScript ile bul (en güvenlisi)
                prev_btn = driver.execute_script("""
                    const nav = document.querySelector('nav[aria-label="Navigation bar"]');
                    if (nav) return nav.querySelector('button');
                    // Alternatif: arrow-left içeren ilk buton
                    const btns = document.querySelectorAll('button');
                    for (let btn of btns) {
                        const use = btn.querySelector('use');
                        if (use && use.getAttribute('href') && use.getAttribute('href').includes('arrow-left')) return btn;
                    }
                    return null;
                """)
                
                if prev_btn:
                    driver.execute_script("arguments[0].click();", prev_btn)
                    if attempt % 3 == 0:
                        print(f"   ⬅️ Önceki ay ({attempt+1})")
                    time.sleep(1.5)
                else:
                    print("   ❌ Önceki ay butonu bulunamadı!")
                    break
                    
            except Exception as e:
                print(f"   ❌ Navigasyon hatası: {str(e)[:50]}")
                break
        
        print(f"   ❌ Hedef tarihe ({hedef_tarih_iso}) ulaşılamadı")
        return False
        
    except Exception as e:
        print(f"   ❌ KRİTİK HATA: {e}")
        import traceback
        traceback.print_exc()
        return False
# =============================================================================
# 🌐 MAÇ SATIRLARINI BUL
# =============================================================================
def iddaa_mac_satirlarini_bul(driver):
    mac_gruplari = []
    try:
        lig_basliklari = driver.find_elements(By.CSS_SELECTOR, 'h3[data-testid="tournament-name-link"]')
        
        if not lig_basliklari:
            return []
        
        for lig_baslik in lig_basliklari:
            try:
                lig_link = lig_baslik.find_element(By.CSS_SELECTOR, "a[href*='tournament']")
                lig_adi = lig_link.text.strip()
                
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
                
                mac_satirlari = []
                try:
                    parent_container = lig_baslik.find_element(By.XPATH, "./ancestor::div[contains(@class, 'match-list') or contains(@class, 'tournament')]")
                    mac_divler = parent_container.find_elements(By.CSS_SELECTOR, "div[role='row'], div[class*='match-row'], div[class*='MatchRow']")
                except:
                    mac_divler = lig_baslik.find_elements(By.XPATH, "./following-sibling::div[contains(@class, 'match') or contains(@class, 'row') or @role='row']")
                
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
                    except:
                        continue
                
                if mac_satirlari:
                    mac_gruplari.extend(mac_satirlari)
            except:
                continue
        
        return mac_gruplari
    except Exception as e:
        print(f"❌ Maç satırları hatası: {e}")
        return []

# =============================================================================
# 🌐 ANA ÇEKİM FONKSİYONU
# =============================================================================
def iddaa_get_skorlar_tek_gun(driver, hedef_tarih_iso):
    print(f"\n{'='*70}")
    print(f"📅 İDDAA İŞLENİYOR: {hedef_tarih_iso}")
    print(f"{'='*70}")
    
    skor_listesi = []
    gorulen = {}
    gecerli_sayisi = 0
    
    try:
        print("🔧 [1/4] Takvim navigasyonu...")
        basarili = iddaa_takvimde_gezin(driver, hedef_tarih_iso)
        if not basarili:
            print("❌ Takvim başarısız, gün atlanıyor...")
            return []
        
        debug_sayfa_kaydet(driver, hedef_tarih_iso)
        
        print("🔧 [2/4] Sayfa kaydırılıyor...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        max_adim = 200
        
        for adim in range(max_adim):
            driver.execute_script(f"window.scrollBy(0, {ADIM_KAYDIRMA_MIKTARI});")
            time.sleep(1.0)
            
            mac_gruplari = iddaa_mac_satirlarini_bul(driver)
            
            if not mac_gruplari:
                continue
            
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
                    
                    s_ev, s_dep = 0, 0
                    iy_ev, iy_dep = 0, 0
                    
                    # SKOR ÇEKME
                    try:
                        tum_score = satir.find_elements(By.CSS_SELECTOR, "div.rounded-match__score, div.relative.flex.h-\\[1\\.125rem\\].justify-center.w-6")
                        if len(tum_score) >= 4:
                            s_ev = rakam_bul(tum_score[0].text)
                            s_dep = rakam_bul(tum_score[1].text)
                            iy_ev = rakam_bul(tum_score[2].text)
                            iy_dep = rakam_bul(tum_score[3].text)
                    except: pass
                    
                    if s_ev == 0 and s_dep == 0:
                        try:
                            font_med = satir.find_elements(By.CSS_SELECTOR, "div.rounded-match__score.font-medium, div.relative.flex.h-\\[1\\.125rem\\].justify-center.w-6.font-medium")
                            font_norm = satir.find_elements(By.CSS_SELECTOR, "div.rounded-match__score.font-normal, div.relative.flex.h-\\[1\\.125rem\\].justify-center.w-6.font-normal")
                            if len(font_med) >= 1 and len(font_norm) >= 1:
                                s_dep = rakam_bul(font_med[0].text)
                                s_ev = rakam_bul(font_norm[0].text)
                        except: pass
                    
                    if s_ev == 0 and s_dep == 0:
                        try:
                            tum_w6 = satir.find_elements(By.CSS_SELECTOR, "div.w-6")
                            sayilar = [int(div.text.strip()) for div in tum_w6 if div.text.strip().isdigit()]
                            if len(sayilar) >= 4:
                                s_ev, s_dep, iy_ev, iy_dep = sayilar[0], sayilar[1], sayilar[2], sayilar[3]
                            elif len(sayilar) >= 2:
                                s_ev, s_dep = sayilar[0], sayilar[1]
                        except: pass
                    
                    if kimlik in gorulen:
                        continue
                    
                    durum = "baslamadi"
                    if s_ev > 0 or s_dep > 0:
                        durum = "bitti"
                    elif iy_ev > 0 or iy_dep > 0:
                        durum = "devam ediyor"
                    
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
                    print(f"   ✅ [{gecerli_sayisi}] {ev_isim} - {dep_isim} | MS:{s_ev}-{s_dep} | İY:{iy_ev}-{iy_dep} | {lig_adi}")
                except:
                    continue
            
            try:
                son_durum = driver.execute_script("return window.innerHeight + window.scrollY >= document.body.scrollHeight - 500;")
                if son_durum:
                    break
            except:
                pass
        
        print(f"\n📊 {hedef_tarih_iso}: {len(skor_listesi)} veri çekildi.")
        
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
    if not mac_listesi or not tum_veriler:
        return 0
    
    print(f"\n🧠 EŞLEŞTİRME (±2 GÜN TOLERANS)...")
    guncelleme_sayisi = 0
    kullanilan = set()
    
    def tarih_farki(t1, t2):
        try:
            d1 = datetime.datetime.strptime(str(t1).strip(), "%Y-%m-%d").date()
            d2 = datetime.datetime.strptime(str(t2).strip(), "%Y-%m-%d").date()
            return abs((d1 - d2).days)
        except:
            return 999
    
    for y_veri in tum_veriler:
        y_ev = y_veri["ev_sahibi"]
        y_dep = y_veri["deplasman"]
        y_tarih = str(y_veri["tarih"]).strip()
        
        en_oran = 0
        en_idx = -1
        en_ters = False
        
        for idx, mac in enumerate(mac_listesi):
            if idx in kullanilan:
                continue
            
            mac_tarih = str(mac.get("tarih", "")).strip()
            if mac_tarih and y_tarih and tarih_farki(mac_tarih, y_tarih) > 2:
                continue
            
            oran_n = benzerlik_orani(mac["ev_sahibi"], y_ev) + benzerlik_orani(mac["deplasman"], y_dep)
            oran_t = benzerlik_orani(mac["ev_sahibi"], y_dep) + benzerlik_orani(mac["deplasman"], y_ev)
            
            tb = 0.0
            if mac_tarih and y_tarih:
                fark = tarih_farki(mac_tarih, y_tarih)
                if fark == 0: tb = 2.0
                elif fark == 1: tb = 1.5
                elif fark == 2: tb = 1.0
            
            toplam = max(oran_n + tb, oran_t + tb)
            if toplam > en_oran:
                en_oran = toplam
                en_idx = idx
                en_ters = (oran_t + tb) > (oran_n + tb)
        
        if en_oran >= ESLESME_SEVIYESI * 2 and en_idx != -1:
            mac = mac_listesi[en_idx]
            if not en_ters:
                se, sd = y_veri["skor_ev"], y_veri["skor_dep"]
                iye, iyd = y_veri["skor_1y_ev"], y_veri["skor_1y_dep"]
            else:
                se, sd = y_veri["skor_dep"], y_veri["skor_ev"]
                iye, iyd = y_veri["skor_1y_dep"], y_veri["skor_1y_ev"]
            
            mac["skor_ev"], mac["skor_dep"] = se, sd
            mac["skor_1y_ev"], mac["skor_1y_dep"] = iye, iyd
            mac["durum"] = y_veri["durum"]
            
            kullanilan.add(en_idx)
            guncelleme_sayisi += 1
            print(f"   ✅ [{guncelleme_sayisi}] {mac['ev_sahibi']} - {mac['deplasman']} | MS:{se}-{sd}")
            
    return guncelleme_sayisi

# =============================================================================
# 🚀 ANA ÇALIŞTIRICI
# =============================================================================
if __name__ == "__main__":
    print("="*70)
    print("⚽ İDDAA.COM SCORE SCRAPER")
    print("="*70)
    
    mevcut_yapi = load_mac_json()
    if not mevcut_yapi:
        exit()
    
    tarihler = tarihleri_olustur(BASLANGIC_TARIHI, BITIS_TARIHI)
    if not tarihler:
        exit()
    
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
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        tum_veriler = []
        for gun_iso in tarihler:
            driver.get(BASE_LINK)
            time.sleep(SAYFA_YUKLEME_BEKLEME)
            gunluk_veri = iddaa_get_skorlar_tek_gun(driver, gun_iso)
            tum_veriler.extend(gunluk_veri)
            
    except Exception as genel:
        print(f"❌ GENEL HATA: {genel}")
    finally:
        if driver is not None:
            try: driver.quit()
            except: pass
    
    if tum_veriler:
        guncellenen = skorlari_eslestir_ve_guncelle(mevcut_yapi, tum_veriler)
        if guncellenen > 0:
            print(f"\n✅ {guncellenen} MAÇ GÜNCELLENDİ!")
            if save_mac_json(mevcut_yapi):
                git_islemlerini_yap()
    else:
        print("\n❌ HİÇ VERİ ÇEKİLEMEDİ!")
    
    print("\n" + "="*70)
    input("✅ TAMAMLANDI - Enter...")