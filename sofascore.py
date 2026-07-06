import re
import time
import json
import datetime
import subprocess
import traceback
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
GIT_BRANCH = "main"

PAGE_LOAD_TIMEOUT = 60


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


# =========================
# DRIVER
# =========================
def build_driver():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )

    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver


# =========================
# LİG TOGGLE BUTONLARINI BUL (JavaScript ile)
# =========================
def lig_toggle_butonlari_bul(driver):
    """
    JavaScript ile tüm butonları tarar, içinde M11.99 18 (chevron down) 
    path'i olan SVG bulunanları döndürür.
    """
    script = """
    var result = [];
    var buttons = document.querySelectorAll('button');
    for (var i = 0; i < buttons.length; i++) {
        var btn = buttons[i];
        var svg = btn.querySelector('svg');
        if (svg) {
            var path = svg.querySelector('path');
            if (path) {
                var d = path.getAttribute('d');
                if (d && d.includes('M11.99 18')) {
                    result.push(btn);
                }
            }
        }
    }
    return result;
    """
    
    try:
        butonlar = driver.execute_script(script)
        return butonlar if butonlar else []
    except Exception as e:
        print(f"   JS Hatası: {e}")
        return []


# =========================
# LİG ADINI AL
# =========================
def lig_adi_al(toggle_btn):
    """Toggle butonunun üstündeki lig adını bulur"""
    try:
        # 3 seviye yukarı çık ve bdi ara
        parent = toggle_btn.find_element(By.XPATH, "./ancestor::div[.//bdi][1]")
        bdi = parent.find_element(By.TAG_NAME, "bdi")
        return bdi.text.strip()
    except:
        try:
            # Alternatif: Kardeş div'de bdi ara
            parent = toggle_btn.find_element(By.XPATH, "./parent::div/parent::div")
            bdi = parent.find_element(By.TAG_NAME, "bdi")
            return bdi.text.strip()
        except:
            return "Bilinmeyen Lig"


