import json
import re
import time
import datetime
import traceback
import subprocess
from pathlib import Path
from difflib import SequenceMatcher

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC

# =========================
# ⚙️ AYARLAR
# =========================
BASLANGIC_TARIHI = "13.06.2026"
BITIS_TARIHI = "15.06.2026"

BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
SPORDB_URL = "https://www.spordb.com/iddaa-programi/"

TARIH_TOLERANSI_GUN = 3        # ±3 gün tolerans
GUCLU_TAKIM_ESIGI = 0.80       # Tek takım eşleşmesi için gereken benzerlik
MIN_TOPLAM_PUAN = 1.10         # İki takımın toplam benzerlik alt sınırı

BEKLEME_KISA = 2
BEKLEME_ORTA = 4
BEKLEME_UZUN = 6
MAX_DENEME = 2

# =========================================================
# 🧠 İSİM HAFIZASI (TAKMA ADLAR)
# Format:  "sitedeki/spordb'deki isim" : "standart isim"
# Hepsi küçük harf. Bot otomatik küçültüp bakar.
# 🟡 YAKIN-ELENEN loglarını bana attıkça burayı büyüteceğiz.
# =========================================================
TAKIM_TAKMA_ADLAR = {
    # ====== GENEL / AVRUPA ======
    "psg": "paris saint germain",
    "paris sg": "paris saint germain",
    "man utd": "manchester united",
    "man city": "manchester city",
    "inter milan": "inter",
    "internazionale": "inter",
    "athletic club": "athletic bilbao",
    "sporting cp": "sporting lizbon",
    "saint": "saint etienne",

    # ====== KAZAKİSTAN ======
    "k kyzylorda": "kaisar",
    "kaysar": "kaisar",
    "kaisar kyzylorda": "kaisar",
    "fc astana": "astana",
    "altay vko": "altay",
    "altay oskemen": "altay",
    "fc ordabasy": "ordabasy",
    "ordabasy shymkent": "ordabasy",

    # ====== PORTEKİZ ======
    "amarante fc": "amarante",
    "ud santarem": "santarem",
    "u.d. santarem": "santarem",

    # ====== ETİYOPYA ======
    "arba minch kenema": "arba minch",
    "arba minch city": "arba minch",
    "wolaita dicha sc": "wolaita dicha",
    "wolaitta dicha": "wolaita dicha",
    "bahir dar kenema fc": "bahir dar kenema",
    "bahir dar city": "bahir dar kenema",
    "welwalu adigrat": "welwalo adigrat",
    "welwalo adigrat university": "welwalo adigrat",

    # ====== ARJANTİN ======
    "argentinos j": "argentinos juniors",
    "argentinos jrs": "argentinos juniors",
    "ath lanus": "lanus",
    "ca lanus": "lanus",
    "ca acassuso": "acassuso",
    "ca defensores de belgrano": "defensores de belgrano",
    "def belgrano": "defensores de belgrano",
    "ca chaco for ever": "chaco for ever",
    "dep madryn": "deportivo madryn",
    "san": "san lorenzo",

    # ====== MACARİSTAN ======
    "bfc siofok": "siofok",
    "erdi vse": "erd",
    "erd vse": "erd",

    # ====== ÇİN ======
    "pekin guoan": "beijing guoan",
    "shanghai sipg": "shanghai port",
    "shenzhen juniors fc": "shenzhen juniors",
    "shenzhen peng city": "shenzhen juniors",

    # ====== AVUSTRALYA ======
    "north eastern metrostars sc": "metrostars",
    "ne metrostars": "metrostars",
    "edgeworth fc": "edgeworth",
    "edgeworth eagles": "edgeworth",
    "maitland fc": "maitland",
    "para hills knights sc": "para hills knights",
    "para hills": "para hills knights",
    "fc bulleen lions": "bulleen lions",
    "bulleen": "bulleen lions",
    "melb. sharks": "melbourne sharks",
    "melb sharks": "melbourne sharks",
    "port melbourne sharks": "melbourne sharks",
    "magic united tfa": "magic united",
    "magic utd": "magic united",
    "adelaide city fc": "adelaide city",
    "white city fk beograd": "white city",
    "white city woodville": "white city",

    # ====== İSVİÇRE ======
    "sc bruhl st gallen": "sc bruhl",
    "sc brühl": "sc bruhl",
    "bruhl sg": "sc bruhl",
    "sc cham": "cham",
    "bsc young boys": "young boys",

    # ====== NORVEÇ / DANİMARKA ======
    "il gneist": "gneist",
    "nykoebing": "nykobing",
    "nykobing fc": "nykobing",

    # ====== KANADA / ABD ======
    "atl ottawa": "atletico ottawa",
    "forge fc": "forge",
    "av alta fc": "av alta",
    "avs alta": "av alta",
    "new york cosmos": "ny cosmos",
    "n.y. cosmos": "ny cosmos",

    # ====== FAS ======
    "chabab atlas khenifra": "chabab khenifra",
    "cak khenifra": "chabab khenifra",

    # ====== PERU ======
    "asociacion deportiva tarma": "adt tarma",
    "adt": "adt tarma",
    "ad tarma": "adt tarma",

    # ====== GÜNEY AMERİKA DİĞER ======
    "ldu": "ldu quito",
    "sao": "sao paulo",

    # ====== HOLLANDA (Jong karışmasın!) ======
    "jong ajax": "ajax 2",
    "ajax amsterdam": "ajax",
    "jong utrecht": "utrecht 2",
    "fc utrecht": "utrecht",
    "jong psv": "psv 2",
    "jong az": "az 2",

    # ====== BOSNA / DİĞER ======
    "bfc": "bfc daugavpils",
    "ifk": "ifk mariehamn",
    "zrinjski": "zrinjski mostar",

    # 👉 🟡 YAKIN-ELENEN loglarından buraya ekleyeceğiz...
}

