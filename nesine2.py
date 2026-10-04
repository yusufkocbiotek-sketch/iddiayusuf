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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ============================================================
# AYARLAR
# ============================================================

URL_BASE = "https://www.nesine.com/iddaa"

REPO_ROOT = Path(__file__).resolve().parent
CIKTI_DOSYA = str(REPO_ROOT / "public" / "data" / "mac.json")

MAX_SCROLL_STEPS = 300
STABLE_LIMIT = 18
SCROLL_PX = 600
SCROLL_SLEEP_RANGE = (1.1, 2.0)

MAX_SCRAPE = 9999
SLEEP_BETWEEN_MATCHES = (1.1, 2.4)

# Her kaç maçta Chrome kapat/aç yapılacağı
HARVEST_MAC_SAYISI = 50

SEARCH_SEL = 'input[data-test-id="srch-box"]'
PANEL_BTN_SEL = 'div[data-test-id="date-league-btn-title"]'
EXPAND_SEL = "span.f17af500409a2f819a68"

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")
ODD_RE = re.compile(r"^\d{1,3}([.,]\d{1,2})$")
SKOR_RE = re.compile(r"^\d{1,2}[:\-]\d{1,2}\+?$")


# ============================================================
# YASAK MARKETLER
# ============================================================

SILINECEK_BASLANGICLAR = (
    "oyuncu",
    "takim",
    "takimlar",
    "karsilasma ozel bahisleri",
    "kaleci",
    "kurtaris",
    "kurtarisi",
    "korner",
    "corner",
    "toplam korner",
    "ilk yari korner",
    "1 yari korner",
    "1. yari korner",
    "ilk yari toplam korner",
    "1 yari toplam korner",
    "1. yari toplam korner",
    "ev sahibi toplam korner",
    "deplasman toplam korner",
    "ev sahibi korner",
    "deplasman korner",
    "kart",
    "sari kart",
    "kirmizi kart",
    "toplam kart",
)

MENU_KELIMELER = {
    "bulten", "canli", "canli sonuclar",
    "sonuclar", "kuponum", "kuponlarim",
    "spor toto", "yardim", "giris",
    "uye ol", "nesine", "futbol",
    "basketbol", "tenis", "voleybol",
    "hentbol", "buz hokeyi",
    "amerikan futbolu", "e-futbol",
    "mma", "tumu", "yukle",
    "bugun", "yarin",
}


# ============================================================
# TARİH
# ============================================================

def bugunun_tarihi():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def yarinin_tarihi():
    return (
        datetime.datetime.now() + datetime.timedelta(days=1)
    ).strftime("%Y-%m-%d")


def nesine_dt_url(tarih_iso):
    try:
        tarih = datetime.datetime.strptime(
            tarih_iso,
            "%Y-%m-%d"
        )

        return (
            f"{URL_BASE}?et=1&le=2&"
            f"dt={tarih.strftime('%d.%m.%Y')}"
        )

    except Exception:
        return f"{URL_BASE}?et=1&le=2"


def url_tarih_uyuyor_mu(url, tarih_iso):
    try:
        tarih = datetime.datetime.strptime(
            tarih_iso,
            "%Y-%m-%d"
        )

        hedef = tarih.strftime("%d.%m.%Y")

        found = re.search(r"dt=([^&]+)", url or "")

        if not found:
            return False

        gunler = found.group(1).split("%7C")

        return gunler == [hedef]

    except Exception:
        return False


# ============================================================
# GİT
# ============================================================

ENABLE_GIT_AUTOPUSH = True


def find_git_exe():
    git = shutil.which("git")

    if git:
        return git

    candidates = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
    ]

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    return None


def run_cmd(command, cwd=None):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="ignore",
        )

        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "code": result.returncode,
        }

    except Exception as exc:
        return {
            "ok": False,
            "stdout": "",
            "stderr": str(exc),
            "code": -1,
        }


def git_force_push():
    if not ENABLE_GIT_AUTOPUSH:
        return

    if not (REPO_ROOT / ".git").exists():
        print("❌ Git klasörü bulunamadı.")
        return

    git = find_git_exe()

    if not git:
        print("❌ Git bulunamadı.")
        return

    print("\n🔄 GİT İŞLEMLERİ BAŞLADI...")

    run_cmd([git, "checkout", "-B", "main"], cwd=str(REPO_ROOT))
    run_cmd([git, "add", "-A"], cwd=str(REPO_ROOT))

    zaman = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    mesaj = f"Otomatik guncelleme | {zaman}"

    run_cmd(
        [git, "commit", "-m", mesaj, "--allow-empty"],
        cwd=str(REPO_ROOT)
    )

    print(f"   ✅ Commit: {mesaj}")

    push = run_cmd(
        [git, "push", "-f", "origin", "main"],
        cwd=str(REPO_ROOT)
    )

    if push["ok"]:
        print("✅ Git push başarılı.")
    else:
        print("❌ Git push başarısız:")
        print(push["stderr"])


# ============================================================
# DRIVER
# ============================================================

def build_driver():
    options = Options()

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    options.add_experimental_option(
        "useAutomationExtension",
        False
    )

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    driver.set_page_load_timeout(60)
    driver.set_script_timeout(30)

    try:
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
    except Exception:
        pass

    return driver


def cookie_kabul_et(driver):
    try:
        driver.execute_script("""
            const texts = [
                "Kabul Et",
                "Tümünü Kabul Et",
                "Çerezleri Kabul Et",
                "Tamam",
                "Accept",
                "Accept All",
                "Anladım"
            ];

            for (const el of document.querySelectorAll(
                "button, div, span, a"
            )) {
                const text = (
                    el.innerText ||
                    el.textContent ||
                    ""
                ).trim();

                if (texts.includes(text)) {
                    try {
                        el.click();
                        return true;
                    } catch (e) {}
                }
            }

            return false;
        """)

        time.sleep(1)

    except Exception:
        pass


