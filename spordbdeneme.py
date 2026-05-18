import json, os, re, time, datetime, traceback, shutil, unicodedata
from pathlib import Path
from difflib import SequenceMatcher

# =========================
# 🔴 GELİŞTİRİLMİŞ TAKIM İŞLEMLERİ
# =========================
def clean_team_name(name):
    if not name: return ""
    n = name.lower().strip()
    
    # Kısaltma listesi - bunları takım ismi olarak alma
    kisa_kodlar = {"bra1", "bra2", "isp1", "isp2", "isl1", "isl2", "fın1", "fın2", "pol1", "pol2", "bul1", "bul2", 
                   "isc1", "isc2", "rom1", "rom2", "svc1", "svc2", "irlp", "inp", "izl", "sili", "bol1", "ukr p", "urug p", "sin d1"}
    
    if n in kisa_kodlar or len(n) <= 3:
        return ""

    prefixes = ["ad ", "cd ", "ca ", "fc ", "ac ", "sc ", "us ", "ud ", "fk ", "sk ", "jk ", "bk ", "as ", "al ", "el ", "da ", "de ",
        "real ", "athletic ", "atletico ", "deportivo ", "club ", "kulübü ", "spor "]
    suffixes = [" fc", " sc", " ac", " us", " ud", " fk", " sk", " jk", " bk", " as", " ad", " cd", " ca", "spor", "kulübü", "club"]
    
    for p in prefixes:
        if n.startswith(p): n = n[len(p):].strip()
    for s in suffixes:
        if n.endswith(s): n = n[:-len(s)].strip()

    replacements = {"ceuta": "ceuta", "al ain": "alain", "dibba al ain": "dibba", "dibba": "dibba"}
    for key, val in replacements.items(): n = n.replace(key, val)
        
    n = n.replace(".", "").replace("-", " ").replace("'", "").replace("’", "")
    n = " ".join(n.split())
    return n.strip() if len(n) > 2 else ""

OZEL_ESLESTIRMELER = {
    "spordb": {"ceuta": "ad ceuta", "al ain": "al ain fc", "dibba": "dibba al ain"},
    "macjson": {"ad ceuta": "ceuta", "al ain fc": "al ain", "dibba al ain": "dibba"}
}

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC

# =========================
# PATH & AYARLAR
# =========================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
GECMIS_JSON_PATH = BASE_DIR / "public" / "data" / "gecmis_maclar.json"
OUTPUT_SKOR_JSON = BASE_DIR / "public" / "data" / "skorlar_spordb.json"

SPORDB_URL = "https://www.spordb.com/iddaa-programi"

DAYS_BACK_FINISHED = 5     
INCLUDE_TODAY = True       

UPDATE_MAC_JSON = True
UPDATE_GECMIS_JSON = True
ADD_MISSING_MATCHES = False

PAGE_LOAD_TIMEOUT = 60
WAIT_LONG = 25

DATESELECTOR_CSS = "#iddaa_dateselector"
CANLI_LINK_SELECTOR = "a[href*='/canli/'][href*='-maci-']"
CANLI_HREF_RE = re.compile(r"/canli/(?P<id>\d+)/(?P<date>\d{2}-\d{2}-\d{4})-(?P<teams>.+?)-maci-(?P<h>\d+)-(?P<a>\d+)/?$", re.IGNORECASE)
LOAD_MORE_XPATH = "//button[contains(., 'Daha') or contains(., 'Load more')]"

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
    if not s or len(s) < 3: return ""
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
# JSON IO
# =========================
def load_json_safe(path: Path):
    if not path.exists(): return {"version": 2, "updated": "", "matches": []}
    try: return json.loads(path.read_text(encoding="utf-8"))
    except: return {"version": 2, "updated": "", "matches": []}

def save_json_atomic(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
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
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver

# =========================
# DİNAMİK YÜK
# =========================
def wait_canli_links_stable(driver, timeout=20, min_count=1):
    try:
        end = time.time() + timeout
        last = -1
        while time.time() < end:
            n = len(driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR))
            if n >= min_count and n == last: return True
            last = n
            time.sleep(0.5)
        return False
    except: return False

def deep_scroll_collect(driver):
    for _ in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.7)

