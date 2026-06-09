import json
import re
import time
import datetime
import traceback
import subprocess
from pathlib import Path
from difflib import SequenceMatcher

# =========================
# 🔴 TAKIM İSİMLERİ DÜZELTME
# =========================
def clean_team_name(name, karşısı=""):
    if not name or name is None:
        return "", ""

    name = str(name).lower().strip()
    karşısı = str(karşısı).lower().strip()

    BILINEN_MAC_DUZELTME = {
        ("ifk", "mariehamn fc lahti"): ("IFK Mariehamn", "FC Lahti"),
        ("honka", "vjs"): ("Honka", "VJS"),
        ("borac", "banja luka posusje"): ("Borac Banja Luka", "Posusje"),
        ("sloga", "doboj rudar prijedor"): ("Sloga Doboj", "Rudar Prijedor"),
        ("fas", "burundi"): ("Fas", "Burundi"),
        ("bfc", "daugavpils auda"): ("BFC Daugavpils", "Auda"),
        ("zrinjski", "mostar velez mostar"): ("Zrinjski Mostar", "Velez Mostar"),
        ("saint", "etienne nice"): ("Saint Etienne", "Nice"),
        ("deportivo", "pereira jaguares de cordoba"): ("Deportivo Pereira", "Jaguares de Cordoba"),
        ("lanus", "mirassol fc"): ("Lanus", "Mirassol FC"),
        ("ldu", "quito always ready"): ("LDU Quito", "Always Ready"),
        ("millonarios", "o higgins"): ("Millonarios", "O Higgins"),
        ("sao", "paulo boston river"): ("Sao Paulo", "Boston River"),
        ("gremio", "ca torque"): ("Gremio", "CA Torque"),
        ("palestino", "deportivo"): ("Palestino", "Deportivo"),
        ("estudiantes", "medellin"): ("Estudiantes", "Medellin"),
        ("flamengo", "cusco fc"): ("Flamengo", "Cusco FC"),
        ("nacional", "de football coquimbo unido"): ("Nacional De Football", "Coquimbo Unido"),
        ("san", "deportivo recoleta"): ("San Lorenzo", "Deportivo Recoleta"),
        ("santos", "deportivo cuenca"): ("Santos", "Deportivo Cuenca"),
        ("psg", "paris saint germain"): ("Paris Saint Germain", "Paris Saint Germain"),
        ("oleksandria", "zorya luhansk"): ("Oleksandria", "Zorya Luhansk")
    }

    for (e_kisa, d_kisa), (e_tam, d_tam) in BILINEN_MAC_DUZELTME.items():
        if e_kisa in name and d_kisa in karşısı:
            return e_tam, d_tam

    TEKIL_DUZELT = {
        "san": "San Lorenzo", "sao": "Sao Paulo", "ldu": "LDU Quito",
        "bfc": "BFC Daugavpils", "ifk": "IFK Mariehamn", "zrinjski": "Zrinjski Mostar",
        "saint": "Saint Etienne", "deportivo": "Deportivo Pereira", "psg": "Paris Saint Germain"
    }
    if name in TEKIL_DUZELT:
        return TEKIL_DUZELT[name], karşısı.title() if karşısı else ""
    if karşısı in TEKIL_DUZELT:
        return name.title() if name else "", TEKIL_DUZELT[karşısı]

    name = re.sub(r"[^a-zA-Z0-9ığüşöçİĞÜŞÖÇ\s-]", "", name)
    karşısı = re.sub(r"[^a-zA-Z0-9ığüşöçİĞÜŞÖÇ\s-]", "", karşısı)
    return name.title().strip(), karşısı.title().strip()

def normalize_key(ev, dep):
    def norm(s):
        if not s: return ""
        s = str(s).lower()
        s = re.sub(r"[^\w\s]", "", s)
        s = re.sub(r"\s+", "", s)
        return s
    return f"{norm(ev)}|{norm(dep)}"

# =========================
# 📂 JSON - %100 İSTEDİĞİN FORMAT
# =========================
def load_json_safe(path):
    try:
        if not path.exists():
            return {"matches": [], "son_guncelleme": ""}
        with open(path, "r", encoding="utf-8") as f:
            veri = json.load(f)
            if "matches" not in veri or not isinstance(veri["matches"], list):
                veri["matches"] = []
            return veri
    except Exception as e:
        print(f"⚠️ JSON OKUMA HATASI: {e} - YENİ OLUŞTURULUYOR...")
        return {"matches": [], "son_guncelleme": ""}