def reklam_kapat(driver):
    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.4)
    except Exception:
        pass

    try:
        driver.execute_script("""
            const selectors = [
                "button[class*='close' i]",
                "[class*='close' i][role='button']",
                "[class*='kapat' i]",
                "[aria-label*='close' i]",
                "[aria-label*='kapat' i]",
                "[title*='close' i]",
                "[title*='kapat' i]",
                ".quiz-banner-close",
                "[class*='banner-close' i]",
                "[class*='popup-close' i]"
            ];

            for (const selector of selectors) {
                for (const el of document.querySelectorAll(selector)) {
                    try {
                        const rect = el.getBoundingClientRect();

                        if (rect.width > 0 && rect.height > 0) {
                            el.click();
                        }
                    } catch (e) {}
                }
            }
        """)

        time.sleep(0.5)

    except Exception:
        pass


# ============================================================
# MAÇ SATIRI BULMA
# ============================================================

def find_match_cards(driver):
    try:
        rows = driver.execute_script("""
            function visible(el) {
                if (!el) return false;

                const rect = el.getBoundingClientRect();
                const style = getComputedStyle(el);

                return (
                    rect.width > 100 &&
                    rect.height > 10 &&
                    rect.height < 400 &&
                    style.display !== "none" &&
                    style.visibility !== "hidden"
                );
            }

            const timeNodes = Array.from(
                document.querySelectorAll(
                    "span[data-testid^='time-']"
                )
            );

            const candidates = [];

            for (const timeNode of timeNodes) {
                let node = timeNode;

                for (let i = 0; i < 10 && node; i++) {
                    const text = (node.innerText || "").trim();

                    if (
                        visible(node) &&
                        text.length > 30 &&
                        text.length < 2000 &&
                        text.includes("-")
                    ) {
                        candidates.push(node);
                        break;
                    }

                    node = node.parentElement;
                }
            }

            const unique = [...new Set(candidates)];

            return unique
                .filter(el =>
                    !unique.some(
                        other => other !== el && el.contains(other)
                    )
                )
                .slice(0, 1000);
        """)

        return rows or []

    except Exception:
        return []


def satir_sayisi_bekle(driver, max_sure=20):
    start = time.time()

    while time.time() - start < max_sure:
        count = len(find_match_cards(driver))

        if count > 0:
            return count

        time.sleep(1)

    return 0


def sayfa_saglikli_mi(driver):
    try:
        text = driver.find_element(By.TAG_NAME, "body").text.strip()
        lower = text.lower()

        errors = (
            "hay aksi",
            "aw snap",
            "page unresponsive",
            "out of memory",
            "status_access_violation",
        )

        if len(text) < 50:
            return False

        return not any(error in lower for error in errors)

    except Exception:
        return False


def guvenli_yukle(driver, url, max_deneme=3):
    for deneme in range(1, max_deneme + 1):
        try:
            print(f"      🌐 Sayfa yükleniyor... {deneme}/{max_deneme}")

            driver.get(url)
            time.sleep(5)

            cookie_kabul_et(driver)
            reklam_kapat(driver)

            satir = satir_sayisi_bekle(driver, 15)

            print(f"      🔎 Bulunan satır: {satir}")

            if satir > 0:
                return driver, True

        except Exception as exc:
            print(f"      ⚠️ Yükleme hatası: {str(exc)[:100]}")

        time.sleep(2)

    return driver, False


def chrome_hizli_yeniden_baslat(driver, url_gun):
    """
    50 maçta bir basit kapat/aç.
    JSON kaydı yapmaz.
    """

    try:
        driver.quit()
    except Exception:
        pass

    print("   🔴 Chrome kapatıldı.")
    time.sleep(2)

    print("   🟢 Chrome açılıyor...")

    new_driver = build_driver()

    try:
        new_driver.get(url_gun)
    except Exception as exc:
        print(f"   ⚠️ URL açma hatası: {str(exc)[:100]}")

    time.sleep(4)

    cookie_kabul_et(new_driver)
    reklam_kapat(new_driver)

    satir = satir_sayisi_bekle(new_driver, 12)

    print(f"   ✅ Yeni Chrome hazır | Satır: {satir}")

    return new_driver


def gun_sayfasini_yukle(driver, url_gun, max_deneme=2):
    for deneme in range(1, max_deneme + 1):
        try:
            driver.get(url_gun)
            time.sleep(4)

            cookie_kabul_et(driver)
            reklam_kapat(driver)

            satir = satir_sayisi_bekle(driver, 15)

            print(f"   🔎 Gün satır sayısı: {satir}")

            if satir > 0:
                return driver, True

        except Exception:
            pass

        try:
            driver.refresh()
            time.sleep(4)
        except Exception:
            pass

    return driver, False


# ============================================================
# SCROLL
# ============================================================

def init_scroll_target(driver):
    try:
        driver.execute_script("""
            const elements = Array.from(
                document.querySelectorAll("*")
            );

            const candidates = elements.filter(el => {
                const style = getComputedStyle(el);

                return (
                    (style.overflowY === "auto" ||
                     style.overflowY === "scroll") &&
                    el.scrollHeight - el.clientHeight > 600 &&
                    el.clientHeight > 300
                );
            });

            candidates.sort(
                (a, b) =>
                    (b.scrollHeight - b.clientHeight) -
                    (a.scrollHeight - a.clientHeight)
            );

            window.__scrollEl = candidates[0] || null;
        """)
    except Exception:
        pass


