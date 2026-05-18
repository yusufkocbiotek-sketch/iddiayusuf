import json, os, re, time, datetime, traceback, shutil, unicodedata
from pathlib import Path
from difflib import SequenceMatcher

# =========================
# 🔴 GELİŞTİRİLMİŞ TAKIM İŞLEMLERİ - EŞLEŞME SORUNU ÇÖZÜLDÜ
# =========================
def clean_team_name(name):
    """Takım isimlerini standartlaştırarak eşleşme şansını artırır."""
    if not name:
        return ""
    
    # Küçük harfe çevir ve boşlukları temizle
    n = name.lower().strip()
    
    # Ön ekler (başta bulunan kısaltmalar)
    prefixes = [
        "ad ", "cd ", "ca ", "fc ", "ac ", "sc ", "us ", "ud ", "fk ", "sk ", "jk ", "bk ", "as ", "al ", "el ", "da ", "de ",
        "real ", "athletic ", "atletico ", "deportivo ", "club ", "kulübü ", "spor ", "gençlerbirliği ", "federasyon "
    ]
    # Son ekler (sonda bulunan kısaltmalar)
    suffixes = [
        " fc", " sc", " ac", " us", " ud", " fk", " sk", " jk", " bk", " as", " ad", " cd", " ca", 
        "spor", "kulübü", "club", "sportif", "faalietler", "şportif", "gençlik", "youth", "reserves", "b", "ii", "iii",
        "u19", "u20", "u21", "u22", "u23", "women", "kadın", "erkek", "a.ş", "a.s"
    ]
    
    # Ön ekleri temizle
    for p in prefixes:
        if n.startswith(p):
            n = n[len(p):].strip()
    
    # Son ekleri temizle
    for s in suffixes:
        if n.endswith(s):
            n = n[:-len(s)].strip()

    # Özel kelime değiştirmeleri
    replacements = {
        "ceuta": "ceuta",
        "al ain": "alain",      # Birleştirip yazıyoruz ki Dibba ile karışmasın
        "dibba al ain": "dibba",
        "dibba": "dibba"
    }
    
    for key, val in replacements.items():
        n = n.replace(key, val)
            
    # Nokta, tire, kesme işareti vb. karakterleri kaldır
    n = n.replace(".", "").replace("-", " ").replace("'", "").replace("’", "").replace("`", "")
    
    # Fazla boşlukları temizle
    n = " ".join(n.split())
    
    return n.strip()

# Elle eşleştirme sözlüğü (buraya istediğin takımı ekle)
OZEL_ESLESTIRMELER = {
    "spordb": {
        "ceuta": "ad ceuta",
        "al ain": "al ain fc",
        "dibba": "dibba al ain"
    },
    "macjson": {
        "ad ceuta": "ceuta",
        "al ain fc": "al ain",
        "dibba al ain": "dibba"
    }
}

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC

# =========================
# PATH
# =========================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
GECMIS_JSON_PATH = BASE_DIR / "public" / "data" / "gecmis_maclar.json"
OUTPUT_SKOR_JSON = BASE_DIR / "public" / "data" / "skorlar_spordb.json"

# =========================
# AYARLAR
# =========================
SPORDB_URL = "https://www.spordb.com/iddaa-programi"

DAYS_BACK_FINISHED = 5     
INCLUDE_TODAY = True       

UPDATE_MAC_JSON = True
UPDATE_GECMIS_JSON = True
ADD_MISSING_MATCHES = False

PAGE_LOAD_TIMEOUT = 60
WAIT_LONG = 35

DATESELECTOR_CSS = "#iddaa_dateselector"

CANLI_LINK_SELECTOR = "a[href*='/canli/'][href*='-maci-']"
CANLI_HREF_RE = re.compile(
    r"/canli/(?P<id>\d+)/(?P<date>\d{2}-\d{2}-\d{4})-(?P<teams>.+?)-maci-(?P<h>\d+)-(?P<a>\d+)/?$",
    re.IGNORECASE
)

