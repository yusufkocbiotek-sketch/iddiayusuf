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

# =========================
# SPORDB PARSE
# =========================
_ODDS_RE = re.compile(r"^\d+([.,]\d+)?$")

def _is_noise_text(t: str) -> bool:
    t = (t or "").strip()
    if not t: return True
    if re.fullmatch(r"\d{1,2}:\d{2}", t): return True  # Saat bilgisi
    if re.fullmatch(r"\d+\s*-\s*\d+", t): return True  # Skor formatı
    if re.fullmatch(r"[A-Z]{2,6}", t): return True     # Lig kısaltması
    if _ODDS_RE.fullmatch(t):                           # Oran bilgisi
        try:
            v = float(t.replace(",", "."))
            if 1.0 <= v <= 99.99: return True
        except: pass
    if t.isdigit(): return True                         # Saf sayı
    return False                                        # Bunlar dışındakiler takım ismi adayıdır


def parse_spordb_canli(href: str):
    """
    Canlı maç linkinin URL'sinden maç ID, tarih, takım adı ve skorları çıkarır.
    Örnek URL: /canli/12345/18-05-2026-ad-ceuta-real-madrid-maci-1-0/
    """
    m = CANLI_HREF_RE.search(href or "")
    if not m: return None
    
    sp_id = m.group("id")
    ddmmyyyy = m.group("date")
    skor1 = int(m.group("h"))
    skor2 = int(m.group("a"))
    teams_slug = m.group("teams")
    
    try:
        tarih_iso = datetime.datetime.strptime(ddmmyyyy, "%d-%m-%Y").date().isoformat()
    except ValueError:
        return None

    return {
        "spordb_match_id": sp_id, 
        "tarih": tarih_iso, 
        "teams_slug": teams_slug, 
        "skor1": skor1, 
        "skor2": skor2,
        "cekme_zamani": datetime.datetime.now().isoformat(), 
        "sp_home": None, 
        "sp_away": None,
        "iy_skor1": 0,
        "iy_skor2": 0
    }


def split_row_cells(driver, a):
    """
    Maç linkinin bulunduğu satırdaki (tr) tüm hücreleri (td) ve metinleri alır.
    Hangi hücrede link varsa onun indeksini de döner.
    """
    return driver.execute_script("""
        const a = arguments[0]; 
        const cell = a.closest('td,th'); 
        const tr = a.closest('tr');
        if(!cell || !tr) return null;
        const cells = Array.from(tr.querySelectorAll('th,td,div'));
        const idx = cells.indexOf(cell);
        const texts = cells.map(x => (x.innerText || '').trim());
        return { idx, texts };
    """, a)


def pick_home_away(texts, idx):
    """
    Satırdaki metin listesinden gürültüleri (saat, oran, skor) eleyerek
    ev sahibi ve deplasman takım isimlerini bulur.
    """
    # Linkin solundaki hücreleri kontrol et
    left = [t for t in texts[:idx] if t and t.strip()]
    # Linkin sağındaki hücreleri kontrol et
    right = [t for t in texts[idx+1:] if t and t.strip()]
    
    home = None
    # Sağ taraftan geriye doğru, gürültü olmayan ilk değeri al (Ev Sahibi)
    for t in reversed(right):
        if not _is_noise_text(t): 
            home = t.strip()
            break
            
    away = None
    # Sol taraftan ileriye doğru, gürültü olmayan ilk değeri al (Deplasman)
    for t in left:
        if not _is_noise_text(t): 
            away = t.strip()
            break

    # Eğer tam tersi çıktıysa düzeltme denemesi
    if not home and away:
        home, away = away, None
        for t in right:
            if not _is_noise_text(t):
                away = t.strip()
                break

    return home, away


