import json, os, re, time, datetime, traceback, shutil, unicodedata, subprocess
from pathlib import Path
from difflib import SequenceMatcher

def clean_team_name(name):
    """Takım isimlerini standartlaştırarak eşleşme şansını artırır."""
    if not name:
        return ""
    
    # Küçük harfe çevir
    n = name.lower().strip()
    
    # Yaygın kısaltmaları ve ön ekleri kaldır
    # Örnek: "Deportivo" -> "deport", "Atletico" -> "atletico" (kalsın), "CA" -> ""
    replacements = {
        "deportivo": "deport",
        "athletic": "athletic",
        "atletico": "atletico",
        "club": "",
        "ca ": "", " ca": "", # CA (Club Atletico) gibi kısaltmaları sil
        "fc ": "", " fc": "",
        "ac ": "", " ac": "",
        "sc ": "", " sc": "",
        "us ": "", " us": "",
        "fk ": "", " fk": "",
        "sk ": "", " sk": "",
        "real ": "real",
        "sporting ": "sporting"
    }
    
    for key, val in replacements.items():
        # Kelimenin başında veya sonunda geçiyorsa değiştir
        if n.startswith(key + " "):
            n = val + n[len(key):]
        elif n.endswith(" " + key):
            n = n[:-len(key)-1] + (" " + val if val else "")
        elif n == key:
            n = val
            
    # Fazla boşlukları temizle
    n = " ".join(n.split())
    
    # Nokta ve tireleri kaldır
    n = n.replace(".", "").replace("-", " ")
    
    return n.strip()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

# =========================
# PATH
# =========================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
GECMIS_JSON_PATH = BASE_DIR / "public" / "data" / "gecmis_maclar.json"
OUTPUT_SKOR_JSON = BASE_DIR / "public" / "data" / "skorlar_spordb.json"

# =========================
# AYAR (SON 3 GÜN VE BUGÜN DAHİL)
# =========================
SPORDB_URL = "https://www.spordb.com/iddaa-programi"

DAYS_BACK_FINISHED = 5     # Son 3 gün
INCLUDE_TODAY = True       # Bugünün maçlarını da al

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

THRESH_OK = 0.80
THRESH_MAYBE = 0.70
MIN_GAP = 0.06

# =========================
# NORMALİZASYON
# =========================
_TMAP = str.maketrans({"İ":"i","I":"i","ı":"i","Ş":"s","ş":"s","Ğ":"g","ğ":"g","Ü":"u","ü":"u","Ö":"o","ö":"o","Ç":"c","ç":"c"})
_STOP = {"fk","fc","sk","jk","bk","ac","as","a.s","a.ş","spor","club","kulubu","kulübü",
         "u19","u20","u21","u23","women","reserves","b","ii","ca","cd","cf","sc","ud"}

def _deaccent(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))

def norm_team(s: str) -> str:
    s = (s or "").strip()
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
    return (2 * len(A & B)) / (len(A) + len(B))

def team_sim(a: str, b: str) -> float:
    a = norm_team(a); b = norm_team(b)
    if not a or not b: return 0.0
    if a in b or b in a: return 1.0
    return max(token_dice(a, b), seq_ratio(a, b))

def match_score(local_home, local_away, sp_home, sp_away):
    # 1. İsimleri temizle (Yeni eklenen fonksiyonu kullan)
    l_home = clean_team_name(local_home)
    l_away = clean_team_name(local_away)
    s_home = clean_team_name(sp_home)
    s_away = clean_team_name(sp_away)
    
    # 2. Puanlama yap
    score = 0
    
    # Ev sahibi kontrolü
    if l_home == s_home: 
        score += 50
    elif l_home in s_home or s_home in l_home: 
        score += 25 # Kısmi eşleşme
        
    # Deplasman kontrolü
    if l_away == s_away: 
        score += 50
    elif l_away in s_away or s_away in l_away: 
        score += 25
        
    return score

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
        if n > last: last = n; stable = 0
        else:
            stable += 1
            if stable >= 9: break
    return last

