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
from webdriver_manager.chrome import ChromeDriverManager


# ============================================================
# AYARLAR
# ============================================================
BASE_DIR = Path(__file__).resolve().parent

URL = "https://www.iddaa.com/program/futbol"
CIKTI_DOSYA = BASE_DIR / "public" / "data" / "mac.json"

MAX_SCROLL_STEPS = 300
STABLE_LIMIT = 18
SCROLL_PX = 600
SCROLL_SLEEP_RANGE = (1.1, 2.0)

MAX_SCRAPE = 9999
SLEEP_BETWEEN_MATCHES = (1.1, 2.4)

# Kaç maçtan sonra Chrome tamamen kapatılıp açılsın?
HARVEST_MAC_SAYISI = 50

MATCH_CARD_SEL = "li.i_tnw__t8AmC"
SEARCH_INPUT_SEL = "#eventSearch"

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")
ODD_RE = re.compile(r"^\d{1,3}([.,]\d{1,2})$")

SILINECEK_BASLANGICLAR = (
    "oyuncu",
    "100.00",
    "takım",
    "karşılaşma özel bahisleri",
    "kaleci kurtarışı",
)

ENABLE_GIT_AUTOPUSH = True
REPO_ROOT = BASE_DIR


# ============================================================
# TARİH
# ============================================================
def bugunun_tarihi():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def yarinin_tarihi():
    return (
        datetime.datetime.now() + datetime.timedelta(days=1)
    ).strftime("%Y-%m-%d")


def parse_league_text(text):
    if not text:
        return ""

    lines = [
        x.strip()
        for x in str(text).splitlines()
        if x.strip()
    ]

    temiz = []

    for line in lines:
        line = (
            line.replace("Bugün", "")
            .replace("Yarın", "")
            .replace("Today", "")
            .replace("Tomorrow", "")
            .strip()
        )

        if not line:
            continue

        if TIME_RE.fullmatch(line):
            continue

        if ODD_RE.fullmatch(line.replace(",", ".")):
            continue

        if re.fullmatch(r"\d+", line):
            continue

        if line in (
            "1", "0", "2", "X", "H",
            "Alt", "Üst", "Var", "Yok",
        ):
            continue

        temiz.append(line)

    return temiz[0] if temiz else ""


# ============================================================
# GİT
# ============================================================
def _find_git_exe():
    exe = shutil.which("git")
    if exe:
        return exe

    adaylar = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
    ]

    for aday in adaylar:
        if os.path.exists(aday):
            return aday

    return None


def _run_cmd(cmd, cwd=None):
    try:
        sonuc = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="ignore",
        )

        return {
            "ok": sonuc.returncode == 0,
            "kod": sonuc.returncode,
            "stdout": sonuc.stdout.strip(),
            "stderr": sonuc.stderr.strip(),
        }

    except Exception as exc:
        return {
            "ok": False,
            "hata": str(exc),
        }


def git_push():
    if not ENABLE_GIT_AUTOPUSH:
        print("ℹ️ Git otomatik gönderim kapalı.")
        return

    if not (REPO_ROOT / ".git").exists():
        print("⚠️ Git klasörü bulunamadı.")
        return

    git_exe = _find_git_exe()
    if not git_exe:
        print("⚠️ Git programı bulunamadı.")
        return

    print("\n🔄 GİT İŞLEMLERİ BAŞLADI...")

    ekle = _run_cmd(
        [git_exe, "add", "."],
        cwd=str(REPO_ROOT),
    )

    if not ekle.get("ok"):
        print(f"❌ Git add hatası: {ekle.get('stderr', '')}")
        return

    zaman = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    mesaj = f"Otomatik guncelleme | {zaman}"

    commit = _run_cmd(
        [git_exe, "commit", "-m", mesaj, "--allow-empty"],
        cwd=str(REPO_ROOT),
    )

    if not commit.get("ok"):
        print(f"❌ Git commit hatası: {commit.get('stderr', '')}")
        return

    # Bilerek force kullanılmıyor.
    push = _run_cmd(
        [git_exe, "push", "origin", "main"],
        cwd=str(REPO_ROOT),
    )

    if push.get("ok"):
        print("✅ GİT BAŞARILI!")
    else:
        print(f"❌ Git push hatası: {push.get('stderr', '')}")