# =========================
# 🔴 TAKIM İSİMLERİ DÜZELTME (çekim sırasında)
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

    name = re.sub(r"[^a-zA-Z0-9ığüşöçİĞÜŞÖÇ\s\-\(\)\.]", "", name)
    karşısı = re.sub(r"[^a-zA-Z0-9ığüşöçİĞÜŞÖÇ\s\-\(\)\.]", "", karşısı)
    return name.title().strip(), karşısı.title().strip()

# =========================================================
# 🔍 İSİM NORMALİZE + BENZERLİK
# 🚨 Genç/Rezerv(II)/Kadın etiketleri KORUNUR, silinmez!
# Böylece Jong Ajax skoru asla Ajax'a yazılmaz.
# =========================================================
def isim_normalize(s):
    """İsmi küçült, takma adlardan geçir. Kategori etiketlerini KORUR."""
    if not s:
        return ""
    s = str(s).lower().strip()

    # Önce takma ad sözlüğüne bak (ham haliyle)
    if s in TAKIM_TAKMA_ADLAR:
        s = TAKIM_TAKMA_ADLAR[s]

    # 🚨 KATEGORİ ETİKETLERİ: Silme → STANDARTLAŞTIR
    s = s.replace("(k)", " kadin ").replace("(w)", " kadin ")
    if s.startswith("jong "):                          # Jong Ajax → ajax 2
        s = s[5:].strip() + " 2"
    s = re.sub(r"\b(ii)\b", "2", s)                    # Luzern II → luzern 2
    s = re.sub(r"\b(genc|gencler|gençler|youth|u19|u20|u21|u23|junior|juniors)\b", "genc", s)
    s = re.sub(r"\b(kadin|kadın|women|ladies|fem|feminino)\b", "kadin", s)

    # Türkçe karakter sadeleştir
    tr_map = str.maketrans("çğıöşü", "cgiosu")
    s = s.translate(tr_map)
    s = re.sub(r"[^a-z0-9\s]", "", s)

    # Sadece ZARARSIZ ekleri at (u19/u21 ARTIK BURADA YOK!)
    for ek in [" fc", " fk", " sk", " jk", " cf", " sc", " club", " spor"]:
        if s.endswith(ek):
            s = s[: -len(ek)]
    for on_ek in ["fc ", "fk ", "sc ", "ca ", "cd ", "ud ", "il "]:
        if s.startswith(on_ek):
            s = s[len(on_ek):]
    s = re.sub(r"\s+", " ", s).strip()

    # Normalize edilmiş halini de sözlükten geçir
    if s in TAKIM_TAKMA_ADLAR:
        s = TAKIM_TAKMA_ADLAR[s]

    return s

def benzerlik(a, b):
    a_n = isim_normalize(a)
    b_n = isim_normalize(b)
    if not a_n or not b_n:
        return 0.0

    # 🛡️ KATEGORİ KORUMASI:
    # Biri genç/rezerv/kadın, diğeri A takımsa → eşleşme İMKANSIZ
    for etiket in ["2", "genc", "kadin"]:
        a_var = etiket in a_n.split()
        b_var = etiket in b_n.split()
        if a_var != b_var:
            return 0.10

    if a_n == b_n:
        return 1.0
    # Biri diğerinin içinde geçiyorsa (örn: "kyzylorda" ⊂ "kaisar kyzylorda")
    if a_n in b_n or b_n in a_n:
        return 0.90
    return SequenceMatcher(None, a_n, b_n).ratio()

