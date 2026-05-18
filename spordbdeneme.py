import json, os, re, time, datetime, traceback, shutil, unicodedata
from pathlib import Path
from difflib import SequenceMatcher

# =========================
# 🔴 GELİŞTİRİLMİŞ TAKIM İŞLEMLERİ
# =========================
def clean_team_name(name):
    if not name: return ""
    n = name.lower().strip()
    
    gurtu_kelimeler = {"bra", "isp", "isl", "fın", "pol", "bul", "isc", "rom", "svc", "irl", "inp", "izl", "sili", "bol", "ukr", "urug", "sin", "p"}
    if n in gurtu_kelimeler:
        return ""

    prefixes = ["ad ", "cd ", "ca ", "fc ", "ac ", "sc ", "us ", "ud ", "fk ", "sk ", "jk ", "bk ", "as ", "al ", "el ", "da ", "de ",
        "real ", "athletic ", "atletico ", "deportivo ", "club ", "kulübü ", "spor "]
    suffixes = [" fc", " sc", " ac", " us", " ud", " fk", " sk", " jk", " bk", " as", " ad", " cd", " ca", "spor", "kulübü", "club"]
    
    for p in prefixes:
        if n.startswith(p): n = n[len(p):].strip()
    for s in suffixes:
        if n.endswith(s): n = n[:-len(s)].strip()

    replacements = {"ceuta": "ceuta", "al ain": "alain", "dibba al ain": "dibba", "dibba": "dibba", "ıstanbul": "istanbul"}
    for key, val in replacements.items(): n = n.replace(key, val)
        
    n = n.replace(".", "").replace("-", " ").replace("'", "").replace("’", "")
    n = " ".join(n.split())
    return n.strip() if len(n) > 1 else ""

OZEL_ESLESTIRMELER = {
    "spordb": {"ceuta": "ad ceuta", "al ain": "al ain fc", "dibba": "dibba al ain", "bjk": "besiktas"},
    "macjson": {"ad ceuta": "ceuta", "al ain fc": "al ain", "dibba al ain": "dibba"}
}

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

# =========================
# PATH & AYARLAR
# =========================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
GECMIS_JSON_PATH = BASE_DIR / "public" / "data" / "gecmis_maclar.json"
OUTPUT_SKOR_JSON = BASE_DIR / "public" / "data" / "skorlar_spordb.json"

SPORDB_URL = "https://www.spordb.com/iddaa-programi"

# ✅ ARTIK KOD KENDİSİ LİSTEDEKİ TÜM TARİHLERİ ALACAK, SAYIYA GEREK YOK
DAYS_BACK_FINISHED = 0     
INCLUDE_TODAY = True       

UPDATE_MAC_JSON = True
UPDATE_GECMIS_JSON = True
ADD_MISSING_MATCHES = True  

PAGE_LOAD_TIMEOUT = 60
WAIT_LONG = 20

DATESELECTOR_CSS = "#iddaa_dateselector"
CANLI_LINK_SELECTOR = "a[href*='/canli/'][href*='-maci-']"
CANLI_HREF_RE = re.compile(r"/canli/(?P<id>\d+)/(?P<date>\d{2}-\d{2}-\d{4})-(?P<teams>.+?)-maci-(?P<h>\d+)-(?P<a>\d+)/?$", re.IGNORECASE)

THRESH_OK = 0.70        
THRESH_MAYBE = 0.55
MIN_GAP = 0.10          

# =========================
# NORMALİZASYON
# =========================
_TMAP = str.maketrans({"İ":"i","I":"i","ı":"i","Ş":"s","ş":"s","Ğ":"g","ğ":"g","Ü":"u","ü":"u","Ö":"o","ö":"o","Ç":"c","ç":"c"})
_STOP = {"fk","fc","sk","jk","bk","ac","as","spor","club","kulubu","kulübü","u19","u20","u21","u23","women","reserves","b","ii"}

def _deaccent(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))

def norm_team(s: str) -> str:
    s = (s or "").strip()
    if not s or len(s) < 2: return ""
    s_lower = s.lower()
    if s_lower in OZEL_ESLESTIRMELER["macjson"]: s = OZEL_ESLESTIRMELER["macjson"][s_lower]
    if s_lower in OZEL_ESLESTIRMELER["spordb"]: s = OZEL_ESLESTIRMELER["spordb"][s_lower]

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
    return (2 * len(A & B)) / (len(A) + len(B))

def weighted_similarity(a: str, b: str) -> float:
    if not a or not b: return 0.0
    cln_a = clean_team_name(a)
    cln_b = clean_team_name(b)
    if not cln_a or not cln_b: return 0.0
    if cln_a == cln_b: return 1.0
    if cln_a in cln_b or cln_b in cln_a: return 0.8

    norm_a = norm_team(a); norm_b = norm_team(b)
    if not norm_a or not norm_b: return 0.0
    t_dice = token_dice(norm_a, norm_b)
    s_seq = seq_ratio(norm_a, norm_b)
    return (t_dice * 0.6) + (s_seq * 0.4)

def team_sim(a: str, b: str) -> float:
    return weighted_similarity(a, b)

