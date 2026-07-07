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
# 📅 TAKVİM - (<use href="...arrow-left...">) HEDEFLİ ZIRHLI MOTOR
# =============================================================================
def iddaa_takvimde_gezin(driver, hedef_tarih_iso):
    print(f"   🔧 İddaa Tarih navigasyonu: {hedef_tarih_iso}")
    
    try:
        hedef_yil, hedef_ay, hedef_gun = map(int, hedef_tarih_iso.split('-'))
        hedef_tarih_obj = datetime.date(hedef_yil, hedef_ay, hedef_gun)
        bugun = datetime.date.today()
        
        time.sleep(3)
        
        # 1. Pop-up ve çerezleri temizle
        try:
            driver.execute_script(r"""
                document.querySelectorAll("button[aria-label='Kapat'], button[class*='close'], button[id*='accept'], button[class*='cookie']").forEach(b => b.click());
            """)
        except:
            pass

        # ⚡ 0. ADIM: Takvim açmadan aranan tarih zaten ekranda mı? (Şerit kontrolü)
        hedef_hucreler = driver.find_elements(By.CSS_SELECTOR, f"[data-day='{hedef_tarih_iso}']")
        if hedef_hucreler and hedef_hucreler[0].is_displayed():
            btns = hedef_hucreler[0].find_elements(By.TAG_NAME, "button")
            tiklanacak = btns[0] if btns else hedef_hucreler[0]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tiklanacak)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", tiklanacak)
            print(f"   ⚡ TARİH DOĞRUDAN SEÇİLDİ: {hedef_tarih_iso}")
            time.sleep(4)
            return True

        # 2. TAKVİMİ AÇMA
        print("   🔍 Takvim butonu aranıyor...")
        takvim_acildi = False
        
        for deneme in range(5):
            try:
                takvim_acildi = driver.execute_script(r"""
                    if (document.querySelector('nav[aria-label="Navigation bar"], div[role="dialog"], table[role="grid"]')) {
                        return true;
                    }
                    
                    // 🎯 1. ÖNCELİK: dates- veya calendar ikonu barındıran buton
                    let dateIcon = document.querySelector('use[href*="dates-"], use[xlink\\:href*="dates-"], use[href*="calendar"]');
                    if (dateIcon) {
                        let btn = dateIcon.closest('button') || dateIcon.closest('div[role="button"]') || dateIcon.parentElement;
                        if (btn) {
                            btn.scrollIntoView({behavior: 'instant', block: 'center'});
                            btn.click();
                            return true;
                        }
                    }
                    
                    // 🎯 2. ÖNCELİK: Bugün / Dün / Yarın veya Tarih yazılı (2 Tem 26, 9 May 26 vb.) butonlar
                    let truncates = Array.from(document.querySelectorAll('span.truncate, button, div[role="button"]'));
                    for (let el of truncates) {
                        let txt = (el.innerText || "").trim();
                        if (/^(Bugün|Dün|Yarın|\d{1,2}\s+[a-zçğıöşü]{3}(\s+\d{2,4})?)$/i.test(txt) ||
                            /(Oca|Şub|Mar|Nis|May|Haz|Tem|Ağu|Eyl|Eki|Kas|Ara)/i.test(txt)) {
                            
                            let clickable = el.closest('button') || el.closest('div[role="button"]') || el.parentElement || el;
                            if (clickable && clickable.clientWidth < 300) {
                                clickable.scrollIntoView({behavior: 'instant', block: 'center'});
                                clickable.click();
                                return true;
                            }
                        }
                    }
                    return false;
                """)
                if takvim_acildi:
                    print("   ✅ Takvim butonu bulundu ve tıklandı!")
                    time.sleep(1.5)
                    break
            except:
                pass
            time.sleep(1)

        if not takvim_acildi:
            print("   ❌ Takvim penceresi açılamadı!")
            return False

        # 3. AY DEĞİŞTİRME VE GÜN SEÇME (Senin attığın arrow-left / arrow-right kuralı!)
        print(f"   🔍 Hedef tarih aranıyor: {hedef_tarih_iso}")

        for adim in range(24):
            # 🎯 HEDEF GÜN EKRANDA MI? (data-day="YYYY-MM-DD")
            hedef_hucreler = driver.find_elements(By.CSS_SELECTOR, f"[data-day='{hedef_tarih_iso}']")
            
            if hedef_hucreler and hedef_hucreler[0].is_displayed():
                btns = hedef_hucreler[0].find_elements(By.TAG_NAME, "button")
                tiklanacak = btns[0] if btns else hedef_hucreler[0]
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tiklanacak)
                time.sleep(0.3)
                driver.execute_script("arguments[0].click();", tiklanacak)
                print(f"   ✅ TARİH SEÇİLDİ: {hedef_tarih_iso}")
                time.sleep(4) # Maçların yüklenmesi için bekle
                return True
            
            # Eğer hedef gün ekranda yoksa, ok tuşuna bas (Senin istediğin <use href="...arrow-left...">)
            yon_str = "left" if hedef_tarih_obj < bugun else "right"
            yon_metin = "Önceki Ay (<)" if yon_str == "left" else "Sonraki Ay (>)"
            
            # 🎯 SENİN VERDİĞİN ETİKETİ TIKLATAN JS MOTORU (<use href="...arrow-left...">)
            ok_tiklandi = driver.execute_script(r"""
                let yon = arguments[0];
                let btn = null;
                
                // 1. ÖNCELİK: Tam senin verdiğin arrow-left / arrow-right taşıyan use etiketinden bulma!
                let useTag = document.querySelector(`use[href*="arrow-${yon}"], use[xlink\\:href*="arrow-${yon}"]`);
                if (useTag) {
                    btn = useTag.closest('button') || useTag.closest('div[role="button"]') || useTag.parentElement;
                }
                
                // 2. ÖNCELİK: aria-label nitelikleriyle bulma
                if (!btn) {
                    if (yon === 'left') {
                        btn = document.querySelector('button[aria-label="Go to the Previous Month"]');
                    } else {
                        btn = document.querySelector('button[aria-label="Go to the Next Month"]');
                    }
                }
                
                // 3. ÖNCELİK: Navigation bar sıra indeksi (0: Önceki Ay, 1: Sonraki Ay)
                if (!btn) {
                    let navBar = document.querySelector('nav[aria-label="Navigation bar"]');
                    if (navBar) {
                        let navBtns = navBar.querySelectorAll('button');
                        if (navBtns.length >= 2) {
                            btn = yon === 'left' ? navBtns[0] : navBtns[1];
                        }
                    }
                }
                
                if (btn) {
                    btn.scrollIntoView({block: 'center', behavior: 'instant'});
                    btn.click();
                    return true;
                }
                return false;
            """, yon_str)
            
            if ok_tiklandi:
                print(f"   🔄 {yon_metin} geçildi (arrow-{yon_str} kullanıldı)...")
                time.sleep(1.2)
            else:
                print("   ❌ Ay değiştirme okları (<use href='...arrow-left...'>) bulunamadı veya limit bitti!")
                break

        print(f"   ❌ Hedef tarih takvimde bulunamadı: {hedef_tarih_iso}")
        return False
            
    except Exception as e:
        print(f"   ❌ TAKVİM HATASI: {e}")
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