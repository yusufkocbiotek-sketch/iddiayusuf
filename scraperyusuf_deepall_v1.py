import json
import os
import datetime
import time
import random
import re
import shutil
import subprocess
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# =========================
# AYARLAR
# =========================
URL = "https://www.iddaa.com/program/futbol"
CIKTI_DOSYA = "public/data/mac.json"

# Deep harvest hedefi
TARGET_UNIQUE = 9999            # 150-250 arası deneme; istersen 250 yap
MAX_SCROLL_STEPS = 120
STABLE_LIMIT = 10              # yeni maç gelmezse kaç tur sonra dur
SCROLL_PX = 1300
SCROLL_SLEEP_RANGE = (1.5, 2.5)

# Kaç maçın oranını çekelim (hepsini istiyorsan TARGET_UNIQUE yap)
MAX_SCRAPE = 9999

# Her maç arasında bekleme (yükü azaltır)
SLEEP_BETWEEN_MATCHES = (1.1, 2.4)

# Selectorlar
MATCH_CARD_SEL = ".i_tnw__t8AmC"
SEARCH_INPUT_SEL = "#eventSearch"  # varsa tıklamayı kolaylaştırır

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")
ODD_RE = re.compile(r"^\d{1,2}([.,]\d{2})$")


# =========================
# GIT OTOMASYON
# =========================
ENABLE_GIT_AUTOPUSH = True
GIT_STAGE_FILES = [CIKTI_DOSYA]
REPO_ROOT = Path(__file__).resolve().parent

def _find_git_exe():
    exe = shutil.which("git")
    if exe:
        return exe
    candidates = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def _run_git(args, cwd=None):
    git_exe = _find_git_exe()
    if not git_exe:
        raise RuntimeError("Git bulunamadı.")
    return subprocess.run([git_exe, *args], cwd=cwd, text=True, capture_output=True)

def _turkce_gun_kisa(dt: datetime.datetime) -> str:
    mapping = ["Pts", "Sal", "Çar", "Per", "Cum", "Cts", "Paz"]
    return mapping[dt.weekday()]

def _format_commit_msg(dt: datetime.datetime) -> str:
    cs = int(dt.microsecond / 10000)
    return f"Otomatik deepall {_turkce_gun_kisa(dt)} {dt.strftime('%d.%m.%Y %H:%M:%S')},{cs:02d}"

def git_add_commit_pull_push():
    if not ENABLE_GIT_AUTOPUSH:
        return
    if not (REPO_ROOT / ".git").exists():
        print("⚠️ Git repo değil, atlandı.")
        return

    r = _run_git(["add", *GIT_STAGE_FILES], cwd=str(REPO_ROOT))
    if r.returncode != 0:
        print("⚠️ git add hata:", (r.stderr or r.stdout).strip()); return

    r = _run_git(["diff", "--cached", "--quiet"], cwd=str(REPO_ROOT))
    if r.returncode == 0:
        print("ℹ️ Git: değişiklik yok."); return

    msg = _format_commit_msg(datetime.datetime.now())
    r = _run_git(["commit", "-m", msg], cwd=str(REPO_ROOT))
    if r.returncode != 0:
        print("⚠️ git commit hata:", (r.stderr or r.stdout).strip()); return

    _run_git(["pull", "--rebase", "--autostash"], cwd=str(REPO_ROOT))
    _run_git(["push"], cwd=str(REPO_ROOT))
    print("✅ Git push tamamlandı.")


# =========================
# DRIVER
# =========================
def build_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)

    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception:
        pass
    return driver

def wait_initial(driver, timeout=40):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, MATCH_CARD_SEL))
        )
        return True
    except Exception:
        return False


# =========================
# SCROLL TARGET (iç container varsa)
# =========================
def init_scroll_target(driver):
    try:
        driver.execute_script("""
          (function(){
            const els = Array.from(document.querySelectorAll('*'));
            const cands = els.filter(el=>{
              const s = getComputedStyle(el);
              const oy = s.overflowY;
              return (oy==='auto' || oy==='scroll') && (el.scrollHeight - el.clientHeight) > 600 && el.clientHeight > 300;
            });
            cands.sort((a,b)=> (b.scrollHeight-b.clientHeight) - (a.scrollHeight-a.clientHeight));
            window.__scrollEl = cands[0] || null;
          })();
        """)
    except Exception:
        pass

def reset_scroll_top(driver):
    try:
        driver.execute_script("""
          if (window.__scrollEl){ window.__scrollEl.scrollTop = 0; }
          window.scrollTo(0,0);
        """)
    except Exception:
        pass