def reset_scroll_top(driver):
    try:
        driver.execute_script("""
            if (window.__scrollEl) {
                window.__scrollEl.scrollTop = 0;
            }

            window.scrollTo(0, 0);
        """)
    except Exception:
        pass


def scroll_step(driver, px=SCROLL_PX):
    try:
        driver.execute_script("""
            const px = arguments[0];

            if (window.__scrollEl) {
                window.__scrollEl.scrollTop += px;
                window.__scrollEl.dispatchEvent(
                    new Event("scroll", { bubbles: true })
                );
            } else {
                window.scrollBy(0, px);
            }
        """, px)
    except Exception:
        pass


# ============================================================
# MAÇLARI LİSTEDEN ÇEK
# ============================================================

def extract_visible(driver, current_date):
    output = []
    seen = set()

    try:
        data = driver.execute_script("""
            function visible(el) {
                if (!el) return false;

                const rect = el.getBoundingClientRect();
                const style = getComputedStyle(el);

                return (
                    rect.width > 100 &&
                    rect.height > 10 &&
                    rect.height < 400 &&
                    style.display !== "none" &&
                    style.visibility !== "hidden"
                );
            }

            const times = Array.from(
                document.querySelectorAll(
                    "span[data-testid^='time-']"
                )
            );

            const rows = [];

            for (const time of times) {
                let node = time;

                for (let i = 0; i < 10 && node; i++) {
                    const text = (node.innerText || "").trim();

                    if (
                        visible(node) &&
                        text.length > 30 &&
                        text.length < 2000 &&
                        text.includes("-")
                    ) {
                        rows.push(node);
                        break;
                    }

                    node = node.parentElement;
                }
            }

            const uniqueRows = [...new Set(rows)]
                .filter(row =>
                    !rows.some(
                        other => other !== row && row.contains(other)
                    )
                );

            function clean(text) {
                return (text || "")
                    .trim()
                    .replace(/\\s+/g, " ");
            }

            function getTime(row) {
                const time = row.querySelector(
                    "span[data-testid^='time-']"
                );

                if (!time) return "";

                const id = time.getAttribute("data-testid") || "";

                return id.startsWith("time-")
                    ? id.replace("time-", "").trim()
                    : clean(time.innerText);
            }

            function getTeams(row) {
                const lines = (row.innerText || "")
                    .split("\\n")
                    .map(clean)
                    .filter(Boolean);

                for (const line of lines) {
                    if (!line.includes(" - ")) continue;

                    const parts = line.split(" - ");

                    if (parts.length >= 2) {
                        const home = parts[0].trim();
                        const away = parts.slice(1).join(" - ").trim();

                        if (
                            home.length > 1 &&
                            away.length > 1 &&
                            home.length < 80 &&
                            away.length < 80
                        ) {
                            return [home, away];
                        }
                    }
                }

                return ["", ""];
            }

            return uniqueRows.map(row => {
                const teams = getTeams(row);

                return {
                    ev: teams[0],
                    dep: teams[1],
                    saat: getTime(row),
                    lig: ""
                };
            });
        """)

    except Exception:
        data = []

    for item in data or []:
        ev = str(item.get("ev") or "").strip()
        dep = str(item.get("dep") or "").strip()
        saat = str(item.get("saat") or "").strip()

        if not ev or not dep or ev == dep:
            continue

        if not TIME_RE.match(saat):
            continue

        if len(ev) > 80 or len(dep) > 80:
            continue

        match = {
            "tarih": current_date,
            "saat": saat,
            "lig": "",
            "ev_sahibi": ev,
            "deplasman": dep,
            "durum": "baslamadi",
            "skor_ev": 0,
            "skor_dep": 0,
            "skor_1y_ev": 0,
            "skor_1y_dep": 0,
            "oranlar": {},
            "kaynak": "nesine.com",
        }

        key = (
            match["tarih"],
            match["ev_sahibi"],
            match["deplasman"],
        )

        if key not in seen:
            seen.add(key)
            output.append(match)

    return output


def sayfayi_scroll_et(driver, hedef_tarih):
    init_scroll_target(driver)
    reset_scroll_top(driver)

    time.sleep(2)

    matches = []
    seen = set()

    stable = 0
    previous_total = 0

    for step in range(1, MAX_SCROLL_STEPS + 1):
        visible = extract_visible(driver, hedef_tarih)

        for match in visible:
            key = (
                match["tarih"],
                match["ev_sahibi"],
                match["deplasman"],
            )

            if key not in seen:
                seen.add(key)
                matches.append(match)

        if len(matches) > previous_total:
            print(
                f"      📈 Step {step}: "
                f"+{len(matches) - previous_total} maç | "
                f"Toplam {len(matches)}"
            )

            previous_total = len(matches)
            stable = 0
        else:
            stable += 1

        if stable >= STABLE_LIMIT:
            break

        scroll_step(driver)
        time.sleep(random.uniform(*SCROLL_SLEEP_RANGE))

    return matches


def deep_harvest(driver):
    today = bugunun_tarihi()
    tomorrow = yarinin_tarihi()

    output = []
    seen = set()

    for tarih, gun_adi in [
        (today, "Bugün"),
        (tomorrow, "Yarın"),
    ]:
        print(f"\n   📅 {gun_adi}: {tarih}")

        url = nesine_dt_url(tarih)
        driver.get(url)

        time.sleep(5)
        cookie_kabul_et(driver)
        reklam_kapat(driver)

        if satir_sayisi_bekle(driver, 15) == 0:
            print("      ⚠️ Maç satırı bulunamadı.")
            continue

        matches = sayfayi_scroll_et(driver, tarih)

        for match in matches:
            key = (
                match["tarih"],
                match["ev_sahibi"],
                match["deplasman"],
            )

            if key not in seen:
                seen.add(key)
                output.append(match)

        print(f"      ✅ Günlük maç: {len(matches)}")

    return output


