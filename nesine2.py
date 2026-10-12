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
from webdriver_manager.chrome import ChromeDriverManager


# ============================================================
# AYARLAR
# ============================================================

URL_BASE = "https://www.nesine.com/iddaa"

REPO_ROOT = Path(__file__).resolve().parent
CIKTI_DOSYA = str(REPO_ROOT / "public" / "data" / "mac.json")

MAX_SCROLL_STEPS = 300
STABLE_LIMIT = 18
SCROLL_PX = 650
SCROLL_SLEEP_RANGE = (1.0, 1.8)

MAX_SCRAPE = 9999
SLEEP_BETWEEN_MATCHES = (1.0, 2.0)

# Siyah reklam sorunları nedeniyle 0 önerilir.
# 50 yaparsan her 50 maçta Chrome kapanır/açılır.
HARVEST_MAC_SAYISI = 0

SEARCH_SEL = 'input[data-test-id="srch-box"]'
EXPAND_SEL = "span.f17af500409a2f819a68"

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")
ODD_RE = re.compile(r"^\d{1,3}([.,]\d{1,2})$")

ENABLE_GIT_AUTOPUSH = True


# ============================================================
# FİLTRELENECEK MARKETLER
# ============================================================

SILINECEK_BASLANGICLAR = (
    "oyuncu",
    "golcu",
    "kaleci",
    "kurtaris",
    "kurtarisi",
    "korner",
    "corner",
    "toplam korner",
    "ilk yari korner",
    "1 yari korner",
    "1. yari korner",
    "ev sahibi korner",
    "deplasman korner",
    "kart",
    "sari kart",
    "kirmizi kart",
    "toplam kart",
)

MENU_KELIMELER = {
    "bulten",
    "canli",
    "canli sonuclar",
    "sonuclar",
    "kuponum",
    "kuponlarim",
    "spor toto",
    "yardim",
    "giris",
    "uye ol",
    "nesine",
    "futbol",
    "basketbol",
    "tenis",
    "voleybol",
    "hentbol",
    "buz hokeyi",
    "amerikan futbolu",
    "e-futbol",
    "mma",
    "tumu",
    "yukle",
    "bugun",
    "yarin",
}


# ============================================================
# GENEL YARDIMCILAR
# ============================================================

