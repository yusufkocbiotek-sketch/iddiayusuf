import json
import os
import datetime
import time
import random
import re
import shutil
import subprocess
import traceback
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# =========================
# AYARLAR
# =========================
URL = "https://www.iddaa.com/program/futbol"
CIKTI_DOSYA = "public/data/mac.json"

MAX_SCROLL_STEPS = 120
STABLE_LIMIT = 10
SCROLL_PX = 1300
SCROLL_SLEEP_RANGE = (1.5, 2.5)

MAX_SCRAPE = 9999
SLEEP_BETWEEN_MATCHES = (1.1, 2.4)
HARVEST_MAC_SAYISI = 50

MATCH_CARD_SEL = ".i_tnw__t8AmC"
DATE_ITEM_SEL = ".i_tnw__dateItem"
SEARCH_INPUT_SEL = "#eventSearch"

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")
ODD_RE = re.compile(r"^\d{1,2}([.,]\d{2})$")

AYLAR = {
    "Ocak": "01", "Şubat": "02", "Mart": "03", "Nisan": "04",
    "Mayıs": "05", "Haziran": "06", "Temmuz": "07", "Ağustos": "08",
    "Eylül": "09", "Ekim": "10", "Kasım": "11", "Aralık": "12",
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}

SILINECEK_BASLANGICLAR = (
    "oyuncu", "100.00", "takım",
    "karşılaşma özel bahisleri", "kaleci kurtarışı"
)


# =========================
# TARİH
# =========================
def bugunun_tarihi():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def yarinin_tarihi():
    return (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")


def get_current_date_text(driver):
    try:
        date_el = driver.find_element(
            By.CSS_SELECTOR, DATE_ITEM_SEL + ".i_tnw__active"
        )
        return date_el.text.strip()
    except Exception:
        bugun = datetime.datetime.now()
        return f"{bugun.day} {list(AYLAR.keys())[bugun.month - 1]} {bugun.year}"


def parse_date_text(text):
    if not text:
        return datetime.datetime.now().strftime("%Y-%m-%d")

    parts = text.split()
    if len(parts) < 2:
        return datetime.datetime.now().strftime("%Y-%m-%d")

    gun = parts[0].zfill(2)
    ay_isim = parts[1]
    ay = AYLAR.get(ay_isim, datetime.datetime.now().strftime("%m"))
    yil = datetime.datetime.now().year
    return f"{yil}-{ay}-{gun}"


# =========================
# GİT
# =========================
ENABLE_GIT_AUTOPUSH = True
REPO_ROOT = Path(__file__).resolve().parent


def _find_git_exe():
    exe = shutil.which("git")
    if exe:
        return exe
    for c in [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
    ]:
        if os.path.exists(c):
            return c
    return None


def _run_cmd(cmd, cwd=None):
    try:
        r = subprocess.run(
            cmd, cwd=cwd, text=True, capture_output=True,
            encoding='utf-8', errors='ignore'
        )
        return {
            "ok": r.returncode == 0,
            "kod": r.returncode,
            "stdout": r.stdout.strip(),
            "stderr": r.stderr.strip()
        }
    except Exception as e:
        return {"ok": False, "hata": str(e)}


def git_force_push():
    if not ENABLE_GIT_AUTOPUSH or not (REPO_ROOT / ".git").exists():
        print("❌ Git klasörü bulunamadı!")
        return

    git_exe = _find_git_exe()
    if not git_exe:
        print("❌ Git programı bulunamadı!")
        return

    print("\n🔄 GİT İŞLEMLERİ BAŞLADI...")

    _run_cmd([git_exe, "checkout", "-B", "main"], cwd=str(REPO_ROOT))
    print("   📌 main branch'e geçildi")

    _run_cmd([git_exe, "add", "."], cwd=str(REPO_ROOT))
    print("   ✅ Dosyalar eklendi")

    zaman = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    mesaj = f"Otomatik guncelleme | {zaman}"
    _run_cmd([git_exe, "commit", "-m", mesaj, "--allow-empty"], cwd=str(REPO_ROOT))
    print(f"   ✅ Commit: {mesaj}")

    print("   🚀 Push ediliyor...")
    r_push = _run_cmd([git_exe, "push", "-f", "origin", "main"], cwd=str(REPO_ROOT))

    if r_push["ok"]:
        print("✅ GİT BAŞARILI!")
    else:
        print(f"❌ HATA: {r_push.get('stderr', '')}")


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
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(30)
    try:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
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


def guvenli_yukle(driver, url, max_deneme=3):
    for deneme in range(max_deneme):
        try:
            driver.set_page_load_timeout(45)
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, MATCH_CARD_SEL))
            )
            body_text = driver.find_element(By.TAG_NAME, "body").text.strip()
            if len(body_text) < 50:
                print(f"      ⚠️ Sayfa beyaz (deneme {deneme + 1})")
                time.sleep(3)
                continue
            time.sleep(1)
            return True
        except Exception as e:
            print(f"      ⚠️ Yükleme hatası (deneme {deneme + 1}): {str(e)[:60]}")
            if deneme < max_deneme - 1:
                time.sleep(3)
                try:
                    driver.quit()
                except Exception:
                    pass
                time.sleep(2)
                try:
                    driver = build_driver()
                    driver.get(url)
                    time.sleep(5)
                except Exception:
                    pass
            else:
                time.sleep(5)
    return False