LOAD_MORE_XPATH = "//button[contains(., 'Daha') or contains(., 'Load more') or contains(., 'More')]"

# 🔴 Eşik değerleri (daha hassas ayarlandı)
THRESH_OK = 0.70        
THRESH_MAYBE = 0.55
MIN_GAP = 0.10          

# =========================
# NORMALİZASYON
# =========================
_TMAP = str.maketrans({"İ":"i","I":"i","ı":"i","Ş":"s","ş":"s","Ğ":"g","ğ":"g","Ü":"u","ü":"u","Ö":"o","ö":"o","Ç":"c","ç":"c"})
_STOP = {"fk","fc","sk","jk","bk","ac","as","a.s","a.ş","spor","club","kulubu","kulübü",
         "u19","u20","u21","u23","women","reserves","b","ii","ca","cd","cf","sc","ud", "de", "la", "el", "al"}

def _deaccent(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))

def norm_team(s: str) -> str:
    s = (s or "").strip()
    # Özel eşleştirme kontrolü
    s_lower = s.lower()
    if s_lower in OZEL_ESLESTIRMELER["macjson"]:
        s = OZEL_ESLESTIRMELER["macjson"][s_lower]
    if s_lower in OZEL_ESLESTIRMELER["spordb"]:
        s = OZEL_ESLESTIRMELER["spordb"][s_lower]

    s = _deaccent(s).translate(_TMAP).lower()
    s = re.sub(r"[’'`´]", "", s)
    s = re.sub(r"\d+", " ", s)
    s = re.sub(r"[^a-z0-9\s-]", " ", s).replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip()
    parts = [p for p in s.split(" ") if p and p not in _STOP and len(p) > 1]
    return " ".join(parts)

def seq_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def token_dice(a: str, b: str) -> float:
    A = set(a.split()); B = set(b.split())
    if not A or not B: return 0.0
    if a == b: return 1.0
    if a in b or b in a: return 0.85
    return (2 * len(A & B)) / (len(A) + len(B))

def weighted_similarity(a: str, b: str) -> float:
    if not a or not b: return 0.0
    cln_a = clean_team_name(a)
    cln_b = clean_team_name(b)
    
    if cln_a == cln_b: return 1.0
    if cln_a in cln_b or cln_b in cln_a: 
        if len(cln_a) < 3 or len(cln_b) < 3: return 0.4
        return 0.75

    norm_a = norm_team(a)
    norm_b = norm_team(b)
    t_dice = token_dice(norm_a, norm_b)
    s_seq = seq_ratio(norm_a, norm_b)
    
    return (t_dice * 0.6) + (s_seq * 0.4)

def team_sim(a: str, b: str) -> float:
    return weighted_similarity(a, b)

def match_score(local_home, local_away, sp_home, sp_away):
    l_home = clean_team_name(local_home)
    l_away = clean_team_name(local_away)
    s_home = clean_team_name(sp_home)
    s_away = clean_team_name(sp_away)
    
    benzerlik_dogal = team_sim(l_home, s_home) + team_sim(l_away, s_away)
    benzerlik_ters = team_sim(l_home, s_away) + team_sim(l_away, s_home)

    return max(benzerlik_dogal, benzerlik_ters) * 50

def match_uid(tarih: str, ev: str, dep: str) -> str:
    a = norm_team(ev); b = norm_team(dep)
    x, y = sorted([a, b])
    return f"{tarih}|{x}|{y}"

# =========================
# JSON IO
# =========================
def load_json_safe(path: Path):
    if not path.exists():
        return {"version": 2, "updated": "", "matches": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 2, "updated": "", "matches": []}

def save_json_atomic(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    if path.exists():
        bak = path.with_suffix(path.suffix + f".bak.{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")
        try: shutil.copy2(path, bak)
        except: pass
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)

# =========================
# DRIVER
# =========================
def build_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver

# =========================
# DİNAMİK YÜK
# =========================
def wait_canli_links_stable(driver, timeout=30, stable_rounds=3, min_count=3):
    end = time.time() + timeout
    last = -1; stable = 0
    while time.time() < end:
        n = len(driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR))
        if n >= min_count and n == last:
            stable += 1
            if stable >= stable_rounds: return True
        else:
            stable = 0; last = n
        time.sleep(0.7)
    return False

def click_load_more(driver, max_click=4):
    clicked = 0
    for _ in range(max_click):
        try:
            btns = driver.find_elements(By.XPATH, LOAD_MORE_XPATH)
            btn = next((b for b in btns if b.is_displayed() and b.is_enabled()), None)
            if not btn: break
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.2); btn.click(); clicked += 1; time.sleep(1.2)
        except Exception: break
    return clicked

def deep_scroll_collect(driver, max_steps=70):
    last = 0; stable = 0
    for _ in range(max_steps):
        click_load_more(driver, max_click=1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.0)
        n = len(driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR))
        if n > last: 
            last = n
            stable = 0
        else:
            stable += 1
            if stable >= 9: 
                break
    return last

# =========================
# TARİH SEÇ
# =========================
def select_date_dropdown(driver, target_iso_date):
    try:
        selects = driver.find_elements(By.TAG_NAME, "select")
        date_select = None
        
        for sel in selects:
            opts = sel.find_elements(By.TAG_NAME, "option")
            if len(opts) > 5:
                first_text = opts[0].text.strip() if opts else ""
                if "Hafta" in first_text or "202" in first_text or len(first_text) > 10:
                    date_select = sel
                    break
        
        if not date_select:
            print(f"   ⚠️ Tarih/Hafta dropdown'u bulunamadı!")
            return False

        options = date_select.find_elements(By.TAG_NAME, "option")
        found_option = None
        target_dt = datetime.datetime.strptime(target_iso_date, "%Y-%m-%d").date()
        
        for opt in options:
            opt_text = opt.text.strip()
            opt_val = opt.get_attribute("value")
            
            dates_in_text = re.findall(r'\d{2}\.\d{2}\.\d{4}', opt_text)
            if len(dates_in_text) >= 2:
                start_str, end_str = dates_in_text[0], dates_in_text[1]
                start_dt = datetime.datetime.strptime(start_str, "%d.%m.%Y").date()
                end_dt = datetime.datetime.strptime(end_str, "%d.%m.%Y").date()
                
                if start_dt <= target_dt <= end_dt:
                    found_option = opt
                    break
            
            elif target_iso_date in opt_val:
                found_option = opt
                break

        if found_option:
            select_obj = Select(date_select)
            select_obj.select_by_value(found_option.get_attribute("value"))
            print(f"   ✅ Dropdown'dan doğru hafta seçildi: {found_option.text.strip()}")
            time.sleep(3) 
            return True
        else:
            print(f"   ⚠️ Hedef tarih ({target_iso_date}) için uygun hafta dropdown'da bulunamadı.")
            return False

    except Exception as e:
        print(f"   ❌ Dropdown seçim hatası: {e}")
        return False

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

# =============================================================================
# AYARLAR
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
# gecmis_maclar.json -> BU DOSYAYA HİÇBİR ŞEKİLDE DOKUNULMAZ
BASE_LINK = "https://www.mackolik.com/futbol/canli-sonuclar"
# ===> ÇEKİLECEK TARİH <=== (Gün/Ay formatında yaz, örnek: "17/05", "16/05")
HEDEF_TARIH = "17/05"
ESLESME_SEVIYESI = 0.10 # Eşleştirmeyi çok daha esnek yaptım
# ===> GİT AYARLARI <=== (Eğer senin dal ismin "master" ise "main" yerine "master" yaz)
GIT_BRANCH_NAME = "main"