# ============================================================
# ORAN ANAHTAR / MARKET KONTROLLERİ
# ============================================================

def tr_key(value):
    text = str(value or "")

    text = (
        text.replace("İ", "i")
        .replace("I", "i")
        .replace("ı", "i")
        .replace("Ş", "s")
        .replace("ş", "s")
        .replace("Ğ", "g")
        .replace("ğ", "g")
        .replace("Ü", "u")
        .replace("ü", "u")
        .replace("Ö", "o")
        .replace("ö", "o")
        .replace("Ç", "c")
        .replace("ç", "c")
    )

    text = text.lower()

    return re.sub(r"\s+", " ", text).strip()


def market_yasak_mi(market):
    normalized = tr_key(market)

    if not normalized:
        return False

    for yasak in SILINECEK_BASLANGICLAR:
        if normalized.startswith(tr_key(yasak)):
            return True

    forbidden_words = [
        "korner",
        "corner",
        "kaleci",
        "kurtaris",
        "kurtarisi",
        "kart",
        "sari kart",
        "kirmizi kart",
        "oyuncu",
        "golcu",
        "gol atar",
        "asist",
        "sut",
        "isabetli sut",
        "ofsayt",
        "tac",
    ]

    return any(word in normalized for word in forbidden_words)


def ham_anahtar_yasak_mi(key):
    key = str(key or "").strip()

    if not key:
        return True

    market = key.split("_", 1)[0].strip()

    return market_yasak_mi(market)


def oran_anahtari_gecerli_mi(key):
    """
    Anahtar zorunlu olarak:
      Market_Seçenek
    yapısında olmalıdır.
    """

    raw = str(key or "").strip()

    if "_" not in raw:
        return False

    market, label = raw.split("_", 1)

    market = market.strip()
    label = label.strip()

    if not market or not label:
        return False

    market_normal = tr_key(market)
    label_normal = tr_key(label)

    # Market yalnızca sayı / oran / skor olamaz.
    if re.match(r"^[0-9]", market_normal):
        return False

    if re.fullmatch(r"\d{1,3}([.,]\d{1,2})?", market_normal):
        return False

    # Label doğrudan oran sayısı olamaz.
    if re.fullmatch(r"\d{1,3}[.,]\d{1,2}", label_normal):
        return False

    if " - " in market:
        return False

    if market_yasak_mi(market):
        return False

    return True


def istenmeyen_anahtar_mi(key):
    normalized = tr_key(key)

    if not normalized:
        return True

    if not oran_anahtari_gecerli_mi(key):
        return True

    market = normalized.split("_", 1)[0]

    if market_yasak_mi(market):
        return True

    # Başlıksız korner marketleri kaçarsa son kez engelle.
    if re.fullmatch(
        r"alt/ust\s+(7\.5|8\.5|9\.5|10\.5|11\.5|12\.5|13\.5|14\.5)_(alt|ust)",
        normalized
    ):
        return True

    return False


# ============================================================
# ORAN STANDARDİZASYONU
# ============================================================

def label_temizle(label):
    label = tr_key(label)

    label = re.sub(
        r"^(ms|hms|cs|iy|2y|1y|au|kg|2\.y|1\.y)\s+",
        "",
        label
    )

    return label.strip()


def market_duzelt(market):
    market = tr_key(market)
    market = re.sub(r"(\d),(\d)", r"\1.\2", market)

    def number():
        found = re.search(r"(\d+(?:\.\d+)?)", market)
        return found.group(1) if found else ""

    first_half = (
        "ilk yari" in market or
        "1. yari" in market
    )

    second_half = (
        "ikinci yari" in market or
        "2. yari" in market
    )

    has_goal_both = (
        "karsilikli gol" in market or
        market == "kg"
    )

    has_over_under = bool(
        re.search(r"\balt(i)?\b|\bust(u)?\b", market)
    )

    has_result = (
        "mac sonucu" in market or
        market in ("ms", "1x2")
    )

    if has_goal_both and has_over_under:
        return f"Altı/Üstü {number()} ve Karşılıklı Gol"

    if has_goal_both and has_result:
        return "Maç Sonucu ve Karşılıklı Gol"

    if has_goal_both and first_half and "sonuc" in market:
        return "İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol"

    if first_half and "sonuc" in market and has_over_under:
        return f"İlk Yarı Sonucu ve Altı/Üstü {number()}"

    if has_result and has_over_under:
        return f"Maç Sonucu ve Alt/Üst {number()}"

    handicap = re.search(
        r"handikap\w*\s*(?:mac sonucu\s*)?(\d+:\d+)",
        market
    )

    if handicap:
        return f"Handikaplı Maç Sonucu {handicap.group(1)}"

    if "handikap" in market:
        return "Handikaplı Maç Sonucu"

    if first_half and has_result:
        return "İlk Yarı / Maç Sonucu"

    if has_result:
        return "Maç Sonucu"

    if "cifte sans" in market:
        if first_half:
            return "İlk Yarı Çifte Şans"
        return "Çifte Şans"

    if "toplam gol" in market:
        return "Toplam Gol"

    if "mac skoru" in market:
        return "Maç Skoru"

    if has_goal_both:
        if first_half:
            return "İlk Yarı Karşılıklı Gol"
        if second_half:
            return "İkinci Yarı Karşılıklı Gol"
        return "Karşılıklı Gol"

    if first_half and "sonuc" in market:
        return "İlk Yarı Sonucu"

    if second_half and "sonuc" in market:
        return "İkinci Yarı Sonucu"

    if re.search(r"tek\s*/?\s*cift", market):
        if first_half:
            return "İlk Yarı Tek / Çift"
        if second_half:
            return "İkinci Yarı Tek / Çift"
        return "Tek / Çift"

    if has_over_under:
        prefix = ""

        if "ev sahibi" in market:
            prefix = "Ev Sahibi "
        elif "deplasman" in market:
            prefix = "Deplasman "

        if first_half:
            return f"{prefix}İlk Yarı Altı/Üstü {number()}".strip()

        return f"{prefix}Alt/Üst {number()}".strip()

    return market