# =========================
# MAÇLARI ÇEK
# =========================
def maclari_cek(driver, hedef_tarih):

    tarih_str = hedef_tarih.strftime("%Y-%m-%d")
    url = BASE_URL + tarih_str

    print(f"\n🌐 {url}")
    driver.get(url)

    # Sayfanın tam yüklenmesi için bekle
    time.sleep(5)
    
    # Cookie kabul et (varsa)
    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Kabul') or contains(text(),'Accept') or contains(text(),'Tümü')]")
        cookie_btn.click()
        time.sleep(1)
    except:
        pass

    # Sayfayı kaydırarak tüm içeriği yükle
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

    skor_listesi = []
    gorulen = set()

    # Toggle butonlarını bul (Chevron down olanlar)
    print("   🔍 Toggle butonları aranıyor...")
    toggle_butonlari = lig_toggle_butonlari_bul(driver)
    
    if not toggle_butonlari:
        print("❌ Hiç lig toggle butonu bulunamadı!")
        return []

    print(f"   ✅ {len(toggle_butonlari)} lig bulundu")

    for i, toggle_btn in enumerate(toggle_butonlari):
        
        lig_adi = lig_adi_al(toggle_btn)
        print(f"\n📋 [{i+1}] {lig_adi}")

        # ===== LİGİ AÇ =====
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", toggle_btn)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", toggle_btn)
            print("   🔽 Açıldı")
            time.sleep(2.5)
        except Exception as e:
            print(f"   ❌ Açılamadı: {e}")
            continue

        # ===== BU LİGİN MAÇLARINI BUL =====
        maclar = []
        try:
            # Toggle butonunun bulunduğu header'dan sonraki div (maç listesi)
            header_div = toggle_btn.find_element(By.XPATH, "./ancestor::div[contains(@class,'h_4xl') or contains(@class,'py_sm')][1]")
            mac_liste_div = header_div.find_element(By.XPATH, "./following-sibling::div[1]")
            
            # Maç linkleri (event-hl-... veya /maç/ içerenler)
            maclar = mac_liste_div.find_elements(By.XPATH, ".//a[contains(@href,'/maç/') or contains(@class,'event')]")
            
            if not maclar:
                # Alternatif: js-list-cell-target divleri
                maclar = mac_liste_div.find_elements(By.XPATH, ".//div[contains(@class,'js-list-cell-target')]")
                
        except Exception as e:
            print(f"   ⚠️ Maç listesi bulunamadı: {e}")

        print(f"   🔎 {len(maclar)} maç")

        # ===== HER MAÇI İŞLE =====
        for mac_idx in range(len(maclar)):
            try:
                # DOM yenilendiği için tekrar bul
                try:
                    header_div = toggle_btn.find_element(By.XPATH, "./ancestor::div[contains(@class,'h_4xl') or contains(@class,'py_sm')][1]")
                    mac_liste_div = header_div.find_element(By.XPATH, "./following-sibling::div[1]")
                    maclar = mac_liste_div.find_elements(By.XPATH, ".//a[contains(@href,'/maç/') or contains(@class,'event')]")
                except:
                    pass

                if mac_idx >= len(maclar):
                    break

                mac = maclar[mac_idx]

                # Takım isimleri
                try:
                    bdiler = mac.find_elements(By.TAG_NAME, "bdi")
                    if len(bdiler) >= 2:
                        ev = bdiler[0].text.strip()
                        dep = bdiler[1].text.strip()
                    else:
                        continue
                except:
                    continue

                if not ev or not dep:
                    continue

                kimlik = f"{ev}|{dep}|{tarih_str}"
                if kimlik in gorulen:
                    continue
                gorulen.add(kimlik)

                print(f"      🔗 {ev} vs {dep}")

                # ===== MAÇA TIKLA =====
                try:
                    # Skor span'ını dene
                    try:
                        skor_span = mac.find_element(By.XPATH, ".//span[contains(@class,'score') or contains(@class,'c_neutral')]")
                        driver.execute_script("arguments[0].click();", skor_span)
                    except:
                        driver.execute_script("arguments[0].click();", mac)
                    
                    time.sleep(3)
                except:
                    continue

                # ===== PANELDEN SKOR AL =====
                ft_skor = "0-0"
                ht_skor = "0-0"

                try:
                    ft_el = driver.find_element(By.XPATH, "//span[text()='FT']/following::span[1]")
                    ft_skor = ft_el.text.strip()
                except:
                    pass

                try:
                    ht_el = driver.find_element(By.XPATH, "//span[text()='HT']/following::span[1]")
                    ht_skor = ht_el.text.strip()
                except:
                    pass

                print(f"         ✅ FT: {ft_skor} | HT: {ht_skor}")

                # Parse
                ft_nums = re.findall(r"\d+", ft_skor)
                ht_nums = re.findall(r"\d+", ht_skor)

                skor_listesi.append({
                    "tarih": tarih_str,
                    "lig": lig_adi,
                    "ev_sahibi": ev,
                    "deplasman": dep,
                    "skor_ev": int(ft_nums[0]) if len(ft_nums) > 0 else 0,
                    "skor_dep": int(ft_nums[1]) if len(ft_nums) > 1 else 0,
                    "skor_1y_ev": int(ht_nums[0]) if len(ht_nums) > 0 else 0,
                    "skor_1y_dep": int(ht_nums[1]) if len(ht_nums) > 1 else 0,
                    "durum": "bitti" if len(ft_nums) >= 2 else "devam" if ft_nums else "baslamadi",
                    "cekme_zamani": datetime.datetime.now().isoformat()
                })

                # Panel kapat
                try:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(0.5)
                except:
                    pass

            except Exception as e:
                print(f"         ❌ Hata: {str(e)[:40]}")
                continue

        # ===== LİGİ KAPAT =====
        try:
            driver.execute_script("arguments[0].click();", toggle_btn)
            print("   ✅ Kapatıldı")
            time.sleep(1)
        except:
            pass

    return skor_listesi


# =========================
# JSON & GIT
# =========================
def save_json(data):
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({"matches": data}, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Kaydedildi: {JSON_PATH}")

def git_push():
    try:
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "commit", "-m", f"Update {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "push", "origin", GIT_BRANCH], cwd=BASE_DIR, check=False)
        print("✅ Git push OK")
    except Exception as e:
        print(f"⚠️ Git: {e}")


# =========================
# ANA
# =========================
if __name__ == "__main__":

    print("\n🚀 SOFASCORE SKOR ÇEKİCİ v5.4 (JavaScript Chevron Fix)\n")

    bas = parse_date(BASLANGIC_TARIHI)
    bit = parse_date(BITIS_TARIHI)
    gunler = gun_listesi_olustur(bas, bit)

    driver = build_driver()
    tum_maclar = []

    try:
        for gun in gunler:
            print("\n" + "="*60)
            print(f"📅 {gun}")
            print("="*60)
            maclar = maclari_cek(driver, gun)
            tum_maclar.extend(maclar)

    except Exception as e:
        print("❌ Kritik hata:", e)
        traceback.print_exc()

    finally:
        driver.quit()

    print(f"\n📊 TOPLAM: {len(tum_maclar)} maç")

    if tum_maclar:
        save_json(tum_maclar)
        git_push()

    input("\n✅ Bitti. ENTER ile çık.")