# =========================
# 📂 JSON İŞLEMLERİ
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
# 📅 TARİH FONKSİYONLARI (±3 GÜN TOLERANS)
# =========================
def esnek_tarih_parse(t):
    """Hem YYYY-MM-DD hem DD.MM.YYYY formatını çözer."""
    t = str(t).strip()[:10]
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d-%m-%Y", "%Y.%m.%d"):
        try:
            return datetime.datetime.strptime(t, fmt).date()
        except:
            continue
    return None

def dates_close(t1, t2):
    d1 = esnek_tarih_parse(t1)
    d2 = esnek_tarih_parse(t2)
    if not d1 or not d2:
        return False
    return abs((d1 - d2).days) <= TARIH_TOLERANSI_GUN

def parse_date(s):
    try:
        return datetime.datetime.strptime(s, "%d.%m.%Y").date()
    except:
        return None

def gun_listesi_olustur(bas, bit):
    """Başlangıç-bitiş arasındaki TÜM günleri tek tek listeler."""
    gunler = []
    aktif = bas
    while aktif <= bit:
        gunler.append(aktif)
        aktif += datetime.timedelta(days=1)
    return gunler

# =========================
# 🚀 DRIVER
# =========================
def build_driver():
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--log-level=3")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--no-first-run")
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)

    try:
        print("🔄 ChromeDriver hazırlanıyor...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(BEKLEME_UZUN)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✅ Tarayıcı başarıyla başlatıldı")
        return driver
    except Exception as e:
        print(f"⚠️ Normal mod başlatılamadı ({e}), Gizli moda geçiliyor...")
        opts.add_argument("--headless=old")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(BEKLEME_UZUN)
        print("✅ Tarayıcı (Gizli Mod) başlatıldı")
        return driver

# =========================
# 📅 HAFTA & GÜN SEÇİMİ
# =========================
def select_week(driver, hedef_tarih):
    """Verilen TEK güne uygun haftayı seçer."""
    print(f"🔄 {hedef_tarih.strftime('%d.%m.%Y')} için hafta seçiliyor...")
    try:
        select_el = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#iddaa_daterange")))
        select_obj = Select(select_el)

        for opt in select_obj.options:
            txt = opt.text.strip()
            if not txt or " - " not in txt:
                continue
            bas_str, bit_str = txt.split(" - ")
            try:
                bas = datetime.datetime.strptime(bas_str.strip(), "%d.%m.%Y").date()
                bit = datetime.datetime.strptime(bit_str.strip(), "%d.%m.%Y").date()
                if bas <= hedef_tarih <= bit:
                    opt.click()
                    time.sleep(BEKLEME_UZUN)
                    print(f"✅ HAFTA SEÇİLDİ: {txt}")
                    return True
            except:
                continue
        print(f"❌ {hedef_tarih} için uygun hafta bulunamadı!")
        return False
    except Exception as e:
        print(f"❌ HAFTA HATA: {e}")
        return False

def get_day_option(driver, hedef_tarih):
    """Seçili haftanın gün listesinden hedef günü bulur."""
    try:
        select_el = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#iddaa_dateselector")))
        select_obj = Select(select_el)
        for opt in select_obj.options:
            val = opt.get_attribute("value")
            txt = opt.text.strip()
            if not val or val == "*":
                continue
            try:
                g_date = datetime.datetime.strptime(txt, "%d.%m.%Y").date()
                if g_date == hedef_tarih:
                    return {
                        "deger": val,
                        "gorunen": txt,
                        "formatli_tarih": g_date.strftime("%Y-%m-%d")
                    }
            except:
                pass
        return None
    except Exception as e:
        print(f"❌ GÜN BULMA HATA: {e}")
        return None

# =========================
# ⚡ MAÇ VERİSİ ÇEKME
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
        sel = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#iddaa_dateselector")))
        Select(sel).select_by_value(gun["deger"])
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href^="/canli/"]')))
        time.sleep(BEKLEME_UZUN)

        # Linkleri listeye kaydet (Stale hatası çözümü)
        link_elemanlari = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/canli/"][href*="-maci-"]')
        linkler = [elem.get_attribute("href") for elem in link_elemanlari
                   if elem.get_attribute("href") and "-maci-" in elem.get_attribute("href")]

        print(f"🔍 {len(linkler)} adet maç bulundu, çekim başlıyor...")

        for i, href in enumerate(linkler, 1):
            try:
                detay = extract_match(driver, href, i)
                if detay.get("ev_sahibi") and detay.get("deplasman"):
                    detay["tarih"] = gun["formatli_tarih"]
                    matches.append(detay)
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