def label_duzelt(label, market):
    raw = str(label or "").strip()
    normalized = tr_key(raw)

    if "&" in normalized:
        parts = [part.strip() for part in normalized.split("&")]

        replace_map = {
            "x": "0",
            "alt": "Alt",
            "ust": "Üst",
            "var": "Var",
            "yok": "Yok",
        }

        return " ve ".join(
            replace_map.get(part, part)
            for part in parts
        )

    if market in ("Çifte Şans", "İlk Yarı Çifte Şans"):
        result = re.fullmatch(
            r"([120x])[-–]([120x])",
            normalized.replace(" ", "")
        )

        if result:
            convert = {
                "x": "0",
                "0": "0",
                "1": "1",
                "2": "2",
            }

            return (
                f"{convert[result.group(1)]} ve "
                f"{convert[result.group(2)]}"
            )

    if market in (
        "Maç Sonucu",
        "İlk Yarı Sonucu",
        "İkinci Yarı Sonucu",
    ):
        if normalized in ("x", "0", "beraberlik"):
            return "0"

        return raw

    general = {
        "alt": "Alt",
        "ust": "Üst",
        "var": "Var",
        "yok": "Yok",
        "evet": "Evet",
        "hayir": "Hayır",
        "esit": "Eşit",
        "tek": "Tek",
        "cift": "Çift",
        "x": "0",
    }

    return general.get(normalized, raw)


def oranlari_standartlastir(oranlar):
    if not isinstance(oranlar, dict):
        return {}

    output = {}

    for key, value in oranlar.items():
        try:
            raw_key = str(key or "").strip()

            # Başlıksız / saçma key daha en başta silinir.
            if not oran_anahtari_gecerli_mi(raw_key):
                continue

            if ham_anahtar_yasak_mi(raw_key):
                continue

            market_raw, label_raw = raw_key.split("_", 1)

            if market_yasak_mi(market_raw):
                continue

            market = market_duzelt(market_raw)
            label = label_duzelt(
                label_temizle(label_raw),
                market
            )

            new_key = f"{market}_{label}".strip("_")

            if not oran_anahtari_gecerli_mi(new_key):
                continue

            if istenmeyen_anahtar_mi(new_key):
                continue

            output[new_key] = float(value)

        except Exception:
            pass

    return output


def oranlar_temizle(oranlar):
    if not isinstance(oranlar, dict):
        return {}

    output = {}

    for key, value in oranlar.items():
        try:
            key = str(key).strip()

            if not oran_anahtari_gecerli_mi(key):
                continue

            if ham_anahtar_yasak_mi(key):
                continue

            if istenmeyen_anahtar_mi(key):
                continue

            output[key] = float(value)

        except Exception:
            pass

    return output


# ============================================================
# ORAN PARSE
# ============================================================

def oran_satiri_mi(text):
    return bool(ODD_RE.match(str(text or "").strip()))


def market_gecerli_mi(text):
    raw = str(text or "").strip()
    normalized = tr_key(raw)

    if not normalized:
        return False

    if len(normalized) > 100:
        return False

    if normalized in MENU_KELIMELER:
        return False

    if oran_satiri_mi(raw):
        return False

    if TIME_RE.match(raw):
        return False

    if SKOR_RE.match(raw):
        return False

    if re.fullmatch(r"\d{3,5}", raw):
        return False

    if " - " in raw:
        return False

    if market_yasak_mi(raw):
        return False

    return True