def collect_scores_for_date(driver, iso_date: str):
    """
    Belirtilen tarihe göre tüm maçları, skorları ve takım isimlerini toplayan ana fonksiyon.
    İY ve MS skorlarını doğrular, eksikse detay sayfasından çeker.
    """
    ok = select_date_dropdown(driver, iso_date)
    if not ok: 
        print(f"   ⚠️ {iso_date} tarihi için liste yüklenemedi, atlanıyor.")
        return []

    wait_canli_links_stable(driver, timeout=WAIT_LONG, min_count=3)
    deep_scroll_collect(driver)
    
    links = driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR)
    out = []
    seen = set() # Aynı maçı birden fazla kez çekmeyi engellemek için

    print(f"   🔍 {len(links)} adet link bulundu, analiz ediliyor...")

    for a in links:
        href = a.get_attribute("href") or ""
        item = parse_spordb_canli(href)
        
        # Filtre: Sadece hedef tarihteki maçları al
        if not item or item["tarih"] != iso_date: 
            continue
        
        # Tekrar kontrolü
        unique_key = (item["spordb_match_id"], item["tarih"], item["skor1"], item["skor2"])
        if unique_key in seen: continue
        seen.add(unique_key)

        # Takım isimlerini satır içinden ayıkla
        res = split_row_cells(driver, a)
        if res and res.get("idx") is not None:
            texts = res.get("texts", [])
            h, aw = pick_home_away(texts, res["idx"])
            item["sp_home"], item["sp_away"] = h, aw

            # ==========================================
            # 🛡️ SKOR GÜVENLİK KONTROLÜ (MS ve İY)
            # ==========================================
            url_ms_h = item.get('skor1', 0)
            url_ms_a = item.get('skor2', 0)
            need_ms_check = (url_ms_h == 0 and url_ms_a == 0) # URL'den skor gelmemiş mi?
            iy_bulundu = False
            found_scores = []

            try:
                row_element = a.find_element(By.XPATH, "./ancestor::tr")
                all_cells = row_element.find_elements(By.TAG_NAME, "td")

                # Tüm hücrelerde skor formatı ara (örn: "2-1", "1:0")
                for cell in all_cells:
                    txt = cell.text.strip()
                    # Sadece makul skor aralıklarını kabul et
                    if re.match(r"^\d+[-:]\d+$", txt):
                        parts = txt.replace(":", "-").split("-")
                        if len(parts) == 2:
                            try:
                                s1, s2 = int(parts[0]), int(parts[1])
                                if s1 < 15 and s2 < 15: # Çok yüksek sayıları eler
                                    found_scores.append((s1, s2))
                            except: pass

                # 1. Eğer URL'de skor yoksa, ilk bulunan skoru MS olarak kabul et
                if need_ms_check and len(found_scores) > 0:
                    item['skor1'], item['skor2'] = found_scores[0]
                    found_scores.pop(0) # MS'yi listeden çıkar, kalanlar İY veya diğer detaylar olabilir

                # 2. Kalanlardan ilkini İY olarak kabul et
                if len(found_scores) > 0:
                    item["iy_skor1"], item["iy_skor2"] = found_scores[0]
                    iy_bulundu = True

            except Exception as e:
                pass # Satır okuma hatası olursa detaya inmeyi deneyeceğiz

            # ==========================================
            # 🕵️ DETAY SAYFASINDAN VERİ ÇEKME (Gerekirse)
            # ==========================================
            # Eğer hala İY skoru yoksa veya 0-0 ise detay sayfasını aç
            if (item.get("iy_skor1", 0) == 0 and item.get("iy_skor2", 0) == 0) or not iy_bulundu:
                try:
                    driver.execute_script("window.open(arguments[0], '_blank');", href)
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(3) # Sayfanın yüklenmesini bekle

                    full_text = driver.find_element(By.TAG_NAME, "body").text
                    # Farklı dillerdeki İY ifadelerini ara
                    pattern = r"(?:İY|Ilk Yari|First Half|Half Time|HT|Devre Arası|1\. Yarı)[:\s]*(\d+)\s*[-:]\s*(\d+)"
                    match = re.search(pattern, full_text, re.IGNORECASE)

                    if match:
                        s1, s2 = int(match.group(1)), int(match.group(2))
                        if s1 < 10 and s2 < 10:
                            item["iy_skor1"], item["iy_skor2"] = s1, s2
                            iy_bulundu = True

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception:
                    # Hata durumunda sekmeyi kapatmayı dene
                    try:
                        if len(driver.window_handles) > 1:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                    except: pass

            # ==========================================
            # 📢 TERMİNAL BİLGİLENDİRME
            # ==========================================
            ms_h, ms_a = item['skor1'], item['skor2']
            iy_h, iy_a = item.get('iy_skor1', 0), item.get('iy_skor2', 0)
            
            # Özellikle eşleşme sorunu yaşadığın takımları burada takip edebilirsin
            debug_name = f"{item['sp_home']} - {item['sp_away']}".lower()
            if "ceuta" in debug_name or "al ain" in debug_name or "dibba" in debug_name:
                print(f"🎯 HEDEF MAÇ: {item['sp_home']} vs {item['sp_away']} | MS: {ms_h}-{ms_a} | İY: {iy_h}-{iy_a}")
            else:
                print(f"✅ {item['sp_home']} vs {item['sp_away']} -> MS: {ms_h}-{ms_a} | İY: {iy_h}-{iy_a}")

        # Geçerli takım ismi olanları listeye ekle
        if item["sp_home"] and item["sp_away"]: 
            out.append(item)

    return out