def save_json_safe(data, path):
    try:
        temiz_mac_listesi = []
        for idx, mac in enumerate(data.get("matches", []), 1):
            ev_sahibi = str(mac.get("ev_sahibi", "")).strip()
            deplasman = str(mac.get("deplasman", "")).strip()
            
            if ev_sahibi and deplasman:
                temiz_mac = {
                    "index": idx,
                    "mac_kodu": str(mac.get("mac_kodu", "")),
                    "ev_sahibi": ev_sahibi,
                    "deplasman": deplasman,
                    "saat": str(mac.get("saat", "")),
                    "lig": str(mac.get("lig", "")),
                    "tarih": str(mac.get("tarih", "")),
                    "cekme_zamani": str(mac.get("cekme_zamani", datetime.datetime.now().isoformat())),
                    "durum": str(mac.get("durum", "baslamadi")),
                    "skor_ev": int(mac.get("skor_ev", 0)),
                    "skor_dep": int(mac.get("skor_dep", 0)),
                    "skor_1y_ev": int(mac.get("skor_1y_ev", 0)),
                    "skor_1y_dep": int(mac.get("skor_1y_dep", 0)),
                    "kaynak": str(mac.get("kaynak", "spordb.com")),
                    "oranlar": mac.get("oranlar", {})
                }
                temiz_mac_listesi.append(temiz_mac)

        data["son_guncelleme"] = datetime.datetime.now().isoformat()
        cikti_verisi = {"matches": temiz_mac_listesi, "son_guncelleme": data["son_guncelleme"]}

        temp_path = path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8", newline='\n') as f:
            json.dump(cikti_verisi, f, ensure_ascii=False, indent=2)
        
        temp_path.replace(path)
        print(f"💾 KAYIT BAŞARILI: {path.name} | Toplam: {len(temiz_mac_listesi)} maç")
        return True
    except Exception as e:
        print(f"❌ KAYIT HATASI: {e}")
        return False

# =========================
# ⚙️ AYARLAR
# =========================
BASLANGIC_TARIHI = "14.05.2026"
BITIS_TARIHI = "14.05.2026"

BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
SPORDB_URL = "https://www.spordb.com/iddaa-programi/"
ESLESME_ORANI = 0.60

BEKLEME_KISA = 2
BEKLEME_ORTA = 4
BEKLEME_UZUN = 6
MAX_DENEME = 2

# =========================
# 🚀 DRIVER
# =========================
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC

def build_driver():
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--disable-features=VizDisplayCompositor")
    opts.add_argument("--remote-debugging-port=0")
    opts.add_argument("--log-level=3")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-web-security")
    opts.add_argument("--allow-running-insecure-content")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-plugins")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)

    try:
        print("🔄 ChromeDriver hazırlanıyor...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(30)
        driver.implicitly_wait(BEKLEME_UZUN)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✅ Tarayıcı başarıyla başlatıldı")
        return driver
    except Exception as e:
        print(f"⚠️ Normal mod başlatılamadı ({e}), Gizli moda geçiliyor...")
        opts.add_argument("--headless=old")
        opts.add_argument("--single-process")
        opts.add_argument("--disable-background-networking")
        opts.add_argument("--disable-sync")
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
            driver.set_page_load_timeout(60)
            driver.implicitly_wait(BEKLEME_UZUN)
            print("✅ Tarayıcı (Gizli Mod) başarıyla başlatıldı")
            return driver
        except Exception as e2:
            print(f"❌ KESİN HATA: {e2}")
            raise e2

def parse_date(s):
    try: 
        return datetime.datetime.strptime(s, "%d.%m.%Y").date()
    except: 
        return None

# =========================
# 📅 TARİH SEÇİMİ
# =========================
def select_week(driver, start_date, end_date):
    print("🔄 Hafta seçiliyor...")
    try:
        select_el = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#iddaa_daterange")))
        select_obj = Select(select_el)
        
        for opt in select_obj.options:
            txt = opt.text.strip()
            if not txt or " - " not in txt: 
                continue
            bas_aralik_str, bit_aralik_str = txt.split(" - ")
            try:
                bas_aralik = datetime.datetime.strptime(bas_aralik_str.strip(), "%d.%m.%Y").date()
                bit_aralik = datetime.datetime.strptime(bit_aralik_str.strip(), "%d.%m.%Y").date()
                if bas_aralik <= start_date <= bit_aralik:
                    opt.click()
                    time.sleep(BEKLEME_UZUN)
                    print(f"✅ SEÇİLDİ: {txt}")
                    return True
            except:
                continue
        print("❌ Uygun tarih aralığı bulunamadı!")
        return False
    except Exception as e:
        print(f"❌ HAFTA HATA: {e}")
        return False

def get_days(driver, start_date, end_date):
    gunler = []
    try:
        select_el = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#iddaa_dateselector")))
        select_obj = Select(select_el)
        for opt in select_obj.options:
            val = opt.get_attribute("value")
            txt = opt.text.strip()
            if not val or val == "*": 
                continue
            try:
                g_date = datetime.datetime.strptime(txt, "%d.%m.%Y").date()
                if start_date <= g_date <= end_date:
                    gunler.append({
                        "deger": val, 
                        "gorunen": txt,
                        "formatli_tarih": g_date.strftime("%Y-%m-%d")
                    })
            except: 
                pass
        return sorted(gunler, key=lambda x: x["gorunen"])
    except Exception as e:
        print(f"❌ GÜN LİSTE HATA: {e}")
        return []

# =========================
# ⚡ VERİ ÇEKME - STALE HATASI ÇÖZÜLDÜ ✅
# =========================
def extract_match(driver, href, sira):
    data = {
        "mac_kodu": "", "ev_sahibi": "", "deplasman": "", "saat": "", "lig": "",
        "tarih": "", "cekme_zamani": datetime.datetime.now().isoformat(),
        "durum": "baslamadi", "skor_ev": 0, "skor_dep": 0, "skor_1y_ev": 0, "skor_1y_dep": 0,
        "kaynak": "spordb.com", "oranlar": {}
    }
    main_tab = driver.current_window_handle
    
    for deneme in range(MAX_DENEME):
        try:
            driver.execute_script("window.open(arguments[0]);", href)
            WebDriverWait(driver, 20).until(lambda d: len(d.window_handles) > 1)
            driver.switch_to.window(driver.window_handles[-1])
            WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(BEKLEME_ORTA)
            page_source = driver.page_source

            # 1. İSİMLER
            h1 = ""
            try:
                h1_elem = driver.find_element(By.CSS_SELECTOR, "h1")
                h1 = h1_elem.text.strip()
            except:
                h1_match = re.search(r"<h1.*?>(.*?)</h1>", page_source, re.DOTALL | re.IGNORECASE)
                if h1_match:
                    h1 = h1_match.group(1).strip()

            if not h1 or " - " not in h1:
                takim_linkleri = re.findall(r'href="/takim/.*?">(.*?)</a>', page_source, re.DOTALL)
                if len(takim_linkleri) >= 2:
                    h1 = f"{takim_linkleri[0].strip()} - {takim_linkleri[1].strip()}"

            if " - " in h1:
                e_x, _, d_x = h1.partition(" - ")
                e_temiz, d_temiz = clean_team_name(e_x, d_x)
                data["ev_sahibi"] = e_temiz
                data["deplasman"] = d_temiz

            # 2. MAÇ SONU SKOR
            skor_match = re.search(r'id=["\']matchdetailscore["\'].*?>(\d+)-(\d+)</', page_source, re.DOTALL)
            if skor_match:
                data["skor_ev"] = int(skor_match.group(1))
                data["skor_dep"] = int(skor_match.group(2))

            # 3. İLK YARI SKOR
            iy_match = re.search(r'id=["\']matchdetailhtscore["\'].*?IY\s*(\d+)-(\d+)\s*</', page_source, re.DOTALL | re.IGNORECASE)
            if iy_match:
                iy_ev = int(iy_match.group(1))
                iy_dep = int(iy_match.group(2))
                if iy_ev <= data["skor_ev"] and iy_dep <= data["skor_dep"]:
                    data["skor_1y_ev"] = iy_ev
                    data["skor_1y_dep"] = iy_dep

            # 4. DURUM
            if "maç sonu" in page_source.lower() or "bitti" in page_source.lower() or skor_match:
                data["durum"] = "bitti"
            elif "devam" in page_source.lower():
                data["durum"] = "devam"

            print(f"✅ {sira:2d}. | {data['ev_sahibi']} - {data['deplasman']} | SKOR: {data['skor_ev']}-{data['skor_dep']} | IY: {data['skor_1y_ev']}-{data['skor_1y_dep']}")
            break

        except Exception as e:
            print(f"⚠️ {sira:2d}. | DENEME {deneme+1}: {str(e)[:30]}")
        finally:
            try:
                if len(driver.window_handles) > 1:
                    driver.close()
                driver.switch_to.window(main_tab)
            except:
                pass

    return data

def fetch_day(driver, gun):
    matches = []
    try:
        print(f"\n📅 {gun['gorunen']} GÜNÜ İŞLENİYOR...")
        # Günü seç
        sel = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#iddaa_dateselector")))
        Select(sel).select_by_value(gun["deger"]) 
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href^="/canli/"]')))
        time.sleep(BEKLEME_UZUN)

        # 🚨 HATA ÇÖZÜMÜ: Linkleri bir listeye KAYDET, elemanları değil linkleri gez!
        link_elemanlari = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/canli/"][href*="-maci-"]')
        linkler = [elem.get_attribute("href") for elem in link_elemanlari if elem.get_attribute("href") and "-maci-" in elem.get_attribute("href")]
        
        print(f"🔍 {len(linkler)} adet maç bulundu, çekim başlıyor...")
        
        # Artık elemanları değil, SADECE linkleri dolaşıyoruz!
        for i, href in enumerate(linkler, 1):
            try:
                detay = extract_match(driver, href, i)
                if detay.get("ev_sahibi") and detay.get("deplasman"):
                    detay["tarih"] = gun["formatli_tarih"] 
                    matches.append(detay)
                # Her maç arası küçük bekleme, sayfanın dinlenmesi için
                time.sleep(BEKLEME_KISA)
            except StaleElementReferenceException:
                print(f"⚠️ {i}. Maçta sayfa yenilendi, geçiliyor...")
                continue
            except Exception as e:
                print(f"❌ {i}. Maç genel hata: {str(e)[:30]}")
                continue

    except Exception as e:
        print(f"❌ GÜN GENEL HATA: {str(e)[:50]}")
    return matches