def nesine_oran_parse(text):
    """
    Market adı olmadan hiçbir oran kaydedilmez.
    Bu nedenle:
      "3": 1.86
      "1-2": 1.59
      "x-2": 1.19
    gibi bozuk anahtarlar oluşmaz.
    """

    odds = {}

    lines = [
        line.strip()
        for line in str(text or "").split("\n")
        if line.strip()
    ]

    current_market = ""
    index = 0

    def add_odd(market, label, raw_value):
        market = str(market or "").strip()
        label = str(label or "").strip()

        # Market yoksa oranı kesinlikle alma.
        if not market:
            return

        if market == "__YASAK__":
            return

        if market_yasak_mi(market):
            return

        if not label:
            return

        try:
            value = float(
                str(raw_value).replace(",", ".")
            )
        except Exception:
            return

        if value < 1.01 or value > 999:
            return

        raw_key = f"{market}_{label}"

        if not oran_anahtari_gecerli_mi(raw_key):
            return

        if ham_anahtar_yasak_mi(raw_key):
            return

        odds[raw_key] = value

    while index < len(lines):
        line = lines[index]
        next_line = lines[index + 1] if index + 1 < len(lines) else ""

        # Yasak market başlığı bulunduysa sonraki markete kadar kapat.
        if market_yasak_mi(line):
            current_market = "__YASAK__"
            index += 1
            continue

        # "1 X 2" ve altında üçlü oran satırı
        if re.fullmatch(r"(?:ms\s+)?1\s+[xX0]\s+2", line):
            values = []

            for jump in range(1, 5):
                if index + jump >= len(lines):
                    break

                found = re.findall(
                    r"\d{1,3}[.,]\d{1,2}",
                    lines[index + jump]
                )

                if found:
                    values = found
                    index += jump
                    break

            if 2 <= len(values) <= 3:
                for label, value in zip(["1", "X", "2"], values):
                    add_odd(current_market, label, value)

            index += 1
            continue

        # "1 2.10 X 3.00 2 2.50"
        tokens = line.split()

        if (
            len(tokens) >= 4 and
            tokens[0].lower() in ("1", "x", "0", "2")
        ):
            pair_ok = True

            for pos in range(1, len(tokens), 2):
                if pos >= len(tokens) or not oran_satiri_mi(tokens[pos]):
                    pair_ok = False
                    break

            if pair_ok:
                for pos in range(0, len(tokens) - 1, 2):
                    add_odd(
                        current_market,
                        tokens[pos],
                        tokens[pos + 1]
                    )

                index += 1
                continue

        # "Alt 1.75", "Var 1.85", "1 2.10"
        inline = re.match(
            r"^(.{1,80}?)\s+(\d{1,3}[.,]\d{1,2})$",
            line
        )

        if inline:
            label = inline.group(1).strip()
            odd = inline.group(2).strip()

            # Seçenek olabilecek kısa etiketler
            if (
                label.lower() in (
                    "1", "x", "0", "2",
                    "alt", "üst", "ust",
                    "var", "yok",
                    "evet", "hayır", "hayir",
                    "tek", "çift", "cift",
                )
                or SKOR_RE.match(label)
                or "&" in label
            ):
                add_odd(current_market, label, odd)

            index += 1
            continue

        # Klasik iki satır:
        # Alt
        # 1.65
        if next_line and oran_satiri_mi(next_line):
            label = line

            if current_market not in ("", "__YASAK__"):
                add_odd(current_market, label, next_line)

            index += 2
            continue

        # Skor etiketi: 0:1 / 1:0 vb.
        if SKOR_RE.match(line):
            index += 1
            continue

        # Yeni market başlığı
        if market_gecerli_mi(line):
            current_market = line

        index += 1

    return odds


# ============================================================
# ARAMA / PANEL
# ============================================================

def arama_kutusunu_temizle(driver):
    try:
        inp = driver.find_element(By.CSS_SELECTOR, SEARCH_SEL)
        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)
        time.sleep(0.4)
    except Exception:
        pass


def arama_yap(driver, text):
    try:
        inp = driver.find_element(By.CSS_SELECTOR, SEARCH_SEL)

        inp.click()
        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)
        inp.send_keys(text)

        time.sleep(2)

        return True

    except Exception:
        return False


def satir_bul(driver, ev, dep):
    ev_short = ev[:20]
    dep_short = dep[:20]

    for row in find_match_cards(driver):
        try:
            text = row.text or ""

            if ev_short in text and dep_short in text:
                return row
        except Exception:
            pass

    return None


def satir_bul_gevsek(driver, ev, dep):
    candidates = [
        (ev[:20], dep[:20]),
        (ev[:12], dep[:12]),
        (ev[:12], None),
    ]

    for home, away in candidates:
        for row in find_match_cards(driver):
            try:
                text = row.text or ""

                if home in text and (
                    away is None or away in text
                ):
                    return row
            except Exception:
                pass

    return None


def satir_bekle(driver, ev, dep, max_sure=6):
    start = time.time()

    while time.time() - start < max_sure:
        row = satir_bul_gevsek(driver, ev, dep)

        if row:
            return row

        time.sleep(0.8)

    return None


def arama_adaylari(isim):
    isim = str(isim or "").strip()

    output = []

    if isim:
        output.append(isim)

    tokens = isim.split()

    if len(tokens) >= 2:
        output.append(" ".join(tokens[:2]))

    if len(tokens) >= 3:
        output.append(" ".join(tokens[:3]))

    unique = []

    for item in output:
        if item and item not in unique:
            unique.append(item)

    return unique


def panel_elementi_bul(driver, row):
    try:
        return driver.execute_script("""
            const row = arguments[0];

            function oddCount(text) {
                return (
                    (text || "").match(/\\d{1,3}[.,]\\d{2}/g) || []
                ).length;
            }

            let sibling = row.nextElementSibling;
            let best = null;
            let bestCount = 0;

            for (let i = 0; i < 5 && sibling; i++) {
                const count = oddCount(sibling.innerText || "");

                if (count > bestCount) {
                    bestCount = count;
                    best = sibling;
                }

                sibling = sibling.nextElementSibling;
            }

            return bestCount >= 3 ? best : null;
        """, row)

    except Exception:
        return None


def panel_metinleri(driver, row):
    try:
        return driver.execute_script("""
            const row = arguments[0];
            const out = [];

            out.push(row.innerText || "");

            let sibling = row.nextElementSibling;

            for (let i = 0; i < 25 && sibling; i++) {
                if (
                    sibling.querySelector &&
                    sibling.querySelector(
                        "span[data-testid^='time-']"
                    )
                ) {
                    break;
                }

                out.push(sibling.innerText || "");
                sibling = sibling.nextElementSibling;
            }

            let parent = row.parentElement;
            let best = null;

            for (let i = 0; i < 6 && parent; i++) {
                const times = Array.from(
                    parent.querySelectorAll(
                        "span[data-testid^='time-']"
                    )
                );

                if (times.length <= 1) {
                    best = parent;
                } else {
                    break;
                }

                parent = parent.parentElement;
            }

            if (best) {
                const text = best.innerText || "";

                if (text.length < 30000) {
                    out.push(text);
                }
            }

            return out;
        """, row)

    except Exception:
        return []