# =========================================================
# 🧠 EŞLEŞTİRME - ÇOKLU GÜNCELLEME + YAKIN-ELENEN DEDEKTÖRÜ
# ±3 gün içinde eşleşen TÜM kayıtlara (kopyalar dahil) skor yazar
# =========================================================
def merge_data(mevcut, yeni):
    mac_listesi = mevcut.get("matches", [])
    guncelle_say = 0
    ekle_say = 0
    kopya_say = 0
    print("\n🔎 EŞLEŞTİRME BAŞLADI (ÇOKLU GÜNCELLEME | ±3 GÜN | KATEGORİ KORUMALI)...")

    for sp in yeni:
        sp_tarih = sp.get("tarih", "")
        sp_ev = sp.get("ev_sahibi", "")
        sp_dep = sp.get("deplasman", "")

        # ─────────────────────────────────────────────
        # 1️⃣ FRENLERİ GEÇEN TÜM ADAYLARI TOPLA
        # ─────────────────────────────────────────────
        adaylar = []  # [(index, puan, detay), ...]

        for idx, mevcut_mac in enumerate(mac_listesi):

            # Tarih kontrolü (±3 gün tolerans)
            if not dates_close(mevcut_mac.get("tarih", ""), sp_tarih):
                continue

            oran_ev = benzerlik(mevcut_mac.get("ev_sahibi", ""), sp_ev)
            oran_dep = benzerlik(mevcut_mac.get("deplasman", ""), sp_dep)
            toplam = oran_ev + oran_dep

            # 🟡 DEDEKTÖR: Eşiğe yakın ama elenenler loglanır (isim avı için!)
            # Bu satırları bana at, hafızaya ekleyeyim.
            if (0.70 <= toplam < MIN_TOPLAM_PUAN) or \
               (toplam >= MIN_TOPLAM_PUAN and min(oran_ev, oran_dep) < 0.35) or \
               (toplam >= MIN_TOPLAM_PUAN and oran_ev < GUCLU_TAKIM_ESIGI and oran_dep < GUCLU_TAKIM_ESIGI):
                print(f"🟡 YAKIN-ELENEN: WEB[{sp_ev} - {sp_dep}] ↔ "
                      f"JSON[{mevcut_mac.get('ev_sahibi','')} - {mevcut_mac.get('deplasman','')}] "
                      f"| ev:{oran_ev:.2f} dep:{oran_dep:.2f}")

            # 🛡️ FREN 1: Toplam benzerlik alt sınırı
            if toplam < MIN_TOPLAM_PUAN:
                continue

            # 🛡️ FREN 2: En az bir takım güçlü eşleşmeli
            if oran_ev < GUCLU_TAKIM_ESIGI and oran_dep < GUCLU_TAKIM_ESIGI:
                continue

            # 🛡️ FREN 3: Bir taraf çöpse ele (farklı maçtır)
            if min(oran_ev, oran_dep) < 0.35:
                continue

            puan = toplam
            d1 = esnek_tarih_parse(mevcut_mac.get("tarih", ""))
            d2 = esnek_tarih_parse(sp_tarih)
            if d1 and d2 and d1 == d2:
                puan += 0.50

            adaylar.append((idx, puan, f"ev:{oran_ev:.2f} dep:{oran_dep:.2f}"))

        # ─────────────────────────────────────────────
        # 2️⃣ TÜM ADAYLARI GÜNCELLE (KOPYALAR DAHİL!)
        # ─────────────────────────────────────────────
        if adaylar:
            adaylar.sort(key=lambda x: x[1], reverse=True)

            for sira, (idx, puan, detay) in enumerate(adaylar):
                mevcut_mac = mac_listesi[idx]

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
                    if sira == 0:
                        guncelle_say += 1
                        print(f"🔄 GÜNCELLE [P:{puan:.2f} | {detay}]: "
                              f"{mevcut_mac['ev_sahibi']} - {mevcut_mac['deplasman']} | "
                              f"{sp['skor_ev']}-{sp['skor_dep']} (IY:{sp['skor_1y_ev']}-{sp['skor_1y_dep']})")
                    else:
                        kopya_say += 1
                        print(f"   👯 KOPYA DA GÜNCELLENDİ [P:{puan:.2f}] ({mevcut_mac.get('tarih','')}): "
                              f"{mevcut_mac['ev_sahibi']} - {mevcut_mac['deplasman']} | "
                              f"{sp['skor_ev']}-{sp['skor_dep']}")
        else:
            # ─────────────────────────────────────────
            # 3️⃣ HİÇ ADAY YOK → YENİ KAYIT
            # ─────────────────────────────────────────
            mac_listesi.append(sp)
            ekle_say += 1
            print(f"➕ YENİ KAYIT: {sp['ev_sahibi']} - {sp['deplasman']} ({sp_tarih})")

    mevcut["matches"] = mac_listesi
    print(f"\n📊 ÖZET: 🔄 {guncelle_say} ana güncelleme | 👯 {kopya_say} kopya senkronize | ➕ {ekle_say} yeni")
    return mevcut, guncelle_say, ekle_say

