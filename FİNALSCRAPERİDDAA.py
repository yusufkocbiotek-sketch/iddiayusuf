import time
import json
import shutil
import subprocess
import traceback
import re
from datetime import date, timedelta, datetime
from pathlib import Path
from difflib import SequenceMatcher

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


# ============================================================
# AYARLAR
# ============================================================

URL = "https://www.iddaa.com/canli-skor/futbol"

OUT_DIR = Path(r"C:\Users\YUSUF\OneDrive\Desktop\iddaa_scraper_output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# GG/AA/YYYY
BASLANGIC_TARIHI = "10/09/2026"
BITIS_TARIHI = "18/09/2026"

# FUZZY EŞLEŞTİRME
ESLESME_TOLERANSI_GUN = 10
BENZERLIK_ESIK = 0.70

# BEKLEME SÜRELERİ
SAYFA_BEKLEME_SURESI = 4
TAKVIM_ACILMA_BEKLEME = 1.5
TARIH_SECILDIKTEN_SONRA_BEKLEME = 3
SCROLL_BEKLEME = 0.8

MAX_IFRAME_DERINLIK = 6
MAX_AY_GECIS = 48
MAX_SCROLL_ADIMI = 220


# ============================================================
# GENEL YARDIMCILAR
# ============================================================

def temiz_isim(text):
    text = str(text or "").lower().strip()
    text = re.sub(r"[^a-z0-9çğıöşü ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def benzerlik(a, b):
    return SequenceMatcher(
        None,
        temiz_isim(a),
        temiz_isim(b)
    ).ratio()


def parse_tarih(value):
    if not value:
        return None

    value = str(value).strip()
    value = value.split("T")[0].split(" ")[0]

    for fmt in [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%Y/%m/%d",
    ]:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    return None


def tarih_farki(t1, t2):
    d1 = parse_tarih(t1)
    d2 = parse_tarih(t2)

    if not d1 or not d2:
        return 999

    return abs((d1 - d2).days)


def tarih_araligi_olustur(baslangic, bitis):
    d1 = datetime.strptime(baslangic, "%d/%m/%Y").date()
    d2 = datetime.strptime(bitis, "%d/%m/%Y").date()

    if d1 > d2:
        raise ValueError("Başlangıç tarihi bitiş tarihinden büyük olamaz.")

    tarihler = []

    while d1 <= d2:
        tarihler.append(d1)
        d1 += timedelta(days=1)

    return tarihler


def get_mac_json_path():
    paths = [
        Path(
            r"C:\Users\YUSUF\OneDrive\Desktop"
            r"\iddiayusuf-main\public\data\mac.json"
        ),
        Path(
            r"C:\Users\YUSUF\Desktop"
            r"\iddiayusuf-main\public\data\mac.json"
        ),
    ]

    for path in paths:
        if path.exists():
            return path

    try:
        current = Path(__file__).resolve().parent

        for _ in range(8):
            test_path = current / "public" / "data" / "mac.json"

            if test_path.exists():
                return test_path

            if current.parent == current:
                break

            current = current.parent

    except Exception:
        pass

    return paths[0]


MAC_JSON_PATH = get_mac_json_path()


# ============================================================
# SELENIUM / CHROME
# ============================================================

def build_driver():
    options = Options()

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    options.add_experimental_option(
        "useAutomationExtension",
        False
    )

    driver = webdriver.Chrome(options=options)

    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    driver.set_page_load_timeout(60)

    return driver


def sayfa_yuklenmesini_bekle(driver, timeout=30):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )
        return True
    except Exception:
        return False


def dismiss_cookies(driver):
    xpaths = [
        "//button[contains(., 'Tümünü Kabul')]",
        "//button[contains(., 'Kabul')]",
        "//button[contains(., 'Accept')]",
        "//button[@id='onetrust-accept-btn-handler']",
    ]

    for xpath in xpaths:
        try:
            for button in driver.find_elements(By.XPATH, xpath):
                if button.is_displayed():
                    driver.execute_script(
                        "arguments[0].click();",
                        button
                    )
                    print("🍪 Çerez bildirimi kapatıldı.")
                    time.sleep(1)
                    return True
        except Exception:
            pass

    return False


def guvenli_tikla(driver, element):
    if not element:
        return False

    try:
        driver.execute_script("""
            arguments[0].scrollIntoView({
                block: 'center',
                inline: 'center'
            });
        """, element)

        time.sleep(0.2)

        driver.execute_script(
            "arguments[0].click();",
            element
        )

        return True

    except Exception:
        try:
            element.click()
            return True
        except Exception:
            return False


def debug_kaydet(driver, prefix):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        image_path = OUT_DIR / f"{prefix}_{stamp}.png"
        driver.save_screenshot(str(image_path))
        print(f"📸 Debug ekran görüntüsü: {image_path}")
    except Exception:
        pass

    try:
        html_path = OUT_DIR / f"{prefix}_{stamp}.html"
        html_path.write_text(
            driver.page_source,
            encoding="utf-8"
        )
        print(f"📄 Debug HTML: {html_path}")
    except Exception:
        pass


# ============================================================
# IFRAME RECURSIVE ARAMA
# ============================================================

def recursive_context_bul(driver, condition_func, depth=0, path="ana-sayfa"):
    if depth > MAX_IFRAME_DERINLIK:
        return False

    try:
        if condition_func(driver):
            print(f"✅ Uygun içerik bulundu: {path}")
            return True
    except Exception:
        pass

    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
    except Exception:
        return False

    for index, iframe in enumerate(iframes):
        try:
            driver.switch_to.frame(iframe)

            if recursive_context_bul(
                driver,
                condition_func,
                depth + 1,
                f"{path} > iframe[{index}]"
            ):
                return True

            driver.switch_to.parent_frame()

        except Exception:
            try:
                driver.switch_to.parent_frame()
            except Exception:
                driver.switch_to.default_content()

    return False


# ============================================================
# TAKVİM / TARİH SEÇİMİ
# ============================================================

INGILIZCE_GUNLER = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]