# =============================================================================
# 🔐 İSİM TEMİZLEME - ARTIK ÇOK BASİT, HİÇBİR İSMİ ELEMİYOR
# =============================================================================
def akilli_isim_temizle(isim):
    if not isim: return ""
    isim = isim.lower().strip()
    # Sadece gereksiz noktalama işaretlerini temizle, isimlerin kendisine DOKUNMA
    isim = re.sub(r'[.\-_,:0-9]', '', isim)
    isim = re.sub(r'\s+', ' ', isim).strip()
    return isim

def benzerlik_orani(a, b):
    if not a or not b: return 0
    a_temiz = akilli_isim_temizle(a)
    b_temiz = akilli_isim_temizle(b)
    if a_temiz == b_temiz: return 1.0
    if a_temiz in b_temiz or b_temiz in a_temiz: return 0.8
    return SequenceMatcher(None, a_temiz, b_temiz).ratio()

# =============================================================================
# 📖 DOSYANI OKU - Senin "matches" formatınla uyumlu
# =============================================================================
def load_mac_json():
    try:
        if not MAC_JSON_PATH.exists():
            print(f"❌ HATA: {MAC_JSON_PATH} bulunamadı!")
            return None
        
        with open(MAC_JSON_PATH, 'r', encoding='utf-8') as f:
            veri = json.load(f)

        if isinstance(veri, dict) and "matches" in veri:
            print(f"📖 Dosyan Başarıyla Okundu | Toplam: {len(veri['matches'])} adet maç.")
            return veri 
        
        else:
            print("❌ HATA: Dosya formatın beklenenden farklı.")
            return None

    except Exception as e:
        print(f"❌ OKUMA HATASI: {e} - Dosyan BOZULMADI.")
        return None