# =========================
# ⏰ TARİH TOLERANS FONKSİYONU (YENİ EKLENDİ)
# =========================
def tarih_farki_uygun_mu(t1_str, t2_str):
    def format_cevir(s):
        if not s: return None
        s = str(s).replace(".", "-").replace("/", "-")
        try:
            parcalar = s.split("-")
            if len(parcalar) == 3:
                if len(parcalar[0]) == 4: # YYYY-MM-DD
                    return datetime.date(int(parcalar[0]), int(parcalar[1]), int(parcalar[2]))
                else: # DD-MM-YYYY
                    return datetime.date(int(parcalar[2]), int(parcalar[1]), int(parcalar[0]))
        except:
            return None
        return None

    d1 = format_cevir(t1_str)
    d2 = format_cevir(t2_str)
    
    # Tarih okunamıyorsa eski sistemdeki gibi birebir uyum kontrol et
    if not d1 or not d2:
        return str(t1_str).replace("-", "").replace(".", "") == str(t2_str).replace("-", "").replace(".", "")
        
    fark = abs((d1 - d2).days)
    return fark <= 2  # ±2 GÜN TOLERANS

# =========================
# 🧠 EŞLEŞTİRME (±2 GÜN KORUMALI)
# =========================
def merge_data(mevcut, yeni):
    mac_listesi = mevcut.get("matches", [])
    guncelle_say = 0
    ekle_say = 0
    print("\n🔎 EŞLEŞTİRME BAŞLADI (±2 Gün Toleranslı)...")

    for sp in yeni:
        eslesti = False
        for idx, mevcut_mac in enumerate(mac_listesi):
            # 🚨 YENİ SİSTEM: Eski "tar1 != tar2" yerine "tarih_farki_uygun_mu" kullanılıyor!
            if not tarih_farki_uygun_mu(mevcut_mac.get("tarih", ""), sp.get("tarih", "")): 
                continue
                
            oran_ev = SequenceMatcher(None, normalize_key(mevcut_mac["ev_sahibi"], ""), normalize_key(sp["ev_sahibi"], "")).ratio()
            oran_dep = SequenceMatcher(None, normalize_key(mevcut_mac["deplasman"], ""), normalize_key(sp["deplasman"], "")).ratio()
            
            if (oran_ev >= ESLESME_ORANI and oran_dep >= ESLESME_ORANI):
                degisti_mi = False
                if mevcut_mac["skor_ev"] != sp["skor_ev"] or mevcut_mac["skor_dep"] != sp["skor_dep"]:
                    degisti_mi = True
                    mevcut_mac["skor_ev"] = sp["skor_ev"]
                    mevcut_mac["skor_dep"] = sp["skor_dep"]
                if mevcut_mac["skor_1y_ev"] != sp["skor_1y_ev"] or mevcut_mac["skor_1y_dep"] != sp["skor_1y_dep"]:
                    degisti_mi = True
                    mevcut_mac["skor_1y_ev"] = sp["skor_1y_ev"]
                    mevcut_mac["skor_1y_dep"] = sp["skor_1y_dep"]
                if mevcut_mac["durum"] != sp["durum"] and sp["durum"] != "baslamadi":
                    degisti_mi = True
                    mevcut_mac["durum"] = sp["durum"]
                
                if degisti_mi:
                    mevcut_mac["cekme_zamani"] = datetime.datetime.now().isoformat()
                    guncelle_say += 1
                    print(f"🔄 GÜNCELLE : {mevcut_mac['ev_sahibi']} - {mevcut_mac['deplasman']}")
                eslesti = True
                break
        if not eslesti:
            mac_listesi.append(sp)
            ekle_say += 1
            print(f"➕ YENİ KAYIT: {sp['ev_sahibi']} - {sp['deplasman']}")

    mevcut["matches"] = mac_listesi
    return mevcut, guncelle_say, ekle_say