def genislet_dogrula(driver, ev, dep):
    for _ in range(3):
        row = satir_bul(driver, ev, dep)

        if not row:
            time.sleep(1)
            continue

        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                row
            )
        except Exception:
            pass

        clicked = False

        try:
            for target in row.find_elements(By.CSS_SELECTOR, EXPAND_SEL):
                try:
                    target.click()
                    clicked = True
                    break
                except Exception:
                    pass
        except Exception:
            pass

        if not clicked:
            try:
                clicked = driver.execute_script("""
                    const row = arguments[0];

                    const spans = Array.from(
                        row.querySelectorAll("span")
                    );

                    const target = spans.find(span => {
                        const text = (
                            span.innerText ||
                            ""
                        ).trim();

                        return (
                            !text &&
                            span.offsetWidth > 0 &&
                            span.offsetWidth < 50
                        );
                    });

                    if (target) {
                        target.click();
                        return true;
                    }

                    return false;
                """, row)
            except Exception:
                clicked = False

        if not clicked:
            continue

        for _ in range(8):
            time.sleep(0.5)

            fresh_row = satir_bul(driver, ev, dep)

            if fresh_row:
                panel = panel_elementi_bul(driver, fresh_row)

                if panel:
                    return fresh_row, panel

    return None, None


def kapat_dogrula(driver, ev, dep):
    row = satir_bul(driver, ev, dep)

    if not row:
        return

    if panel_elementi_bul(driver, row) is None:
        return

    try:
        for target in row.find_elements(By.CSS_SELECTOR, EXPAND_SEL):
            try:
                target.click()
                break
            except Exception:
                pass
    except Exception:
        pass

    time.sleep(0.5)


def panel_oranlari_cek(driver, ev, dep, max_sure=12):
    toplam = {}
    stable = 0
    start = time.time()

    while time.time() - start < max_sure:
        row = satir_bul(driver, ev, dep)

        if not row:
            stable += 1

            if stable >= 3:
                break

            time.sleep(0.8)
            continue

        previous = len(toplam)

        for text in panel_metinleri(driver, row):
            toplam.update(nesine_oran_parse(text))

        if len(toplam) == previous:
            stable += 1
        else:
            stable = 0

        if stable >= 3:
            break

        time.sleep(0.8)

    return toplam


def mac_oranlari_cek(driver, match):
    ev = match["ev_sahibi"]
    dep = match["deplasman"]

    try:
        row = None

        for candidate in arama_adaylari(ev):
            if arama_yap(driver, candidate[:24]):
                row = satir_bekle(driver, ev, dep)

                if row:
                    break

        if not row:
            for candidate in arama_adaylari(dep):
                if arama_yap(driver, candidate[:24]):
                    row = satir_bekle(driver, ev, dep)

                    if row:
                        break

        if not row:
            arama_kutusunu_temizle(driver)
            return None

        _, panel = genislet_dogrula(driver, ev, dep)

        if panel:
            raw_odds = panel_oranlari_cek(driver, ev, dep)
        else:
            raw_odds = {}

        kapat_dogrula(driver, ev, dep)
        arama_kutusunu_temizle(driver)

        return oranlar_temizle(
            oranlari_standartlastir(raw_odds)
        )

    except Exception as exc:
        print(f"   ⚠️ Oran hatası: {str(exc)[:100]}")

        arama_kutusunu_temizle(driver)

        return {}


# ============================================================
# JSON KAYDET
# ============================================================

