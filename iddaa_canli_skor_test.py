import time, re, datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import WebDriverException, TimeoutException

from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.iddaa.com/canli-skor/futbol"

OUT_DIR = Path("debug_canli_skor")
OUT_DIR.mkdir(exist_ok=True)

DATE_LABEL_RE = re.compile(r"^\s*(\d{1,2})\s+([A-Za-z]{3})\s+(\d{2})\s*$")
SCORE_ANY_RE = re.compile(r"\b\d+\s*[-–—:]\s*\d+\b")


MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}
MONTH_ABBR_BY_NUM = {v: k for k, v in MONTHS.items()}


def build_driver():
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-notifications")
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.set_page_load_timeout(60)
    return d


def dump(driver, tag):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html = OUT_DIR / f"{tag}_{ts}.html"
    png = OUT_DIR / f"{tag}_{ts}.png"
    try:
        driver.switch_to.default_content()
    except Exception:
        pass
    html.write_text(driver.page_source, encoding="utf-8")
    driver.save_screenshot(str(png))
    print("🧾 HTML:", html.resolve())
    print("🖼️ PNG :", png.resolve())


def click_cookie_if_any(driver):
    xps = [
        "//button[contains(.,'Kabul') or contains(.,'kabul')]",
        "//button[contains(.,'Accept') or contains(.,'I agree')]",
        "//button[contains(.,'Tamam')]",
        "//button[contains(.,'OK')]",
    ]
    for xp in xps:
        try:
            btns = driver.find_elements(By.XPATH, xp)
            for b in btns[:2]:
                if b.is_displayed():
                    driver.execute_script("arguments[0].click();", b)
                    time.sleep(0.5)
                    return
        except Exception:
            pass


def debug_takvim_candidates(driver, context="default"):
    candidates = driver.find_elements(By.XPATH, "//button[@aria-haspopup='dialog']")
    matched = []
    for b in candidates:
        try:
            aria = (b.get_attribute("aria-label") or "").strip()
            txt = (b.text or "").strip()
            disp = b.is_displayed()
            controls = (b.get_attribute("aria-controls") or "").strip()
            aria_l = aria.lower()
            txt_l = txt.lower()
            if ("takvim" in aria_l) or ("takvim" in txt_l) or ("bugün" in txt_l) or ("bugun" in txt_l):
                matched.append((aria, txt, disp, controls, b))
        except Exception:
            continue
    print(f"\n--- TAKVİM ADAYLARI ({context}) ---")
    print("TOPLAM matching:", len(matched))
    for i, (aria, txt, disp, controls, _) in enumerate(matched[:10], 1):
        print(f"{i}) displayed={disp} aria-label={aria!r} text={txt!r} aria-controls={controls!r}")
    return matched


def find_takvim_in_any_iframe(driver):
    matched_main = debug_takvim_candidates(driver, context="main")
    if matched_main:
        btn = next((item[-1] for item in matched_main if item[2]), matched_main[0][-1])
        return ("main", None, btn)

    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"\niframe sayısı: {len(iframes)}")

    for idx, fr in enumerate(iframes):
        try:
            driver.switch_to.frame(fr)
            matched = debug_takvim_candidates(driver, context=f"iframe[{idx}]")
            if matched:
                btn = next((item[-1] for item in matched if item[2]), matched[0][-1])
                return (f"iframe[{idx}]", idx, btn)
        except Exception:
            pass
        finally:
            try:
                driver.switch_to.default_content()
            except Exception:
                pass

    return (None, None, None)


def _calendar_visible_in_doc(driver):
    els = driver.find_elements(
        By.XPATH,
        "//*[@role='dialog' or @aria-modal='true' or @data-radix-dialog-content]"
    )
    for el in els:
        try:
            if el.is_displayed():
                return True
        except Exception:
            continue
    return False


def wait_for_calendar_open_any_context(driver, timeout=25):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        # default
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        try:
            if _calendar_visible_in_doc(driver):
                return
        except Exception:
            pass

        # iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for fr in iframes:
            try:
                driver.switch_to.frame(fr)
                if _calendar_visible_in_doc(driver):
                    return
            except Exception:
                pass
            finally:
                try:
                    driver.switch_to.default_content()
                except Exception:
                    pass

        time.sleep(0.2)

    raise TimeoutException("Takvim dialog'u açıldı ama görünür yakalayamadım.")


def click_takvim(driver):
    _, ctx_idx, btn = find_takvim_in_any_iframe(driver)
    if btn is None:
        raise RuntimeError("Takvim butonu bulunamadı.")

    if ctx_idx is not None:
        driver.switch_to.default_content()
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframes[ctx_idx])

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(btn))
        btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn)

    wait_for_calendar_open_any_context(driver, timeout=25)


def iter_contexts(driver):
    # default + all iframes (ilkini bulmak için yeterli)
    contexts = [("default", None)]
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for i in range(len(iframes)):
        contexts.append((f"iframe[{i}]", i))
    return contexts, iframes