# ============================================================
# CHROME
# ============================================================
def build_driver():
    options = Options()

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"],
    )
    options.add_experimental_option(
        "useAutomationExtension",
        False,
    )

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(
        service=service,
        options=options,
    )

    driver.set_page_load_timeout(60)
    driver.set_script_timeout(30)

    try:
        driver.execute_script("""
            Object.defineProperty(
                navigator,
                'webdriver',
                {get: () => undefined}
            );
        """)
    except Exception:
        pass

    return driver


def cookie_kabul_et(driver):
    try:
        tiklandi = driver.execute_script("""
            const metinler = [
                'Kabul Et',
                'Tümünü Kabul Et',
                'Tümünü kabul et',
                'Tamam',
                'Accept',
                'Accept All'
            ];

            const elemanlar = Array.from(
                document.querySelectorAll('button, a, span')
            );

            for (const el of elemanlar) {
                const text = (
                    el.innerText ||
                    el.textContent ||
                    ''
                ).trim();

                if (metinler.includes(text)) {
                    el.click();
                    return true;
                }
            }

            return false;
        """)

        if tiklandi:
            time.sleep(1)

    except Exception:
        pass


def sayfa_saglikli_mi(driver):
    try:
        body_text = driver.find_element(
            By.TAG_NAME,
            "body",
        ).text.strip()

        body_lower = body_text.lower()

        hata_metinleri = (
            "hay aksi",
            "aw, snap",
            "aw snap",
            "sayfa yanıt vermiyor",
            "page unresponsive",
            "out of memory",
            "status_access_violation",
        )

        if len(body_text) < 50:
            print("      ⚠️ Sayfa boş veya beyaz.")
            return False

        if any(x in body_lower for x in hata_metinleri):
            print("      ⚠️ Chrome çökme sayfası algılandı.")
            return False

        return True

    except Exception as exc:
        print(
            "      ⚠️ Sayfa sağlık kontrolü başarısız:",
            str(exc)[:100],
        )
        return False


def wait_initial(driver, timeout=40):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(
                d.find_element(By.TAG_NAME, "body").text.strip()
            ) > 1000
        )
        return True

    except Exception as exc:
        print(
            "      ⚠️ İlk içerik bekleme hatası:",
            str(exc)[:120],
        )
        return False


def find_match_cards(driver):
    """
    Yalnızca içinde en az iki span[title] bulunan görünür
    maç elemanlarını döndürür.
    """
    try:
        cards = driver.find_elements(
            By.CSS_SELECTOR,
            MATCH_CARD_SEL,
        )
    except Exception:
        return []

    sonuc = []
    element_ids = set()

    for card in cards:
        try:
            if not card.is_displayed():
                continue

            spans = card.find_elements(
                By.CSS_SELECTOR,
                "span[title]",
            )

            takimlar = []

            for span in spans:
                isim = (
                    span.get_attribute("title")
                    or span.text
                    or ""
                ).strip()

                if not isim:
                    continue

                if re.fullmatch(r"\d+", isim):
                    continue

                if isim not in takimlar:
                    takimlar.append(isim)

            if len(takimlar) < 2:
                continue

            if takimlar[0] == takimlar[1]:
                continue

            if card.id in element_ids:
                continue

            element_ids.add(card.id)
            sonuc.append(card)

        except Exception:
            continue

    return sonuc


