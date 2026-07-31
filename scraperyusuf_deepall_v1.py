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

TARGET_UNIQUE = 9999
MAX_SCROLL_STEPS = 120
STABLE_LIMIT = 10
SCROLL_PX = 1300
SCROLL_SLEEP_RANGE = (1.5, 2.5)

MAX_SCRAPE = 9999
SLEEP_BETWEEN_MATCHES = (1.1, 2.4)

MATCH_CARD_SEL = ".i_tnw__t8AmC"
DATE_ITEM_SEL = ".i_tnw__dateItem"
SEARCH_INPUT_SEL = "#eventSearch"

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")
ODD_RE = re.compile(r"^\d{1,2}([.,]\d{2})$")

AYLAR = {
    "Ocak": "01", "Şubat": "02", "Mart": "03", "Nisan": "04", "Mayıs": "05", "Haziran": "06",
    "Temmuz": "07", "Ağustos": "08", "Eylül": "09", "Ekim": "10", "Kasım": "11", "Aralık": "12",
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}


# =========================
# ✅ GİT - ARTIK KESİN GÖNDERİM (SORUN ÇÖZÜLDÜ)
# =========================
ENABLE_GIT_AUTOPUSH = True
GIT_STAGE_FILES = [CIKTI_DOSYA]
REPO_ROOT = Path(__file__).resolve().parent

def _find_git_exe():
    exe = shutil.which("git")
    if exe: return exe
    candidates = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
    ]
    for c in candidates:
        if os.path.exists(c): return c
    return None

def _run_cmd(cmd, cwd=None):
    try:
        r = subprocess.run(
            cmd, cwd=cwd, text=True, capture_output=True, encoding='utf-8', errors='ignore'
        )
        return {"ok": r.returncode == 0, "kod": r.returncode, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}
    except Exception as e:
        return {"ok": False, "hata": str(e)}

def git_force_push():
    """Her durumda main branch'e push eder. Detached HEAD, vs. hepsini halleder."""
    if not ENABLE_GIT_AUTOPUSH or not (REPO_ROOT / ".git").exists():
        print("❌ Git klasörü bulunamadı!")
        return

    git_exe = _find_git_exe()
    if not git_exe:
        print("❌ Git programı bulunamadı!")
        return

    print("\n🔄 GİT İŞLEMLERİ BAŞLADI...")

    # 1. Detay HEAD kontrolü ve düzeltme
    r = _run_cmd([git_exe, "status"], cwd=str(REPO_ROOT))
    if "detached HEAD" in r.get("stdout", "") or "ayrışmış HEAD" in r.get("stdout", ""):
        print("   ⚠️ Detached HEAD tespit edildi, düzeltiliyor...")
        _run_cmd([git_exe, "checkout", "-B", "main"], cwd=str(REPO_ROOT))

    # 2. Branch main'de mi kontrol et
    r_branch = _run_cmd([git_exe, "branch", "--show-current"], cwd=str(REPO_ROOT))
    mevcut_branch = r_branch.get("stdout", "").strip()
    print(f"   📌 Mevcut branch: {mevcut_branch or '(detached)'}")

    if mevcut_branch != "main":
        print(f"   🔄 main branch'e geçiliyor...")
        _run_cmd([git_exe, "checkout", "-B", "main"], cwd=str(REPO_ROOT))

    # 3. Dosyaları ekle
    _run_cmd([git_exe, "add", "."], cwd=str(REPO_ROOT))
    print("   ✅ Dosyalar eklendi")

    # 4. Commit et (yeni değişiklik varsa)
    zaman = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    mesaj = f"Otomatik guncelleme | {zaman}"
    r_commit = _run_cmd([git_exe, "commit", "-m", mesaj, "--allow-empty"], cwd=str(REPO_ROOT))

    if r_commit["ok"]:
        print(f"   ✅ Commit yapıldı: {mesaj}")
    else:
        print(f"   ⚠️ Commit hatası: {r_commit.get('stderr', '')}")

    # 5. Remote'e force push
    print("   🚀 Push ediliyor...")
    r_push = _run_cmd([git_exe, "push", "-f", "origin", "main"], cwd=str(REPO_ROOT))

    if r_push["ok"]:
        print("✅ GİT BAŞARILI - GitHub'a gönderildi!")
    else:
        # Bir daha dene (remote ayarı olmayabilir)
        print("   ⚠️ İlk push başarısız, remote kontrol ediliyor...")
        _run_cmd([git_exe, "remote", "add", "origin", 
                  "https://github.com/yusufkocbiotek-sketch/iddiayusuf.git"], 
                 cwd=str(REPO_ROOT))
        _run_cmd([git_exe, "branch", "-M", "main"], cwd=str(REPO_ROOT))
        r_push2 = _run_cmd([git_exe, "push", "-f", "-u", "origin", "main"], cwd=str(REPO_ROOT))

        if r_push2["ok"]:
            print("✅ GİT BAŞARILI - Remote ayarlandı ve gönderildi!")
        else:
            print(f"❌ GİT HATASI: {r_push2.get('stderr', '')}")