# =========================
# TARİH SEÇ (dropdown)
# =========================
def load_all_matches_via_dropdown(driver):
    """
    Dropdown menüsünden 'Hepsi' veya 'Tüm Maçlar' seçeneğini seçer
    ve sayfanın tüm maçları yüklemesini sağlar.
    """
    try:
        print("   📂 Dropdown'dan 'Hepsi' seçeneği aranıyor...")
        
        # 1. Dropdown elementini bul
        selects = driver.find_elements(By.TAG_NAME, "select")
        target_select = None
        
        for sel in selects:
            opts = sel.find_elements(By.TAG_NAME, "option")
            # İçinde 'Hepsi', 'All', 'Tümü' geçen veya çok fazla seçeneği olan dropdown
            for opt in opts:
                txt = opt.text.lower()
                if "hepsi" in txt or "tümü" in txt or "all" in txt or len(opts) > 50:
                    target_select = sel
                    break
            if target_select: break
            
        if not target_select:
            print("   ⚠️ 'Hepsi' seçeneği bulunan dropdown bulunamadı, varsayılan liste kullanılıyor.")
            return False

        # 2. 'Hepsi' seçeneğini bul ve seç
        options = target_select.find_elements(By.TAG_NAME, "option")
        selected = False
        
        for opt in options:
            txt = opt.text.lower()
            val = opt.get_attribute("value")
            
            # Mantık: Ya metninde 'hepsi' geçecek ya da value'su boş/'all' olacak
            if "hepsi" in txt or "tümü" in txt or "all" in txt or val == "" or val == "all":
                Select(target_select).select_by_value(val)
                print(f"   ✅ Dropdown'dan doğru hafta seçildi: {found_option.text.strip()}")
            
            # --- YENİ EKLEME: SAYFA YENİLENMESİNİ BEKLE ---
            # Sayfanın tamamen yenilenmesi ve maçların gelmesi için bekle
            time.sleep(5) 
            
            # Maç linklerinin gelmesini bekle (Spinner kaybolana kadar)
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, CANLI_LINK_SELECTOR))
                )
                print("   ℹ️ Maç listesi yüklendi.")
            except:
                print("   ⚠️ Maç listesi yüklenmedi, devam ediliyor.")
            # ---------------------------------------------
            
            return True

    except Exception as e:
        print(f"   ❌ Dropdown hatası: {e}")
        return False# =========================
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
    return False

def parse_spordb_canli(href: str):
    m = CANLI_HREF_RE.search(href or "")
    if not m: return None
    sp_id = m.group("id"); ddmmyyyy = m.group("date")
    skor1 = int(m.group("h")); skor2 = int(m.group("a"))
    teams_slug = m.group("teams")
    tarih_iso = datetime.datetime.strptime(ddmmyyyy, "%d-%m-%Y").date().isoformat()
    return {"spordb_match_id": sp_id, "tarih": tarih_iso, "teams_slug": teams_slug, "skor1": skor1, "skor2": skor2,
            "cekme_zamani": datetime.datetime.now().isoformat(), "sp_home": None, "sp_away": None}

def split_row_cells(driver, a):
    return driver.execute_script("""
        const a = arguments[0]; const cell = a.closest('td,th'); const tr = a.closest('tr');
        if(!cell || !tr) return null;
        const cells = Array.from(tr.querySelectorAll('th,td'));
        const idx = cells.indexOf(cell);
        const texts = cells.map(x => (x.innerText || '').trim());
        return { idx, texts };
    """, a)

def pick_home_away(texts, idx):
    left = [t for t in texts[:idx] if t and t.strip()]
    right = [t for t in texts[idx+1:] if t and t.strip()]
    home = None
    for t in reversed(left):
        if not _is_noise_text(t): home = t.strip(); break
    away = None
    for t in right:
        if not _is_noise_text(t): away = t.strip(); break
    return home, away