def guvenli_yukle(driver, url, max_deneme=3):
    """
    Sayfayı yükler. Driver yenilenirse yeni driver nesnesini döndürür.

    Dönüş:
        driver, True
        driver, False
    """
    for deneme in range(1, max_deneme + 1):
        try:
            print(
                f"      🌐 Sayfa yükleniyor... "
                f"deneme {deneme}/{max_deneme}"
            )

            driver.set_page_load_timeout(60)
            driver.get(url)

            time.sleep(8)
            cookie_kabul_et(driver)

            try:
                driver.execute_script("window.scrollTo(0, 400);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
            except Exception:
                pass

            if not sayfa_saglikli_mi(driver):
                raise RuntimeError("Sayfa sağlıklı değil")

            body_text = driver.find_element(
                By.TAG_NAME,
                "body",
            ).text.strip()

            kart_sayisi = len(find_match_cards(driver))

            print(
                f"      🔎 Body uzunluk: {len(body_text)} | "
                f"Kart: {kart_sayisi}"
            )

            print("      ✅ Sayfa yüklendi")
            return driver, True

        except Exception as exc:
            print(
                f"      ⚠️ Yükleme hatası ({deneme}): "
                f"{str(exc)[:150]}"
            )

            if deneme >= max_deneme:
                return driver, False

            try:
                driver.quit()
            except Exception:
                pass

            time.sleep(3)
            print("      🔄 Chrome yeniden açılıyor...")

            try:
                driver = build_driver()
            except Exception as build_error:
                print(
                    "      ❌ Chrome açma hatası:",
                    str(build_error)[:150],
                )
                time.sleep(5)

    return driver, False


def chrome_yeniden_baslat(driver, url=URL):
    """
    Mevcut Chrome'u kapatır ve yeni Chrome döndürür.
    """
    try:
        driver.quit()
    except Exception:
        pass

    print("   🔴 Chrome kapatıldı")
    time.sleep(5)

    son_hata = ""

    for deneme in range(1, 4):
        yeni_driver = None

        try:
            print(
                f"   🟢 Chrome yeniden açılıyor "
                f"({deneme}/3)..."
            )

            yeni_driver = build_driver()
            yeni_driver, ok = guvenli_yukle(
                yeni_driver,
                url,
                max_deneme=2,
            )

            if ok and sayfa_saglikli_mi(yeni_driver):
                print("   ✅ Yeni Chrome hazır")
                return yeni_driver

            son_hata = "Sayfa sağlıklı yüklenmedi"

        except Exception as exc:
            son_hata = str(exc)
            print(
                "   ⚠️ Yeniden başlatma hatası:",
                son_hata[:120],
            )

        if yeni_driver:
            try:
                yeni_driver.quit()
            except Exception:
                pass

        time.sleep(5)

    raise RuntimeError(
        f"Chrome yeniden başlatılamadı: {son_hata}"
    )


# ============================================================
# SCROLL
# ============================================================
def init_scroll_target(driver):
    try:
        driver.execute_script("""
            (function () {
                const elements = Array.from(
                    document.querySelectorAll('*')
                );

                const candidates = elements.filter(el => {
                    const style = getComputedStyle(el);
                    const overflowY = style.overflowY;

                    return (
                        (overflowY === 'auto' ||
                         overflowY === 'scroll') &&
                        (el.scrollHeight - el.clientHeight) > 600 &&
                        el.clientHeight > 300
                    );
                });

                candidates.sort((a, b) => {
                    const aSize = a.scrollHeight - a.clientHeight;
                    const bSize = b.scrollHeight - b.clientHeight;
                    return bSize - aSize;
                });

                window.__scrollEl = candidates[0] || null;
            })();
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
    driver.execute_script("""
        const px = arguments[0];

        if (window.__scrollEl) {
            window.__scrollEl.scrollTop += px;
        } else {
            window.scrollBy(0, px);
        }
    """, px)


# ============================================================
# TARİH FİLTRESİ
# ============================================================
def tarih_menusunu_ac(driver):
    try:
        sonuc = driver.execute_script("""
            const spans = Array.from(
                document.querySelectorAll('span')
            );

            const tarih = spans.find(el => {
                const text = (
                    el.innerText ||
                    el.textContent ||
                    ''
                ).trim();

                return text === 'Tarih';
            });

            if (!tarih) {
                return false;
            }

            tarih.click();
            return true;
        """)

        if sonuc:
            time.sleep(1)

        return bool(sonuc)

    except Exception:
        return False


def gun_butonuna_tikla(driver, gun_adi):
    """
    Lig başlığındaki em etiketine değil, gerçek label'a tıklar.
    """
    try:
        tarih_menusunu_ac(driver)

        sonuc = driver.execute_script("""
            const hedef = arguments[0];

            function temizText(el) {
                return (
                    el.textContent ||
                    el.innerText ||
                    ''
                ).replace(/\\s+/g, ' ').trim();
            }

            const labels = Array.from(
                document.querySelectorAll('label')
            );

            const label = labels.find(el => {
                if (el.closest('[data-lh]')) {
                    return false;
                }

                const children = Array.from(
                    el.querySelectorAll('i, span, em')
                );

                return (
                    temizText(el) === hedef ||
                    children.some(child => {
                        return temizText(child) === hedef;
                    })
                );
            });

            if (!label) {
                return false;
            }

            label.scrollIntoView({
                block: 'center',
                inline: 'center'
            });

            label.click();
            return true;
        """, gun_adi)

        if sonuc:
            time.sleep(3)

        return bool(sonuc)

    except Exception as exc:
        print(
            f"      ⚠️ '{gun_adi}' tıklama hatası: "
            f"{str(exc)[:120]}"
        )
        return False


# ============================================================
# MAÇ VE LİG OKUMA
# ============================================================
def extract_visible(driver, current_date):
    out = []
    seen = set()

    cards = find_match_cards(driver)

    for card in cards:
        try:
            info = driver.execute_script("""
                const card = arguments[0];

                function validName(text) {
                    text = (text || '').trim();

                    if (!text) return false;
                    if (/^\\d+$/.test(text)) return false;
                    if (text.length < 2 || text.length > 80) {
                        return false;
                    }

                    const bad = [
                        '1', '0', '2', 'x', 'h',
                        'alt', 'üst', 'ust', 'var', 'yok'
                    ];

                    return !bad.includes(text.toLowerCase());
                }

                function getTeams() {
                    const spans = Array.from(
                        card.querySelectorAll('span[title]')
                    );

                    const names = [];

                    for (const span of spans) {
                        const name = (
                            span.getAttribute('title') ||
                            span.innerText ||
                            ''
                        ).trim();

                        if (
                            validName(name) &&
                            !names.includes(name)
                        ) {
                            names.push(name);
                        }
                    }

                    return names.slice(0, 2);
                }

                function cleanLeague(text) {
                    return (text || '')
                        .replace('Bugün', '')
                        .replace('Yarın', '')
                        .replace('Today', '')
                        .replace('Tomorrow', '')
                        .trim();
                }

                function findHeader() {
                    let node = card;

                    while (node) {
                        let previous = node.previousElementSibling;

                        while (previous) {
                            const text = previous.innerText || '';

                            if (
                                previous.hasAttribute &&
                                previous.hasAttribute('data-lh')
                            ) {
                                return {
                                    lig: cleanLeague(text),
                                    gun: (
                                        previous.querySelector('em')
                                            ?.innerText || ''
                                    ).trim()
                                };
                            }

                            if (
                                previous.querySelector &&
                                previous.querySelector('img.flag')
                            ) {
                                return {
                                    lig: cleanLeague(text),
                                    gun: (
                                        previous.querySelector('em')
                                            ?.innerText || ''
                                    ).trim()
                                };
                            }

                            if (text.includes('CANLI MAÇLAR')) {
                                return {
                                    lig: '',
                                    gun: 'CANLI'
                                };
                            }

                            previous =
                                previous.previousElementSibling;
                        }

                        node = node.parentElement;
                    }

                    return {
                        lig: '',
                        gun: ''
                    };
                }

                function findTime(ev, dep) {
                    const timeRegex =
                        /\\b([01]?\\d|2[0-3]):[0-5]\\d\\b/;

                    let node = card;

                    for (let i = 0; i < 7 && node; i++) {
                        const text = node.innerText || '';

                        if (
                            text.includes(ev) &&
                            text.includes(dep) &&
                            text.length < 1600
                        ) {
                            const match = text.match(timeRegex);
                            if (match) {
                                return match[0];
                            }
                        }

                        node = node.parentElement;
                    }

                    let previous = card.previousElementSibling;

                    for (let i = 0; i < 10 && previous; i++) {
                        const text = previous.innerText || '';

                        if (text.includes('CANLI MAÇLAR')) {
                            return '';
                        }

                        const match = text.match(timeRegex);

                        if (match) {
                            return match[0];
                        }

                        previous =
                            previous.previousElementSibling;
                    }

                    return '';
                }

                const teams = getTeams();

                if (teams.length < 2) {
                    return null;
                }

                const header = findHeader();

                return {
                    ev: teams[0],
                    dep: teams[1],
                    saat: findTime(teams[0], teams[1]),
                    lig: header.lig || '',
                    gun: header.gun || ''
                };
            """, card)

            if not info:
                continue

            ev = str(info.get("ev") or "").strip()
            dep = str(info.get("dep") or "").strip()
            saat = str(info.get("saat") or "").strip()
            lig = parse_league_text(info.get("lig") or "")
            gun = str(info.get("gun") or "").strip()

            if not ev or not dep or ev == dep:
                continue

            if re.fullmatch(r"\d+", ev):
                continue

            if re.fullmatch(r"\d+", dep):
                continue

            if gun == "CANLI":
                continue

            if not TIME_RE.fullmatch(saat):
                continue

            match = {
                "tarih": current_date,
                "saat": saat,
                "lig": lig,
                "ev_sahibi": ev,
                "deplasman": dep,
                "durum": "baslamadi",
                "skor_ev": 0,
                "skor_dep": 0,
                "skor_1y_ev": 0,
                "skor_1y_dep": 0,
                "oranlar": {},
                "kaynak": "iddaa.com",
            }

            key = (
                match["tarih"],
                match["ev_sahibi"],
                match["deplasman"],
            )

            if key in seen:
                continue

            seen.add(key)
            out.append(match)

        except Exception:
            continue

    return out


def sayfayi_scroll_et(
    driver,
    hedef_tarih,
    max_step=MAX_SCROLL_STEPS,
):
    init_scroll_target(driver)
    reset_scroll_top(driver)
    time.sleep(2)

    maclar = []
    seen = set()

    stable = 0
    last_total = 0

    for step in range(1, max_step + 1):
        if not sayfa_saglikli_mi(driver):
            print(
                "      ⚠️ Sayfa scroll sırasında çöktü. "
                "Mevcut maçlarla devam ediliyor."
            )
            break

        visible_matches = extract_visible(
            driver,
            hedef_tarih,
        )

        for match in visible_matches:
            key = (
                match["tarih"],
                match["ev_sahibi"],
                match["deplasman"],
            )

            if key in seen:
                continue

            seen.add(key)
            maclar.append(match)

        if len(maclar) > last_total:
            artis = len(maclar) - last_total

            print(
                f"      📈 Step {step}: "
                f"+{artis} maç | "
                f"Toplam {len(maclar)}"
            )

            last_total = len(maclar)
            stable = 0
        else:
            stable += 1

        if stable >= STABLE_LIMIT:
            break

        scroll_step(driver, SCROLL_PX)
        time.sleep(
            random.uniform(*SCROLL_SLEEP_RANGE)
        )

    return maclar


def deep_harvest(driver):
    """
    Sıralama önemlidir:

    1. Bugün seçilir ve çekilir.
    2. Bugün kapatılır.
    3. Yarın seçilir ve çekilir.

    Böylece Bugün ve Yarın aynı anda seçili kalmaz.
    """
    bugun = bugunun_tarihi()
    yarin = yarinin_tarihi()

    print(
        f"   🎯 Bugün: {bugun} | "
        f"Yarın: {yarin}"
    )

    harvest = []
    hset = set()

    # --------------------------------------------------------
    # BUGÜN
    # --------------------------------------------------------
    print(f"\n   📅 Bugün ({bugun}) seçiliyor...")

    if not gun_butonuna_tikla(driver, "Bugün"):
        print("      ❌ 'Bugün' butonu bulunamadı")
    else:
        print("      ✅ Yalnızca Bugün çekiliyor...")
        time.sleep(5)

        reset_scroll_top(driver)
        bugun_maclari = sayfayi_scroll_et(
            driver,
            bugun,
        )

        for match in bugun_maclari:
            key = (
                match["tarih"],
                match["ev_sahibi"],
                match["deplasman"],
            )

            if key not in hset:
                hset.add(key)
                harvest.append(match)

        print(
            f"      📊 Bugün: "
            f"{len(bugun_maclari)} maç"
        )

    # --------------------------------------------------------
    # YARIN
    # --------------------------------------------------------
    print(f"\n   📅 Yarın ({yarin}) seçiliyor...")

    # Bugün filtresini kapat.
    if gun_butonuna_tikla(driver, "Bugün"):
        print("      ✅ Bugün filtresi kapatıldı")
    else:
        print("      ⚠️ Bugün filtresi kapatılamadı")

    time.sleep(2)

    # Yarın filtresini aç.
    if not gun_butonuna_tikla(driver, "Yarın"):
        print("      ❌ 'Yarın' butonu bulunamadı")
    else:
        print("      ✅ Yalnızca Yarın çekiliyor...")
        time.sleep(5)

        reset_scroll_top(driver)
        yarin_maclari = sayfayi_scroll_et(
            driver,
            yarin,
        )

        for match in yarin_maclari:
            key = (
                match["tarih"],
                match["ev_sahibi"],
                match["deplasman"],
            )

            if key not in hset:
                hset.add(key)
                harvest.append(match)

        print(
            f"      📊 Yarın: "
            f"{len(yarin_maclari)} maç"
        )

    bugun_adet = sum(
        1 for match in harvest
        if match["tarih"] == bugun
    )

    yarin_adet = sum(
        1 for match in harvest
        if match["tarih"] == yarin
    )

    print(
        f"\n   🎯 Toplam: {len(harvest)} maç "
        f"(Bugün: {bugun_adet}, "
        f"Yarın: {yarin_adet})"
    )

    return harvest


# ============================================================
# MAÇ DETAYI VE ORANLAR
# ============================================================
def clear_and_type(element, text):
    element.click()
    time.sleep(0.1)

    # CTRL+A ve Delete
    element.send_keys("\uE009a")
    element.send_keys("\uE003")

    time.sleep(0.1)
    element.send_keys(text)


def card_teams(card):
    try:
        spans = card.find_elements(
            By.CSS_SELECTOR,
            "span[title]",
        )

        names = []

        for span in spans:
            name = (
                span.get_attribute("title")
                or span.text
                or ""
            ).strip()

            if name and name not in names:
                names.append(name)

        return names[:2]

    except Exception:
        return []


def match_card_click(driver, card):
    try:
        driver.execute_script(
            """
            arguments[0].scrollIntoView({
                block: 'center',
                inline: 'center'
            });
            """,
            card,
        )

        time.sleep(0.3)

        try:
            ActionChains(driver).move_to_element(
                card
            ).pause(0.2).click().perform()
        except Exception:
            driver.execute_script(
                "arguments[0].click();",
                card,
            )

        return True

    except Exception:
        return False


def click_match(driver, ev, dep):
    """
    Önce arama kutusuyla bulur.
    Bulamazsa scroll yaparak arar.
    """
    try:
        search_input = WebDriverWait(
            driver,
            15,
        ).until(
            lambda d: d.find_element(
                By.CSS_SELECTOR,
                SEARCH_INPUT_SEL,
            )
        )

        clear_and_type(search_input, ev[:22])
        time.sleep(1)

        for card in find_match_cards(driver):
            names = card_teams(card)

            if len(names) >= 2:
                if names[0] == ev and names[1] == dep:
                    return match_card_click(driver, card)

            text = card.text or ""

            if ev in text and dep in text:
                return match_card_click(driver, card)

        clear_and_type(search_input, dep[:22])
        time.sleep(1)

        for card in find_match_cards(driver):
            names = card_teams(card)

            if len(names) >= 2:
                if names[0] == ev and names[1] == dep:
                    return match_card_click(driver, card)

            text = card.text or ""

            if ev in text and dep in text:
                return match_card_click(driver, card)

    except Exception:
        pass

    # Arama kutusuyla bulunamazsa scroll ile ara.
    init_scroll_target(driver)
    reset_scroll_top(driver)

    for _ in range(25):
        if not sayfa_saglikli_mi(driver):
            return False

        for card in find_match_cards(driver):
            try:
                names = card_teams(card)

                if len(names) >= 2:
                    if names[0] == ev and names[1] == dep:
                        return match_card_click(driver, card)

                text = card.text or ""

                if ev in text and dep in text:
                    return match_card_click(driver, card)

            except Exception:
                continue

        scroll_step(driver, 800)
        time.sleep(1)

    return False


def tumu_bekle(driver, max_sure=15):
    for _ in range(max_sure):
        try:
            body = driver.find_element(
                By.TAG_NAME,
                "body",
            ).text

            if "Tümü" in body:
                return True

        except Exception:
            pass

        time.sleep(1)

    return False


def nokta_var_mi(text):
    try:
        value = float(
            str(text).replace(",", ".")
        )
        return 1.01 <= value <= 999.99
    except Exception:
        return False


def detay_parse(driver):
    oranlar = {}
    atlanan = 0

    try:
        body_text = driver.find_element(
            By.TAG_NAME,
            "body",
        ).text
    except Exception:
        return oranlar

    lines = [
        line.strip()
        for line in body_text.splitlines()
        if line.strip()
    ]

    try:
        index = lines.index("Tümü")
    except ValueError:
        return oranlar

    i = index + 1
    market = ""

    while i < len(lines) - 1:
        current = lines[i]
        next_line = lines[i + 1]

        if nokta_var_mi(next_line):
            full_key = (
                f"{market}_{current}"
                if market else current
            )

            normalized = full_key.strip().lower()

            if normalized.startswith(
                SILINECEK_BASLANGICLAR
            ):
                atlanan += 1
            else:
                try:
                    oranlar[full_key] = float(
                        next_line.replace(",", ".")
                    )
                except Exception:
                    pass

            i += 2
        else:
            market = current
            i += 1

    if atlanan:
        print(
            f"   🚫 {atlanan} gereksiz oran filtrelendi"
        )

    return oranlar


# ============================================================
# JSON KAYDET
# ============================================================
def mac_json_kaydet(yeni_maclar):
    data = {
        "version": 2,
        "updated": "",
        "matches": [],
    }

    if CIKTI_DOSYA.exists():
        try:
            with CIKTI_DOSYA.open(
                "r",
                encoding="utf-8",
            ) as file:
                loaded = json.load(file)

            if (
                isinstance(loaded, dict)
                and isinstance(
                    loaded.get("matches"),
                    list,
                )
            ):
                data = loaded

        except Exception as exc:
            print(
                f"   ⚠️ Eski JSON okunamadı: "
                f"{str(exc)[:120]}"
            )
            return

    def key(match):
        return (
            str(match.get("tarih") or "").strip(),
            str(match.get("saat") or "").strip(),
            str(match.get("ev_sahibi") or "").strip(),
            str(match.get("deplasman") or "").strip(),
        )

    def birlestir(eski, yeni):
        sonuc = dict(eski)

        for alan, deger in yeni.items():
            if deger not in (None, "", {}, []):
                sonuc[alan] = deger

        yeni_lig = str(
            yeni.get("lig") or ""
        ).strip()

        eski_lig = str(
            eski.get("lig") or ""
        ).strip()

        sonuc["lig"] = (
            yeni_lig
            if yeni_lig else eski_lig
        )

        yeni_oran = yeni.get("oranlar") or {}
        eski_oran = eski.get("oranlar") or {}

        sonuc["oranlar"] = (
            yeni_oran
            if yeni_oran else eski_oran
        )

        return sonuc

    matches_map = {}

    for match in data.get("matches", []):
        match_key = key(match)

        if all(match_key):
            matches_map[match_key] = match

    for match in yeni_maclar or []:
        match_key = key(match)

        if not all(match_key):
            continue

        if match_key in matches_map:
            matches_map[match_key] = birlestir(
                matches_map[match_key],
                match,
            )
        else:
            yeni = dict(match)
            yeni.setdefault("lig", "")
            yeni.setdefault("oranlar", {})
            matches_map[match_key] = yeni

    data["matches"] = sorted(
        matches_map.values(),
        key=lambda x: (
            x.get("tarih", ""),
            x.get("saat", "00:00"),
            x.get("ev_sahibi", ""),
        ),
    )

    for index, match in enumerate(
        data["matches"],
        start=1,
    ):
        match["index"] = index
        match.setdefault("lig", "")
        match.setdefault("oranlar", {})

    data["updated"] = (
        datetime.datetime.now().isoformat()
    )

    CIKTI_DOSYA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_file = CIKTI_DOSYA.with_suffix(
        ".json.tmp"
    )

    backup_file = CIKTI_DOSYA.with_suffix(
        ".json.bak"
    )

    try:
        with temp_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

        if CIKTI_DOSYA.exists():
            shutil.copy2(
                CIKTI_DOSYA,
                backup_file,
            )

        os.replace(
            temp_file,
            CIKTI_DOSYA,
        )

        print(
            f"   💾 Kaydedildi: "
            f"{len(data['matches'])} maç | "
            f"{CIKTI_DOSYA}"
        )

    except Exception as exc:
        print(
            f"   ❌ JSON yazma hatası: "
            f"{str(exc)[:150]}"
        )


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 70)
    print("⚽ IDDAA SCRAPER")
    print(
        "📅",
        datetime.datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        ),
    )
    print("=" * 70)

    driver = None
    results = []

    success = 0
    fail = 0

    try:
        # ----------------------------------------------------
        # İLK AÇILIŞ
        # ----------------------------------------------------
        print("\n🟢 Chrome açılıyor...")
        driver = build_driver()

        driver, ok = guvenli_yukle(
            driver,
            URL,
        )

        if not ok:
            print("❌ İlk yükleme başarısız")
            return

        if not wait_initial(driver):
            print("❌ İçerik yüklenemedi")
            return

        # ----------------------------------------------------
        # MAÇ LİSTESİ
        # ----------------------------------------------------
        print("\n⬇️ Maçlar ve ligler çekiliyor...")

        harvested = deep_harvest(driver)
        toplam = len(harvested)

        print(f"\n📋 {toplam} maç bulundu")

        if not harvested:
            print("❌ Hiç maç bulunamadı")
            return

        # Maçlar, oranlar alınmadan önce de kaydedilir.
        # Böylece oranı alınamayan yeni maçlar kaybolmaz.
        mac_json_kaydet(harvested)

        # ----------------------------------------------------
        # ORANLAR
        # ----------------------------------------------------
        print("\n🔽 Oranlar alınıyor...")

        for idx, match in enumerate(
            harvested[:MAX_SCRAPE],
            start=1,
        ):
            print(
                f"[{idx}/{toplam}] "
                f"{match['tarih']} "
                f"{match['saat']} | "
                f"({match.get('lig', '')}) | "
                f"{match['ev_sahibi']} - "
                f"{match['deplasman']}"
            )

            # ------------------------------------------------
            # HER 50 MAÇTA CHROME YENİLE
            # ------------------------------------------------
            if (
                idx > 1
                and (idx - 1) % HARVEST_MAC_SAYISI == 0
            ):
                print()
                print("=" * 60)
                print(
                    f"🔄 {idx - 1} maç işlendi. "
                    "Chrome tamamen yeniden başlatılıyor..."
                )
                print("=" * 60)

                mac_json_kaydet(results)

                driver = chrome_yeniden_baslat(
                    driver,
                    URL,
                )

                print("=" * 60)
                print()

            # ------------------------------------------------
            # ANA SAYFAYI AÇ
            # ------------------------------------------------
            try:
                driver.set_page_load_timeout(45)
                driver.get(URL)
                time.sleep(4)

            except Exception as exc:
                print(
                    "   ⚠️ Sayfa açma hatası:",
                    str(exc)[:100],
                )

            # Beyaz veya Hay aksi kontrolü
            if not sayfa_saglikli_mi(driver):
                print(
                    "   🔄 Sayfa sağlıklı değil. "
                    "Chrome yeniden başlatılıyor..."
                )

                mac_json_kaydet(results)

                try:
                    driver = chrome_yeniden_baslat(
                        driver,
                        URL,
                    )
                except Exception as exc:
                    print(
                        "   ❌ Chrome yenilenemedi:",
                        str(exc)[:120],
                    )
                    fail += 1
                    continue

            # ------------------------------------------------
            # MAÇI BUL VE TIKLA
            # ------------------------------------------------
            try:
                bulundu = click_match(
                    driver,
                    match["ev_sahibi"],
                    match["deplasman"],
                )
            except Exception as exc:
                print(
                    "   ❌ Maç arama hatası:",
                    str(exc)[:100],
                )
                bulundu = False

            if not bulundu:
                print("   ❌ Maç bulunamadı")
                fail += 1
                continue

            time.sleep(2)

            # ------------------------------------------------
            # ORANLARI AL
            # ------------------------------------------------
            try:
                driver.execute_script(
                    "window.scrollTo(0, 800);"
                )
                time.sleep(0.5)

                if tumu_bekle(driver, 12):
                    oranlar = detay_parse(driver)
                    match["oranlar"] = oranlar

                    print(
                        f"   ✅ {len(oranlar)} oran"
                    )
                else:
                    print("   ⚠️ Tümü bulunamadı")
                    match["oranlar"] = {}

            except Exception as exc:
                print(
                    "   ⚠️ Oran hatası:",
                    str(exc)[:100],
                )
                match["oranlar"] = {}

            results.append(match)
            success += 1

            # Her 10 başarılı maçta kaydet.
            if success % 10 == 0:
                mac_json_kaydet(results)

            time.sleep(
                random.uniform(
                    *SLEEP_BETWEEN_MATCHES
                )
            )

        # Son kayıt
        mac_json_kaydet(results)

        print(
            f"\n✅ BİTTİ | "
            f"Başarılı: {success} | "
            f"Başarısız: {fail}"
        )

    except KeyboardInterrupt:
        print("\n⚠️ Kullanıcı programı durdurdu.")

        if results:
            print("   💾 Mevcut sonuçlar kaydediliyor...")
            mac_json_kaydet(results)

    except Exception as exc:
        print(f"\n❌ ANA HATA: {exc}")
        traceback.print_exc()

        if results:
            print("   💾 Mevcut sonuçlar kaydediliyor...")
            mac_json_kaydet(results)

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

        try:
            git_push()
        except Exception as exc:
            print(
                "⚠️ Git işlemi sırasında hata:",
                str(exc)[:120],
            )

        input("\nÇıkmak için Enter tuşuna basın...")


if __name__ == "__main__":
    main()