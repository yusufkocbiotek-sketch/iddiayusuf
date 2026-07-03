import re
import time
import datetime
import traceback
import json
import subprocess
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager


# =========================
# AYARLAR
# =========================
BASLANGIC_TARIHI = "01.07.2026"
BITIS_TARIHI     = "02.07.2026"

BASE_URL = "https://www.sofascore.com/tr/football/"
PAGE_LOAD_TIMEOUT = 90
WAIT_LONG = 8
WAIT_SHORT = 2

BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
GIT_BRANCH = "main"


# =========================
# TARİH
# =========================
def parse_date(s):
    return datetime.datetime.strptime(s, "%d.%m.%Y").date()

def gun_listesi_olustur(bas, bit):
    gunler = []
    aktif = bas
    while aktif <= bit:
        gunler.append(aktif)
        aktif += datetime.timedelta(days=1)
    return gunler

def dates_close(t1, t2):
    try:
        d1 = datetime.datetime.strptime(str(t1)[:10], "%Y-%m-%d").date()
        d2 = datetime.datetime.strptime(str(t2)[:10], "%Y-%m-%d").date()
        return abs((d1 - d2).days) <= 15
    except:
        return False


# =========================
# DRIVER | GELİŞMİŞ BOT KORUMASI
# =========================
def build_driver():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--lang=tr-TR")
    opts.add_argument("--accept-lang=tr,en;q=0.9")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-web-security")
    opts.add_argument("--allow-running-insecure-content")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")

    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )

    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    driver.implicitly_wait(WAIT_SHORT)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en-US', 'en']});")
    return driver


# =========================
# LİGLERİ TEK TEK AÇ | GÜNCELLENMİŞ SEÇİCİLER
# =========================
def ligleri_tek_tek_ac_ve_cek(driver):
    print("🔽 Ligler aranıyor ve açılıyor...")
    tum_maclar = []

    # ✅ Sofascore'un en güncel yapısına uygun SEÇİCİLER
    lig_satirlari = driver.find_elements(
        By.XPATH,
        "//div[contains(@class, 'tournamentHeader') or contains(@class, 'event__header') or contains(@class, 'sc-fqkvVR') or contains(@class, 'sc-ktHwxA')]"
    )

    if not lig_satirlari:
        print("   ⚠️ Klasik seçicilerle bulunamadı, alternatif yöntem deneniyor...")
        lig_satirlari = driver.find_elements(
            By.XPATH,
            "//div[.//h2 or .//h3 or .//span[contains(@class, 'tournament')]]"
        )

    print(f"   📍 {len(lig_satirlari)} lig grubu bulundu")

    for lig_idx, lig in enumerate(lig_satirlari):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", lig)
            time.sleep(1)

            # ✅ Genişletme butonu
            try:
                ok_buton = lig.find_element(
                    By.XPATH,
                    ".//button | .//*[name()='svg' and (@viewBox='0 0 24 24' or @viewBox='0 0 16 16')]/.."
                )
                driver.execute_script("arguments[0].click();", ok_buton)
                print(f"   ✅ Lig {lig_idx+1} açıldı")
                time.sleep(WAIT_LONG)
            except:
                print(f"   ℹ️ Lig {lig_idx+1} zaten açık veya buton yok")

            # ✅ Maç satırları | GÜNCELLENMİŞ
            mac_satirlari = lig.find_elements(
                By.XPATH,
                "./following-sibling::div[1]//div[contains(@class, 'event__match') or contains(@class, 'sc-fjdhpX') or contains(@class, 'sc-ghqWyX')]"
            )

            if not mac_satirlari:
                continue

            print(f"      📋 {len(mac_satirlari)} maç bulundu")

            for mac in mac_satirlari:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", mac)
                    time.sleep(0.5)

                    # Link ve takım isimleri
                    mac_link = mac.find_element(By.TAG_NAME, "a").get_attribute("href")
                    bdiler = mac.find_elements(By.TAG_NAME, "bdi")
                    ev, dep = None, None
                    for bdi in bdiler:
                        metin = bdi.text.strip()
                        if re.match(r'\d{2}:\d{2}|\d+\.\d+\.\d+', metin):
                            continue
                        if ev is None and metin:
                            ev = metin
                        elif ev and metin:
                            dep = metin
                            break

                    ev = ev or "Bilinmiyor"
                    dep = dep or "Bilinmiyor"

                    # ✅ Detay sayfasına girip İY + MS al
                    ana_pencere = driver.current_window_handle
                    driver.execute_script(f"window.open('{mac_link}', '_blank');")
                    time.sleep(1.5)
                    driver.switch_to.window(driver.window_handles[-1])

                    WebDriverWait(driver, 12).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='detail']"))
                    )
                    time.sleep(2)

                    skor_ev = skor_dep = iy_ev = iy_dep = 0
                    durum = "baslamadi"

                    try:
                        iy_blok = driver.find_element(By.XPATH, "//div[contains(text(), 'İY') or contains(text(), 'HT')]/following-sibling::div[1]")
                        iy_metin = iy_blok.text.strip().replace(":", "-")
                        iy_ev, iy_dep = map(int, iy_metin.split("-"))

                        ft_blok = driver.find_element(By.XPATH, "//div[contains(text(), 'MS') or contains(text(), 'FT') or contains(text(), 'Maç sonu')]/following-sibling::div[1]")
                        ft_metin = ft_blok.text.strip().replace(":", "-")
                        skor_ev, skor_dep = map(int, ft_metin.split("-"))
                        durum = "bitti"
                    except:
                        pass

                    if len(driver.window_handles) > 1:
                        driver.close()
                    driver.switch_to.window(ana_pencere)

                    tum_maclar.append({
                        "ev_sahibi": ev,
                        "deplasman": dep,
                        "skor_ev": skor_ev,
                        "skor_dep": skor_dep,
                        "skor_1y_ev": iy_ev,
                        "skor_1y_dep": iy_dep,
                        "durum": durum,
                        "kaynak": "selenium",
                        "cekme_zamani": datetime.datetime.now().isoformat()
                    })

                except Exception as e:
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(ana_pencere)
                    continue

        except:
            continue

    return tum_maclar