# =========================
# TARİH SEÇ
# =========================
def select_date_dropdown(driver, target_iso_date):
    try:
        selects = driver.find_elements(By.TAG_NAME, "select")
        date_select = None
        for sel in selects:
            if "iddaa_dateselector" in sel.get_attribute("id") or "Hafta" in sel.text or "202" in sel.text:
                date_select = sel
                break
        if not date_select: return False

        options = date_select.find_elements(By.TAG_NAME, "option")
        found_opt = None
        target_dt = datetime.datetime.strptime(target_iso_date, "%Y-%m-%d").date()
        
        for opt in options:
            txt = opt.text.strip()
            val = opt.get_attribute("value")
            tarihler = re.findall(r'\d{2}\.\d{2}\.\d{4}', txt)
            if len(tarihler)>=2:
                b = datetime.datetime.strptime(tarihler[0],"%d.%m.%Y").date()
                s = datetime.datetime.strptime(tarihler[1],"%d.%m.%Y").date()
                if b <= target_dt <= s:
                    found_opt = opt
                    break
            elif target_iso_date in val:
                found_opt = opt
                break

        if found_opt:
            Select(date_select).select_by_value(found_opt.get_attribute("value"))
            time.sleep(2.5)
            return True
        return False
    except Exception as e:
        print(f"   ❌ Tarih seçim hatası: {e}")
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
    if re.fullmatch(r"[A-Z]{2,6}", t): return True
    if _ODDS_RE.fullmatch(t):
        try:
            v = float(t.replace(",", "."))
            if 1.0 <= v <= 99.99: return True
        except: pass
    if t.isdigit(): return True
    # Kısaltma kontrolü
    if len(t) <= 3 or t in ["BRA", "ISP", "FİN", "POL", "BUL", "İSÇ", "ROM", "İSV", "İRL"]: return True
    return False

