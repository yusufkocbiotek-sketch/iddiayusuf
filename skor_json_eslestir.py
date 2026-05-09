import json, os, re, time, datetime, traceback, shutil, unicodedata
from pathlib import Path
from difflib import SequenceMatcher

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

# =========================
# PATH (nereden çalıştırırsan çalıştır doğru yere yazsın)
# =========================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
OUTPUT_SKOR_JSON = BASE_DIR / "public" / "data" / "skorlar_spordb.json"

# =========================
# AYARLAR
# =========================
SPORDB_URL = "https://www.spordb.com/iddaa-programi"
PAGE_LOAD_TIMEOUT = 60
WAIT_LONG = 35

CANLI_LINK_SELECTOR = "a[href*='/canli/'][href*='-maci-']"
CANLI_HREF_RE = re.compile(
    r"/canli/(?P<id>\d+)/(?P<date>\d{2}-\d{2}-\d{4})-(?P<teams>.+?)-maci-(?P<h>\d+)-(?P<a>\d+)/?$",
    re.IGNORECASE
)

LOAD_MORE_XPATH = "//button[contains(., 'Daha') or contains(., 'Load more') or contains(., 'More')]"

# Eşleştirme
THRESH_OK = 0.80
THRESH_MAYBE = 0.70
MIN_GAP = 0.06  # best ile ikinci best farkı küçükse update yerine "ekle"ye yöneliriz

# Bu FLAG: mac.json'da yoksa ekle
ADD_MISSING_MATCHES = True

# =========================
# NORMALİZASYON
# =========================
_TMAP = str.maketrans({
    "İ":"i","I":"i","ı":"i","Ş":"s","ş":"s","Ğ":"g","ğ":"g","Ü":"u","ü":"u","Ö":"o","ö":"o","Ç":"c","ç":"c",
})
_STOP = {
    "fk","fc","sk","jk","bk","ac","as","a.s","a.ş","spor","club","kulubu","kulübü",
    "u19","u20","u21","u23","women","reserves","b","ii",
    "ca","cd","cf","sc","ud"
}

def _deaccent(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))

def norm_team(s: str) -> str:
    s = (s or "").strip()
    s = _deaccent(s)
    s = s.translate(_TMAP).lower()
    s = re.sub(r"[’'`´]", "", s)
    s = re.sub(r"\d+", " ", s)
    s = re.sub(r"[^a-z0-9\s-]", " ", s).replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip()
    parts = [p for p in s.split(" ") if p and p not in _STOP and len(p) > 1]
    return " ".join(parts)

def seq_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def token_dice(a: str, b: str) -> float:
    A = set(a.split())
    B = set(b.split())
    if not A or not B:
        return 0.0
    return (2 * len(A & B)) / (len(A) + len(B))

def team_sim(a: str, b: str) -> float:
    a = norm_team(a); b = norm_team(b)
    if not a or not b:
        return 0.0
    if a in b or b in a:
        return 1.0
    return max(token_dice(a, b), seq_ratio(a, b))

def match_score(local_home, local_away, sp_home, sp_away):
    d1 = (team_sim(local_home, sp_home) + team_sim(local_away, sp_away)) / 2
    d2 = (team_sim(local_home, sp_away) + team_sim(local_away, sp_home)) / 2
    return max(d1, d2)

def match_uid(tarih: str, ev: str, dep: str) -> str:
    # aynı gün aynı maç tekrar eklenmesin diye
    a = norm_team(ev)
    b = norm_team(dep)
    # ev/dep ters olsa da aynı UID olsun:
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
    except Exception as e:
        print(f"❌ JSON okunamadı: {path} -> {e}")
        return {"version": 2, "updated": "", "matches": []}

def save_json_atomic(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")

    if path.exists():
        bak = path.with_suffix(path.suffix + f".bak.{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")
        try:
            shutil.copy2(path, bak)
            print(f"   🧾 Yedek: {bak}")
        except Exception as e:
            print(f"   ⚠️ Yedekleme hatası: {e}")

    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)
    print(f"   💾 Kaydedildi: {path}")