# =========================
# UPDATE ENGINE
# =========================
def update_db(db_data: dict, scores: list, today_iso: str):
    matches = db_data.get("matches", [])
    if not isinstance(matches, list): 
        matches = []
        db_data["matches"] = matches
    
    uid_set = set()
    for m in matches:
        if m.get("tarih") and m.get("ev_sahibi") and m.get("deplasman"):
            uid_set.add(match_uid(m["tarih"], m["ev_sahibi"], m["deplasman"]))
    
    by_date = {}
    for m in matches:
        if m.get("tarih"): 
            by_date.setdefault(m["tarih"], []).append(m)
    
    matched = updated = noop = added = skipped = not_matched = 0
    
    for sp in scores:
        cands = by_date.get(sp["tarih"], [])
        best = None
        best_sc = -1.0
        second_sc = -1.0
        
        for m in cands:
            sc = match_score(m.get("ev_sahibi",""), m.get("deplasman",""), sp["sp_home"], sp["sp_away"])
            if sc > best_sc: 
                second_sc = best_sc
                best_sc = sc
                best = m
            elif sc > second_sc: 
                second_sc = sc
        
        # Eşleşme kriteri: En yüksek puan yeterli ve ikinciden belirgin fark varsa
        if best and best_sc >= THRESH_MAYBE and (best_sc - second_sc) >= MIN_GAP:
            if best_sc >= THRESH_OK:
                matched += 1
                
                # Ev/Dep eşleşme kontrolü (Saha ters mi?)
                s_direct = team_sim(best.get("ev_sahibi",""), sp["sp_home"]) + team_sim(best.get("deplasman",""), sp["sp_away"])
                s_swap = team_sim(best.get("ev_sahibi",""), sp["sp_away"]) + team_sim(best.get("deplasman",""), sp["sp_home"])
                
                # MS Skorlarını belirle
                skor_ev, skor_dep = (sp["skor2"], sp["skor1"]) if s_swap > s_direct else (sp["skor1"], sp["skor2"])

                # --- İY SKORLARINI GÜNCELLE (Varsa) ---
                iy_ev = sp.get("iy_skor1") 
                iy_dep = sp.get("iy_skor2")
                
                if iy_ev is not None and iy_dep is not None:
                    # Eğer saha tersse İY skorları da ters düşer
                    if s_swap > s_direct:
                        best["skor_1y_ev"] = int(iy_dep)
                        best["skor_1y_dep"] = int(iy_ev)
                    else:
                        best["skor_1y_ev"] = int(iy_ev)
                        best["skor_1y_dep"] = int(iy_dep)

                # Değişiklik var mı?
                changed = (best.get("skor_ev") != skor_ev or 
                           best.get("skor_dep") != skor_dep or 
                           best.get("spordb_match_id") != sp["spordb_match_id"])
                
                # Veritabanını güncelle
                best["skor_ev"] = skor_ev
                best["skor_dep"] = skor_dep
                best["durum"] = "bitti"
                best["spordb_match_id"] = sp["spordb_match_id"]
                best["kaynak"] = "spordb.com"
                best["cekme_zamani"] = sp["cekme_zamani"]
                
                if changed: 
                    updated += 1
                else: 
                    noop += 1
                continue
            
            skipped += 1
            continue        

        # EŞLEŞME BAŞARISIZ - DEBUG BİLGİSİ
        if not best or best_sc < THRESH_MAYBE:
            print(f"⚠️ EŞLEŞMEDİ: SPORDB='{sp['sp_home']} vs {sp['sp_away']}' | Tarih={sp['tarih']} | Skor={sp['skor1']}-{sp['skor2']}")
            cands = by_date.get(sp["tarih"], [])
            if cands:
                aday_listesi = [f"{m['ev_sahibi']} vs {m['deplasman']}" for m in cands[:3]]
                print(f"   -> Adaylar: {aday_listesi}") 
            else:
                print(f"   -> O tarihte hiç maç yok!")

        # Eğer eşleşen maç bulunamadıysa ve yeni maç ekleme özelliği açıksa ekle
        if ADD_MISSING_MATCHES:
            uid = match_uid(sp["tarih"], sp["sp_home"], sp["sp_away"])
            if uid not in uid_set:
                matches.append({
                    "index": 0, 
                    "mac_kodu": "", 
                    "ev_sahibi": sp["sp_home"], 
                    "deplasman": sp["sp_away"], 
                    "saat": "", 
                    "lig": "", 
                    "tarih": sp["tarih"], 
                    "cekme_zamani": sp["cekme_zamani"], 
                    "durum": "bitti", 
                    "skor_ev": sp["skor1"], 
                    "skor_dep": sp["skor2"], 
                    "skor_1y_ev": sp.get("iy_skor1", 0), 
                    "skor_1y_dep": sp.get("iy_skor2", 0),
                    "spordb_match_id": sp["spordb_match_id"],
                    "kaynak": "spordb.com - eklendi"
                })
                uid_set.add(uid)
                added += 1
                print(f"➕ YENİ MAÇ EKLENDİ: {sp['sp_home']} - {sp['sp_away']} ({sp['tarih']})")
            else:
                skipped += 1
        else:
            not_matched += 1

    # İstatistikleri yazdır
    print(f"\n📊 ÖZET: Eşleşti={matched} | Güncellendi={updated} | Değişmedi={noop} | Eklendi={added} | Eşleşemedi={not_matched} | Atlandı={skipped}")
    db_data["updated"] = datetime.datetime.now().isoformat()
    return db_data