def collect_scores_for_date(driver, iso_date: str):
    ok = select_date_dropdown(driver, iso_date)
    if not ok: return []
    wait_canli_links_stable(driver, timeout=WAIT_LONG, min_count=3)
    deep_scroll_collect(driver)
    links = driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR)
    out, seen = [], set()
    for a in links:
        href = a.get_attribute("href") or ""
        item = parse_spordb_canli(href)
        if not item or item["tarih"] != iso_date: continue
        
        # Unik kontrol
        k = (item["spordb_match_id"], item["tarih"], item["skor1"], item["skor2"])
        if k in seen: continue
        seen.add(k)
        
        res = split_row_cells(driver, a)
        if res and res.get("idx") is not None:
            texts = res.get("texts", [])
            h, aw = pick_home_away(texts, res["idx"])
            item["sp_home"], item["sp_away"] = h, aw
            
            # ==========================================
            # SKOR GÜVENLİK KONTROLÜ (MS VE İY)
            # ==========================================
            
            # Mevcut durum: URL'den gelen skorlar (Genelde MS'tir)
            current_ms_h = item.get('skor1', 0)
            current_ms_a = item.get('skor2', 0)
            
            # Eğer URL'den skor gelmediyse (0-0 ise) veya emin değilseniz, HTML'i tara
            need_ms_check = (current_ms_h == 0 and current_ms_a == 0)
            
            iy_bulundu = False
            ms_html_bulundu = False
            
            try:
                row_element = a.find_element(By.XPATH, "./ancestor::tr")
                all_cells = row_element.find_elements(By.TAG_NAME, "td")
                
                # Tüm hücrelerdeki sayı-sayı formatını tara
                found_scores = []
                for cell in all_cells:
                    txt = cell.text.strip()
                    if re.match(r"^\d+[-:]\d+$", txt):
                        parts = txt.replace(":", "-").split("-")
                        if len(parts) == 2:
                            try:
                                s1, s2 = int(parts[0]), int(parts[1])
                                if s1 < 10 and s2 < 10 and (s1+s2) < 12: # Makul skor
                                    found_scores.append((s1, s2))
                            except: pass
                
                # STRATEJİ: 
                # Genelde sıralama şöyledir: [MS Ev-Dep] ... [İY Ev-Dep]
                # 1. Eğer URL'den MS gelmediyse, listedeki İLK skoru MS kabul et.
                if need_ms_check and len(found_scores) > 0:
                    item['skor1'], item['skor2'] = found_scores[0]
                    ms_html_bulundu = True
                    # Listeden çıkar ki İY ararken karışmasın
                    found_scores.pop(0) 
                
                # 2. Kalan skorlardan ilkini İY kabul et (Eğer henüz bulunamadıysa)
                if len(found_scores) > 0:
                    item["iy_skor1"], item["iy_skor2"] = found_scores[0]
                    iy_bulundu = True

            except Exception:
                pass

            # ==========================================
            # DETAY SAYFASINDAN EK ÇEKİM (İY için)
            # ==========================================
            # Eğer hala İY skoru 0-0 ise detaya gir
            if item.get("iy_skor1", 0) == 0 and item.get("iy_skor2", 0) == 0:
                try:
                    driver.execute_script("window.open(arguments[0], '_blank');", href)
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(4) # Bekle
                    
                    full_text = driver.find_element(By.TAG_NAME, "body").text
                    pattern = r"(?:İY|Ilk Yari|First Half|Half Time|HT|Devre Arası)[:\s]*(\d+)\s*[-:]\s*(\d+)"
                    match = re.search(pattern, full_text, re.IGNORECASE)
                    
                    if match:
                        s1, s2 = int(match.group(1)), int(match.group(2))
                        if s1 < 10 and s2 < 10:
                            item["iy_skor1"], item["iy_skor2"] = s1
                            iy_bulundu = True
                    
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except:
                    try:
                        if len(driver.window_handles) > 1:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                    except: pass

            # ==========================================
            # TERNİNAL RAPORU (MS VE İY BİRLİKTE)
            # ==========================================
            ms_h, ms_a = item['skor1'], item['skor2']
            iy_h, iy_a = item.get('iy_skor1', 0), item.get('iy_skor2', 0)
            
            # Sadece skor bulunanları veya değişenleri raporla
            if (ms_h + ms_a) > 0 or iy_bulundu:
                print(f"✅ {item['sp_home']} vs {item['sp_away']} -> MS: {ms_h}-{ms_a} | İY: {iy_h}-{iy_a}")

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
        
        # DİKKAT: Burası 'for m in cands' döngüsünün DIŞINDA olmalı
        if best and best_sc >= THRESH_MAYBE and (best_sc - second_sc) >= MIN_GAP:
            if best_sc >= THRESH_OK:
                matched += 1
                
                # Ev/Dep eşleşme kontrolü
                s_direct = team_sim(best.get("ev_sahibi",""), sp["sp_home"]) + team_sim(best.get("deplasman",""), sp["sp_away"])
                s_swap = team_sim(best.get("ev_sahibi",""), sp["sp_away"]) + team_sim(best.get("deplasman",""), sp["sp_home"])
                
                # MS Skorlarını belirle
                skor_ev, skor_dep = (sp["skor2"], sp["skor1"]) if s_swap > s_direct else (sp["skor1"], sp["skor2"])

                # --- İY SKORLARINI GÜNCELLE (Varsa) ---
                iy_ev = sp.get("iy_skor1") 
                iy_dep = sp.get("iy_skor2")
                
                if iy_ev is not None and iy_dep is not None:
                    best["skor_1y_ev"] = int(iy_ev)
                    best["skor_1y_dep"] = int(iy_dep)
                # -------------------------------------

                # --- KRİTİK EKLEME: 'changed' DEĞİŞKENİNİ TANIMLA ---
                # Mevcut değerlerle yeni gelen değerleri karşılaştır
                changed = (best.get("skor_ev") != skor_ev or 
                           best.get("skor_dep") != skor_dep or 
                           best.get("spordb_match_id") != sp["spordb_match_id"])
                # ----------------------------------------------------
                
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
        # ==========================================
        # YENİ EKLENECEK KISIM BURADA (DEBUG)
        # ==========================================
        if not best or best_sc < THRESH_MAYBE:
            # EŞLEŞME BAŞARISIZ - DEBUG BİLGİSİ
            print(f"⚠️ EŞLEŞMEDİ: SPORDB='{sp['sp_home']} vs {sp['sp_away']}' | Tarih={sp['tarih']} | Skor={sp['skor1']}-{sp['skor2']}")
            
            # Mac.json'da buna benzeyen bir şey var mı diye bakalım:
            cands = by_date.get(sp["tarih"], [])
            if cands:
                # İlk 3 adayı göster (f-string içinde tırnak hatası olmamasına dikkat et)
                aday_listesi = [f"{m['ev_sahibi']} vs {m['deplasman']}" for m in cands[:3]]
                print(f"   -> Adaylar: {aday_listesi}") 
            else:
                print(f"   -> O tarihte hiç maç yok!")
        # ==========================================

        # Buradan sonrası eski kodun devamı
        if ADD_MISSING_MATCHES:
            uid = match_uid(sp["tarih"], sp["sp_home"], sp["sp_away"])
            if uid not in uid_set:
                # ... (yeni maç ekleme kodları) ...
                added += 1
            else: 
                not_matched += 1
        else: 
            not_matched += 1
        
        # Eğer eşleşen maç bulunamadıysa ve ADD_MISSING_MATCHES açıksa ekle
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
                    # İY Skorları da burada eklendi
                    "skor_1y_ev": sp.get("iy_skor1", 0), 
                    "skor_1y_dep": sp.get("iy_skor2", 0), 
                    "kaynak": "spordb.com", 
                    "spordb_match_id": sp["spordb_match_id"], 
                    "oranlar": {}
                })
                by_date.setdefault(sp["tarih"], []).append(matches[-1])
                uid_set.add(uid)
                added += 1
            else: 
                not_matched += 1
        else: 
            not_matched += 1
            
    db_data["matches"] = matches
    db_data["updated"] = datetime.datetime.now().isoformat()
    return matched, updated, noop, added, skipped, not_matched