# =========================
# 📤 GİT İŞLEMLERİ
# =========================
def git_islemleri():
    try:
        print("\n🔄 GİT İŞLEMLERİ BAŞLATILIYOR...")
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True, capture_output=True, text=True)

        zaman = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        commit_mesaji = f"Veri Güncelleme | {zaman} | Akıllı Eşleştirme"

        subprocess.run(["git", "commit", "--allow-empty", "-m", commit_mesaji],
                       cwd=BASE_DIR, capture_output=True, text=True)
        subprocess.run(["git", "push", "origin", "main"],
                       cwd=BASE_DIR, check=True, capture_output=True, text=True)
        print("✅ GİT BAŞARILI")
        return True
    except Exception as e:
        print(f"❌ GİT HATA: {e}")
        return False

# =========================
# 🎯 ANA AKIŞ (GÜN GÜN DÖNGÜ)
# =========================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 SPORDB | HAFIZA + KATEGORİ KORUMASI + DEDEKTÖR ✅")
    print("=" * 60)

    bas_tar = parse_date(BASLANGIC_TARIHI)
    bit_tar = parse_date(BITIS_TARIHI)
    if not bas_tar or not bit_tar:
        print("❌ Tarih hatası! Format: GG.AA.YYYY")
        input("Devam...")
        exit()

    hedef_gunler = gun_listesi_olustur(bas_tar, bit_tar)
    print(f"📅 İşlenecek {len(hedef_gunler)} gün:")
    for g in hedef_gunler:
        print(f"   • {g.strftime('%d.%m.%Y')}")

    driver = None
    tum_yeni = []

    try:
        driver = build_driver()

        # Her gün için: sayfa sıfırdan + hafta yeniden + gün seç + çek
        for gun_tarihi in hedef_gunler:
            print("\n" + "#" * 60)
            print(f"# 📅 GÜN: {gun_tarihi.strftime('%d.%m.%Y')}")
            print("#" * 60)

            try:
                driver.get(SPORDB_URL)
                time.sleep(BEKLEME_UZUN)

                if not select_week(driver, gun_tarihi):
                    print(f"⏭️ {gun_tarihi} atlandı (hafta yok)")
                    continue
                time.sleep(BEKLEME_ORTA)

                gun = get_day_option(driver, gun_tarihi)
                if not gun:
                    print(f"⏭️ {gun_tarihi} atlandı (gün listede yok)")
                    continue

                gunluk = fetch_day(driver, gun)
                tum_yeni.extend(gunluk)
                print(f"📊 {gun['gorunen']} SONUÇ: {len(gunluk)} maç çekildi")

            except Exception as gun_hata:
                print(f"❌ {gun_tarihi} işlenirken hata: {str(gun_hata)[:50]}")
                continue

        print(f"\n📊 TOPLAM ÇEKİLEN: {len(tum_yeni)} maç")

        if tum_yeni:
            mevcut_veri = load_json_safe(MAC_JSON_PATH)
            yeni_veri, guncelle, ekle_say = merge_data(mevcut_veri, tum_yeni)

            if save_json_safe(yeni_veri, MAC_JSON_PATH):
                print(f"\n🎉 İŞLEM TAMAMLANDI: {guncelle} Güncellendi | {ekle_say} Yeni Eklendi")
                git_islemleri()
        else:
            print("\n⚠️ Hiç veri çekilemedi, JSON'a dokunulmadı.")

    except Exception as err:
        print(f"\n❌ KRİTİK HATA: {err}")
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
        input("\n✅ TAMAMLANDI. Kapatmak için ENTER...")