# =========================
# ANA ÇALIŞTIRMA FONKSİYONU
# =========================
def main():
    print("="*60)
    print("📢 SPORDB SKOR ÇEKME & GÜNCELLEME BAŞLADI")
    print("="*60)

    # Tarih hesaplamaları
    today = datetime.date.today()
    dates_to_process = []

    if INCLUDE_TODAY:
        dates_to_process.append(today.isoformat())

    for bk in range(1, DAYS_BACK_FINISHED + 1):
        dates_to_process.append((today - datetime.timedelta(days=bk)).isoformat())

    print(f"📅 İşlenecek tarihler: {dates_to_process}")

    # Driver başlat
    driver = None
    try:
        driver = build_driver()
        driver.get(SPORDB_URL)
        WebDriverWait(driver, WAIT_LONG).until(EC.presence_of_element_located((By.CSS_SELECTOR, DATESELECTOR_CSS)))
        print("✅ Sayfa yüklendi, işleme başlanıyor...")

        all_scores = []
        for iso_date in dates_to_process:
            print(f"\n" + "-"*50)
            print(f"⏳ Tarih işleniyor: {iso_date}")
            print("-"*50)
            scores = collect_scores_for_date(driver, iso_date)
            all_scores.extend(scores)
            # Her tarihten sonra ana sayfaya geri dön
            driver.get(SPORDB_URL)
            time.sleep(2)

        # Ham skor verisini yedekle
        save_json_atomic({"updated": datetime.datetime.now().isoformat(), "scores": all_scores}, OUTPUT_SKOR_JSON)
        print(f"💾 Ham veriler kaydedildi: {OUTPUT_SKOR_JSON}")

        # Ana JSON dosyasını güncelle
        if UPDATE_MAC_JSON:
            print("\n🔄 mac.json dosyası güncelleniyor...")
            mac_data = load_json_safe(MAC_JSON_PATH)
            updated_data = update_db(mac_data, all_scores, today.isoformat())
            save_json_atomic(updated_data, MAC_JSON_PATH)
            print(f"✅ Güncel mac.json kaydedildi: {MAC_JSON_PATH}")

        # Geçmiş maçlar dosyasını güncelle
        if UPDATE_GECMIS_JSON:
            print("\n📁 gecmis_maclar.json güncelleniyor...")
            gecmis_data = load_json_safe(GECMIS_JSON_PATH)
            updated_gecmis = update_db(gecmis_data, all_scores, today.isoformat())
            save_json_atomic(updated_gecmis, GECMIS_JSON_PATH)
            print(f"✅ Güncel gecmis_maclar.json kaydedildi: {GECMIS_JSON_PATH}")

    except Exception as e:
        print(f"❌ KRİTİK HATA: {e}")
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
        print("\n✅ TÜM İŞLEMLER TAMAMLANDI.")


# Programı çalıştır - BU KISIM ÇOK ÖNEMLİ, OLMADAN TERMİNAL ÇALIŞMAZ!
if __name__ == "__main__":
    main()