# =========================
# DRIVER - ESKİ HALİYLE
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
    try: driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except: pass
    return driver

def wait_initial(driver, timeout=40):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, MATCH_CARD_SEL)))
        return True
    except: return False


# =========================
# SCROLL - ESKİ HALİYLE
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
    except: pass

def reset_scroll_top(driver):
    try:
        driver.execute_script("""
          if (window.__scrollEl){ window.__scrollEl.scrollTop = 0; }
          window.scrollTo(0,0);
        """)
    except: pass

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
# ✅ TARİH OKUMA - HER MAÇA 2026-05-31 İŞLENİYOR
# =========================
def get_current_date_text(driver):
    try:
        date_el = driver.find_element(By.CSS_SELECTOR, DATE_ITEM_SEL + ".i_tnw__active")
        return date_el.text.strip()
    except:
        bugun = datetime.datetime.now()
        return f"{bugun.day} {list(AYLAR.keys())[bugun.month-1]} {bugun.year}"

def parse_date_text(text):
    if not text:
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")
    
    parts = text.split()
    if len(parts) < 2:
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")
    
    gun = parts[0].zfill(2)
    ay_isim = parts[1]
    ay = AYLAR.get(ay_isim, "05")
    yil = datetime.datetime.now().year
    return f"{yil}-{ay}-{gun}"

def parse_card(card, current_date):
    txt = (card.text or "").strip()
    if not txt: return None

    lines = [x.strip() for x in txt.split("\n") if x.strip() and x.strip() != "-"]

    saat = ""
    for x in lines:
        if TIME_RE.match(x):
            saat = x
            break

    filtered = []
    for x in lines:
        if TIME_RE.match(x): continue
        if ODD_RE.match(x.replace(",", ".")): continue
        if re.fullmatch(r"[A-Z]{2,6}", x): continue
        filtered.append(x)

    if len(filtered) < 2: return None
    ev, dep = filtered[0], filtered[1]
    if not ev or not dep or ev == dep: return None

    return {
        "tarih": current_date,
        "saat": saat,
        "ev_sahibi": ev,
        "deplasman": dep,
        "durum": "baslamadi",
        "skor_ev": 0, "skor_dep": 0, "skor_1y_ev": 0, "skor_1y_dep": 0,
        "oranlar": {},
        "kaynak": "iddaa.com"
    }


def extract_visible(driver, current_date):
    out = []
    seen = set()
    cards = driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL)
    for c in cards:
        m = parse_card(c, current_date)
        if not m: continue
        k = (m["tarih"], m["saat"], m["ev_sahibi"], m["deplasman"])
        if k in seen: continue
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
        date_text = get_current_date_text(driver)
        current_date = parse_date_text(date_text)

        vis = extract_visible(driver, current_date)
        for m in vis:
            k = (m["tarih"], m["saat"], m["ev_sahibi"], m["deplasman"])
            if k not in hset:
                hset.add(k)
                harvest.append(m)

        if len(harvest) > last_total:
            print(f"   📈 Step {step}: unique {last_total} -> {len(harvest)} | Tarih: {current_date}")
            last_total = len(harvest)
            stable = 0
        else:
            stable += 1

        if len(harvest) >= TARGET_UNIQUE: break
        if stable >= STABLE_LIMIT: break

        scroll_step(driver, SCROLL_PX)
        time.sleep(random.uniform(*SCROLL_SLEEP_RANGE))

    return harvest


# =========================
# ❌ İSTENMEYEN ORAN KATEGORİLERİ
# =========================
FILTRELE_MARKET = [
    "Oyuncu Gol Atar",
    "Oyuncu İlk Golü Atar",
    "Oyuncu Son Golü Atar",
    "Oyuncu 2+ Gol Atar",
    "Oyuncu 3+ Gol Atar",
    "Oyuncu Asist Yapar",
    "Oyuncu Ceza Sahası Dışından Gol Atar",
    "Oyuncu Gol Atar Ve Takımı Kazanır",
    "Oyuncu Gol Atar Ve Takımı Kazanır",
    "Oyuncu Ofsayta Düşer",
    "Oyuncu Kafa İle Gol Atar",
    "Oyuncu Frikikten Gol Atar",
    "Oyuncu Hat-trick Yapar",
    "Oyuncu Her Iki Yarı Da Gol Atar",
    "Oyuncu Gol Atar veya Asist Yapar",
    "Oyuncu Kaleyi Bulan Şut Çeker",
    "Oyuncu Kart Görür",
    "Oyuncu Şut",
    "Oyuncu İsabetli Şut",
    "Karşılaşma Özel Bahisleri",
    "Kaleci Kurtarışı",
    "Takım Şut",
    "Takım İsabetli Şut",
    "Takım Faul",
    "Takım Ofsayt",
    "Takım Korner",
    "Takım Kart",
]

# =========================
# ORAN ÇEKME - FİLTRELİ
# =========================
def clear_and_type(el, text):
    el.click(); time.sleep(0.1)
    el.send_keys("\uE009a\uE003"); time.sleep(0.05)
    el.send_keys(text)