# =========================
# DRIVER
# =========================
def build_driver():
    print("🌐 Chrome başlatılıyor (Spordb)...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver

# =========================
# DİNAMİK YÜK
# =========================
def wait_canli_links_stable(driver, timeout=30, stable_rounds=3, min_count=5):
    end = time.time() + timeout
    last = -1
    stable = 0
    while time.time() < end:
        n = len(driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR))
        if n >= min_count and n == last:
            stable += 1
            if stable >= stable_rounds:
                return True
        else:
            stable = 0
            last = n
        time.sleep(0.7)
    return False

def click_load_more(driver, max_click=3):
    clicked = 0
    for _ in range(max_click):
        try:
            btns = driver.find_elements(By.XPATH, LOAD_MORE_XPATH)
            btn = next((b for b in btns if b.is_displayed() and b.is_enabled()), None)
            if not btn:
                break
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.2)
            btn.click()
            clicked += 1
            time.sleep(1.5)
        except Exception:
            break
    return clicked

def deep_scroll_collect(driver, max_steps=50):
    last = 0
    stable = 0
    for _ in range(max_steps):
        click_load_more(driver, max_click=1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.1)
        n = len(driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR))
        if n > last:
            last = n
            stable = 0
        else:
            stable += 1
            if stable >= 7:
                break
    return last

# =========================
# SPORDB PARSE
# =========================
_ODDS_RE = re.compile(r"^\d+([.,]\d+)?$")

def _is_noise_text(t: str) -> bool:
    t = (t or "").strip()
    if not t:
        return True
    if re.fullmatch(r"\d{1,2}:\d{2}", t):
        return True
    if re.fullmatch(r"\d+\s*-\s*\d+", t):
        return True
    if re.fullmatch(r"[A-Z]{2,6}", t):
        return True
    if _ODDS_RE.fullmatch(t):
        try:
            v = float(t.replace(",", "."))
            if 1.0 <= v <= 99.99:
                return True
        except:
            pass
    if t.isdigit():
        return True
    return False

def parse_spordb_canli(href: str, text: str):
    m = CANLI_HREF_RE.search(href or "")
    if not m:
        return None

    sp_id = m.group("id")
    ddmmyyyy = m.group("date")
    teams_slug = m.group("teams")
    skor1 = int(m.group("h"))
    skor2 = int(m.group("a"))

    tarih_iso = datetime.datetime.strptime(ddmmyyyy, "%d-%m-%Y").date().isoformat()
    return {
        "spordb_match_id": sp_id,
        "tarih": tarih_iso,
        "teams_slug": teams_slug,
        "skor1": skor1,
        "skor2": skor2,
        "score_text": (text or "").strip(),
        "cekme_zamani": datetime.datetime.now().isoformat(),
        "sp_home": None,
        "sp_away": None,
        "left_cells": [],
        "right_cells": [],
    }

def split_row_cells(driver, a):
    return driver.execute_script("""
        const a = arguments[0];
        const cell = a.closest('td,th');
        const tr = a.closest('tr');
        if(!cell || !tr) return null;

        const cells = Array.from(tr.querySelectorAll('th,td'));
        const idx = cells.indexOf(cell);
        const texts = cells.map(x => (x.innerText || '').trim());
        return { idx, texts };
    """, a)

def pick_sp_home_away(left_cells, right_cells):
    # HOME: left tarafın son anlamlısı
    sp_home = None
    for t in reversed(left_cells):
        if not _is_noise_text(t):
            sp_home = t.strip()
            break
    # AWAY: right tarafın ilk anlamlısı
    sp_away = None
    for t in right_cells:
        if not _is_noise_text(t):
            sp_away = t.strip()
            break
    return sp_home, sp_away