INGILIZCE_AYLAR = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]


def ingilizce_sira_eki(gun):
    if 10 < gun % 100 < 14:
        return "th"

    return {
        1: "st",
        2: "nd",
        3: "rd"
    }.get(gun % 10, "th")


def hedef_aria_label_olustur(target_date):
    return (
        f"{INGILIZCE_GUNLER[target_date.weekday()]}, "
        f"{INGILIZCE_AYLAR[target_date.month - 1]} "
        f"{target_date.day}{ingilizce_sira_eki(target_date.day)}, "
        f"{target_date.year}"
    )


def aria_tarih_parse(label):
    try:
        match = re.search(
            r"^[A-Za-z]+,\s+([A-Za-z]+)\s+"
            r"(\d{1,2})(st|nd|rd|th),\s+(\d{4})$",
            str(label or "").strip()
        )

        if not match:
            return None

        month_name = match.group(1)
        day_number = int(match.group(2))
        year_number = int(match.group(4))

        if month_name not in INGILIZCE_AYLAR:
            return None

        month_number = INGILIZCE_AYLAR.index(month_name) + 1

        return date(year_number, month_number, day_number)

    except Exception:
        return None


def tarih_alani_var_mi(driver):
    js_code = r"""
        const dateText = /^\d{1,2}\s+[A-Za-zÇĞİÖŞÜçğıöşü]+\s+\d{2,4}$/;
        const ariaDate = /^[A-Za-z]+,\s+[A-Za-z]+\s+\d{1,2}(st|nd|rd|th),\s+\d{4}$/;

        for (const el of document.querySelectorAll(
            "button, [role='button'], span.truncate, use"
        )) {
            const text = (el.innerText || el.textContent || "")
                .trim()
                .replace(/\s+/g, " ");

            const aria = el.getAttribute("aria-label") || "";
            const href =
                el.getAttribute("href") ||
                el.getAttribute("xlink:href") ||
                "";

            if (/^(Bugün|Today)$/i.test(text)) return true;
            if (dateText.test(text)) return true;
            if (ariaDate.test(aria)) return true;
            if (href.toLowerCase().includes("calendar")) return true;
        }

        return false;
    """

    try:
        return bool(driver.execute_script(js_code))
    except Exception:
        return False


def tarih_contextine_gec(driver):
    driver.switch_to.default_content()

    return recursive_context_bul(
        driver,
        tarih_alani_var_mi
    )