def click_match(driver, ev, dep):
    try:
        inp = driver.find_element(By.CSS_SELECTOR, SEARCH_INPUT_SEL)
        clear_and_type(inp, ev[:22]); time.sleep(0.8)
        for c in driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL):
            t = c.text
            if ev in t and dep in t:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", c)
                ActionChains(driver).move_to_element(c).pause(0.2).click().perform()
                return True
        clear_and_type(inp, dep[:22]); time.sleep(0.8)
        for c in driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL):
            t = c.text
            if ev in t and dep in t:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", c)
                ActionChains(driver).move_to_element(c).pause(0.2).click().perform()
                return True
    except: pass
    reset_scroll_top(driver)
    for _ in range(20):
        for c in driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL):
            try:
                t = c.text
                if ev in t and dep in t:
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", c)
                    ActionChains(driver).move_to_element(c).pause(0.2).click().perform()
                    return True
            except: pass
        scroll_step(driver, 800); time.sleep(1)
    return False

def tumu_bekle(driver, max_sure=15):
    for _ in range(max_sure):
        if "Tümü" in driver.find_element(By.TAG_NAME, "body").text:
            return True
        time.sleep(1)
    return False

def nokta_var_mi(t):
    try: return 1.01 <= float(t) <= 99.99
    except: return False

def detay_parse(driver):
    oranlar = {}
    atlanan = 0
    lines = [x.strip() for x in driver.find_element(By.TAG_NAME, "body").text.split("\n") if x.strip()]
    try: idx = lines.index("Tümü")
    except: return oranlar
    i = idx+1
    market=""
    while i < len(lines)-1:
        if nokta_var_mi(lines[i+1]):
            full_key = f"{market}_{lines[i]}" if market else lines[i]
            yasak = any(full_key.lower().startswith(f.lower()) for f in FILTRELE_MARKET)
            if yasak:
                atlanan += 1
            else:
                oranlar[full_key] = float(lines[i+1])
            i+=2
        else:
            market=lines[i]; i+=1
    if atlanan > 0:
        print(f"   🚫 {atlanan} gereksiz oran filtrelendi")
    return oranlar

# =========================
# KAYDET - TARİH SIRALI
# =========================
def mac_json_kaydet(yeni_maclar):
    data = {"version":2, "updated":"", "matches":[]}
    if os.path.exists(CIKTI_DOSYA):
        try:
            with open(CIKTI_DOSYA, "r", encoding="utf-8") as f:
                data = json.load(f)
        except: pass

    def key(m): return (m.get("tarih",""), m.get("saat",""), m.get("ev_sahibi",""), m.get("deplasman",""))
    var = {key(m):m for m in data["matches"]}
    for m in yeni_maclar: var[key(m)] = m

    data["matches"] = sorted(var.values(), key=lambda x:(x.get("tarih",""),x.get("saat","00:00")))
    for i,m in enumerate(data["matches"],1): m["index"]=i
    data["updated"] = datetime.datetime.now().isoformat()

    os.makedirs(os.path.dirname(CIKTI_DOSYA), exist_ok=True)
    with open(CIKTI_DOSYA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"   💾 Kaydedildi: {len(data['matches'])} maç | {CIKTI_DOSYA}")


# =========================
# MAIN - ESKİ HALİYLE
# =========================
def main():
    print("="*70)
    print("⚽ IDDAA | KESİN GÖNDERİM SÜRÜMÜ")
    print("📅", datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
    print("="*70)

    driver = None
    results = []
    success=fail=0
    try:
        driver = build_driver()
        driver.get(URL)

        if not wait_initial(driver):
            print("❌ İçerik yüklenemedi"); return

        print("\n⬇️ Maçlar çekiliyor...")
        harvested = deep_harvest(driver)
        print(f"\n📋 {len(harvested)} maç bulundu (Tarihleri işlendi)")

        print("\n🔽 Oranlar alınıyor...")
        for idx,m in enumerate(harvested[:MAX_SCRAPE],1):
            print(f"[{idx}] {m['tarih']} {m['saat']} | {m['ev_sahibi']} - {m['deplasman']}")
            driver.get(URL); time.sleep(3)
            if not click_match(driver, m["ev_sahibi"], m["deplasman"]):
                print("   ❌ Bulunamadı"); fail+=1; continue

            time.sleep(2)
            driver.execute_script("window.scrollTo(0,800)"); time.sleep(0.5)
            if tumu_bekle(driver,12):
                oran = detay_parse(driver)
                print(f"   ✅ {len(oran)} oran")
                m["oranlar"] = oran
            else:
                m["oranlar"] = {}

            results.append(m)
            success+=1
            if idx%10==0: mac_json_kaydet(results)
            time.sleep(random.uniform(*SLEEP_BETWEEN_MATCHES))

        mac_json_kaydet(results)
        print(f"\n✅ BİTTİ | Başarılı:{success} Başarısız:{fail}")

        # ✅ GİT - ARTIK KESİN GÖNDERİM
        git_force_main_branch()

    finally:
        if driver:
            try: driver.quit()
            except: pass
        input("\n🔚 Kapatmak için ENTER...")

if __name__ == "__main__":
    main()