def scroll_step(driver, px=SCROLL_PX):
    driver.execute_script("""
      const px = arguments[0];
      if (window.__scrollEl){
        window.__scrollEl.scrollTop = window.__scrollEl.scrollTop + px;
      } else {
        window.scrollBy(0, px);
      }
    """, px)


# =========================
# HARVEST
# =========================
def parse_card(card):
    txt = (card.text or "").strip()
    if not txt:
        return None

    lines = [x.strip() for x in txt.split("\n") if x.strip() and x.strip() != "-"]

    # saat bul
    saat = ""
    for x in lines:
        if TIME_RE.match(x):
            saat = x
            break

    # takım satırı seç (time/odd gibi satırları ele)
    filtered = []
    for x in lines:
        if TIME_RE.match(x):
            continue
        if ODD_RE.match(x.replace(",", ".")):
            continue
        # lig kısaltması gibi (LBRK, SUDAK vb) ele
        if re.fullmatch(r"[A-Z]{2,6}", x):
            continue
        filtered.append(x)

    if len(filtered) < 2:
        return None

    ev, dep = filtered[0], filtered[1]
    if not ev or not dep or ev == dep:
        return None

    return {"ev": ev, "dep": dep, "saat": saat}


def extract_visible(driver):
    out = []
    seen = set()
    cards = driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL)
    for c in cards:
        m = parse_card(c)
        if not m:
            continue
        k = (m["ev"], m["dep"], m.get("saat",""))
        if k in seen:
            continue
        seen.add(k)
        out.append(m)
    return out


def deep_harvest(driver):
    init_scroll_target(driver)
    reset_scroll_top(driver)

    harvest = []
    hset = set()
    stable = 0
    last_total = 0

    for step in range(1, MAX_SCROLL_STEPS + 1):
        vis = extract_visible(driver)
        for m in vis:
            k = (m["ev"], m["dep"], m.get("saat",""))
            if k not in hset:
                hset.add(k)
                harvest.append(m)

        if len(harvest) > last_total:
            print(f"   📈 Step {step}: unique {last_total} -> {len(harvest)}")
            last_total = len(harvest)
            stable = 0
        else:
            stable += 1

        if len(harvest) >= TARGET_UNIQUE:
            break
        if stable >= STABLE_LIMIT:
            break

        scroll_step(driver, SCROLL_PX)
        time.sleep(random.uniform(*SCROLL_SLEEP_RANGE))

    return harvest


# =========================
# CLICK (arama ile daha stabil)
# =========================
def clear_and_type(el, text):
    el.click()
    time.sleep(0.1)
    el.send_keys("\uE009" + "a")  # CTRL+A
    time.sleep(0.05)
    el.send_keys("\uE003")        # BACKSPACE
    time.sleep(0.05)
    el.send_keys(text)

def click_match(driver, ev, dep):
    # arama varsa önce onu dene
    try:
        inp = driver.find_element(By.CSS_SELECTOR, SEARCH_INPUT_SEL)
        clear_and_type(inp, ev[:22])
        time.sleep(0.8)

        cards = driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL)
        for c in cards:
            t = c.text or ""
            if ev in t and dep in t:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", c)
                time.sleep(0.2)
                ActionChains(driver).move_to_element(c).pause(0.2).click().perform()
                return True

        # dep ile tekrar dene
        clear_and_type(inp, dep[:22])
        time.sleep(0.8)
        cards = driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL)
        for c in cards:
            t = c.text or ""
            if ev in t and dep in t:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", c)
                time.sleep(0.2)
                ActionChains(driver).move_to_element(c).pause(0.2).click().perform()
                return True
    except Exception:
        pass

    # arama yoksa ya da bulamadıysa: üstten aşağı tarama
    init_scroll_target(driver)
    reset_scroll_top(driver)
    for _ in range(18):
        cards = driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL)
        for c in cards:
            try:
                t = c.text or ""
                if ev in t and dep in t:
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", c)
                    time.sleep(0.2)
                    ActionChains(driver).move_to_element(c).pause(0.2).click().perform()
                    return True
            except Exception:
                continue
        scroll_step(driver, 1200)
        time.sleep(0.9)

    return False


# =========================
# ODDS PARSE
# =========================
def tumu_bekle(driver, max_sure=15):
    for _ in range(max_sure):
        try:
            if "Tümü" in driver.find_element(By.TAG_NAME, "body").text:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

def nokta_var_mi(text):
    try:
        if "." not in text:
            return False
        val = float(text)
        return 1.01 <= val <= 99.99
    except:
        return False