# =========================
# TARİH SEÇ (dropdown) - BURAYA YAPIŞTIR!
# =========================
def select_date_dropdown(driver, target_iso_date):
    """
    Hedef tarihi içeren haftayı dropdown'dan bulur ve seçer.
    target_iso_date: '2026-05-12' formatında
    """
    try:
        # 1. Dropdown elementini bul
        selects = driver.find_elements(By.TAG_NAME, "select")
        date_select = None
        
        for sel in selects:
            opts = sel.find_elements(By.TAG_NAME, "option")
            if len(opts) > 5: # Tarih/Hafta dropdown'u genelde çok seçeneklidir
                first_text = opts[0].text.strip() if opts else ""
                if "Hafta" in first_text or "202" in first_text or len(first_text) > 10:
                    date_select = sel
                    break
        
        if not date_select:
            print(f"   ⚠️ Tarih/Hafta dropdown'u bulunamadı!")
            return False

        # 2. Dropdown içindeki tüm seçenekleri tara
        options = date_select.find_elements(By.TAG_NAME, "option")
        found_option = None
        
        target_dt = datetime.datetime.strptime(target_iso_date, "%Y-%m-%d").date()
        
        for opt in options:
            opt_text = opt.text.strip()
            opt_val = opt.get_attribute("value")
            
            # STRATEJİ A: Option metninde tarih aralığı var mı? (örn: "12.05.2026 - 18.05.2026")
            dates_in_text = re.findall(r'\d{2}\.\d{2}\.\d{4}', opt_text)
            if len(dates_in_text) >= 2:
                start_str, end_str = dates_in_text[0], dates_in_text[1]
                start_dt = datetime.datetime.strptime(start_str, "%d.%m.%Y").date()
                end_dt = datetime.datetime.strptime(end_str, "%d.%m.%Y").date()
                
                if start_dt <= target_dt <= end_dt:
                    found_option = opt
                    break
            
            # STRATEJİ B: Value'da tarih var mı?
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
# HİBRİT MAIN FONKSİYONU (V6.2 - TEK SEFERDE TÜMÜNÜ ÇEK & FİLTRELE)
# =========================
def main():
    print("=" * 70)
    print("⚽ SPORDB SKOR ÇEKİCİ (V6.2) - TEK YÜKLEME & AKILLI FİLTRELEME")
    print("=" * 70)

    today = datetime.date.today()
    today_iso = today.isoformat()

    # Hedef günleri belirle
    if INCLUDE_TODAY:
        dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(DAYS_BACK_FINISHED)]
    else:
        dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(1, DAYS_BACK_FINISHED + 1)]

    print("📅 Hedeflenen günler:", dates)

    driver = None
    all_scores = [] 
    
    try:
        driver = build_driver()
        driver.get(SPORDB_URL)
        time.sleep(3)

        # --- ADIM 1: DROPDOWN'DAN EN GENİŞ ARALIĞI SEÇ (HEPSİ) ---
        print("\n📂 ADIM 1: Mümkün olan en geniş liste yükleniyor...")
        
        selects = driver.find_elements(By.TAG_NAME, "select")
        target_select = None
        
        for sel in selects:
            opts = sel.find_elements(By.TAG_NAME, "option")
            # 'Hepsi', 'All', 'Tümü' veya çok fazla seçeneği olanı bul
            for opt in opts:
                txt = opt.text.lower()
                if "hepsi" in txt or "tümü" in txt or "all" in txt or len(opts) > 100:
                    target_select = sel
                    break
            if target_select: break
            
        if target_select:
            options = target_select.find_elements(By.TAG_NAME, "option")
            selected_val = None
            
            # Önce 'Hepsi'ni ara
            for opt in options:
                txt = opt.text.lower()
                val = opt.get_attribute("value")
                if "hepsi" in txt or "tümü" in txt or "all" in txt or val == "" or val == "all":
                    selected_val = val
                    print(f"   ✅ '{opt.text}' seçildi.")
                    break
            
            # 'Hepsi' yoksa, ilk opsiyonu (genelde en geniş hafta) seç
            if not selected_val:
                Select(target_select).select_by_index(0)
                print("   ℹ️ 'Hepsi' bulunamadı, varsayılan geniş aralık seçildi.")
            else:
                Select(target_select).select_by_value(selected_val)
            
            time.sleep(3)
        else:
            print("   ⚠️ Dropdown bulunamadı, mevcut liste kullanılıyor.")

        # --- ADIM 2: SAYFAYI SONUNA KADAR KAYDIR (TÜM MAÇLARI YÜKLE) ---
        print("📜 Sayfa sonuna kadar kaydırılıyor (Binlerce maç yükleniyor)...")
        deep_scroll_collect(driver)
        time.sleep(2)
        
        # TÜM LİNKLERİ BİR DEFA TOPLA
        all_links = driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR)
        print(f"✅ Hafızaya {len(all_links)} adet maç linki alındı.")

        # --- ADIM 3: TARİHLERE GÖRE FİLTRELE VE İŞLE ---
        print("\n🔍 ADIM 3: Maçlar tarihlerine göre filtrelenip işleniyor...")
        
        for d in dates:
            print(f"\n🔎 Gün: {d} işleniyor...")
            day_scores = []
            seen = set()
            
            for a in all_links:
                href = a.get_attribute("href") or ""
                item = parse_spordb_canli(href)
                
                # SADECE HEDEF GÜNÜ AL
                if not item or item["tarih"] != d: 
                    continue
                
                k = (item["spordb_match_id"], item["tarih"], item["skor1"], item["skor2"])
                if k in seen: continue
                seen.add(k)
                
                # SKOR ÇEKME İŞLEMİ (AYNI GÜÇLÜ KOD)
                res = split_row_cells(driver, a)
                if res and res.get("idx") is not None:
                    texts = res.get("texts", [])
                    h, aw = pick_home_away(texts, res["idx"])
                    item["sp_home"], item["sp_away"] = h, aw
                    
                    # --- MS VE İY SKORU GÜVENLİK KONTROLÜ ---
                    current_ms_h = item.get('skor1', 0)
                    current_ms_a = item.get('skor2', 0)
                    need_ms_check = (current_ms_h == 0 and current_ms_a == 0)
                    iy_bulundu = False
                    
                    try:
                        row_element = a.find_element(By.XPATH, "./ancestor::tr")
                        all_cells = row_element.find_elements(By.TAG_NAME, "td")
                        found_scores = []
                        
                        for cell in all_cells:
                            txt = cell.text.strip()
                            if re.match(r"^\d+[-:]\d+$", txt):
                                parts = txt.replace(":", "-").split("-")
                                if len(parts) == 2:
                                    try:
                                        s1, s2 = int(parts[0]), int(parts[1])
                                        if s1 < 10 and s2 < 10 and (s1+s2) < 12:
                                            found_scores.append((s1, s2))
                                    except: pass
                        
                        if need_ms_check and len(found_scores) > 0:
                            item['skor1'], item['skor2'] = found_scores[0]
                            found_scores.pop(0) 
                        
                        if len(found_scores) > 0:
                            item["iy_skor1"], item["iy_skor2"] = found_scores[0]
                            iy_bulundu = True
                    except: pass

                    # Detaydan İY Çek (Gerekirse)
                    if item.get("iy_skor1", 0) == 0 and item.get("iy_skor2", 0) == 0:
                        try:
                            driver.execute_script("window.open(arguments[0], '_blank');", href)
                            driver.switch_to.window(driver.window_handles[-1])
                            time.sleep(4)
                            full_text = driver.find_element(By.TAG_NAME, "body").text
                            pattern = r"(?:İY|Ilk Yari|First Half|Half Time|HT|Devre Arası)[:\s]*(\d+)\s*[-:]\s*(\d+)"
                            match = re.search(pattern, full_text, re.IGNORECASE)
                            if match:
                                s1, s2 = int(match.group(1)), int(match.group(2))
                                if s1 < 10 and s2 < 10:
                                    item["iy_skor1"], item["iy_skor2"] = s1
                                    iy_bulundu = True
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        except:
                            try:
                                if len(driver.window_handles) > 1:
                                    driver.close()
                                    driver.switch_to.window(driver.window_handles[0])
                            except: pass

                    ms_h, ms_a = item['skor1'], item['skor2']
                    iy_h, iy_a = item.get('iy_skor1', 0), item.get('iy_skor2', 0)
                    if (ms_h + ms_a) > 0 or iy_bulundu:
                        print(f"✅ {item['sp_home']} vs {item['sp_away']} -> MS: {ms_h}-{ms_a} | İY: {iy_h}-{iy_a}")
                        
                if item["sp_home"] and item["sp_away"]: 
                    day_scores.append(item)
            
            print(f"   ✅ {d} için {len(day_scores)} maç bulundu.")
            all_scores.extend(day_scores)

        print(f"\n✅ TOPLAM SKOR KAYDI (SON {DAYS_BACK_FINISHED} GÜN): {len(all_scores)}")

        # --- JSON KAYIT VE GÜNCELLEME (AYNI) ---
        save_json_atomic({
            "created_at": datetime.datetime.now().isoformat(), "source_url": SPORDB_URL,
            "days": dates, "count": len(all_scores), "matches": all_scores
        }, OUTPUT_SKOR_JSON)

        if UPDATE_MAC_JSON:
            mac = load_json_safe(MAC_JSON_PATH)
            m,u,noop,a,s,nm = update_db(mac, all_scores, today_iso)
            mac["matches"] = sorted(mac.get("matches", []), key=lambda x: (x.get("tarih",""), x.get("saat","00:00"), x.get("ev_sahibi",""), x.get("deplasman","")))
            for i, mm in enumerate(mac["matches"], 1): mm["index"] = i
            save_json_atomic(mac, MAC_JSON_PATH)
            print(f"\n🧾 mac.json -> matched:{m} updated:{u} noop:{noop} added:{a} skipped:{s} not_matched:{nm}")

        if UPDATE_GECMIS_JSON:
            gec = load_json_safe(GECMIS_JSON_PATH)
            m,u,noop,a,s,nm = update_db(gec, all_scores, today_iso)
            gec["matches"] = sorted(gec.get("matches", []), key=lambda x: (x.get("tarih",""), x.get("saat","00:00"), x.get("ev_sahibi",""), x.get("deplasman","")))
            for i, mm in enumerate(gec["matches"], 1): mm["index"] = i
            save_json_atomic(gec, GECMIS_JSON_PATH)
            print(f"🧾 gecmis_maclar.json -> matched:{m} updated:{u} noop:{noop} added:{a} skipped:{s} not_matched:{nm}")

    except Exception:
        traceback.print_exc()
    finally:
        if driver:
            try: driver.quit()
            except WebDriverException: pass
        
        # === GİT OTOMASYONU ===
        try:
            if len(all_scores) > 0:
                print("\n🚀 Git otomasyonu başlatılıyor...")
                repo_dir = BASE_DIR
                files_to_add = ["public/data/mac.json", "public/data/gecmis_maclar.json", "public/data/skorlar_spordb.json"]
                
                for f in files_to_add:
                    if (repo_dir / f).exists():
                        subprocess.run(["git", "add", f], cwd=repo_dir, capture_output=True)
                
                status_result = subprocess.run(["git", "status", "--porcelain"], cwd=repo_dir, capture_output=True, text=True)
                if status_result.stdout.strip():
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    msg = f"🤖 Spordb Otomatik Skor Güncellemesi (Son {DAYS_BACK_FINISHED} Gün) - {now_str}"
                    subprocess.run(["git", "commit", "-m", msg], cwd=repo_dir, capture_output=True)
                    
                    print("🔄 Git pull yapılıyor (Çakışma önleme)...")
                    pull_res = subprocess.run(["git", "pull", "--rebase"], cwd=repo_dir, capture_output=True, text=True)
                    if pull_res.returncode != 0:
                        print(f"⚠️ Git pull hatası: {pull_res.stderr}")
                        subprocess.run(["git", "rebase", "--abort"], cwd=repo_dir, capture_output=True)
                    else:
                        print("✅ Git pull başarılı.")
                    
                    push_res = subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True, text=True)
                    if push_res.returncode == 0:
                        print("✅ Git push başarılı! Veriler depoya yüklendi.")
                    else:
                        print(f"⚠️ Git push hatası: {push_res.stderr}")
                else:
                    print("ℹ️ Git'te commit edilecek yeni değişiklik bulunamadı.")
        except Exception as e:
            print(f"⚠️ Git işlemi hatası: {e}")

    print("\n==============================================================")
    print("    🎉 TÜM İŞLEMLER TAMAMLANDI! (Kapanmak için bir tuşa basın)")
    print("==============================================================")
    input()

if __name__ == "__main__":
    main()