def extract_scores_from_spordb(driver, target_dates: set[str]):
    wait_canli_links_stable(driver, timeout=WAIT_LONG, min_count=5)
    deep_scroll_collect(driver)

    links = driver.find_elements(By.CSS_SELECTOR, CANLI_LINK_SELECTOR)
    out, seen = [], set()

    for a in links:
        try:
            href = a.get_attribute("href") or ""
            txt = a.text
            item = parse_spordb_canli(href, txt)
            if not item or item["tarih"] not in target_dates:
                continue

            key = (item["spordb_match_id"], item["tarih"], item["skor1"], item["skor2"])
            if key in seen:
                continue
            seen.add(key)

            res = split_row_cells(driver, a)
            if res and res.get("idx") is not None:
                idx = res["idx"]
                texts = res.get("texts", []) or []
                left = [t for t in texts[:idx] if t and t.strip()]
                right = [t for t in texts[idx+1:] if t and t.strip()]
                item["left_cells"] = left
                item["right_cells"] = right
                item["sp_home"], item["sp_away"] = pick_sp_home_away(left, right)

            out.append(item)
        except Exception:
            continue

    return out

# =========================
# MAIN
# =========================
def main():
    print("=" * 70)
    print("⚽ SPORDB OTOMATİK SKOR GÜNCELLEYİCİ (V5.0)")
    print("   (mac.json'da yoksa maç ekler + skor yazar)")
    print("=" * 70)

    today = datetime.date.today()
    target_dates = {
        today.isoformat(),
        (today - datetime.timedelta(days=1)).isoformat(),
        (today - datetime.timedelta(days=2)).isoformat(),
    }
    print("📅 Target dates:", sorted(target_dates, reverse=True))

    mac_data = load_json_safe(MAC_JSON_PATH)
    local = mac_data.get("matches", [])
    if not isinstance(local, list):
        local = []

    # Son 3 gün adayları
    local_by_date = {}
    for m in local:
        if m.get("tarih") in target_dates:
            local_by_date.setdefault(m.get("tarih"), []).append(m)

    # duplicate koruması için uid set (tüm local içinde)
    uid_set = set()
    for m in local:
        if m.get("tarih") and m.get("ev_sahibi") and m.get("deplasman"):
            uid_set.add(match_uid(m["tarih"], m["ev_sahibi"], m["deplasman"]))

    print("📚 mac.json (son 3 gün) kayıt:", sum(len(v) for v in local_by_date.values()))

    driver = None
    try:
        driver = build_driver()
        driver.get(SPORDB_URL)

        print("⏳ Spordb linkleri bekleniyor...")
        scores = extract_scores_from_spordb(driver, target_dates)
        print(f"✅ Spordb’den son 3 gün skor linki: {len(scores)}")

        matched = updated = skipped = not_matched = noop = added = 0

        for sp in scores:
            date_key = sp["tarih"]
            cands = local_by_date.get(date_key, [])

            # Spordb takım adı çıkmadıysa: bu kaydı atla
            if not sp.get("sp_home") or not sp.get("sp_away"):
                not_matched += 1
                continue

            # 1) Eşleştirme dene
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

            # 2) Güvenli eşleşme varsa güncelle
            if best and best_sc >= THRESH_MAYBE and (best_sc - second_sc) >= MIN_GAP:
                if best_sc >= THRESH_OK:
                    matched += 1

                    # yön kontrolü (swap)
                    s_direct = team_sim(best.get("ev_sahibi",""), sp["sp_home"]) + team_sim(best.get("deplasman",""), sp["sp_away"])
                    s_swap   = team_sim(best.get("ev_sahibi",""), sp["sp_away"]) + team_sim(best.get("deplasman",""), sp["sp_home"])
                    if s_swap > s_direct:
                        skor_ev, skor_dep = sp["skor2"], sp["skor1"]
                    else:
                        skor_ev, skor_dep = sp["skor1"], sp["skor2"]

                    changed = (
                        best.get("skor_ev") != skor_ev
                        or best.get("skor_dep") != skor_dep
                        or best.get("spordb_match_id") != sp.get("spordb_match_id")
                        or (best.get("durum") != "bitti" and date_key < today.isoformat())
                    )

                    best["skor_ev"] = skor_ev
                    best["skor_dep"] = skor_dep
                    best["spordb_match_id"] = sp.get("spordb_match_id")
                    best["kaynak"] = "spordb.com"
                    best["cekme_zamani"] = sp["cekme_zamani"]

                    if date_key < today.isoformat():
                        best["durum"] = "bitti"
                    else:
                        if best.get("durum") in (None, "", "baslamadi"):
                            best["durum"] = "devam"

                    if changed:
                        updated += 1
                    else:
                        noop += 1

                    continue  # bu sp kaydı işlendi

                else:
                    skipped += 1
                    continue

            # 3) Eşleşme yoksa -> mac.json'a ekle (son 3 gün için)
            if ADD_MISSING_MATCHES:
                uid = match_uid(date_key, sp["sp_home"], sp["sp_away"])
                if uid in uid_set:
                    # aynı maç zaten var ama eşleşme yakalayamadık
                    not_matched += 1
                    continue

                # skor yönü burada: sp_home left->home kabul (senin tabloda böyle)
                skor_ev, skor_dep = sp["skor1"], sp["skor2"]

                new_m = {
                    "index": 0,
                    "mac_kodu": "",
                    "ev_sahibi": sp["sp_home"],
                    "deplasman": sp["sp_away"],
                    "saat": "",           # spordb sayfasında saat var ama satırdan almak ayrı iş; şimdilik boş
                    "lig": "",
                    "tarih": date_key,
                    "cekme_zamani": sp["cekme_zamani"],
                    "durum": "bitti" if date_key < today.isoformat() else "devam",
                    "skor_ev": skor_ev,
                    "skor_dep": skor_dep,
                    "skor_1y_ev": 0,
                    "skor_1y_dep": 0,
                    "kaynak": "spordb.com",
                    "spordb_match_id": sp.get("spordb_match_id"),
                    "oranlar": {}
                }

                local.append(new_m)
                local_by_date.setdefault(date_key, []).append(new_m)
                uid_set.add(uid)
                added += 1
            else:
                not_matched += 1

        # reindex + kaydet
        local_sorted = sorted(
            local,
            key=lambda x: (x.get("tarih",""), x.get("saat","00:00"), x.get("ev_sahibi",""), x.get("deplasman",""))
        )
        for i, m in enumerate(local_sorted, 1):
            m["index"] = i

        mac_data["matches"] = local_sorted
        mac_data["updated"] = datetime.datetime.now().isoformat()
        save_json_atomic(mac_data, MAC_JSON_PATH)

        save_json_atomic({
            "created_at": datetime.datetime.now().isoformat(),
            "source_url": SPORDB_URL,
            "count": len(scores),
            "matches": scores
        }, OUTPUT_SKOR_JSON)

        print("\n" + "=" * 70)
        print("🎉 ÖZET")
        print("=" * 70)
        print(f"Spordb skor linki        : {len(scores)}")
        print(f"Eşleşti (güvenli)        : {matched}")
        print(f"Güncellendi              : {updated}")
        print(f"Eşleşti ama aynı (no-op) : {noop}")
        print(f"Eklendi (mac.json'a yeni): {added}")
        print(f"Şüpheli/kararsız (skip)  : {skipped}")
        print(f"Eşleşmedi                : {not_matched}")
        print("=" * 70)

        print("\n📌 Git:")
        print("   git pull --rebase")
        print("   git add public/data/mac.json public/data/skorlar_spordb.json")
        print('   git commit -m "Skor guncelleme (son 3 gun)"')
        print("   git push origin main")

    except Exception:
        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
            except WebDriverException:
                pass

if __name__ == "__main__":
    main()