def takvim_tetikleyicisini_bul(driver):
    js_code = r"""
        const dateText = /^\d{1,2}\s+[A-Za-zÇĞİÖŞÜçğıöşü]+\s+\d{2,4}$/;

        const clickables = Array.from(
            document.querySelectorAll("button, [role='button'], a")
        );

        for (const el of clickables) {
            const text = (el.innerText || el.textContent || "")
                .trim()
                .replace(/\s+/g, " ");

            if (/^(Bugün|Today)$/i.test(text)) return el;
        }

        for (const el of clickables) {
            const text = (el.innerText || el.textContent || "")
                .trim()
                .replace(/\s+/g, " ");

            if (dateText.test(text)) return el;
        }

        for (const el of clickables) {
            const value = (
                (el.getAttribute("aria-label") || "") + " " +
                (el.getAttribute("title") || "")
            ).toLowerCase();

            if (
                value.includes("calendar") ||
                value.includes("takvim")
            ) {
                return el;
            }
        }

        const spans = Array.from(document.querySelectorAll("span.truncate"));

        for (const span of spans) {
            const text = (span.innerText || span.textContent || "")
                .trim()
                .replace(/\s+/g, " ");

            if (/^(Bugün|Today)$/i.test(text) || dateText.test(text)) {
                const parent =
                    span.closest("button") ||
                    span.closest("[role='button']") ||
                    span.closest("a");

                if (parent) return parent;
            }
        }

        return null;
    """

    try:
        return driver.execute_script(js_code)
    except Exception:
        return None


def takvimde_tarih_butonlari(driver):
    js_code = r"""
        const pattern =
            /^[A-Za-z]+,\s+[A-Za-z]+\s+\d{1,2}(st|nd|rd|th),\s+\d{4}$/;

        return Array.from(document.querySelectorAll("button"))
            .map(btn => btn.getAttribute("aria-label") || "")
            .filter(label => pattern.test(label));
    """

    try:
        return driver.execute_script(js_code) or []
    except Exception:
        return []


def takvim_contexti_var_mi(driver):
    return len(takvimde_tarih_butonlari(driver)) > 0


def takvim_contextine_gec(driver):
    driver.switch_to.default_content()

    return recursive_context_bul(
        driver,
        takvim_contexti_var_mi
    )


def takvim_ac(driver):
    if not tarih_contextine_gec(driver):
        print("❌ Tarih alanı bulunamadı.")
        driver.switch_to.default_content()
        debug_kaydet(driver, "tarih_alani_bulunamadi")
        return False

    trigger = takvim_tetikleyicisini_bul(driver)

    if not trigger:
        print("❌ Takvim tetikleyicisi bulunamadı.")
        return False

    print("📅 Takvim açma alanına tıklanıyor...")

    if not guvenli_tikla(driver, trigger):
        print("❌ Takvim açma alanına tıklanamadı.")
        return False

    time.sleep(TAKVIM_ACILMA_BEKLEME)

    for _ in range(10):
        if takvim_contextine_gec(driver):
            labels = takvimde_tarih_butonlari(driver)

            if labels:
                print(f"✅ Takvim açıldı. İlk tarih: {labels[0]}")
                return True

        time.sleep(0.5)

    return False


def takvimde_hedef_butonu(driver, target_label):
    try:
        return driver.execute_script("""
            const target = arguments[0];

            for (const button of document.querySelectorAll("button")) {
                if ((button.getAttribute("aria-label") || "") === target) {
                    return button;
                }
            }

            return null;
        """, target_label)
    except Exception:
        return None


def takvimde_gorunen_tarihler(driver):
    output = []

    for label in takvimde_tarih_butonlari(driver):
        parsed = aria_tarih_parse(label)

        if parsed:
            output.append(parsed)

    return sorted(set(output))


def takvim_ok_butonu(driver, direction):
    arrow_name = "arrow-left" if direction == "left" else "arrow-right"

    js_code = r"""
        const arrow = arguments[0];

        for (const use of document.querySelectorAll("use")) {
            const href =
                use.getAttribute("href") ||
                use.getAttribute("xlink:href") ||
                "";

            if (href.includes(arrow)) {
                const btn =
                    use.closest("button") ||
                    use.closest("[role='button']");

                if (btn) return btn;
            }
        }

        return null;
    """

    try:
        return driver.execute_script(js_code, arrow_name)
    except Exception:
        return None