# =========================
# ANA ÇEKİM FONKSİYONU
# =========================
def maclari_cek_selenium(driver, hedef_tarih):
    tarih_str = hedef_tarih.strftime("%Y-%m-%d")
    url = BASE_URL + tarih_str

    print(f"\n🌐 Yükleniyor: {url}")
    try:
        driver.get(url)
    except TimeoutException:
        print("   ⚠️ Zaman aşımı, devam ediliyor...")

    # Sayfanın tam yüklenmesi için bekle
    try:
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='event'], div[class*='tournament']"))
        )
    except:
        print("   ⚠️ İçerik bulunamadı")
        return []

    time.sleep(WAIT_LONG * 2)
    return ligleri_tek_tek_ac_ve_cek(driver)


# =========================
# VERİ YÖNETİMİ
# =========================
def load_json_safe():
    try:
        if not JSON_PATH.exists():
            return {"matches": []}
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"matches": []}

def merge_data(mevcut, yeni):
    mac_listesi = mevcut.get("matches", [])
    guncelle = ekle = 0

    for sp in yeni:
        if sp["durum"] == "baslamadi":
            continue
        bulundu = False
        for mc in mac_listesi:
            if (dates_close(mc["tarih"], sp["tarih"]) and
                mc["ev_sahibi"].lower().strip() == sp["ev_sahibi"].lower().strip() and
                mc["deplasman"].lower().strip() == sp["deplasman"].lower().strip()):

                if any(mc.get(k) != sp.get(k) for k in ["skor_ev", "skor_dep", "skor_1y_ev", "skor_1y_dep"]):
                    mc.update(sp)
                    guncelle += 1
                bulundu = True
                break
        if not bulundu:
            mac_listesi.append(sp)
            ekle += 1

    mevcut["matches"] = mac_listesi
    mevcut["son_guncelleme"] = datetime.datetime.now().isoformat()
    return mevcut, guncelle, ekle

def save_json_safe(data):
    try:
        JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def git_push():
    try:
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"Güncelleme: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"], cwd=BASE_DIR, capture_output=True)
        subprocess.run(["git", "push", "origin", GIT_BRANCH], cwd=BASE_DIR, check=True, capture_output=True)
        return True
    except:
        return False


# =========================
# ANA
# =========================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 SOFASCORE SKOR ÇEKİCİ | v6 - Seçiciler + Bot Koruması Güncellendi")
    print("=" * 60)

    bas = parse_date(BASLANGIC_TARIHI)
    bit = parse_date(BITIS_TARIHI)
    gunler = gun_listesi_olustur(bas, bit)

    driver = build_driver()
    tum_maclar = []

    try:
        for gun in gunler:
            print("\n" + "=" * 60)
            print(f"📆 {gun.strftime('%d.%m.%Y')}")
            print("=" * 60)

            maclar = maclari_cek_selenium(driver, gun)
            tum_maclar.extend(maclar)

            print(f"   ✅ Bu gün: {len(maclar)} maç")
            time.sleep(3)

    except Exception as e:
        print(f"\n❌ GENEL HATA: {e}")
        traceback.print_exc()

    finally:
        driver.quit()
        print("\n🔒 Tarayıcı kapatıldı")

    print("\n" + "=" * 60)
    print(f"📊 TOPLAM ÇEKİLEN: {len(tum_maclar)}")
    print("=" * 60)

    if tum_maclar:
        mevcut = load_json_safe()
        yeni_veri, guncelleme, ekleme = merge_data(mevcut, tum_maclar)
        if save_json_safe(yeni_veri):
            print(f"✅ {guncelleme} güncellendi, {ekleme} yeni eklendi")
            git_push()
    else:
        print("ℹ️ Hiç veri alınamadı")

    input("\nÇıkmak için ENTER...")