# =========================
# 📤 GİT
# =========================
def git_islemleri():
    try:
        print("\n🔄 GİT İŞLEMLERİ BAŞLATILIYOR...")
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True, capture_output=True, text=True)
        
        zaman = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        commit_mesaji = f"Veri Güncelleme | {zaman} | Hata Düzeltme"
        
        subprocess.run(["git", "commit", "--allow-empty", "-m", commit_mesaji], cwd=BASE_DIR, capture_output=True, text=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True, capture_output=True, text=True)
        print("✅ GİT BAŞARILI")
        return True
    except Exception as e:
        print(f"❌ GİT HATA: {e}")
        return False

# =========================
# 🎯 ANA AKIŞ
# =========================
if __name__ == "__main__":
    print("="*60)
    print("🚀 SPORDB | STALE HATASI ÇÖZÜLDÜ | ±2 GÜN TOLERANS ✅")
    print("="*60)

    bas_tar = parse_date(BASLANGIC_TARIHI)
    bit_tar = parse_date(BITIS_TARIHI)
    if not bas_tar or not bit_tar:
        print("❌ Tarih hatası!")
        input("Devam...")
        exit()

    driver = None
    try:
        driver = build_driver()
        driver.get(SPORDB_URL)
        time.sleep(BEKLEME_UZUN)

        if not select_week(driver, bas_tar, bit_tar):
            raise Exception("Hafta seçilemedi!")
        time.sleep(BEKLEME_UZUN)

        gunler = get_days(driver, bas_tar, bit_tar)
        if not gunler:
            raise Exception("Gün bulunamadı!")

        tum_yeni = []
        for gun in gunler:
            tum_yeni.extend(fetch_day(driver, gun))

        mevcut_veri = load_json_safe(MAC_JSON_PATH)
        yeni_veri, guncelle, ekle_say = merge_data(mevcut_veri, tum_yeni)

        if save_json_safe(yeni_veri, MAC_JSON_PATH):
            print(f"\n🎉 İŞLEM TAMAMLANDI: {guncelle} Güncellendi | {ekle_say} Yeni Eklendi")
            git_islemleri()

    except Exception as err:
        print(f"\n❌ KRİTİK HATA: {err}")
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
        input("\n✅ TAMAMLANDI. Kapatmak için ENTER...")