def tr_key(value):
    text = str(value or "")

    replacements = {
        "İ": "i",
        "I": "i",
        "ı": "i",
        "Ş": "s",
        "ş": "s",
        "Ğ": "g",
        "ğ": "g",
        "Ü": "u",
        "ü": "u",
        "Ö": "o",
        "ö": "o",
        "Ç": "c",
        "ç": "c",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.lower()
    return re.sub(r"\s+", " ", text).strip()


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


# ============================================================
# MARKET / ORAN ANAHTARI KONTROLÜ
# ============================================================

def market_yasak_mi(market):
    normalized = tr_key(market)

    if not normalized:
        return False

    for yasak in SILINECEK_BASLANGICLAR:
        if normalized.startswith(tr_key(yasak)):
            return True

    yasak_kelimeler = (
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
    )

    return any(word in normalized for word in yasak_kelimeler)


def oran_anahtari_gecerli_mi(key):
    """
    Market_Seçenek formatı zorunludur.

    Geçerli:
        Alt/Üst 2.5_Alt
        1,5 Gol Alt/Üst_Alt
        Handikaplı Maç Sonucu 0:2_1

    Geçersiz:
        3
        2.58
        x-2
        3_1
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

    # Market yalnızca sayı olamaz.
    if re.fullmatch(r"\d+", market_normal):
        return False

    # Market yalnızca oran değeri olamaz.
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{1,2})?", market_normal):
        return False

    # Market en az bir harf içermeli.
    if not re.search(r"[a-zçğıöşü]", market_normal):
        return False

    # Label doğrudan oran sayısı olamaz.
    if re.fullmatch(r"\d{1,3}[.,]\d{1,2}", label_normal):
        return False

    # Takım adı yanlışlıkla market olmuşsa.
    if " - " in market:
        return False

    if market_yasak_mi(market):
        return False

    return True


def istenmeyen_anahtar_mi(key):
    if not oran_anahtari_gecerli_mi(key):
        return True

    normalized = tr_key(key)
    market = normalized.split("_", 1)[0]

    if market_yasak_mi(market):
        return True

    # Market başlığı düşmüş korner oranları.
    if re.fullmatch(
        r"alt/ust\s+"
        r"(7\.5|8\.5|9\.5|10\.5|11\.5|12\.5|13\.5|14\.5)"
        r"_(alt|ust)",
        normalized
    ):
        return True

    return False


def label_temizle(label):
    label = tr_key(label)

    return re.sub(
        r"^(ms|hms|cs|iy|2y|1y|au|kg|2\.y|1\.y)\s+",
        "",
        label
    ).strip()


# ============================================================
# MARKET STANDARDİZASYONU
# ============================================================

def market_duzelt(market):
    """
    Nesine market başlıklarını frontend'in kullandığı anahtarlara çevirir.
    """

    raw_market = str(market or "").strip()

    market = tr_key(raw_market)
    market = re.sub(r"(\d),(\d)", r"\1.\2", market)
    market = re.sub(r"\s+", " ", market).strip()

    # 1.Y / 1. Y / 1. Yarı / 1 Y gibi yazımları normalize et.
    market = re.sub(r"\b1\s*\.\s*y\b", "1. yari", market)
    market = re.sub(r"\b1\s*y\b", "1. yari", market)
    market = re.sub(r"\b1\s*\.\s*yar[ıi]\b", "1. yari", market)
    market = re.sub(r"\b1\s*yar[ıi]\b", "1. yari", market)

    market = re.sub(r"\b2\s*\.\s*y\b", "2. yari", market)
    market = re.sub(r"\b2\s*y\b", "2. yari", market)
    market = re.sub(r"\b2\s*\.\s*yar[ıi]\b", "2. yari", market)
    market = re.sub(r"\b2\s*yar[ıi]\b", "2. yari", market)

    # Handikaplı Maç Sonucu (0:2) -> 0:2
    market = market.replace("(", " ").replace(")", " ")
    market = re.sub(r"\s+", " ", market).strip()

    def goal_line_number():
        """
        1. yari 1.5 gol alt/ust -> 1.5

        İlk yarıdaki "1" değerini yanlışlıkla limit olarak almaz.
        """

        found = re.search(
            r"(\d+(?:\.\d+)?)\s*gol\s*(?:alti|alt|ustu|ust|alt/ust)",
            market
        )

        if found:
            return found.group(1)

        decimals = re.findall(r"\d+\.\d+", market)

        if decimals:
            return decimals[-1]

        numbers = re.findall(r"\d+", market)

        return numbers[-1] if numbers else ""

    first_half = (
        "ilk yari" in market or
        "1. yari" in market
    )

    second_half = (
        "ikinci yari" in market or
        "2. yari" in market
    )

    both_score = (
        "karsilikli gol" in market or
        market == "kg"
    )

    over_under = bool(
        re.search(r"\balt(i)?\b|\bust(u)?\b", market)
    )

    match_result = (
        "mac sonucu" in market or
        market in ("ms", "1x2")
    )

    line = goal_line_number()

    # --------------------------------------------------------
    # 1. YARI / 2. YARI KARŞILIKLI GOL
    #
    # 1. Yarı / 2. Yarı Karşılıklı Gol
    # İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur
    # --------------------------------------------------------
    if both_score and first_half and second_half:
        return "Her İki Yarıda Karşılıklı Gol"

    # --------------------------------------------------------
    # İki Yarı da Alt / Üst
    #
    # İki Yarı da 1,5 Alt
    # Her İki Yarıda da 1,5 Üst
    # --------------------------------------------------------
    if "iki yari" in market or "her iki yari" in market:
        if re.search(r"\balt\b", market):
            return f"Her İki Yarıda da Alt {line}".strip()

        if re.search(r"\bust\b", market):
            return f"Her İki Yarıda da Üst {line}".strip()

    # --------------------------------------------------------
    # Handikaplı Maç Sonucu
    # --------------------------------------------------------
    handicap = re.search(
        r"handikap\w*\s*(?:mac sonucu\s*)?(\d+\s*:\s*\d+)",
        market
    )

    if handicap:
        handicap_value = re.sub(
            r"\s*",
            "",
            handicap.group(1)
        )

        return f"Handikaplı Maç Sonucu {handicap_value}"

    if "handikap" in market:
        return "Handikaplı Maç Sonucu"

    # --------------------------------------------------------
    # Kombine marketler
    # --------------------------------------------------------
    if both_score and over_under:
        return f"Altı/Üstü {line} ve Karşılıklı Gol"

    if both_score and match_result:
        return "Maç Sonucu ve Karşılıklı Gol"

    if both_score and first_half and "sonuc" in market:
        return "İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol"

    if first_half and "sonuc" in market and over_under:
        return f"İlk Yarı Sonucu ve Altı/Üstü {line}"

    if match_result and over_under:
        return f"Maç Sonucu ve Alt/Üst {line}"

    # --------------------------------------------------------
    # Maç sonucu / İlk yarı maç sonucu
    # --------------------------------------------------------
    if first_half and match_result:
        return "İlk Yarı / Maç Sonucu"

    if match_result:
        return "Maç Sonucu"

    # --------------------------------------------------------
    # Çifte şans
    # --------------------------------------------------------
    if "cifte sans" in market:
        if first_half:
            return "İlk Yarı Çifte Şans"

        return "Çifte Şans"

    # --------------------------------------------------------
    # Toplam gol / Maç skoru
    # --------------------------------------------------------
    if "toplam gol" in market:
        return "Toplam Gol"

    if "mac skoru" in market:
        return "Maç Skoru"

    # --------------------------------------------------------
    # Karşılıklı gol
    # --------------------------------------------------------
    if both_score:
        if first_half:
            return "İlk Yarı Karşılıklı Gol"

        if second_half:
            return "İkinci Yarı Karşılıklı Gol"

        return "Karşılıklı Gol"

    # --------------------------------------------------------
    # Yarı sonucu
    # --------------------------------------------------------
    if first_half and "sonuc" in market:
        return "İlk Yarı Sonucu"

    if second_half and "sonuc" in market:
        return "İkinci Yarı Sonucu"

    # --------------------------------------------------------
    # Tek / Çift
    # --------------------------------------------------------
    if re.search(r"tek\s*/?\s*cift", market):
        if first_half:
            return "İlk Yarı Tek / Çift"

        if second_half:
            return "İkinci Yarı Tek / Çift"

        return "Tek / Çift"

    # --------------------------------------------------------
    # Alt / Üst
    # --------------------------------------------------------
    if over_under:
        prefix = ""

        if "ev sahibi" in market:
            prefix = "Ev Sahibi "
        elif "deplasman" in market:
            prefix = "Deplasman "

        if first_half:
            return f"{prefix}İlk Yarı Altı/Üstü {line}".strip()

        if second_half:
            return f"{prefix}İkinci Yarı Altı/Üstü {line}".strip()

        return f"{prefix}Alt/Üst {line}".strip()

    # Tanınmayan marketler silinmesin.
    return market.strip()


def label_duzelt(label, market):
    """
    Market seçeneklerini frontend uyumlu hale getirir.
    """

    raw = str(label or "").strip()
    normalized = tr_key(raw)

    # --------------------------------------------------------
    # 1. Yarı / 2. Yarı KG kombinasyonu
    #
    # Evet / Evet  -> EE
    # Evet / Hayır -> EH
    # Hayır / Evet -> HE
    # Hayır / Hayır -> HH
    # --------------------------------------------------------
    if market == "Her İki Yarıda Karşılıklı Gol":
        compact = normalized.replace(" ", "")

        mapping = {
            "evet/evet": "EE",
            "evet/hayir": "EH",
            "hayir/evet": "HE",
            "hayir/hayir": "HH",

            "var/var": "EE",
            "var/yok": "EH",
            "yok/var": "HE",
            "yok/yok": "HH",
        }

        if compact in mapping:
            return mapping[compact]

    # Alt & Var -> Alt ve Var
    if "&" in normalized:
        mapping = {
            "x": "0",
            "alt": "Alt",
            "ust": "Üst",
            "var": "Var",
            "yok": "Yok",
            "evet": "Evet",
            "hayir": "Hayır",
        }

        return " ve ".join(
            mapping.get(part.strip(), part.strip())
            for part in normalized.split("&")
        )

    # Çifte Şans
    if market in ("Çifte Şans", "İlk Yarı Çifte Şans"):
        found = re.fullmatch(
            r"([120x])[-–]([120x])",
            normalized.replace(" ", "")
        )

        if found:
            mapping = {
                "1": "1",
                "0": "0",
                "x": "0",
                "2": "2",
            }

            return (
                f"{mapping[found.group(1)]} ve "
                f"{mapping[found.group(2)]}"
            )

    # Maç sonucu / yarı sonucu
    if market in (
        "Maç Sonucu",
        "İlk Yarı Sonucu",
        "İkinci Yarı Sonucu",
    ):
        if normalized in ("x", "0", "beraberlik"):
            return "0"

        return raw

    mapping = {
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

    return mapping.get(normalized, raw)


def oranlari_standartlastir(oranlar):
    """
    Ham oranları frontend standartlarına dönüştürür.

    Aynı anahtar tekrar gelirse:
      Son gelen oran kullanılır.
      Köşeli parantezli ek anahtar üretilmez.
    """

    if not isinstance(oranlar, dict):
        return {}

    output = {}
    collision_count = 0
    error_count = 0

    for raw_key, raw_value in oranlar.items():
        try:
            raw_key = str(raw_key or "").strip()

            if "_" not in raw_key:
                continue

            market_raw, label_raw = raw_key.split("_", 1)

            market_raw = market_raw.strip()
            label_raw = label_raw.strip()

            if not market_raw or not label_raw:
                continue

            if market_yasak_mi(market_raw):
                continue

            # Label direkt bir oran sayısı olamaz.
            if re.fullmatch(
                r"\d{1,3}[.,]\d{1,2}",
                label_raw
            ):
                continue

            market = market_duzelt(market_raw)

            if not market:
                market = market_raw

            label = label_duzelt(
                label_temizle(label_raw),
                market
            )

            if not label:
                label = label_raw

            new_key = f"{market}_{label}".strip()

            if istenmeyen_anahtar_mi(new_key):
                continue

            value = float(raw_value)

            if new_key in output and output[new_key] != value:
                collision_count += 1

            # Aynı key tekrar gelirse son oran geçerli sayılır.
            output[new_key] = value

        except Exception as exc:
            error_count += 1

            if error_count <= 5:
                print(
                    f"   ⚠️ Standardizasyon hatası | "
                    f"Key: {raw_key!r} | "
                    f"Hata: {type(exc).__name__}: {exc}"
                )

    if collision_count > 0:
        print(
            f"   ℹ️ Aynı anahtarda güncellenen oran: "
            f"{collision_count}"
        )

    if error_count > 0:
        print(
            f"   ⚠️ Standardizasyon hata sayısı: "
            f"{error_count}"
        )

    return output


def oranlar_temizle(oranlar):
    """
    Son JSON filtresi.
    """

    if not isinstance(oranlar, dict):
        return {}

    output = {}

    for key, value in oranlar.items():
        try:
            key = str(key or "").strip()

            if not key:
                continue

            if istenmeyen_anahtar_mi(key):
                continue

            output[key] = float(value)

        except Exception:
            pass

    return output


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

        time.sleep(0.4)

    except Exception:
        pass


def reklam_kapat(driver):
    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
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

        time.sleep(0.4)

    except Exception:
        pass


def siyah_ekran_ve_popup_temizle(driver):
    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    except Exception:
        pass

    try:
        driver.execute_script("""
            function visible(el) {
                if (!el) return false;

                const rect = el.getBoundingClientRect();
                const style = getComputedStyle(el);

                return (
                    rect.width > 0 &&
                    rect.height > 0 &&
                    style.display !== "none" &&
                    style.visibility !== "hidden"
                );
            }

            const width = window.innerWidth;
            const height = window.innerHeight;

            for (const el of document.querySelectorAll(
                "iframe, video, canvas, div, section, aside, dialog"
            )) {
                try {
                    if (!visible(el)) continue;

                    const rect = el.getBoundingClientRect();
                    const style = getComputedStyle(el);

                    const fullScreen =
                        rect.width >= width * 0.75 &&
                        rect.height >= height * 0.65;

                    const layer =
                        style.position === "fixed" ||
                        style.position === "absolute";

                    if (!fullScreen || !layer) continue;

                    const text = (
                        el.innerText ||
                        el.textContent ||
                        ""
                    ).toLowerCase();

                    const classText = (
                        String(el.className || "") + " " +
                        String(el.id || "")
                    ).toLowerCase();

                    const ad = (
                        el.tagName === "IFRAME" ||
                        el.tagName === "VIDEO" ||
                        el.tagName === "CANVAS" ||
                        text.includes("reklam") ||
                        text.includes("kampanya") ||
                        text.includes("bonus") ||
                        text.includes("kapat") ||
                        classText.includes("popup") ||
                        classText.includes("overlay") ||
                        classText.includes("modal") ||
                        classText.includes("advert") ||
                        classText.includes("banner")
                    );

                    if (ad) {
                        el.style.display = "none";
                        el.style.pointerEvents = "none";
                    }

                } catch (e) {}
            }

            document.body.style.overflow = "auto";
            document.documentElement.style.overflow = "auto";
        """)

        time.sleep(0.5)

    except Exception:
        pass


# ============================================================
# MAÇ SATIRI BULMA
# ============================================================

def find_match_cards(driver):
    try:
        return driver.execute_script("""
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

            return unique.filter(el =>
                !unique.some(
                    other => other !== el && el.contains(other)
                )
            );
        """) or []

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
        text = driver.find_element(By.TAG_NAME, "body").text.strip().lower()

        if len(text) < 50:
            return False

        errors = (
            "hay aksi",
            "aw snap",
            "page unresponsive",
            "out of memory",
            "status_access_violation",
        )

        return not any(item in text for item in errors)

    except Exception:
        return False


def gun_sayfasini_yukle(driver, url_gun, max_deneme=2):
    for _ in range(max_deneme):
        try:
            driver.get(url_gun)
            time.sleep(5)

            for _ in range(3):
                cookie_kabul_et(driver)
                reklam_kapat(driver)
                siyah_ekran_ve_popup_temizle(driver)
                time.sleep(0.6)

            count = satir_sayisi_bekle(driver, 15)

            print(f"   🔎 Gün satır sayısı: {count}")

            if count > 0:
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
# SCROLL / MAÇ TOPLAMA
# ============================================================

def init_scroll_target(driver):
    try:
        driver.execute_script("""
            const all = Array.from(document.querySelectorAll("*"));

            const candidates = all.filter(el => {
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


def extract_visible(driver, current_date):
    output = []
    seen = set()

    try:
        data = driver.execute_script("""
            function clean(text) {
                return (text || "")
                    .trim()
                    .replace(/\\s+/g, " ");
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
                    const text = node.innerText || "";

                    if (
                        text.includes("-") &&
                        text.length > 30 &&
                        text.length < 2000
                    ) {
                        rows.push(node);
                        break;
                    }

                    node = node.parentElement;
                }
            }

            const uniqueRows = [...new Set(rows)].filter(row =>
                !rows.some(
                    other => other !== row && row.contains(other)
                )
            );

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
                        return [
                            parts[0].trim(),
                            parts.slice(1).join(" - ").trim()
                        ];
                    }
                }

                return ["", ""];
            }

            return uniqueRows.map(row => {
                const teams = getTeams(row);

                return {
                    home: teams[0],
                    away: teams[1],
                    time: getTime(row)
                };
            });
        """)

    except Exception:
        data = []

    for item in data or []:
        home = str(item.get("home") or "").strip()
        away = str(item.get("away") or "").strip()
        saat = str(item.get("time") or "").strip()

        if not home or not away or home == away:
            continue

        if not TIME_RE.match(saat):
            continue

        match = {
            "tarih": current_date,
            "saat": saat,
            "lig": "",
            "ev_sahibi": home,
            "deplasman": away,
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
    old_total = 0

    for step in range(1, MAX_SCROLL_STEPS + 1):
        current = extract_visible(driver, hedef_tarih)

        for match in current:
            key = (
                match["tarih"],
                match["ev_sahibi"],
                match["deplasman"],
            )

            if key not in seen:
                seen.add(key)
                matches.append(match)

        if len(matches) > old_total:
            print(
                f"      📈 Step {step}: "
                f"+{len(matches) - old_total} | "
                f"Toplam {len(matches)}"
            )

            old_total = len(matches)
            stable = 0
        else:
            stable += 1

        if stable >= STABLE_LIMIT:
            break

        scroll_step(driver)
        time.sleep(random.uniform(*SCROLL_SLEEP_RANGE))

    return matches


def deep_harvest(driver):
    dates = [
        (bugunun_tarihi(), "Bugün"),
        (yarinin_tarihi(), "Yarın"),
    ]

    output = []
    seen = set()

    for tarih, title in dates:
        print(f"\n   📅 {title}: {tarih}")

        driver, ok = gun_sayfasini_yukle(
            driver,
            nesine_dt_url(tarih)
        )

        if not ok:
            print("      ⚠️ Gün sayfası yüklenemedi.")
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


def arama_adaylari(name):
    name = str(name or "").strip()

    candidates = []

    if name:
        candidates.append(name)

    tokens = name.split()

    if len(tokens) >= 2:
        candidates.append(" ".join(tokens[:2]))

    if len(tokens) >= 3:
        candidates.append(" ".join(tokens[:3]))

    return list(dict.fromkeys(candidates))


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


def satir_bekle(driver, ev, dep, max_sure=6):
    start = time.time()

    while time.time() - start < max_sure:
        row = satir_bul(driver, ev, dep)

        if row:
            return row

        time.sleep(0.8)

    return None


def panel_elementi_bul(driver, row):
    try:
        return driver.execute_script("""
            const row = arguments[0];

            function oddCount(text) {
                return (
                    (text || "").match(/\\d{1,3}[.,]\\d{2}/g) || []
                ).length;
            }

            let node = row.nextElementSibling;
            let best = null;
            let bestCount = 0;

            for (let i = 0; i < 6 && node; i++) {
                const count = oddCount(node.innerText || "");

                if (count > bestCount) {
                    best = node;
                    bestCount = count;
                }

                node = node.nextElementSibling;
            }

            return bestCount >= 2 ? best : null;
        """, row)
    except Exception:
        return None


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
            time.sleep(0.4)
        except Exception:
            pass

        clicked = False

        try:
            for button in row.find_elements(By.CSS_SELECTOR, EXPAND_SEL):
                try:
                    button.click()
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

                    const target = spans.find(el => {
                        return (
                            !(el.innerText || "").trim() &&
                            el.offsetWidth > 0 &&
                            el.offsetWidth < 50
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

        for _ in range(10):
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

    try:
        for button in row.find_elements(By.CSS_SELECTOR, EXPAND_SEL):
            try:
                button.click()
                break
            except Exception:
                pass
    except Exception:
        pass

    time.sleep(0.5)


# ============================================================
# DOM'DAN ORAN ÇEKME
# ============================================================

def panel_oranlarini_domdan_cek(driver, ev, dep):
    row = satir_bul(driver, ev, dep)

    if not row:
        return {}

    js_code = r"""
        const row = arguments[0];

        function clean(value) {
            return (value || "")
                .replace(/\s+/g, " ")
                .trim();
        }

        function isNumberOnly(value) {
            return /^\d+$/.test(value || "");
        }

        let parent = row.parentElement;
        let bestParent = null;
        let bestGroupCount = 0;

        for (let i = 0; i < 10 && parent; i++) {
            const groups = parent.querySelectorAll(
                "div[data-test-id^='group-']"
            );

            const timeNodes = parent.querySelectorAll(
                "span[data-testid^='time-']"
            );

            if (
                groups.length > 0 &&
                timeNodes.length <= 1 &&
                groups.length >= bestGroupCount
            ) {
                bestParent = parent;
                bestGroupCount = groups.length;
            }

            parent = parent.parentElement;
        }

        if (!bestParent) {
            bestParent = row.parentElement;
        }

        const marketRows = Array.from(
            bestParent.querySelectorAll("div[data-test-id]")
        ).filter(node => {
            const id = node.getAttribute("data-test-id") || "";

            return /^\d+_\d+_\d+$/.test(id);
        });

        const results = [];
        const seen = new Set();

        for (const marketRow of marketRows) {
            try {
                let marketTitle = "";

                const infoButton = marketRow.querySelector(
                    "button[data-test-info][data-test-title]"
                );

                if (infoButton) {
                    marketTitle = clean(
                        infoButton.getAttribute("data-test-title")
                    );
                }

                if (!marketTitle) {
                    const marketButton = marketRow.querySelector(
                        "button[data-test-m-id]"
                    );

                    if (marketButton) {
                        const header = marketButton.parentElement;

                        if (header) {
                            const spans = Array.from(
                                header.querySelectorAll("span")
                            )
                            .map(span => clean(
                                span.innerText || span.textContent
                            ))
                            .filter(text => {
                                if (!text) return false;
                                if (text === "-") return false;
                                if (text === "undefined") return false;
                                if (isNumberOnly(text)) return false;
                                return true;
                            });

                            if (spans.length > 0) {
                                marketTitle = spans[spans.length - 1];
                            }
                        }
                    }
                }

                if (!marketTitle) {
                    continue;
                }

                const options = Array.from(
                    marketRow.querySelectorAll(
                        "[data-test-title][data-test-value]"
                    )
                );

                for (const option of options) {
                    const label = clean(
                        option.getAttribute("data-test-title")
                    );

                    const rawValue = clean(
                        option.getAttribute("data-test-value")
                    );

                    if (!label || label === "-") continue;
                    if (!rawValue || rawValue === "-") continue;

                    if (!/^\d{1,3}[.,]\d{1,2}$/.test(rawValue)) {
                        continue;
                    }

                    const value = parseFloat(
                        rawValue.replace(",", ".")
                    );

                    if (
                        Number.isNaN(value) ||
                        value < 1.01 ||
                        value > 999
                    ) {
                        continue;
                    }

                    const key = marketTitle + "_" + label;

                    if (seen.has(key)) {
                        continue;
                    }

                    seen.add(key);

                    results.push({
                        market: marketTitle,
                        label: label,
                        value: value
                    });
                }

            } catch (error) {}
        }

        return {
            groupCount: bestGroupCount,
            marketRowCount: marketRows.length,
            optionNodeCount: bestParent.querySelectorAll(
                "[data-test-title][data-test-value]"
            ).length,
            entries: results
        };
    """

    try:
        result = driver.execute_script(js_code, row)

        if not isinstance(result, dict):
            return {}

        entries = result.get("entries", [])

        print(
            f"   🔍 Panel DOM | "
            f"Grup: {result.get('groupCount', 0)} | "
            f"Market satırı: {result.get('marketRowCount', 0)} | "
            f"Oran düğümü: {result.get('optionNodeCount', 0)} | "
            f"Okunan: {len(entries)}"
        )

        output = {}

        for item in entries:
            if not isinstance(item, dict):
                continue

            market = str(item.get("market", "")).strip()
            label = str(item.get("label", "")).strip()

            try:
                value = float(item.get("value"))
            except Exception:
                continue

            if not market or not label:
                continue

            if market_yasak_mi(market):
                continue

            raw_key = f"{market}_{label}"

            if not oran_anahtari_gecerli_mi(raw_key):
                continue

            output[raw_key] = value

        return output

    except Exception as exc:
        print(f"   ⚠️ DOM panel okuma hatası: {str(exc)[:120]}")
        return {}


def panel_oranlari_cek(driver, ev, dep, max_sure=10):
    output = {}
    stable_count = 0
    start_time = time.time()

    while time.time() - start_time < max_sure:
        old_count = len(output)

        dom_odds = panel_oranlarini_domdan_cek(
            driver,
            ev,
            dep
        )

        if dom_odds:
            output.update(dom_odds)

        if len(output) > old_count:
            print(
                f"      ➕ {len(output) - old_count} yeni oran | "
                f"Toplam: {len(output)}"
            )
            stable_count = 0
        else:
            stable_count += 1

        if stable_count >= 4:
            break

        time.sleep(0.7)

    print(f"   🔍 Panelden toplam DOM ham oran: {len(output)}")

    return output


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
            reklam_kapat(driver)
            siyah_ekran_ve_popup_temizle(driver)

            for candidate in arama_adaylari(ev):
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
            print("   ⚠️ Oran paneli açılamadı.")
            raw_odds = {}

        kapat_dogrula(driver, ev, dep)
        arama_kutusunu_temizle(driver)

        standardized = oranlari_standartlastir(raw_odds)
        cleaned = oranlar_temizle(standardized)

        print(
            f"   📊 Ham: {len(raw_odds)} | "
            f"Standart: {len(standardized)} | "
            f"Kaydedilecek: {len(cleaned)}"
        )

        return cleaned

    except Exception as exc:
        print(f"   ⚠️ Oran hatası: {str(exc)[:100]}")

        try:
            arama_kutusunu_temizle(driver)
        except Exception:
            pass

        return None


# ============================================================
# MAC.JSON KORUMALI KAYIT
# ============================================================

def mac_json_kaydet(yeni_maclar):
    """
    APPEND-ONLY kayıt.

    Eski mac.json kayıtları silinmez.
    Yeni maç veya değişmiş oran snapshot'ı listenin sonuna eklenir.
    """

    if not os.path.exists(CIKTI_DOSYA):
        data = {
            "matches": [],
            "son_guncelleme": ""
        }
    else:
        try:
            with open(CIKTI_DOSYA, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception as exc:
            print("\n❌ KRİTİK: mac.json okunamadı.")
            print("❌ Mevcut dosyanın üstüne yazılmayacak.")
            print(f"   Hata: {exc}")
            return

    if not isinstance(data, dict):
        print("❌ mac.json root yapısı bozuk. Yazma iptal.")
        return

    if not isinstance(data.get("matches"), list):
        print("❌ mac.json matches alanı liste değil. Yazma iptal.")
        return

    existing_matches = data["matches"]

    print(f"\n📂 Korunan eski kayıt: {len(existing_matches)}")
    print(f"📥 Yeni çekilen maç: {len(yeni_maclar)}")

    output_path = Path(CIKTI_DOSYA)

    try:
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_path = output_path.with_name(
            f"{output_path.stem}_backup_{stamp}{output_path.suffix}"
        )

        shutil.copy2(output_path, backup_path)
        print(f"💾 Yedek: {backup_path}")

    except Exception as exc:
        print(f"⚠️ Yedek alınamadı: {exc}")

    def mac_identity(match):
        return (
            str(match.get("tarih", "")).strip(),
            str(match.get("saat", "")).strip(),
            tr_key(match.get("ev_sahibi", "")),
            tr_key(match.get("deplasman", "")),
        )

    def normalize_odds(odds):
        if not isinstance(odds, dict):
            return {}

        output = {}

        for key, value in odds.items():
            try:
                output[str(key).strip()] = round(float(value), 6)
            except Exception:
                output[str(key).strip()] = str(value)

        return output

    def odds_changed(old_odds, new_odds):
        return normalize_odds(old_odds) != normalize_odds(new_odds)

    latest_by_match = {}

    for old_match in existing_matches:
        if not isinstance(old_match, dict):
            continue

        key = mac_identity(old_match)

        if key not in latest_by_match:
            latest_by_match[key] = old_match
            continue

        old_time = str(old_match.get("cekme_zamani", ""))
        current_time = str(
            latest_by_match[key].get("cekme_zamani", "")
        )

        if old_time >= current_time:
            latest_by_match[key] = old_match

    now_iso = datetime.datetime.now().isoformat()

    new_count = 0
    changed_count = 0
    same_count = 0
    empty_count = 0

    for incoming in yeni_maclar:
        if not isinstance(incoming, dict):
            continue

        match = dict(incoming)

        if isinstance(incoming.get("oranlar"), dict):
            match["oranlar"] = dict(incoming["oranlar"])
        else:
            match["oranlar"] = {}

        key = mac_identity(match)
        previous = latest_by_match.get(key)

        # Yeni maç.
        if previous is None:
            match["cekme_zamani"] = now_iso

            existing_matches.append(match)
            latest_by_match[key] = match

            new_count += 1
            continue

        # Yeni oran yoksa eski kaydı değiştirme.
        if not match["oranlar"]:
            empty_count += 1
            continue

        # Oran değişmemişse snapshot ekleme.
        if not odds_changed(
            previous.get("oranlar", {}),
            match.get("oranlar", {})
        ):
            same_count += 1
            continue

        # Lig boş geldiyse eskiyi kullan.
        if not str(match.get("lig", "")).strip():
            match["lig"] = previous.get("lig", "")

        # Bitmiş skorları bozma.
        if str(previous.get("durum", "")).lower() == "bitti":
            match["durum"] = previous.get("durum", "bitti")
            match["skor_ev"] = previous.get("skor_ev", 0)
            match["skor_dep"] = previous.get("skor_dep", 0)
            match["skor_1y_ev"] = previous.get("skor_1y_ev", 0)
            match["skor_1y_dep"] = previous.get("skor_1y_dep", 0)
            match["kaynak"] = previous.get("kaynak", "iddaa.com")

        # Eski kayıt kalır, yenisi sona eklenir.
        match["cekme_zamani"] = now_iso

        existing_matches.append(match)
        latest_by_match[key] = match

        changed_count += 1

    # Eski liste sırası korunur, sadece index yenilenir.
    for index, match in enumerate(existing_matches, start=1):
        if isinstance(match, dict):
            match["index"] = index

    data["matches"] = existing_matches
    data["son_guncelleme"] = now_iso
    data["updated"] = now_iso

    temp_path = output_path.with_suffix(".tmp")

    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
            )

        temp_path.replace(output_path)

    except Exception as exc:
        print(f"❌ mac.json yazılamadı: {exc}")
        return

    print("\n" + "=" * 62)
    print("💾 APPEND-ONLY JSON KAYIT TAMAMLANDI")
    print("=" * 62)
    print(f"   Yeni maç: {new_count}")
    print(f"   Oranı değişen snapshot: {changed_count}")
    print(f"   Oranı aynı olan: {same_count}")
    print(f"   Boş oranlı atlanan: {empty_count}")
    print(f"   Toplam kayıt: {len(existing_matches)}")
    print("=" * 62)


# ============================================================
# GIT
# ============================================================

def find_git_exe():
    git = shutil.which("git")

    if git:
        return git

    paths = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
    ]

    for path in paths:
        if os.path.exists(path):
            return path

    return None


def run_cmd(command, cwd=None):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        return result.returncode == 0, result.stdout, result.stderr

    except Exception as exc:
        return False, "", str(exc)


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

    run_cmd([git, "checkout", "-B", "main"], str(REPO_ROOT))
    run_cmd([git, "add", "-A"], str(REPO_ROOT))

    message = (
        "Otomatik guncelleme | "
        f"{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
    )

    run_cmd(
        [git, "commit", "-m", message, "--allow-empty"],
        str(REPO_ROOT)
    )

    ok, _, error = run_cmd(
        [git, "push", "-f", "origin", "main"],
        str(REPO_ROOT)
    )

    if ok:
        print("✅ Git push başarılı.")
    else:
        print("❌ Git push başarısız:")
        print(error)


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

        driver, ok = gun_sayfasini_yukle(
            driver,
            URL_BASE
        )

        if not ok:
            print("❌ İlk sayfa yüklenemedi.")
            return

        print("\n⬇️ Maçlar çekiliyor...")
        harvested = deep_harvest(driver)

        print(f"\n📋 Toplam maç: {len(harvested)}")

        if not harvested:
            return

        grouped = {}

        for match in harvested[:MAX_SCRAPE]:
            grouped.setdefault(
                match["tarih"],
                []
            ).append(match)

        print("\n🔽 Oranlar çekiliyor...")

        for tarih_iso in sorted(grouped.keys()):
            day_matches = grouped[tarih_iso]
            day_url = nesine_dt_url(tarih_iso)

            driver, ok = gun_sayfasini_yukle(
                driver,
                day_url
            )

            if not ok:
                print(f"❌ Gün yüklenemedi: {tarih_iso}")
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

                if (
                    HARVEST_MAC_SAYISI > 0
                    and processed > 1
                    and (processed - 1) % HARVEST_MAC_SAYISI == 0
                ):
                    print("\n🔄 Chrome yeniden başlatılıyor...")

                    try:
                        driver.quit()
                    except Exception:
                        pass

                    time.sleep(2)

                    driver = build_driver()

                    driver, ok = gun_sayfasini_yukle(
                        driver,
                        day_url
                    )

                    if not ok:
                        fail += 1
                        continue

                if (
                    not sayfa_saglikli_mi(driver)
                    or len(find_match_cards(driver)) == 0
                ):
                    driver, ok = gun_sayfasini_yukle(
                        driver,
                        day_url
                    )

                    if not ok:
                        fail += 1
                        continue

                odds = mac_oranlari_cek(driver, match)

                if odds is None:
                    print("   ❌ Maç bulunamadı / oran çekilemedi.")
                    fail += 1
                    continue

                match["oranlar"] = odds

                print(f"   ✅ {len(odds)} oran kaydedildi")

                results.append(match)
                success += 1

                time.sleep(
                    random.uniform(*SLEEP_BETWEEN_MATCHES)
                )

        print("\n💾 Final JSON kaydı yapılıyor...")
        mac_json_kaydet(results)

        print(
            f"\n✅ BİTTİ | "
            f"Başarılı: {success} | "
            f"Başarısız: {fail}"
        )

    except KeyboardInterrupt:
        print("\n⚠️ İşlem kullanıcı tarafından durduruldu.")

        if results:
            mac_json_kaydet(results)

    except Exception as exc:
        print(f"\n❌ ANA HATA: {exc}")
        traceback.print_exc()

        if results:
            print("💾 Şu ana kadarki veriler kaydediliyor...")
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