# =========================
# SCROLL
# =========================
def init_scroll_target(driver):
    try:
        driver.execute_script("""
          (function(){
            const els = Array.from(document.querySelectorAll('*'));
            const cands = els.filter(el=>{
              const s = getComputedStyle(el);
              const oy = s.overflowY;
              return (oy==='auto' || oy==='scroll')
                && (el.scrollHeight - el.clientHeight) > 600
                && el.clientHeight > 300;
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
# MAÇ KART OKUMA
# =========================
def parse_card(card, current_date):
    txt = (card.text or "").strip()
    if not txt:
        return None

    lines = [
        x.strip() for x in txt.split("\n")
        if x.strip() and x.strip() != "-"
    ]

    saat = ""
    for x in lines:
        if TIME_RE.match(x):
            saat = x
            break

    filtered = []
    for x in lines:
        if TIME_RE.match(x):
            continue
        if ODD_RE.match(x.replace(",", ".")):
            continue
        if re.fullmatch(r"[A-Z]{2,6}", x):
            continue
        filtered.append(x)

    if len(filtered) < 2:
        return None

    ev, dep = filtered[0], filtered[1]
    if not ev or not dep or ev == dep:
        return None

    return {
        "tarih": current_date,
        "saat": saat,
        "ev_sahibi": ev,
        "deplasman": dep,
        "durum": "baslamadi",
        "skor_ev": 0, "skor_dep": 0,
        "skor_1y_ev": 0, "skor_1y_dep": 0,
        "oranlar": {},
        "kaynak": "iddaa.com"
    }


def extract_visible(driver, current_date):
    out = []
    seen = set()
    cards = driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL)
    for c in cards:
        m = parse_card(c, current_date)
        if not m:
            continue
        k = (m["tarih"], m["saat"], m["ev_sahibi"], m["deplasman"])
        if k in seen:
            continue
        seen.add(k)
        out.append(m)
    return out


# =========================
# DEEP HARVEST (BUGÜN + YARIN BUTONLARI)
# =========================
def gun_sec(driver, gun_adi):
    """Bugün veya Yarın butonuna tıkla"""
    tiklandi = driver.execute_script("""
        var labels = document.querySelectorAll('label, i, em, span');
        for (var i = 0; i < labels.length; i++) {
            var t = labels[i].textContent.trim();
            if (t === arguments[0]) {
                labels[i].click();
                return true;
            }
        }
        return false;
    """, gun_adi)
    return tiklandi


def sayfayi_scroll_et(driver, hedef_tarih, max_step=MAX_SCROLL_STEPS):
    """Tek sayfanın tüm maçlarını scroll ile çek"""
    init_scroll_target(driver)
    reset_scroll_top(driver)
    time.sleep(2)

    maclar = []
    seen = set()
    stable = 0
    last_total = 0

    for step in range(1, max_step + 1):
        vis = extract_visible(driver, hedef_tarih)
        for m in vis:
            if m["tarih"] != hedef_tarih:
                continue
            k = (m["tarih"], m["saat"], m["ev_sahibi"], m["deplasman"])
            if k not in seen:
                seen.add(k)
                maclar.append(m)

        if len(maclar) > last_total:
            print(f"      📈 Step {step}: {len(maclar)} maç")
            last_total = len(maclar)
            stable = 0
        else:
            stable += 1

        if stable >= STABLE_LIMIT:
            break

        scroll_step(driver, SCROLL_PX)
        time.sleep(random.uniform(*SCROLL_SLEEP_RANGE))

    return maclar


def deep_harvest(driver):
    bugun = bugunun_tarihi()
    yarin = yarinin_tarihi()
    print(f"   🎯 Bugün: {bugun} | Yarın: {yarin}")

    harvest = []
    hset = set()

    for gun_tarih, gun_adi in [(bugun, "Bugün"), (yarin, "Yarın")]:
        print(f"\n   📅 {gun_adi} ({gun_tarih}) seçiliyor...")

        tiklandi = gun_sec(driver, gun_adi)
        if not tiklandi:
            print(f"      ❌ '{gun_adi}' butonu bulunamadı")
            continue

        time.sleep(3)
        print(f"      ✅ '{gun_adi}' seçildi")

        maclar = sayfayi_scroll_et(driver, gun_tarih)

        for m in maclar:
            k = (m["tarih"], m["saat"], m["ev_sahibi"], m["deplasman"])
            if k not in hset:
                hset.add(k)
                harvest.append(m)

        bugun_adet = sum(1 for h in harvest if h["tarih"] == bugun)
        yarin_adet = sum(1 for h in harvest if h["tarih"] == yarin)
        print(f"      📊 {len(maclar)} maç çekildi | Toplam: {len(harvest)} (Bugün:{bugun_adet} Yarın:{yarin_adet})")

    bugun_adet = sum(1 for m in harvest if m["tarih"] == bugun)
    yarin_adet = sum(1 for m in harvest if m["tarih"] == yarin)
    print(f"\n   🎯 Toplam: {len(harvest)} maç (Bugün: {bugun_adet}, Yarın: {yarin_adet})")
    return harvest


# =========================
# ORAN ÇEKME
# =========================
def clear_and_type(el, text):
    el.click()
    time.sleep(0.1)
    el.send_keys("\uE009a\uE003")
    time.sleep(0.05)
    el.send_keys(text)


def click_match(driver, ev, dep):
    try:
        inp = driver.find_element(By.CSS_SELECTOR, SEARCH_INPUT_SEL)

        clear_and_type(inp, ev[:22])
        time.sleep(0.8)
        for c in driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL):
            t = c.text
            if ev in t and dep in t:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", c
                )
                ActionChains(driver).move_to_element(c).pause(0.2).click().perform()
                return True

        clear_and_type(inp, dep[:22])
        time.sleep(0.8)
        for c in driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL):
            t = c.text
            if ev in t and dep in t:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", c
                )
                ActionChains(driver).move_to_element(c).pause(0.2).click().perform()
                return True

    except Exception:
        pass

    reset_scroll_top(driver)
    for _ in range(20):
        for c in driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL):
            try:
                t = c.text
                if ev in t and dep in t:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});", c
                    )
                    ActionChains(driver).move_to_element(c).pause(0.2).click().perform()
                    return True
            except Exception:
                pass
        scroll_step(driver, 800)
        time.sleep(1)

    return False


def tumu_bekle(driver, max_sure=15):
    for _ in range(max_sure):
        if "Tümü" in driver.find_element(By.TAG_NAME, "body").text:
            return True
        time.sleep(1)
    return False


def nokta_var_mi(t):
    try:
        return 1.01 <= float(t) <= 99.99
    except Exception:
        return False


def detay_parse(driver):
    oranlar = {}
    atlanan = 0
    lines = [
        x.strip() for x in
        driver.find_element(By.TAG_NAME, "body").text.split("\n")
        if x.strip()
    ]
    try:
        idx = lines.index("Tümü")
    except ValueError:
        return oranlar

    i = idx + 1
    market = ""

    while i < len(lines) - 1:
        if nokta_var_mi(lines[i + 1]):
            full_key = f"{market}_{lines[i]}" if market else lines[i]
            k = full_key.strip().lower()

            if k.startswith(SILINECEK_BASLANGICLAR):
                atlanan += 1
            else:
                oranlar[full_key] = float(lines[i + 1])

            i += 2
        else:
            market = lines[i]
            i += 1

    if atlanan > 0:
        print(f"   🚫 {atlanan} gereksiz oran filtrelendi")

    return oranlar


# =========================
# JSON KAYDET
# =========================
def mac_json_kaydet(yeni_maclar):
    data = {"version": 2, "updated": "", "matches": []}
    if os.path.exists(CIKTI_DOSYA):
        try:
            with open(CIKTI_DOSYA, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    def key(m):
        return (
            m.get("tarih", ""), m.get("saat", ""),
            m.get("ev_sahibi", ""), m.get("deplasman", "")
        )

    var = {key(m): m for m in data["matches"]}
    for m in yeni_maclar:
        var[key(m)] = m

    data["matches"] = sorted(
        var.values(),
        key=lambda x: (x.get("tarih", ""), x.get("saat", "00:00"))
    )
    for i, m in enumerate(data["matches"], 1):
        m["index"] = i
    data["updated"] = datetime.datetime.now().isoformat()

    os.makedirs(os.path.dirname(CIKTI_DOSYA), exist_ok=True)
    with open(CIKTI_DOSYA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"   💾 Kaydedildi: {len(data['matches'])} maç | {CIKTI_DOSYA}")


# =========================
# MAIN
# =========================
def main():
    print("=" * 70)
    print("⚽ IDDAA SCRAPER")
    print("📅", datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
    print("=" * 70)

    driver = None
    results = []
    success = fail = 0

    try:
        print("\n🟢 Chrome açılıyor...")
        driver = build_driver()

        if not guvenli_yukle(driver, URL):
            print("❌ İlk yükleme başarısız")
            return

        if not wait_initial(driver):
            print("❌ İçerik yüklenemedi")
            return

        print("\n⬇️ Maçlar çekiliyor...")
        harvested = deep_harvest(driver)
        toplam = len(harvested)
        print(f"\n📋 {toplam} maç bulundu")

        print("\n🔽 Oranlar alınıyor...")
        for idx, m in enumerate(harvested[:MAX_SCRAPE], 1):
            print(
                f"[{idx}/{toplam}] {m['tarih']} {m['saat']} | "
                f"{m['ev_sahibi']} - {m['deplasman']}"
            )

            if idx > 1 and idx % HARVEST_MAC_SAYISI == 1:
                print(f"\n{'=' * 50}")
                print(f"🔄 {HARVEST_MAC_SAYISI} maç tamamlandı, Chrome yenileniyor...")
                print(f"{'=' * 50}")

                mac_json_kaydet(results)

                try:
                    driver.quit()
                except Exception:
                    pass
                print("   🔴 Chrome kapatıldı")

                time.sleep(5)
                print("   ⏳ 5 saniye bekleniyor...")

                try:
                    driver = build_driver()
                    print("   🟢 Yeni Chrome açıldı")
                except Exception as e:
                    print(f"   ❌ Chrome açılamadı: {e}")
                    time.sleep(10)
                    driver = build_driver()
                    print("   🟢 Yeni Chrome açıldı (2. deneme)")

                if not guvenli_yukle(driver, URL):
                    print("   ❌ Sayfa yüklenemedi")
                    time.sleep(5)
                    driver.get(URL)
                    time.sleep(10)

                print("   ✅ Devam ediliyor...")
                print(f"{'=' * 50}\n")

            try:
                driver.set_page_load_timeout(45)
                driver.get(URL)
                time.sleep(3)
            except Exception as e:
                print(f"   ⚠️ Sayfa yüklenemedi: {str(e)[:60]}")
                time.sleep(5)
                try:
                    driver.quit()
                except Exception:
                    pass
                try:
                    driver = build_driver()
                    driver.get(URL)
                    time.sleep(5)
                except Exception:
                    print("   ❌ Driver yenilenemedi, maç atlanıyor")
                    fail += 1
                    continue

            try:
                if not click_match(driver, m["ev_sahibi"], m["deplasman"]):
                    print("   ❌ Bulunamadı")
                    fail += 1
                    continue
            except Exception as e:
                print(f"   ❌ Maç arama hatası: {str(e)[:60]}")
                fail += 1
                continue

            time.sleep(2)
            try:
                driver.execute_script("window.scrollTo(0,800)")
                time.sleep(0.5)
                if tumu_bekle(driver, 12):
                    oran = detay_parse(driver)
                    print(f"   ✅ {len(oran)} oran")
                    m["oranlar"] = oran
                else:
                    print("   ⚠️ Tümü bulunamadı")
                    m["oranlar"] = {}
            except Exception as e:
                print(f"   ⚠️ Oran hatası: {str(e)[:60]}")
                m["oranlar"] = {}

            results.append(m)
            success += 1

            if idx % 10 == 0:
                mac_json_kaydet(results)

            time.sleep(random.uniform(*SLEEP_BETWEEN_MATCHES))

        mac_json_kaydet(results)
        print(f"\n✅ BİTTİ | Başarılı: {success} | Başarısız: {fail}")

    except Exception as e:
        print(f"\n❌ ANA HATA: {e}")
        traceback.print_exc()
        if results:
            print("   💾 Mevcut veriler kaydediliyor...")
            mac_json_kaydet(results)

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

        git_force_push()


if __name__ == "__main__":
    main()