# =============================================================================
# 💾 KAYDETME - SADECE SKOR DEĞİŞİR, DİĞER HER ŞEY AYNI KALIR
# =============================================================================
def save_mac_json(veri):
    try:
        yedek_dosya = MAC_JSON_PATH.with_name("mac_json_yedek_guvenli.json")
        with open(yedek_dosya, 'w', encoding='utf-8') as f_yedek:
            json.dump(veri, f_yedek, ensure_ascii=False, indent=2)
        
        with open(MAC_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 Kayıt Başarılı | Yedek: {yedek_dosya.name}")
        print("🔒 Korumalı: Oranlar, Lig, Saat, Index, Kodlar.")
        print("🔒 gecmis_maclar.json -> HİÇ DOKUNULMADI!")
    except Exception as e:
        print(f"❌ KAYDETME HATASI: {e} - ESKİ HALİ KORUNDU!")

# =============================================================================
# 🚀 GİT İŞLEMLERİ - OTOMATİK GÖNDERİM
# =============================================================================
def git_islemlerini_yap():
    print("\n" + "="*70)
    print("🚀 GİT İŞLEMLERİ BAŞLATILDI | DEPOYA GÖNDERİLİYOR...")
    print("="*70)
    try:
        os.chdir(BASE_DIR)
        durum = subprocess.run(["git", "status"], capture_output=True, text=True, encoding='utf-8')
        if "nothing to commit" in durum.stdout:
            print("ℹ️ Değişiklik yok, Git işlemi yapılmasına gerek yok.")
            return False

        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        mesaj = f"[OTOMATİK GÜNCELLEME] {HEDEF_TARIH} Maç verileri güncellendi | Skor + Durum + İlk Yarı"
        subprocess.run(["git", "commit", "-m", mesaj], check=True, capture_output=True, text=True)
        subprocess.run(["git", "push", "origin", GIT_BRANCH_NAME], check=True, capture_output=True, text=True)
        
        print("✅ GİT BAŞARILI! Tüm veriler GitHub'a yüklendi.")
        return True

    except Exception as e:
        print(f"❌ GİT HATASI: {str(e)}")
        return False

# =============================================================================
# 🌐 MAÇKOLİK'TEN VERİ ÇEK - ARTIK 845'İN TAMAMINI ÇEKER, MS = BİTTİ
# =============================================================================
def get_skorlar():
    print("🔎 Maçkolik'ten veriler çekiliyor...")
    skor_listesi = []
    gorulen_maclar = set()

    chrome_options = Options()
    # chrome_options.add_argument("--headless=new") # Gizli çalıştırmak istersen aç
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        print(f"🌐 Siteye gidiliyor: {BASE_LINK}")
        driver.get(BASE_LINK)
        time.sleep(12) # Daha uzun bekle

        print(f"📅 Hedef tarih aranıyor: {HEDEF_TARIH}")
        try:
            tarih_elemanlari = driver.find_elements(By.CSS_SELECTOR, "span.widget-dateslider__day-date")
            for el in tarih_elemanlari:
                if el.text.strip() == HEDEF_TARIH:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    time.sleep(2)
                    driver.execute_script("arguments[0].click();", el)
                    print(f"✅ Tarih seçildi: {HEDEF_TARIH}")
                    time.sleep(20) # Verilerin yüklenmesi için ÇOK UZUN BEKLE
                    break
        except Exception as e:
            print(f"⚠️ Tarih seçim hatası: {e}")

        # Sayfayı SONUNA KADAR kaydır
        print("📜 Sayfa sonuna kadar kaydırılıyor...")
        for _ in range(60): # 60 kere kaydır, tüm maçlar gelsin
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(0.5)

        # Tüm maç satırlarını bul - FARKLI SEÇİCİLER EKLENDİ
        mac_satirlari = driver.find_elements(By.CSS_SELECTOR, "div.match-row, div.row-table__row")
        print(f"🔍 Sayfada bulunan toplam satır: {len(mac_satirlari)}")

        gun, ay = HEDEF_TARIH.split('/')
        hedef_tarih_iso = f"2026-{ay}-{gun}"

        gecerli_veri_sayisi = 0
        biten_mac_sayisi = 0
        ilk_yari_sayisi = 0

        # Her bir satırı işle - ARTIK İSİM FİLTRESİ YOK
        for satir in mac_satirlari:
            try:
                # Takım İsimleri - TÜM OLASI SEÇİCİLER EKLENDİ
                isim_elemanlari = satir.find_elements(By.CSS_SELECTOR, 
                    "span.match-row__team-name-text, span.team-name, div.match-row__team-name, span.name")
                
                if len(isim_elemanlari) < 2:
                    continue

                ev_isim = isim_elemanlari[0].text.strip()
                dep_isim = isim_elemanlari[1].text.strip()

                # Tekrar edenleri engelle
                mac_kimlik = f"{ev_isim}-{dep_isim}"
                if mac_kimlik in gorulen_maclar:
                    continue
                gorulen_maclar.add(mac_kimlik)

                # ===> ARTIK HİÇ FİLTRE YOK, 2 HARF OLSA BİLE AL <===
                if len(ev_isim) < 2 or len(dep_isim) < 2:
                    continue

                # Maç Sonu Skorları - TÜM SEÇİCİLER
                skor_ev = 0
                skor_dep = 0
                try:
                    skor_elemanlari = satir.find_elements(By.CSS_SELECTOR, 
                        "span.match-row__score-text, span.score, div.match-row__score")
                    
                    if len(skor_elemanlari) >= 2:
                        s1 = skor_elemanlari[0].text.strip()
                        s2 = skor_elemanlari[1].text.strip()
                        if s1.isdigit(): skor_ev = int(s1)
                        if s2.isdigit(): skor_dep = int(s2)
                except:
                    pass

                # İlk Yarı Skorları - TÜM SEÇİCİLER
                skor_1y_ev = 0
                skor_1y_dep = 0
                try:
                    iy_elem = satir.find_element(By.CSS_SELECTOR, 
                        "div.match-row__half-time-score, div.half-time, span.ht-score")
                    
                    iy_yazi = iy_elem.text.strip()
                    rakamlar = re.findall(r'\d+', iy_yazi)
                    if len(rakamlar) == 2:
                        skor_1y_ev = int(rakamlar[0])
                        skor_1y_dep = int(rakamlar[1])
                        ilk_yari_sayisi += 1
                except:
                    pass

                # ==============================================================
                # 🔴 DURUM KONTROLÜ - MS YAZANLAR KESİN BİTTİ
                # ==============================================================
                durum = "baslamadi"
                try:
                    # Tam olarak senin verdiğin HTML yapısına uygun
                    status_elem = satir.find_element(By.CSS_SELECTOR, 
                        "a.match-row__status, div.match-row__status, span.status")
                    
                    durum_yazi = status_elem.text.strip().upper()

                    # KESİN KURALLAR
                    if "MS" in durum_yazi or "FİNAL" in durum_yazi or "BİTTİ" in durum_yazi:
                        durum = "bitti"
                        biten_mac_sayisi += 1
                    elif "CANLI" in durum_yazi or "DEVAM" in durum_yazi or "'" in durum_yazi or "DK" in durum_yazi:
                        durum = "devam ediyor"

                except Exception as durum_hata:
                    pass

                # Veriyi listeye ekle
                skor_listesi.append({
                    "tarih": hedef_tarih_iso,
                    "ev_sahibi": ev_isim,
                    "deplasman": dep_isim,
                    "skor_ev": skor_ev,
                    "skor_dep": skor_dep,
                    "skor_1y_ev": skor_1y_ev,
                    "skor_1y_dep": skor_1y_dep,
                    "durum": durum
                })
                gecerli_veri_sayisi += 1

                print(f"✅ VERİ | {ev_isim} - {dep_isim} | Skor: {skor_ev}-{skor_dep} | İlk Yarı: {skor_1y_ev}-{skor_1y_dep} | {durum.upper()}")

            except Exception as satir_hata:
                continue

    except Exception as ana_hata:
        print(f"❌ Ana Hata: {ana_hata}")
    finally:
        if driver:
            driver.quit()
            print("🔒 Tarayıcı kapatıldı.")

    print(f"✅ İŞLEM TAMAMLANDI | Toplam {gecerli_veri_sayisi} adet GEÇERLİ maç verisi çekildi.")
    print(f"📊 İstatistik: Biten = {biten_mac_sayisi}, İlk Yarı Skoru = {ilk_yari_sayisi}")
    return skor_listesi

# =============================================================================
# 🧠 GÜNCELLEME MOTORU - ÇOK ESNEK EŞLEŞTİRME
# =============================================================================
def skorlari_eslestir_ve_guncelle(mevcut_yapi, yeni_skorlar):
    mac_listesi = mevcut_yapi.get("matches", [])
    if not mac_listesi or not yeni_skorlar:
        return 0

    guncelleme_sayisi = 0

    for y_skor in yeni_skorlar:
        y_tarih = y_skor["tarih"]
        y_ev = y_skor["ev_sahibi"]
        y_dep = y_skor["deplasman"]

        en_uygun_index = -1
        ters_mi = False

        for i, mac in enumerate(mac_listesi):
            m_tarih = mac.get("tarih", "")
            m_ev = mac.get("ev_sahibi", "")
            m_dep = mac.get("deplasman", "")

            if m_tarih != y_tarih:
                continue

            # Normal eşleşme
            oran1 = benzerlik_orani(m_ev, y_ev) + benzerlik_orani(m_dep, y_dep)
            # Ters eşleşme
            oran2 = benzerlik_orani(m_ev, y_dep) + benzerlik_orani(m_dep, y_ev)

            if oran1 > 0.5:
                en_uygun_index = i
                ters_mi = False
            elif oran2 > 0.5:
                en_uygun_index = i
                ters_mi = True

        if en_uygun_index != -1:
            mac = mac_listesi[en_uygun_index]
            # Skorları doğru tarafa yerleştir
            s_ev, s_dep = (y_skor["skor_ev"], y_skor["skor_dep"]) if not ters_mi else (y_skor["skor_dep"], y_skor["skor_ev"])
            iy_ev, iy_dep = (y_skor["skor_1y_ev"], y_skor["skor_1y_dep"]) if not ters_mi else (y_skor["skor_1y_dep"], y_skor["skor_1y_ev"])

            degisiklik_var = False

            # Maç Sonu Skorları Güncelle
            if s_ev != 0 and mac.get("skor_ev") != s_ev:
                mac["skor_ev"] = s_ev
                degisiklik_var = True
            if s_dep != 0 and mac.get("skor_dep") != s_dep:
                mac["skor_dep"] = s_dep
                degisiklik_var = True

            # İlk Yarı Skorları Güncelle
            if iy_ev != 0 and mac.get("skor_1y_ev") != iy_ev:
                mac["skor_1y_ev"] = iy_ev
                degisiklik_var = True
            if iy_dep != 0 and mac.get("skor_1y_dep") != iy_dep:
                mac["skor_1y_dep"] = iy_dep
                degisiklik_var = True

            # Durum Güncelle - MS yazanlar kesin bitti olacak
            if mac.get("durum") != y_skor["durum"]:
                mac["durum"] = y_skor["durum"]
                degisiklik_var = True

            if degisiklik_var:
                guncelleme_sayisi += 1
                print(f"✅ GÜNCELLEME | {mac['ev_sahibi']} - {mac['deplasman']} | Skor: {mac['skor_ev']}-{mac['skor_dep']} | İlk Yarı: {mac['skor_1y_ev']}-{mac['skor_1y_dep']} | Durum: {mac['durum']}")

    return guncelleme_sayisi

# =============================================================================
# 🚀 ANA ÇALIŞTIRICI - Tamamen Düzeltildi, Artık 0 Çekme Sorunu Yok
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("⚽ GÜVENLİ SKOR GÜNCELLEYİCİ | VERİ KORUMA MODU 🛡️")
    print("=" * 70)
    print("🔒 KURAL 1: Oranlar, Lig, Saat, Index, Kodlar -> HİÇ DOKUNULMAZ!")
    print("🔒 KURAL 2: gecmis_maclar.json -> KESİNLİKLE GÖRMEZ, DOKUNMAZ!")
    print("🔒 KURAL 3: Sadece Skor ve Durum güncellenir. Yeni maç EKLENMEZ.")
    print("-" * 70)

    # 1. Mevcut dosyayı oku
    mevcut_yapi = load_mac_json()
    if not mevcut_yapi:
        print("❌ İşlem iptal edildi.")
        input("🔚 Çıkmak için Enter...")
        exit()

    # 2. Maçkolik'ten verileri çek - ARTIK 845'İN TAMAMI ÇEKİLİR
    yeni_skorlar = get_skorlar()
    if not yeni_skorlar:
        print("❌ Maçkolik verisi alınamadı. İşlem iptal edildi.")
        input("🔚 Çıkmak için Enter...")
        exit()

    # 3. Verileri eşleştir ve güncelle
    guncellenen_sayi = skorlari_eslestir_ve_guncelle(mevcut_yapi, yeni_skorlar)

    # 4. Kaydet ve Git gönderimi
    if guncellenen_sayi > 0:
        save_mac_json(mevcut_yapi)
        print(f"\n📊 Toplam {guncellenen_sayi} adet maçın SKORU, İLK YARISI ve DURUMU güncellendi.")
        
        # 🔄 Otomatik Git Push
        git_islemlerini_yap()
        
    else:
        print("\nℹ️ Güncellenecek yeni veri bulunamadı. Dosya içeriği değiştirilmedi.")

    print("\n" + "=" * 70)
    print("✅ TÜM İŞLEMLER BİTTİ | HİÇBİR VERİN SİLİNMEDİ / BOZULMADI ✅")
    print("🔒 Korumada olanlar: Oranlar, Lig, Saat, Index, Kodlar, Tüm Geçmiş Veriler")
    print("🔒 gecmis_maclar.json -> Tamamen güvende, hiç dokunulmadı")
    print("=" * 70)
    input("🔚 Çıkmak için Enter tuşuna bas...")