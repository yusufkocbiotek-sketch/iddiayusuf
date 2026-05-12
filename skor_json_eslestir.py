import json, os, re, time, datetime, traceback, shutil, unicodedata, subprocess
from pathlib import Path
from difflib import SequenceMatcher

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

DAYS_BACK_FINISHED = 3     # Son 3 gün
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
    d1 = (team_sim(local_home, sp_home) + team_sim(local_away, sp_away)) / 2
    d2 = (team_sim(local_home, sp_away) + team_sim(local_away, sp_home)) / 2
    return max(d1, d2)

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
def select_date_dropdown(driver, iso_date: str) -> bool:
    try:
        sel_el = driver.find_element(By.CSS_SELECTOR, DATESELECTOR_CSS)
        sel = Select(sel_el)
        values = [o.get_attribute("value") for o in sel.options]
        if iso_date not in values: return False
        before = len(driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR))
        sel.select_by_value(iso_date)
        time.sleep(0.8)
        for _ in range(25):
            now = len(driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR))
            if now != before and now >= 0: break
            time.sleep(0.3)
        return True
    except Exception: return False

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
        k = (item["spordb_match_id"], item["tarih"], item["skor1"], item["skor2"])
        if k in seen: continue
        seen.add(k)
        res = split_row_cells(driver, a)
        if res and res.get("idx") is not None:
            texts = res.get("texts", [])
            h, aw = pick_home_away(texts, res["idx"])
            item["sp_home"], item["sp_away"] = h, aw
            
  # ... (href ve item oluşturma kısmı aynı) ...
        
        # --- YENİ YÖNTEM: DOĞRUDAN HTML ELEMENTİNDEN ÇEKME ---
        # Satırın kendisini (tr) bulmaya çalışalım ki içinde arama yapabilelim
        try:
            # Önce satırı (tr) bulalım (a etiketinin atası)
            row_element = a.find_element(By.XPATH, "./ancestor::tr")
            
            # Strateji A: 'hide-on-mobile' class'ına sahip hücreleri al
            # Genelde İY skoru buradadır
            iy_cells = row_element.find_elements(By.CSS_SELECTOR, "td.hide-on-mobile")
            
            iy_found = False
            if iy_cells:
                for cell in iy_cells:
                    txt = cell.text.strip()
                    # Skor formatını kontrol et (örn: 1-0)
                    if re.match(r"^\d+[-:]\d+$", txt):
                        parts = txt.replace(":", "-").split("-")
                        s1, s2 = int(parts[0]), int(parts[1])
                        
                        # Son bir mantık kontrolü (futbol skoru olmalı)
                        if s1 < 10 and s2 < 10 and (s1+s2) < 10:
                            item["iy_skor1"] = s1
                            item["iy_skor2"] = s2
                            iy_found = True
                            break
            
            # Strateji B: Eğer hide-on-mobile yoksa, MS skorundan sonraki ilk skor hücresini dene
            if not iy_found:
                all_score_cells = row_element.find_elements(By.XPATH, ".//td[contains(text(), '-')]")
                ms_str = f"{item['skor1']}-{item['skor2']}"
                
                found_ms = False
                for cell in all_score_cells:
                    txt = cell.text.strip()
                    if re.match(r"^\d+[-:]\d+$", txt):
                        if txt == ms_str or txt == f"{item['skor1']}:{item['skor2']}":
                            found_ms = True # MS skorunu bulduk, bir sonrakine geç
                            continue
                        
                        if found_ms:
                            # Bu MS'den sonraki ilk skor, muhtemelen İY'dir
                            parts = txt.replace(":", "-").split("-")
                            s1, s2 = int(parts[0]), int(parts[1])
                            if s1 < 10 and s2 < 10: # again safety check
                                item["iy_skor1"] = s1
                                item["iy_skor2"] = s2
                                break
        except Exception as e:
            pass # Hata olursa sessizce geç, eski (0-0) kalsın
        # -------------------------------------------------------

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
# MAIN
# =========================
def main():
    print("=" * 70)
    print("⚽ SPORDB SKOR ÇEKİCİ (V5.5) - Dropdown ile SON 3 GÜN (BUGÜN DAHİL)")
    print("=" * 70)

    today = datetime.date.today()
    today_iso = today.isoformat()

    if INCLUDE_TODAY:
        dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(DAYS_BACK_FINISHED)]
    else:
        dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(1, DAYS_BACK_FINISHED + 1)]

    print("📅 Taranacak günler:", dates)

    driver = None
    all_scores = [] 
    try:
        driver = build_driver()
        driver.get(SPORDB_URL)

        for d in dates:
            print(f"\n🔎 Gün: {d}")
            day_scores = collect_scores_for_date(driver, d)
            print(f"   ✅ {d} skor kaydı: {len(day_scores)}")
            all_scores.extend(day_scores)

        print(f"\n✅ Toplam skor kaydı (son {DAYS_BACK_FINISHED} gün): {len(all_scores)}")

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
        
        # === GİT OTOMASYONU (PULL EKLENMİŞ) ===
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
                    msg = f"🤖 Spordb Otomatik Skor Güncellemesi (Son 3 Gün) - {now_str}"
                    subprocess.run(["git", "commit", "-m", msg], cwd=repo_dir, capture_output=True)
                    
                    # --- ÇAKIŞMA ÖNLEME: GIT PULL ---
                    print("🔄 Git pull yapılıyor (Çakışma önleme)...")
                    pull_res = subprocess.run(["git", "pull", "--rebase"], cwd=repo_dir, capture_output=True, text=True)
                    if pull_res.returncode != 0:
                        print(f"⚠️ Git pull hatası (Çakışma olabilir): {pull_res.stderr}")
                        subprocess.run(["git", "rebase", "--abort"], cwd=repo_dir, capture_output=True)
                    else:
                        print("✅ Git pull başarılı.")
                    # --------------------------------
                    
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