def tarih_sec(driver, target_date):
    target_label = hedef_aria_label_olustur(target_date)

    print(f"🔎 Hedef tarih: {target_date.strftime('%d.%m.%Y')}")
    print(f"🔎 Hedef aria-label: {target_label}")

    date_url = f"{URL}?date={target_date.strftime('%d.%m.%Y')}"

    try:
        print(f"🌐 Önce tarih URL'si deneniyor: {date_url}")
        driver.switch_to.default_content()
        driver.get(date_url)
        sayfa_yuklenmesini_bekle(driver)
        time.sleep(3)
        dismiss_cookies(driver)
    except Exception:
        pass

    if not takvim_ac(driver):
        return False

    for attempt in range(1, MAX_AY_GECIS + 1):
        target_button = takvimde_hedef_butonu(driver, target_label)

        if target_button:
            print("✅ Hedef tarih takvimde bulundu.")

            if guvenli_tikla(driver, target_button):
                time.sleep(TARIH_SECILDIKTEN_SONRA_BEKLEME)
                print(f"✅ Tarih seçildi: {target_date.strftime('%d.%m.%Y')}")
                return True

            return False

        visible = takvimde_gorunen_tarihler(driver)

        if not visible:
            print("❌ Takvimde tarih okunamadı.")
            return False

        oldest = min(visible)
        newest = max(visible)

        if target_date < oldest:
            direction = "left"
        else:
            direction = "right"

        print(
            f"   [{attempt:02d}] Takvim aralığı: "
            f"{oldest.strftime('%d.%m.%Y')} -> "
            f"{newest.strftime('%d.%m.%Y')} | {direction}"
        )

        arrow = takvim_ok_butonu(driver, direction)

        if not arrow:
            print("❌ Takvim yön oku bulunamadı.")
            return False

        if not guvenli_tikla(driver, arrow):
            return False

        time.sleep(0.7)

    return False


# ============================================================
# MAÇ CONTENT / IFRAME
# ============================================================

def mac_icerigi_var_mi(driver):
    selectors = [
        "[role='row']",
        ".rounded-match",
        ".rounded-match__score",
    ]

    for selector in selectors:
        try:
            if driver.find_elements(By.CSS_SELECTOR, selector):
                return True
        except Exception:
            pass

    return False


def mac_contextini_bul(driver):
    driver.switch_to.default_content()

    return recursive_context_bul(
        driver,
        mac_icerigi_var_mi
    )


# ============================================================
# MAÇ ÇEKME
# ============================================================

def extract_matches_with_js(driver, target_date_str):
    js_code = r"""
        const results = [];
        const processed = new Set();

        function clean(t) {
            return (t || "")
                .replace(/\n/g, " ")
                .replace(/\s+/g, " ")
                .trim();
        }

        function isBad(text) {
            if (!text || text.length < 2) return true;
            if (/^\d+$/.test(text)) return true;
            if (/^\d{1,2}:\d{2}$/.test(text)) return true;
            if (/^\d{1,2}\s+[A-Za-zÇĞİÖŞÜçğıöşü]+\s+\d{2,4}$/.test(text)) return true;
            if (/^(Bugün|Yarın|Dün|MS|İY|IY|Canlı|Bitti|Başlamadı)$/i.test(text)) return true;
            return false;
        }

        const headers = Array.from(
            document.querySelectorAll("h3[data-testid='tournament-name-link']")
        );

        const rows = Array.from(
            document.querySelectorAll(
                "[role='row'], .rounded-match, [data-testid*='match']"
            )
        );

        for (const row of rows) {
            if (processed.has(row)) continue;

            const nestedRows = row.querySelectorAll("[role='row']");

            if (
                row.getAttribute("role") !== "row" &&
                nestedRows.length > 0
            ) {
                continue;
            }

            const names = [];

            for (const node of row.querySelectorAll(".truncate")) {
                const text = clean(node.innerText || node.textContent || "");

                if (isBad(text)) continue;
                if (/Favorilere|arrow|Takvim/i.test(text)) continue;

                if (!names.includes(text)) {
                    names.push(text);
                }
            }

            if (names.length < 2) continue;

            const home = names[0];
            const away = names[1];

            if (!home || !away || home === away) continue;

            const nums = [];

            for (const box of row.querySelectorAll(
                ".rounded-match__score, div.w-6"
            )) {
                const text = clean(box.innerText || box.textContent || "");

                if (/^\d+$/.test(text)) {
                    nums.push(text);
                }
            }

            if (nums.length < 2) continue;

            let league = "Bilinmeyen Lig";

            for (let i = headers.length - 1; i >= 0; i--) {
                const header = headers[i];

                if (
                    header.compareDocumentPosition(row) &
                    Node.DOCUMENT_POSITION_FOLLOWING
                ) {
                    league = clean(header.innerText || header.textContent || "");
                    break;
                }
            }

            processed.add(row);

            results.push({
                tarih: arguments[0],
                league: league,
                home: home,
                away: away,
                score: nums[0] + "-" + nums[1],
                iy_home: nums.length >= 4 ? nums[2] : "-",
                iy_away: nums.length >= 4 ? nums[3] : "-",
                status: "MS"
            });
        }

        return results;
    """

    try:
        return driver.execute_script(js_code, target_date_str) or []
    except Exception as exc:
        print(f"❌ Maç JS hatası: {exc}")
        return []


