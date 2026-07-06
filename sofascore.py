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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
# LİG BAŞLIKLARINI BUL
# =========================
def lig_bashliklari_bul(driver):
    """
    Lig başlık divlerini bulur (bdi içeren, ok butonu olanlar)
    """
    return driver.find_elements(
        By.XPATH,
        "//div[contains(@class,'h_4xl') and .//bdi and .//button[.//svg]]"
    )


# =========================
# OK BUTONUNU BUL (Chevron Down)
# =========================
def ok_butonunu_bul(lig_div):
    """
    Lig divi içindeki chevron-down (aşağı ok) butonunu bulur.
    Yıldız değil, genişletme oku.
    """
    try:
        # SVG'si chevron-down olan buton (path'te 11.99 18 koordinatları var)
        # veya daha genel: lig divi içindeki son button veya svg'li button
        buttons = lig_div.find_elements(By.TAG_NAME, "button")
        
        for btn in buttons:
            try:
                svg = btn.find_element(By.TAG_NAME, "svg")
                # Chevron down SVG'sinin özelliği: path'te "18" ve "8.5" koordinatları var
                svg_html = svg.get_attribute("outerHTML")
                if "11.99 18" in svg_html or "M11.99 18" in svg_html or "chevron" in svg_html.lower():
                    return btn
            except:
                continue
        
        # Bulamazsa son button'u dene (genelde en sağdaki ok olur)
        if buttons:
            return buttons[-1]
            
    except:
        pass
    return None


# =========================
# MAÇLARI ÇEK
# =========================
def maclari_cek(driver, hedef_tarih):

    tarih_str = hedef_tarih.strftime("%Y-%m-%d")
    url = BASE_URL + tarih_str

    print(f"\n🌐 {url}")
    driver.get(url)

    wait = WebDriverWait(driver, 20)

    try:
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'h_4xl')]")
            )
        )
    except:
        print("❌ Sayfa yüklenmedi")
        return []

    time.sleep(3)

    # Sayfayı tam yükle
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

    skor_listesi = []
    gorulen = set()

    lig_index = 0

    while True:

        ligler = lig_bashliklari_bul(driver)

        if lig_index >= len(ligler):
            print("✅ Tüm ligler bitti")
            break

        lig_div = ligler[lig_index]

        # Lig adını al
        try:
            lig_adi = lig_div.find_element(By.TAG_NAME, "bdi").text.strip()
        except:
            lig_adi = f"Lig {lig_index+1}"

        print(f"\n📋 [{lig_index+1}] {lig_adi}")

        # ===== OK BUTONUNU BUL VE TIKLA (LİGİ AÇ) =====
        ok_btn = ok_butonunu_bul(lig_div)
        
        if not ok_btn:
            print("   ⚠️ Ok butonu bulunamadı, sonraki lige geçiliyor")
            lig_index += 1
            continue

        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", ok_btn)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", ok_btn)
            print("   🔽 Lig açıldı")
            time.sleep(2)
        except Exception as e:
            print(f"   ❌ Açılamadı: {str(e)[:40]}")
            lig_index += 1
            continue

        # ===== AÇILAN LİGİN MAÇLARINI BUL =====
        # Lig div'inden sonraki kardeş element (açılan liste)
        try:
            # Lig başlığından sonraki div (maç listesi container)
            mac_liste_container = lig_div.find_element(By.XPATH, "./following-sibling::div[1]")
            
            # Maç satırları: event-hl-... linkleri veya js-list-cell-target divleri
            maclar = mac_liste_container.find_elements(
                By.XPATH,
                ".//a[contains(@class,'event-hl-')]"
            )
            
            if not maclar:
                maclar = mac_liste_container.find_elements(
                    By.XPATH,
                    ".//div[contains(@class,'js-list-cell-target')]"
                )
                
        except Exception as e:
            print(f"   ⚠️ Maç listesi bulunamadı: {e}")
            maclar = []

        print(f"   🔎 {len(maclar)} maç bulundu")

        # ===== HER MAÇI İŞLE =====
        for mac_idx in range(len(maclar)):

            try:
                # DOM yenilendiği için tekrar bul
                mac_liste_container = lig_div.find_element(By.XPATH, "./following-sibling::div[1]")
                maclar = mac_liste_container.find_elements(
                    By.XPATH,
                    ".//a[contains(@class,'event-hl-')]"
                )
                if not maclar:
                    maclar = mac_liste_container.find_elements(
                        By.XPATH,
                        ".//div[contains(@class,'js-list-cell-target')]"
                    )

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

                # Duplike kontrol
                kimlik = f"{ev}|{dep}|{tarih_str}"
                if kimlik in gorulen:
                    continue
                gorulen.add(kimlik)

                print(f"      🔗 {ev} vs {dep}")

                # ===== MAÇA TIKLA =====
                try:
                    # Önce skor span'ını dene
                    skor_span = mac.find_element(
                        By.XPATH,
                        ".//span[contains(@class,'score') or contains(@class,'c_neutrals')]"
                    )
                    driver.execute_script("arguments[0].click();", skor_span)
                except:
                    driver.execute_script("arguments[0].click();", mac)

                time.sleep(2.5)

                # ===== PANELDEN FT ve HT AL =====
                ft_skor = "0-0"
                ht_skor = "0-0"

                try:
                    ft_el = driver.find_element(
                        By.XPATH,
                        "//span[text()='FT']/following::span[1]"
                    )
                    ft_skor = ft_el.text.strip()
                except:
                    pass

                try:
                    ht_el = driver.find_element(
                        By.XPATH,
                        "//span[text()='HT']/following::span[1]"
                    )
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
                    "durum": "bitti" if len(ft_nums) >= 2 else "baslamadi",
                    "cekme_zamani": datetime.datetime.now().isoformat()
                })

                # Panel kapat
                try:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(0.8)
                except:
                    pass

            except Exception as e:
                print(f"         ❌ Hata: {str(e)[:40]}")
                continue

        # ===== LİGİ KAPAT (TEKRAR OK'A BAS) =====
        try:
            ok_btn = ok_butonunu_bul(lig_div)
            if ok_btn:
                driver.execute_script("arguments[0].click();", ok_btn)
                print("   ✅ Lig kapatıldı")
                time.sleep(1)
        except:
            pass

        lig_index += 1

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
        print(f"⚠️ Git hata: {e}")


# =========================
# ANA
# =========================
if __name__ == "__main__":

    print("\n🚀 SOFASCORE SKOR ÇEKİCİ v5.2 (Chevron Fix)\n")

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