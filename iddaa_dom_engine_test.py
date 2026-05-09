import json, re, time, datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


URL = "https://www.iddaa.com/canli-skor/futbol"

BASE_DIR = Path(__file__).resolve().parent
OUT_PATH = BASE_DIR / "public" / "data" / "iddaa_canli_skor_dump.json"

DAYS_BACK = 5          # son 5 gün
INCLUDE_TODAY = True   # bugün de dahil olsun

# satır adayları (iddaa next/react => class'lar değişebilir, geniş tutuyoruz)
ROW_SELECTORS = [
    "tr",
    "[class*='match']",
    "[class*='fixture']",
    "[class*='event']",
    "li",
]

SCORE_RE = re.compile(r"(\d+)\s*[-–—]\s*(\d+)")
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}\b")


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
    d = webdriver.Chrome(service=service, options=options)
    d.set_page_load_timeout(60)
    return d


def wait_body(driver, timeout=30):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if driver.find_elements(By.TAG_NAME, "body"):
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def wait_rows_stable(driver, timeout=25, stable_rounds=3):
    """
    Dinamik içerik için: satır sayısı stabil olana kadar bekle.
    """
    t0 = time.time()
    last = -1
    stable = 0
    while time.time() - t0 < timeout:
        n = 0
        for sel in ROW_SELECTORS:
            try:
                n += len(driver.find_elements(By.CSS_SELECTOR, sel))
            except Exception:
                pass

        if n == last and n > 20:
            stable += 1
            if stable >= stable_rounds:
                return True
        else:
            stable = 0
            last = n

        time.sleep(0.7)
    return False


def set_date_try_select(driver, iso_date: str) -> bool:
    """
    Eğer sayfada <select> ile tarih seçimi varsa bunu kullanır.
    """
    try:
        selects = driver.find_elements(By.TAG_NAME, "select")
        for s in selects:
            try:
                sel = Select(s)
                values = [o.get_attribute("value") for o in sel.options]
                if iso_date in values:
                    sel.select_by_value(iso_date)
                    # bazı sayfalarda change event gerekir
                    driver.execute_script("""
                        const el = arguments[0];
                        el.dispatchEvent(new Event('change', {bubbles:true}));
                        el.dispatchEvent(new Event('input', {bubbles:true}));
                    """, s)
                    time.sleep(1.2)
                    return True
            except Exception:
                continue
    except Exception:
        pass
    return False


def set_date_try_click(driver, iso_date: str) -> bool:
    """
    Select yoksa: ekranda iso veya dd.mm.yyyy geçen tıklanabilir eleman arar.
    """
    d = datetime.date.fromisoformat(iso_date)
    ddmmyyyy = d.strftime("%d.%m.%Y")
    ddmmyyyy2 = d.strftime("%d/%m/%Y")

    xps = [
        f"//button[contains(., '{ddmmyyyy}')]|//a[contains(., '{ddmmyyyy}')]|//div[contains(., '{ddmmyyyy}')]",
        f"//button[contains(., '{ddmmyyyy2}')]|//a[contains(., '{ddmmyyyy2}')]|//div[contains(., '{ddmmyyyy2}')]",
        f"//*[@data-date='{iso_date}']",
        f"//*[@aria-label[contains(., '{iso_date}')]]",
    ]

    for xp in xps:
        try:
            els = driver.find_elements(By.XPATH, xp)
            for el in els[:8]:
                try:
                    if not el.is_displayed():
                        continue
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                    time.sleep(0.2)
                    el.click()
                    time.sleep(1.2)
                    return True
                except Exception:
                    continue
        except Exception:
            continue
    return False


def set_date(driver, iso_date: str) -> bool:
    # 1) select ile dene
    if set_date_try_select(driver, iso_date):
        return True
    # 2) click ile dene
    if set_date_try_click(driver, iso_date):
        return True
    return False


def parse_rows(driver, iso_date: str):
    """
    Çok esnek parser: satır text’inden takım + skor + İY skor arar.
    """
    all_rows = []
    for sel in ROW_SELECTORS:
        try:
            all_rows.extend(driver.find_elements(By.CSS_SELECTOR, sel))
        except Exception:
            pass

    out = []
    seen = set()

    for r in all_rows:
        try:
            txt = (r.text or "").strip()
            if not txt:
                continue

            # skor (MS)
            ms = SCORE_RE.search(txt)
            if not ms:
                continue
            skor_ev, skor_dep = int(ms.group(1)), int(ms.group(2))

            # İY skoru (varsa) -> "İY: 0-0" benzeri
            iy_ev = iy_dep = None
            m_iy = re.search(r"(İY|1Y|HT)\s*[:\-]?\s*(\d+)\s*[-–—]\s*(\d+)", txt, re.IGNORECASE)
            if m_iy:
                iy_ev, iy_dep = int(m_iy.group(2)), int(m_iy.group(3))

            # saat (varsa)
            m_time = TIME_RE.search(txt)
            saat = m_time.group(0) if m_time else ""

            # takım isimleri: satırdaki satır satır metinden ilk iki “anlamlı” metni al
            lines = [x.strip() for x in txt.split("\n") if x.strip()]
            # skor/saat/lig gibi satırları ele
            cleaned = []
            for x in lines:
                if TIME_RE.fullmatch(x):
                    continue
                if SCORE_RE.fullmatch(x.replace("–", "-").replace("—", "-")):
                    continue
                if re.fullmatch(r"[A-Z]{2,6}", x):
                    continue
                cleaned.append(x)

            if len(cleaned) < 2:
                continue

            ev, dep = cleaned[0], cleaned[1]
            if ev == dep:
                continue

            key = (iso_date, ev, dep, skor_ev, skor_dep)
            if key in seen:
                continue
            seen.add(key)

            out.append({
                "tarih": iso_date,
                "saat": saat,
                "ev_sahibi": ev,
                "deplasman": dep,
                "skor_ev": skor_ev,
                "skor_dep": skor_dep,
                "skor_1y_ev": iy_ev,
                "skor_1y_dep": iy_dep,
                "kaynak": "iddaa.com/canli-skor",
                "cekme_zamani": datetime.datetime.now().isoformat()
            })
        except Exception:
            continue

    return out


def main():
    driver = None
    try:
        print("="*70)
        print("IDDAA CANLI SKOR TEST (V1) - SONUC/İY ÇEKME")
        print("="*70)

        today = datetime.date.today()
        if INCLUDE_TODAY:
            dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(DAYS_BACK)]
        else:
            dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(1, DAYS_BACK+1)]

        driver = build_driver()
        driver.get(URL)
        wait_body(driver, 30)

        all_data = []
        for d in dates:
            print(f"\n📅 Tarih deneniyor: {d}")
            ok = set_date(driver, d)
            if not ok:
                print("   ⚠️ Tarih seçilemedi (selector gerekebilir) -> yine de parse denenecek")

            wait_rows_stable(driver, timeout=25, stable_rounds=3)

            day_rows = parse_rows(driver, d)
            print(f"   ✅ Bulunan maç: {len(day_rows)}")
            all_data.extend(day_rows)

        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(json.dumps({
            "created_at": datetime.datetime.now().isoformat(),
            "source_url": URL,
            "days": dates,
            "count": len(all_data),
            "matches": all_data
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"\n💾 Yazıldı: {OUT_PATH.resolve()}")

    finally:
        if driver:
            try:
                driver.quit()
            except WebDriverException:
                pass


if __name__ == "__main__":
    main()