def detay_parse(driver):
    oranlar = {}
    body = driver.find_element(By.TAG_NAME, "body")
    lines = [l.strip() for l in body.text.split("\n") if l.strip()]

    try:
        tumu_idx = lines.index("Tümü")
    except ValueError:
        return oranlar

    i = tumu_idx + 1
    current_market = ""
    while i < len(lines) - 1:
        line = lines[i]
        nxt = lines[i + 1]
        if nokta_var_mi(nxt):
            oranlar[f"{current_market}_{line}" if current_market else line] = float(nxt)
            i += 2
            continue
        if not nokta_var_mi(line):
            current_market = line
        i += 1

    return oranlar


# =========================
# mac.json merge save
# =========================
def mac_json_kaydet(yeni_maclar):
    data = {"version": 2, "updated": "", "matches": []}
    if os.path.exists(CIKTI_DOSYA):
        try:
            with open(CIKTI_DOSYA, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            pass

    def key_of(m):
        # tarih+saat+ev+dep ile çakışma azalır
        return f"{m.get('tarih','')}_{m.get('saat','')}_{m.get('ev_sahibi','')}_{m.get('deplasman','')}"

    guncel = {key_of(m): m for m in data.get("matches", [])}
    for m in yeni_maclar:
        guncel[key_of(m)] = m

    yeni_liste = sorted(guncel.values(), key=lambda x: (x.get("tarih",""), x.get("saat","00:00")))
    for i, m in enumerate(yeni_liste, 1):
        m["index"] = i

    data["matches"] = yeni_liste
    data["updated"] = datetime.datetime.now().isoformat()

    os.makedirs(os.path.dirname(CIKTI_DOSYA), exist_ok=True)
    with open(CIKTI_DOSYA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"   💾 Toplam {len(yeni_liste)} maç kaydedildi")


# =========================
# MAIN
# =========================
def main():
    print("=" * 70)
    print("⚽ IDDAA DEEP-ALL (deneme) - tam scroll + 150-250 hedef")
    print("📅", datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
    print("=" * 70)
    print(f"Hedef unique: {TARGET_UNIQUE} | Çekilecek max: {MAX_SCRAPE}")
    print("=" * 70)

    driver = None
    results = []
    success = fail = 0

    try:
        driver = build_driver()
        driver.get(URL)

        if not wait_initial(driver):
            print("❌ İlk içerik gelmedi.")
            return

        print("\n⬇️ Deep harvest başlıyor...")
        harvested = deep_harvest(driver)
        print(f"\n📋 Harvest bitti. Unique: {len(harvested)}")

        # sadece ilk MAX_SCRAPE kadarını çek
        to_scrape = harvested[:MAX_SCRAPE]

        print("\n🔽 Maçlar tek tek açılıyor...\n")
        today = datetime.date.today().isoformat()

        for idx, m in enumerate(to_scrape, 1):
            ev, dep = m["ev"], m["dep"]
            saat = m.get("saat","") or ""
            print(f"[{idx}/{len(to_scrape)}] {saat} | {ev} vs {dep}")

            driver.get(URL)
            time.sleep(4)

            ok = click_match(driver, ev, dep)
            if not ok:
                print("   ❌ tıklanamadı")
                fail += 1
                continue

            time.sleep(2.5)

            # lazy-load tetik
            driver.execute_script("window.scrollTo(0, 600);"); time.sleep(0.7)
            driver.execute_script("window.scrollTo(0, 1200);"); time.sleep(0.7)
            driver.execute_script("window.scrollTo(0, 0);"); time.sleep(0.9)

            tumu = tumu_bekle(driver, 18)
            detay = detay_parse(driver) if tumu else {}
            body = driver.find_element(By.TAG_NAME, "body").text
            odds_count = len(re.findall(r"\b\d{1,2}[.,]\d{2}\b", body))

            print(f"   ✅ tumu={tumu} | detay={len(detay)} | regex_odds={odds_count}")

            results.append({
                "index": 0,
                "mac_kodu": "",
                "ev_sahibi": ev,
                "deplasman": dep,
                "saat": saat,
                "lig": "",
                "tarih": today,
                "cekme_zamani": datetime.datetime.now().isoformat(),
                "durum": "baslamadi",
                "skor_ev": 0,
                "skor_dep": 0,
                "skor_1y_ev": 0,
                "skor_1y_dep": 0,
                "kaynak": "iddaa.com",
                "oranlar": detay
            })

            success += 1

            if idx % 10 == 0:
                mac_json_kaydet(results)

            time.sleep(random.uniform(*SLEEP_BETWEEN_MATCHES))

        mac_json_kaydet(results)

        print("\n" + "=" * 70)
        print("🎉 BİTTİ")
        print("=" * 70)
        print(f"Target: {len(to_scrape)} | Başarılı: {success} | Başarısız: {fail}")
        print("=" * 70)

        git_add_commit_pull_push()

    finally:
        if driver:
            try:
                driver.quit()
            except WebDriverException:
                pass


if __name__ == "__main__":
    main()