def match_score(local_home, local_away, sp_home, sp_away):
    if not local_home or not local_away or not sp_home or not sp_away: return 0
    l_home = clean_team_name(local_home); l_away = clean_team_name(local_away)
    s_home = clean_team_name(sp_home); s_away = clean_team_name(sp_away)
    if not l_home or not l_away or not s_home or not s_away: return 0
    
    benzerlik_dogal = team_sim(l_home, s_home) + team_sim(l_away, s_away)
    benzerlik_ters = team_sim(l_home, s_away) + team_sim(l_away, s_home)
    return max(benzerlik_dogal, benzerlik_ters) * 50

def match_uid(tarih: str, ev: str, dep: str) -> str:
    a = norm_team(ev); b = norm_team(dep)
    if not a or not b: return ""
    x, y = sorted([a, b])
    return f"{tarih}|{x}|{y}"

# =========================
# JSON IO - HATASIZ KAYDETME
# =========================
def load_json_safe(path: Path):
    if not path.exists(): return {"version": 2, "updated": "", "matches": []}
    try: return json.loads(path.read_text(encoding="utf-8"))
    except: return {"version": 2, "updated": "", "matches": []}

def save_json_atomic(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    
    # ✅ NULL / UNDEFINED HATASINI KES
    def temizle(obj):
        if isinstance(obj, dict):
            return {k: temizle(v) for k, v in obj.items() if v is not None}
        elif isinstance(obj, list):
            return [temizle(o) for o in obj if o is not None]
        return obj if obj is not None else ("" if isinstance(obj, (str, type(None))) else 0)
    
    veri = temizle(data)
    tmp.write_text(json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8")
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
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver

# =========================
# DİNAMİK YÜK
# =========================
def wait_canli_links_stable(driver, timeout=20, min_count=0):
    try:
        end = time.time() + timeout
        last_count = -1
        while time.time() < end:
            current_count = len(driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR))
            if current_count == last_count and current_count >= min_count:
                time.sleep(0.5)
                return True
            last_count = current_count
            time.sleep(0.5)
        return False
    except: return False

def deep_scroll_collect(driver):
    for _ in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)

# =========================
# TARİH SEÇİMİ & LİSTE OKUMA
# =========================
def get_all_available_dates(driver):
    """Açılır listedeki TÜM tarihleri okur ve liste olarak döner."""
    try:
        date_select_el = driver.find_element(By.CSS_SELECTOR, DATESELECTOR_CSS)
        select = Select(date_select_el)
        tarihler = []
        for opt in select.options:
            val = opt.get_attribute("value")
            text = opt.text
            if val != "*": # "Hepsi" seçeneğini geç, sadece günleri al
                tarihler.append( (val, text) ) # (tarih_kodu, görüntü_metni)
        print(f"📋 Sitede bulunan tarihler: {[t[1] for t in tarihler]}")
        return tarihler
    except Exception as e:
        print(f"❌ Tarih listesi okunamadı: {e}")
        return []

def select_date_dropdown(driver, target_iso_date):
    try:
        date_select = driver.find_element(By.CSS_SELECTOR, DATESELECTOR_CSS)
        select = Select(date_select)

        found = False
        for opt in select.options:
            val = opt.get_attribute("value")
            if val == target_iso_date:
                select.select_by_value(val)
                print(f"   ✅ Tarih Seçildi: {opt.text} -> {target_iso_date}")
                found = True
                break
        
        if not found:
            print(f"   ❌ Tarih seçilemedi! {target_iso_date}")
            return False

        # Sayfanın yüklenmesi için bekle
        time.sleep(2.5)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return True

    except Exception as e:
        print(f"   ❌ Tarih Seçim Hatası: {str(e)}")
        return False

# =========================
# SPORDB PARSE
# =========================
_ODDS_RE = re.compile(r"^\d+([.,]\d+)?$")

def _is_noise_text(t: str) -> bool:
    t = (t or "").strip()
    if not t: return True
    if re.fullmatch(r"\d{1,2}:\d{2}", t): return True
    if re.fullmatch(r"\d+\s*-\s*\d+", t): return True
    if _ODDS_RE.fullmatch(t):
        try:
            v = float(t.replace(",", "."))
            if 1.0 <= v <= 99.99: return True
        except: pass
    if t.isdigit(): return True
    if len(t) <= 3 and t.isalpha(): return True
    return False


def parse_spordb_canli(href: str):
    m = CANLI_HREF_RE.search(href or "")
    if not m: return None
    sp_id = m.group("id")
    ddmmyyyy = m.group("date")
    skor1 = int(m.group("h"))
    skor2 = int(m.group("a"))
    
    if skor1 > 9 or skor2 > 9:
        skor1 = skor2 = 0

    try:
        tarih_iso = datetime.datetime.strptime(ddmmyyyy, "%d-%m-%Y").date().isoformat()
    except: return None

    return {
        "spordb_match_id": sp_id, 
        "tarih": tarih_iso, 
        "teams_slug": m.group("teams"), 
        "skor1": skor1, 
        "skor2": skor2,
        "cekme_zamani": datetime.datetime.now().isoformat(), 
        "sp_home": "", 
        "sp_away": "",
        "iy_skor1": 0,
        "iy_skor2": 0
    }


def split_row_cells(driver, a):
    return driver.execute_script("""
        const a = arguments[0]; 
        const cell = a.closest('td,th'); 
        const tr = a.closest('tr');
        if(!cell || !tr) return null;
        const cells = Array.from(tr.querySelectorAll('th,td,div'));
        const idx = cells.indexOf(cell);
        const texts = cells.map(x => (x.innerText || '').trim());
        return { idx, texts };