def parse_spordb_canli(href: str):
    m = CANLI_HREF_RE.search(href or "")
    if not m: return None
    sp_id = m.group("id")
    ddmmyyyy = m.group("date")
    skor1 = int(m.group("h"))
    skor2 = int(m.group("a"))
    
    # SKOR FİLTRESİ: 7'den büyük golü alma (anormal durum)
    if skor1 > 7 or skor2 > 7:
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
        "sp_home": None, 
        "sp_away": None,
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
    """, a)


def pick_home_away(texts, idx):
    left = [t for t in texts[:idx] if t and t.strip()]
    right = [t for t in texts[idx+1:] if t and t.strip()]
    
    home = None
    for t in reversed(right):
        if not _is_noise_text(t): 
            home = t.strip()
            break
            
    away = None
    for t in left:
        if not _is_noise_text(t): 
            away = t.strip()
            break

    if not home and away:
        home, away = away, None
        for t in right:
            if not _is_noise_text(t):
                away = t.strip()
                break

    # SON KONTROL: Temiz isimleri tekrar kontrol et, kısaltma ise iptal et
    if home:
        temp_h = clean_team_name(home)
        if not temp_h: home = None
    if away:
        temp_a = clean_team_name(away)
        if not temp_a: away = None

    return home, away


def collect_scores_for_date(driver, iso_date: str):
    ok = select_date_dropdown(driver, iso_date)
    if not ok: 
        print(f"   ⚠️ {iso_date} tarihi için liste yüklenemedi, atlanıyor.")
        return []

    wait_canli_links_stable(driver)
    deep_scroll_collect(driver)
    
    links = driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR)
    out = []
    seen = set()

    print(f"   🔍 {len(links)} adet link bulundu, analiz ediliyor...")

    for a in links:
        href = a.get_attribute("href") or ""
        item = parse_spordb_canli(href)
        
        if not item or item["tarih"] != iso_date: 
            continue
        
        unique_key = (item["spordb_match_id"], item["tarih"], item["skor1"], item["skor2"])
        if unique_key in seen: continue
        seen.add(unique_key)

        res = split_row_cells(driver, a)
        if res and res.get("idx") is not None:
            texts = res.get("texts", [])
            h, aw = pick_home_away(texts, res["idx"])
            item["sp_home"], item["sp_away"] = h, aw

            url_ms_h = item.get('skor1', 0)
            url_ms_a = item.get('skor2', 0)
            need_ms_check = (url_ms_h == 0 and url_ms_a == 0)
            iy_bulundu = False
            found_scores = []

            try:
                row_element = a.find_element(By.XPATH, "./ancestor::tr")
                all_cells = row_element.find_elements(By.TAG_NAME, "td")

                for cell in all_cells:
                    txt = cell.text.strip()
                    if re.match(r"^\d+[-:]\d+$", txt):
                        parts = txt.replace(":", "-").split("-")
                        if len(parts) == 2:
                            try:
                                s1, s2 = int(parts[0]), int(parts[1])
                                # Skor filtresi: 7'den büyükse alma
                                if s1 < 8 and s2 < 8: 
                                    found_scores.append((s1, s2))
                            except: pass

                if need_ms_check and len(found_scores) > 0:
                    item['skor1'], item['skor2'] = found_scores[0]
                    found_scores.pop(0)

                if len(found_scores) > 0:
                    item["iy_skor1"], item["iy_skor2"] = found_scores[0]
                    iy_bulundu = True

            except Exception as e:
                pass

            if (item.get("iy_skor1", 0) == 0 and item.get("iy_skor2", 0) == 0) or not iy_bulundu:
                try:
                    driver.execute_script("window.open(arguments[0], '_blank');", href)
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(2)

                    full_text = driver.find_element(By.TAG_NAME, "body").text
                    pattern = r"(?:İY|Ilk Yari|First Half|Half Time|HT|Devre Arası|1\. Yarı)[:\s]*(\d+)\s*[-:]\s*(\d+)"
                    match = re.search(pattern, full_text, re.IGNORECASE)

                    if match:
                        s1, s2 = int(match.group(1)), int(match.group(2))
                        if s1 < 8 and s2 < 8:
                            item["iy_skor1"], item["iy_skor2"] = s1, s2
                            iy_bulundu = True

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception:
                    try:
                        if len(driver.window_handles) > 1:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                    except: pass

            ms_h, ms_a = item['skor1'], item['skor2']
            iy_h, iy_a = item.get('iy_skor1', 0), item.get('iy_skor2', 0)
            
            if item["sp_home"] and item["sp_away"]:
                print(f"✅ {item['sp_home']} vs {item['sp_away']} -> MS: {ms_h}-{ms_a} | İY: {iy_h}-{iy_a}")
            else:
                if item["sp_home"] or item["sp_away"]:
                    print(f"⚠️ Eksik İsim: {item['sp_home']} - {item['sp_away']} -> Veri atlandı")

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
            uid = match_uid(m["tarih"], m["ev_sahibi"], m["deplasman"])
            if uid: uid_set.add(uid)
    
    by_date = {}
    for m in matches:
        if m.get("tarih"): 
            by_date.setdefault(m["tarih"], []).append(m)
    
    matched = updated = noop = added = skipped = not_matched = 0
    
    for sp in scores:
        if not sp["sp_home"] or not sp["sp_away"]: continue

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
        
        if best and best_sc >= THRESH_MAYBE and (best_sc - second_sc) >= MIN_GAP:
            if best_sc >= THRESH_OK:
                matched += 1
                
                s_direct = team_sim(best.get("ev_sahibi",""), sp["sp_home"]) + team_sim(best.get("deplasman",""), sp["sp_away"])
                s_swap = team_sim(best.get("ev_sahibi",""), sp["sp_away"]) + team_sim(best.get("deplasman",""), sp["sp_home"])
                
                skor_ev, skor_dep = (sp["skor2"], sp["skor1"]) if s_swap > s_direct else (sp["skor1"], sp["skor2"])

                iy_ev = sp.get("iy_skor1") 
                iy_dep = sp.get("iy_skor2")
                
                if iy_ev is not None and iy_dep is not None and (iy_ev < 8 and iy_dep < 8):
                    if s_swap > s_direct:
                        best["skor_1y_ev"] = int(iy_dep)
                        best["skor_1y_dep"] = int(iy_ev)
                    else:
                        best["skor_1y_ev"] = int(iy_ev)
                        best["skor_1y_dep"] = int(iy_dep)

                changed = (best.get("skor_ev") != skor_ev or 
                           best.get("skor_dep") != skor_dep or 
                           best.get("spordb_match_id") != sp["spordb_match_id"])
                
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

        if ADD_MISSING_MATCHES:
            uid = match_uid(sp["tarih"], sp["sp_home"], sp["sp_away"])
            if uid and uid not in uid_set:
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

    print(f"\n📊 ÖZET: Eşleşti={matched} | Güncellendi={updated} | Değişmedi={noop} | Eklendi={added} | Eşleşemedi={not_matched} | Atlandı={skipped}")
    db_data["updated"] = datetime.datetime.now().isoformat()
    return db_data


# =========================
# ANA ÇALIŞTIRMA
# =========================
def main():
    print("="*60)
    print("📢 SPORDB SKOR ÇEKME & GÜNCELLEME BAŞLADI")
    print("="*60)

    today = datetime.date.today()
    dates_to_process = []

    if INCLUDE_TODAY:
        dates_to_process.append(today.isoformat())

    for bk in range(1, DAYS_BACK_FINISHED + 1):
        dates_to_process.append((today - datetime.timedelta(days=bk)).isoformat())

    print(f"📅 İşlenecek tarihler: {dates_to_process}")

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
            driver.get(SPORDB_URL)
            time.sleep(2)

        save_json_atomic({"updated": datetime.datetime.now().isoformat(), "scores": all_scores}, OUTPUT_SKOR_JSON)
        print(f"💾 Ham veriler kaydedildi: {OUTPUT_SKOR_JSON}")

        if UPDATE_MAC_JSON:
            print("\n🔄 mac.json dosyası güncelleniyor...")
            mac_data = load_json_safe(MAC_JSON_PATH)
            updated_data = update_db(mac_data, all_scores, today.isoformat())
            save_json_atomic(updated_data, MAC_JSON_PATH)
            print(f"✅ Güncel mac.json kaydedildi: {MAC_JSON_PATH}")

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


if __name__ == "__main__":
    main()