def unique_matches(matches):
    output = {}

    for match in matches:
        tarih = str(match.get("tarih", ""))
        home = temiz_isim(match.get("home", ""))
        away = temiz_isim(match.get("away", ""))

        if not home or not away:
            continue

        key = f"{tarih}|{home}|{away}"

        if key not in output:
            output[key] = match
            continue

        old_score = str(output[key].get("score", ""))
        new_score = str(match.get("score", ""))

        if old_score in ("", "-") and new_score not in ("", "-"):
            output[key] = match

    return list(output.values())


# ============================================================
# BÜLTEN İÇ SCROLL
# ============================================================

def scroll_container_bilgileri(driver):
    """
    Overflow CSS kontrolüne takılmadan scrollHeight > clientHeight
    olan ve maç alanı içeren tüm kapsayıcıları bulur.
    """

    js_code = r"""
        const all = Array.from(
            document.querySelectorAll("div, main, section, article, ul, body")
        );

        const result = [];

        for (const el of all) {
            try {
                const rect = el.getBoundingClientRect();

                if (rect.width < 200 || rect.height < 100) continue;
                if (el.scrollHeight <= el.clientHeight + 25) continue;

                const rows = el.querySelectorAll("[role='row']").length;
                const scores = el.querySelectorAll(".rounded-match__score").length;
                const matches = el.querySelectorAll(".rounded-match").length;
                const truncates = el.querySelectorAll(".truncate").length;

                if (rows < 1 && scores < 2 && matches < 1 && truncates < 5) {
                    continue;
                }

                const value =
                    rows * 1000000 +
                    scores * 100000 +
                    matches * 100000 +
                    truncates * 1000 +
                    el.scrollHeight;

                result.push({
                    tag: el.tagName,
                    id: el.id || "",
                    className: typeof el.className === "string" ? el.className : "",
                    top: el.scrollTop,
                    height: el.scrollHeight,
                    clientHeight: el.clientHeight,
                    rows: rows,
                    scores: scores,
                    value: value
                });
            } catch (e) {}
        }

        result.sort((a, b) => b.value - a.value);

        return result.slice(0, 12);
    """

    try:
        return driver.execute_script(js_code) or []
    except Exception:
        return []


def scroll_container_element(driver, index):
    js_code = r"""
        const all = Array.from(
            document.querySelectorAll("div, main, section, article, ul, body")
        );

        const result = [];

        for (const el of all) {
            try {
                const rect = el.getBoundingClientRect();

                if (rect.width < 200 || rect.height < 100) continue;
                if (el.scrollHeight <= el.clientHeight + 25) continue;

                const rows = el.querySelectorAll("[role='row']").length;
                const scores = el.querySelectorAll(".rounded-match__score").length;
                const matches = el.querySelectorAll(".rounded-match").length;
                const truncates = el.querySelectorAll(".truncate").length;

                if (rows < 1 && scores < 2 && matches < 1 && truncates < 5) {
                    continue;
                }

                const value =
                    rows * 1000000 +
                    scores * 100000 +
                    matches * 100000 +
                    truncates * 1000 +
                    el.scrollHeight;

                result.push({ el, value });
            } catch (e) {}
        }

        result.sort((a, b) => b.value - a.value);

        return result[arguments[0]] ? result[arguments[0]].el : null;
    """

    try:
        return driver.execute_script(js_code, index)
    except Exception:
        return None