def get_takvim_trigger_labels_any_context(driver):
    """
    Takvim butonundaki görünen truncate label’ı okur:
      ör: '8 May 26' / 'Bugün' / 'Dün'
    """
    labels = set()
    contexts, iframes = iter_contexts(driver)

    for _, idx in contexts:
        try:
            if idx is None:
                driver.switch_to.default_content()
            else:
                driver.switch_to.frame(iframes[idx])
        except Exception:
            continue

        try:
            btns = driver.find_elements(By.XPATH, "//button[@aria-label='Takvim']")
            for b in btns[:5]:
                try:
                    spans = b.find_elements(By.XPATH, ".//span[contains(@class,'truncate')]")
                    if spans:
                        val = (spans[0].text or "").strip()
                    else:
                        val = (b.text or "").strip()
                    if val:
                        labels.add(val)
                except Exception:
                    pass
        except Exception:
            pass

    # default back
    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    return sorted(labels)


def parse_label_or_fallback_to_base_date(base_labels):
    """
    base_labels: takvim buton label'ları listesi
    """
    # Tarih formatlı olanı bul (örn: "8 May 26")
    for lab in base_labels:
        m = DATE_LABEL_RE.match(lab)
        if m:
            day = int(m.group(1))
            mon_abbr = m.group(2)
            yy = int(m.group(3))
            mon = MONTHS.get(mon_abbr)
            if mon:
                year = 2000 + yy
                return datetime.date(year, mon, day)

    # Değilse Bugün/Dün fallback
    norm = {l.strip().lower() for l in base_labels}
    today = datetime.date.today()
    if "bugün" in norm or "bugun" in norm or "today" in norm:
        return today
    if "dün" in norm or "dun" in norm or "yesterday" in norm:
        return today - datetime.timedelta(days=1)

    # en son fallback
    return today


def expected_label_from_iso(iso_date):
    d = datetime.date.fromisoformat(iso_date)
    return f"{d.day} {MONTH_ABBR_BY_NUM[d.month]} {str(d.year % 100).zfill(2)}"


def _find_day_button_in_context(driver, iso_date):
    xpath = f"//*[@data-day='{iso_date}']//button"
    buttons = driver.find_elements(By.XPATH, xpath)
    if not buttons:
        return None

    # Önce disabled/hidden filtrele, sonra ilk görünen
    for b in buttons:
        try:
            if not b.is_displayed():
                continue
            if (b.get_attribute("aria-disabled") or "").lower() == "true":
                continue
            if b.get_attribute("disabled") is not None:
                continue
            return b
        except Exception:
            continue

    for b in buttons:
        try:
            if b.is_displayed():
                return b
        except Exception:
            pass
    return None


def click_day_by_data_day_any_context(driver, iso_date):
    contexts, iframes = iter_contexts(driver)

    for _, idx in contexts:
        try:
            if idx is None:
                driver.switch_to.default_content()
            else:
                driver.switch_to.frame(iframes[idx])
        except Exception:
            continue

        el = _find_day_button_in_context(driver, iso_date)
        if el:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            except Exception:
                pass
            try:
                driver.execute_script("arguments[0].click();", el)
            except Exception:
                try:
                    el.click()
                except Exception:
                    pass
            return True

    return False


def wait_for_label_contains(driver, expected_label, timeout=12):
    end = time.monotonic() + timeout
    last = []
    while time.monotonic() < end:
        try:
            labels = get_takvim_trigger_labels_any_context(driver)
            last = labels
            if expected_label in labels:
                return True, labels
        except Exception:
            pass
        time.sleep(0.2)
    return False, last


def main():
    d = None
    try:
        d = build_driver()
        print("📡 Açılıyor:", URL)
        d.get(URL)
        time.sleep(5)

        click_cookie_if_any(d)

        try:
            body_text = d.find_element(By.TAG_NAME, "body").text
            print("Skor pattern sayısı (body):", len(SCORE_ANY_RE.findall(body_text)))
        except Exception:
            pass

        dump(d, "canli_skor_once")

        # 1) takvimi aç
        print("\n--- TAKVİM AÇ ---")
        click_takvim(d)
        dump(d, "takvim_acildi")

        # 2) mevcut label'ı oku (Bugün/8 May 26 vs)
        base_labels = get_takvim_trigger_labels_any_context(d)
        print("\n--- BASE TAKVİM BUTON LABEL'LARI ---")
        print("base_labels:", base_labels)

        base_date = parse_label_or_fallback_to_base_date(base_labels)
        print("base_date:", base_date.isoformat())

        # 3) hedef: base_date - 1 (dün)
        target_date = base_date - datetime.timedelta(days=1)
        target_iso = target_date.isoformat()
        expected_label = expected_label_from_iso(target_iso)

        print("\n--- DÜN SEÇİMİ ---")
        print("target_iso:", target_iso)
        print("expected_label:", expected_label)

        # 4) hedef günü tıkla
        ok_click = click_day_by_data_day_any_context(d, target_iso)
        print("click_day_by_data_day_any_context ok:", ok_click)

        # 5) label değişimini doğrula (en güvenilir)
        ok, labels = wait_for_label_contains(d, expected_label, timeout=12)
        print("✅ Label beklenenle eşleşti mi?:", ok)
        print("Mevcut label'lar:", labels)

        if not ok:
            dump(d, "takvim_dun_label_fail")

        dump(d, "after_dun")

        print("\n✅ Debug tamam. debug_canli_skor klasörüne bak.")

    except Exception as e:
        print("\n❌ Hata:", e)
        if d:
            dump(d, "takvim_hata")
        raise
    finally:
        if d:
            try:
                d.quit()
            except WebDriverException:
                pass


if __name__ == "__main__":
    main()