def mac_json_kaydet(yeni_maclar):
    data = {
        "matches": [],
        "son_guncelleme": "",
    }

    if os.path.exists(CIKTI_DOSYA):
        try:
            with open(CIKTI_DOSYA, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception:
            pass

    old_matches = data.get("matches", [])

    def match_key(match):
        return (
            match.get("tarih", ""),
            match.get("saat", ""),
            match.get("ev_sahibi", ""),
            match.get("deplasman", ""),
        )

    # Eski maçlarda yalnızca bozuk oranları temizle.
    # Tam standardizasyon yapmadığı için çok yavaşlamaz.
    for old in old_matches:
        odds = old.get("oranlar", {})

        if isinstance(odds, dict):
            old["oranlar"] = oranlar_temizle(odds)
        else:
            old["oranlar"] = {}

    existing = {
        match_key(match): match
        for match in old_matches
    }

    for match in yeni_maclar:
        match["oranlar"] = oranlar_temizle(
            oranlari_standartlastir(
                match.get("oranlar", {})
            )
        )

        key = match_key(match)

        if key in existing:
            old = existing[key]

            # Lig boş geldiyse eski ligi koru.
            if not str(match.get("lig", "")).strip():
                match["lig"] = old.get("lig", "")

            # Oran çekilememişse eski oranları koru.
            if not match.get("oranlar"):
                match["oranlar"] = oranlar_temizle(
                    old.get("oranlar", {})
                )

            # Biten maç skorunu bozma.
            if str(old.get("durum", "")).lower() == "bitti":
                match["durum"] = old.get("durum", "bitti")
                match["skor_ev"] = old.get("skor_ev", 0)
                match["skor_dep"] = old.get("skor_dep", 0)
                match["skor_1y_ev"] = old.get("skor_1y_ev", 0)
                match["skor_1y_dep"] = old.get("skor_1y_dep", 0)
                match["kaynak"] = old.get(
                    "kaynak",
                    "iddaa.com"
                )

        existing[key] = match

    now = datetime.datetime.now().isoformat()

    def to_int(value):
        try:
            return int(value or 0)
        except Exception:
            return 0

    ordered = sorted(
        existing.values(),
        key=lambda item: (
            item.get("tarih", ""),
            item.get("saat", ""),
            item.get("ev_sahibi", ""),
        )
    )

    output_matches = []

    for index, match in enumerate(ordered, start=1):
        output_matches.append({
            "index": index,
            "mac_kodu": str(match.get("mac_kodu", "")),
            "ev_sahibi": str(match.get("ev_sahibi", "")).strip(),
            "deplasman": str(match.get("deplasman", "")).strip(),
            "saat": str(match.get("saat", "")),
            "lig": str(match.get("lig", "")),
            "tarih": str(match.get("tarih", "")),
            "cekme_zamani": str(
                match.get("cekme_zamani", now)
            ),
            "durum": str(match.get("durum", "baslamadi")),
            "skor_ev": to_int(match.get("skor_ev")),
            "skor_dep": to_int(match.get("skor_dep")),
            "skor_1y_ev": to_int(match.get("skor_1y_ev")),
            "skor_1y_dep": to_int(match.get("skor_1y_dep")),
            "kaynak": str(match.get("kaynak", "nesine.com")),
            "oranlar": oranlar_temizle(
                match.get("oranlar", {})
            ),
        })

    output = {
        "matches": output_matches,
        "son_guncelleme": now,
    }

    os.makedirs(
        os.path.dirname(CIKTI_DOSYA),
        exist_ok=True
    )

    path = Path(CIKTI_DOSYA)
    temp = path.with_suffix(".tmp")

    with open(temp, "w", encoding="utf-8") as file:
        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2
        )

    temp.replace(path)

    print(
        f"   💾 Kaydedildi: "
        f"{len(output_matches)} maç | "
        f"{CIKTI_DOSYA}"
    )


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("⚽ NESINE SCRAPER")
    print("📅", datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
    print("=" * 70)

    driver = None
    results = []

    success = 0
    fail = 0
    processed = 0

    try:
        print("\n🟢 Chrome açılıyor...")
        driver = build_driver()

        driver, ok = guvenli_yukle(driver, URL_BASE)

        if not ok:
            print("❌ İlk yükleme başarısız.")
            return

        print("\n⬇️ Maçlar çekiliyor...")
        harvested = deep_harvest(driver)

        print(f"\n📋 Toplam {len(harvested)} maç bulundu.")

        if not harvested:
            return

        grouped = {}

        for match in harvested[:MAX_SCRAPE]:
            grouped.setdefault(
                match["tarih"],
                []
            ).append(match)

        for tarih_iso in sorted(grouped.keys()):
            day_matches = grouped[tarih_iso]
            day_url = nesine_dt_url(tarih_iso)

            driver, ok = gun_sayfasini_yukle(
                driver,
                day_url
            )

            if not ok:
                fail += len(day_matches)
                continue

            for match in day_matches:
                processed += 1

                print(
                    f"[{processed}] "
                    f"{match['tarih']} {match['saat']} | "
                    f"{match['ev_sahibi']} - "
                    f"{match['deplasman']}"
                )

                # Her 50 maçta sadece Chrome kapat/aç.
                # JSON kaydı yapılmaz.
                if (
                    processed > 1 and
                    (processed - 1) % HARVEST_MAC_SAYISI == 0
                ):
                    print("\n" + "=" * 60)
                    print(
                        f"🔄 {processed - 1} maç işlendi. "
                        f"Chrome hızlı yenileniyor..."
                    )
                    print("=" * 60)

                    driver = chrome_hizli_yeniden_baslat(
                        driver,
                        day_url
                    )

                # Sayfa bozulduysa gün URL'sini yenile.
                if (
                    not sayfa_saglikli_mi(driver) or
                    len(find_match_cards(driver)) == 0
                ):
                    print("   ⚠️ Sayfa yenileniyor...")

                    driver, ok = gun_sayfasini_yukle(
                        driver,
                        day_url
                    )

                    if not ok:
                        fail += 1
                        continue

                odds = mac_oranlari_cek(driver, match)

                if odds is None:
                    print("   ❌ Maç bulunamadı.")
                    fail += 1
                    continue

                match["oranlar"] = odds

                print(f"   ✅ {len(odds)} düzgün oran")

                results.append(match)
                success += 1

                time.sleep(
                    random.uniform(*SLEEP_BETWEEN_MATCHES)
                )

        # Tüm maçlar bittikten sonra yalnızca BİR kez kaydeder.
        print("\n💾 Final JSON kaydı yapılıyor...")
        mac_json_kaydet(results)

        print(
            f"\n✅ BİTTİ | "
            f"Başarılı: {success} | "
            f"Başarısız: {fail}"
        )

    except KeyboardInterrupt:
        print("\n⚠️ Kullanıcı işlemi durdurdu.")

        if results:
            print("💾 Mevcut veriler kaydediliyor...")
            mac_json_kaydet(results)

    except Exception as exc:
        print(f"\n❌ ANA HATA: {exc}")
        traceback.print_exc()

        if results:
            print("💾 Mevcut veriler kaydediliyor...")
            mac_json_kaydet(results)

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

        git_force_push()

        try:
            input("Çıkmak için Enter tuşuna basın...")
        except EOFError:
            pass


if __name__ == "__main__":
    main()