def tum_scroll_alanlarini_ilerlet(driver):
    """
    Özel scroll container bulunamazsa tüm kaydırılabilir elementleri
    aynı anda bir miktar aşağı iter.
    """

    js_code = r"""
        const all = Array.from(document.querySelectorAll("*"));

        let moved = 0;
        let total = 0;

        for (const el of all) {
            try {
                if (el.scrollHeight <= el.clientHeight + 20) continue;

                const oldTop = el.scrollTop;
                const amount = Math.max(el.clientHeight * 0.8, 350);

                el.scrollTop = Math.min(
                    el.scrollTop + amount,
                    el.scrollHeight
                );

                if (el.scrollTop > oldTop) {
                    moved++;
                }

                total++;
            } catch (e) {}
        }

        window.scrollBy(0, Math.max(window.innerHeight * 0.8, 500));

        return { moved, total };
    """

    try:
        return driver.execute_script(js_code)
    except Exception:
        return {"moved": 0, "total": 0}


def scroll_bulten_ve_maclari_topla(driver, target_date_str):
    print("🔧 Bültenin iç scroll alanı aranıyor...")

    collected = []
    containers = scroll_container_bilgileri(driver)

    if containers:
        print(f"✅ {len(containers)} olası scroll alanı bulundu.")

        for i, item in enumerate(containers[:5], start=1):
            print(
                f"   [{i}] {item['tag']} | "
                f"scroll={item['top']}/{item['height']} | "
                f"ekran={item['clientHeight']} | "
                f"row={item['rows']} | skor={item['scores']}"
            )

        max_try = min(4, len(containers))

        for index in range(max_try):
            print(f"\n🔽 Scroll container {index + 1}/{max_try} taranıyor...")

            container = scroll_container_element(driver, index)

            if not container:
                continue

            driver.execute_script("""
                arguments[0].scrollTop = 0;
                arguments[0].dispatchEvent(
                    new Event("scroll", { bubbles: true })
                );
            """, container)

            time.sleep(1)

            previous_top = -1
            stuck_count = 0

            for step in range(MAX_SCROLL_ADIMI):
                current = extract_matches_with_js(
                    driver,
                    target_date_str
                )

                collected.extend(current)

                info = driver.execute_script("""
                    const el = arguments[0];

                    return {
                        top: el.scrollTop,
                        height: el.scrollHeight,
                        client: el.clientHeight
                    };
                """, container)

                if not info:
                    break

                if step % 5 == 0:
                    print(
                        f"   adım={step:03d} | "
                        f"scroll={int(info['top'])}/{int(info['height'])} | "
                        f"anlık={len(current)} | ham={len(collected)}"
                    )

                if info["top"] + info["client"] >= info["height"] - 10:
                    print("✅ Container sonuna ulaşıldı.")
                    collected.extend(
                        extract_matches_with_js(
                            driver,
                            target_date_str
                        )
                    )
                    break

                if abs(info["top"] - previous_top) < 2:
                    stuck_count += 1
                else:
                    stuck_count = 0

                if stuck_count >= 4:
                    print("⚠️ Scroll ilerlemedi.")
                    break

                previous_top = info["top"]

                driver.execute_script("""
                    const el = arguments[0];
                    const amount = Math.max(el.clientHeight * 0.75, 400);

                    el.scrollTop = Math.min(
                        el.scrollTop + amount,
                        el.scrollHeight
                    );

                    el.dispatchEvent(
                        new Event("scroll", { bubbles: true })
                    );
                """, container)

                time.sleep(SCROLL_BEKLEME)

    else:
        print("⚠️ Özel iç scroll alanı bulunamadı.")
        print("🔄 Tüm kaydırılabilir alanlar zorla aşağı indiriliyor...")

        previous_count = -1
        no_change_count = 0

        for step in range(MAX_SCROLL_ADIMI):
            current = extract_matches_with_js(
                driver,
                target_date_str
            )

            collected.extend(current)

            result = tum_scroll_alanlarini_ilerlet(driver)

            unique_count = len(unique_matches(collected))

            if step % 5 == 0:
                print(
                    f"   adım={step:03d} | "
                    f"anlık={len(current)} | "
                    f"tekil={unique_count} | "
                    f"hareket={result['moved']}"
                )

            if unique_count == previous_count and result["moved"] == 0:
                no_change_count += 1
            else:
                no_change_count = 0

            if no_change_count >= 5:
                break

            previous_count = unique_count
            time.sleep(SCROLL_BEKLEME)

    result = unique_matches(collected)

    print(
        f"✅ Bülten taraması tamamlandı | "
        f"Ham={len(collected)} | Tekil={len(result)}"
    )

    return result


# ============================================================
# MAC.JSON GÜNCELLEME
# ============================================================

def update_mac_json_safely(scraped_matches):
    print(f"\n🔄 mac.json güncelleniyor: {MAC_JSON_PATH}")

    if not MAC_JSON_PATH.exists():
        print("❌ mac.json bulunamadı.")
        return 0

    backup_path = OUT_DIR / (
        f"mac_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    shutil.copy2(MAC_JSON_PATH, backup_path)
    print(f"💾 Yedek alındı: {backup_path}")

    with open(MAC_JSON_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    valid_matches = []

    for match in scraped_matches:
        score = str(match.get("score", "")).strip()

        if not re.fullmatch(r"\d+\s*-\s*\d+", score):
            continue

        if not temiz_isim(match.get("home", "")):
            continue

        if not temiz_isim(match.get("away", "")):
            continue

        valid_matches.append(match)

    updated_count = 0

    def update_obj(obj):
        nonlocal updated_count

        if not isinstance(obj, dict):
            return

        home = temiz_isim(
            obj.get("home") or
            obj.get("ev_sahibi") or
            obj.get("ev") or
            obj.get("homeTeam") or ""
        )

        away = temiz_isim(
            obj.get("away") or
            obj.get("deplasman") or
            obj.get("dep") or
            obj.get("awayTeam") or ""
        )

        if not home or not away:
            return

        json_date = obj.get("tarih") or obj.get("date") or ""

        best = None
        best_total = 0
        best_home = 0
        best_away = 0

        for scraped in valid_matches:
            scraped_home = temiz_isim(scraped.get("home", ""))
            scraped_away = temiz_isim(scraped.get("away", ""))
            scraped_date = scraped.get("tarih", "")

            if json_date and scraped_date:
                if tarih_farki(json_date, scraped_date) > ESLESME_TOLERANSI_GUN:
                    continue

            h_ratio = benzerlik(home, scraped_home)
            a_ratio = benzerlik(away, scraped_away)

            if h_ratio < BENZERLIK_ESIK:
                continue

            if a_ratio < BENZERLIK_ESIK:
                continue

            if h_ratio + a_ratio > best_total:
                best = scraped
                best_total = h_ratio + a_ratio
                best_home = h_ratio
                best_away = a_ratio

        if not best:
            return

        try:
            new_home, new_away = map(
                int,
                str(best["score"]).split("-")
            )
        except Exception:
            return

        iy_home = (
            int(best["iy_home"])
            if str(best.get("iy_home", "")).isdigit()
            else 0
        )

        iy_away = (
            int(best["iy_away"])
            if str(best.get("iy_away", "")).isdigit()
            else 0
        )

        old_home = obj.get("skor_ev")
        old_away = obj.get("skor_dep")
        old_status = obj.get("durum")

        obj["skor_ev"] = new_home
        obj["skor_dep"] = new_away
        obj["skor_1y_ev"] = iy_home
        obj["skor_1y_dep"] = iy_away
        obj["durum"] = "bitti"
        obj["kaynak"] = "iddaa.com"
        obj["cekme_zamani"] = datetime.now().isoformat()

        if (
            old_home != new_home or
            old_away != new_away or
            old_status != "bitti"
        ):
            updated_count += 1

            print(
                f"✅ EŞLEŞTİ: "
                f"{obj.get('ev_sahibi', obj.get('home', '?'))} vs "
                f"{obj.get('deplasman', obj.get('away', '?'))} | "
                f"MS: {new_home}-{new_away} | "
                f"Benzerlik: {best_home:.2f}/{best_away:.2f}"
            )

    def traverse(item):
        if isinstance(item, dict):
            update_obj(item)

            for value in item.values():
                traverse(value)

        elif isinstance(item, list):
            for value in item:
                traverse(value)

    traverse(data)

    with open(MAC_JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"✅ Güncellenen maç sayısı: {updated_count}")

    return updated_count


# ============================================================
# GIT
# ============================================================

def auto_git_commit_and_push(updated_count):
    if updated_count <= 0:
        print("\nℹ️ Güncelleme olmadığı için Git atlandı.")
        return

    try:
        repo_dir = MAC_JSON_PATH.parent.parent.parent
        relative_file = MAC_JSON_PATH.relative_to(repo_dir)

        subprocess.run(
            ["git", "add", str(relative_file)],
            cwd=repo_dir,
            check=True,
            capture_output=True,
            text=True
        )

        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo_dir
        )

        if diff.returncode == 0:
            print("ℹ️ Commit edilecek fark yok.")
            return

        message = (
            f"Otomatik skor güncellemesi: {updated_count} maç "
            f"({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        )

        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_dir,
            check=True,
            capture_output=True,
            text=True
        )

        push = subprocess.run(
            ["git", "push"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )

        if push.returncode == 0:
            print("✅ Git push başarılı.")
        else:
            print("⚠️ Git push başarısız:")
            print(push.stderr)

    except Exception as exc:
        print(f"❌ Git hatası: {exc}")


# ============================================================
# MAIN
# ============================================================

def main():
    driver = None

    try:
        print("=" * 90)
        print("🌐 İDDAA CANLI SKOR FUTBOL SCRAPER BAŞLIYOR")
        print("=" * 90)

        dates_to_fetch = tarih_araligi_olustur(
            BASLANGIC_TARIHI,
            BITIS_TARIHI
        )

        print(
            f"📅 Tarih aralığı: "
            f"{BASLANGIC_TARIHI} -> {BITIS_TARIHI}"
        )
        print(f"📌 İşlenecek toplam gün: {len(dates_to_fetch)}")
        print(f"📁 mac.json: {MAC_JSON_PATH}")

        print("\n🌐 Chrome başlatılıyor...")
        driver = build_driver()

        # HATA BURADA ÇÖZÜLDÜ:
        # Döngü başlamadan önce mutlaka tanımlıdır.
        all_scraped_matches = []

        for target_date in dates_to_fetch:
            iso_date = target_date.strftime("%Y-%m-%d")

            print("\n" + "=" * 90)
            print(f"📅 TARİH İŞLENİYOR: {iso_date}")
            print("=" * 90)

            success = tarih_sec(driver, target_date)

            if not success:
                print(f"⚠️ Tarih seçilemedi: {iso_date}")
                continue

            if not mac_contextini_bul(driver):
                print(f"⚠️ Maç alanı bulunamadı: {iso_date}")
                continue

            time.sleep(1.5)

            matches = scroll_bulten_ve_maclari_topla(
                driver,
                iso_date
            )

            all_scraped_matches.extend(matches)

            print(
                f"\n✅ {iso_date} için çekilen tekil maç: "
                f"{len(matches)}"
            )

            for index, match in enumerate(matches, 1):
                print(
                    f" [{index:03d}] "
                    f"{match.get('home', '?')} vs "
                    f"{match.get('away', '?')} | "
                    f"MS: {match.get('score', '-')} | "
                    f"İY: {match.get('iy_home', '-')}-"
                    f"{match.get('iy_away', '-')}"
                )

        all_scraped_matches = unique_matches(all_scraped_matches)

        print("\n" + "=" * 90)
        print("🎉 TARİH TARAMASI TAMAMLANDI")
        print("=" * 90)
        print(f"📊 Toplam tekil maç: {len(all_scraped_matches)}")

        if not all_scraped_matches:
            print("⚠️ Hiç maç verisi çekilemedi.")
            return

        raw_file = OUT_DIR / (
            f"matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        raw_file.write_text(
            json.dumps(
                all_scraped_matches,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print(f"💾 Ham veri kaydedildi: {raw_file}")

        updated_count = update_mac_json_safely(all_scraped_matches)
        auto_git_commit_and_push(updated_count)

    except KeyboardInterrupt:
        print("\n⚠️ İşlem kullanıcı tarafından durduruldu.")

    except Exception:
        print("\n❌ KRİTİK HATA:")
        traceback.print_exc()

    finally:
        if driver:
            try:
                driver.quit()
                print("\n🧹 Tarayıcı kapatıldı.")
            except Exception:
                pass

        print("\n" + "=" * 90)

        try:
            input("Çıkmak için Enter tuşuna basın...")
        except EOFError:
            pass


if __name__ == "__main__":
    main()