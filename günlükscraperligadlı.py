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

MAX_SCROLL_STEPS = 300
STABLE_LIMIT = 18
SCROLL_PX = 600
SCROLL_SLEEP_RANGE = (1.1, 2.0)

MAX_SCRAPE = 9999
SLEEP_BETWEEN_MATCHES = (1.1, 2.4)
HARVEST_MAC_SAYISI = 999

MATCH_CARD_SEL = "li.i_tnw__t8AmC"
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

def parse_league_text(text):
    if not text:
        return ""

    lines = [
        x.strip()
        for x in str(text).split("\n")
        if x.strip()
    ]

    temiz = []

    for x in lines:
        x = x.replace("Bugün", "").replace("Yarın", "")
        x = x.replace("Today", "").replace("Tomorrow", "")
        x = x.strip()

        if not x:
            continue

        if TIME_RE.match(x):
            continue

        if ODD_RE.match(x.replace(",", ".")):
            continue

        if re.fullmatch(r"\d+", x):
            continue

        if x in ("1", "0", "2", "X", "H", "Alt", "Üst", "Var", "Yok"):
            continue

        temiz.append(x)

    if temiz:
        return temiz[0]

    return ""

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
            lambda d: len(find_match_cards(d)) > 0
        )
        return True
    except Exception:
        print("      ⚠️ wait_initial: maç kartı bulunamadı")

        try:
            saat_sayisi = driver.execute_script("""
                const txt = document.body.innerText || '';
                const m = txt.match(/\\b\\d{1,2}:\\d{2}\\b/g);
                return m ? m.length : 0;
            """)
            print(f"      ⏱ Body içindeki saat sayısı: {saat_sayisi}")
        except Exception:
            pass

        debug_sayfa(driver)
        selector_debug(driver)
        return False

def guvenli_yukle(driver, url, max_deneme=3):
    for deneme in range(max_deneme):
        try:
            print(f"      🌐 Sayfa yükleniyor... deneme {deneme + 1}/{max_deneme}")

            driver.set_page_load_timeout(60)
            driver.get(url)

            # React içerik için bekle
            time.sleep(8)

            cookie_kabul_et(driver)

            # Sayfayı biraz oynat, lazy-load tetiklensin
            try:
                driver.execute_script("window.scrollTo(0, 400);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, 0);")
                reset_scroll_top(driver)
                time.sleep(2)
            except Exception:
                pass

            body_text = ""
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text.strip()
            except Exception:
                pass

            kart_sayisi = 0
            try:
                kart_sayisi = len(find_match_cards(driver))
            except Exception:
                kart_sayisi = 0

            saat_sayisi = 0
            try:
                saat_sayisi = driver.execute_script("""
                    const txt = document.body.innerText || '';
                    const m = txt.match(/\\b\\d{1,2}:\\d{2}\\b/g);
                    return m ? m.length : 0;
                """)
            except Exception:
                saat_sayisi = 0

            print(
                f"      🔎 Body uzunluk: {len(body_text)} | "
                f"Saat: {saat_sayisi} | Kart: {kart_sayisi}"
            )

            if len(body_text) < 50:
                raise Exception("Sayfa boş/beyaz")

            if kart_sayisi > 0:
                print("      ✅ Sayfa yüklendi")
                return driver, True

            # Kart ilk ekranda yoksa biraz aşağı inip tekrar bak
            try:
                driver.execute_script("window.scrollTo(0, 1200);")
                time.sleep(2)
                kart_sayisi = len(find_match_cards(driver))
                print(f"      🔎 Aşağı kaydırma sonrası Kart: {kart_sayisi}")
            except Exception:
                kart_sayisi = 0

            if kart_sayisi > 0:
                print("      ✅ Sayfa yüklendi")
                return driver, True

            print("      ⚠️ Kart bulunamadı ama sayfa açık. Devam deneniyor...")

            try:
                debug_sayfa(driver)
            except Exception:
                pass

            try:
                selector_debug(driver)
            except Exception:
                pass

            # Sayfa açılmışsa deep_harvest kendi scroll'unda bulmayı denesin
            return driver, True

        except Exception as e:
            print(f"      ⚠️ Yükleme hatası ({deneme + 1}): {str(e)[:150]}")

            if deneme < max_deneme - 1:
                try:
                    driver.quit()
                except Exception:
                    pass

                time.sleep(3)
                print("      🔄 Chrome yeniden açılıyor...")

                try:
                    driver = build_driver()
                    time.sleep(2)
                except Exception as ee:
                    print(f"      ❌ Chrome yeniden açılamadı: {ee}")
                    time.sleep(5)
            else:
                return driver, False

    return driver, False

def cookie_kabul_et(driver):
    try:
        driver.execute_script("""
            const texts = ['Kabul Et', 'Tümünü Kabul Et', 'Tamam', 'Accept', 'Accept All'];
            const els = Array.from(document.querySelectorAll('button, div, span, a'));
            for (const el of els) {
                const t = (el.innerText || el.textContent || '').trim();
                if (texts.includes(t)) {
                    el.click();
                    return true;
                }
            }
            return false;
        """)
        time.sleep(1)
    except Exception:
        pass


def find_match_cards(driver):
    """
    Gerçek maç kartını class'a bağlı kalmadan bulur.
    Takım isimleri span[title] içinden aranır.
    li class değişse bile çalışır.
    """
    try:
        cards = driver.execute_script("""
            function visible(el) {
                if (!el) return false;
                const r = el.getBoundingClientRect();
                const s = getComputedStyle(el);
                return r.width > 80 &&
                       r.height > 10 &&
                       r.height < 260 &&
                       s.display !== 'none' &&
                       s.visibility !== 'hidden' &&
                       Number(s.opacity || 1) > 0;
            }

            function validName(t) {
                t = (t || '').trim();
                if (!t) return false;
                if (/^\\d+$/.test(t)) return false;
                if (t.length < 2 || t.length > 70) return false;

                const bad = ['1', '0', '2', 'x', 'h', 'alt', 'üst', 'ust', 'var', 'yok'];
                if (bad.includes(t.toLowerCase())) return false;

                return /[A-Za-zÇĞİÖŞÜçğıöşü]/.test(t);
            }

            function teamTitles(el) {
                return Array.from(el.querySelectorAll('span[title], [title]'))
                    .map(s => (s.getAttribute('title') || s.innerText || '').trim())
                    .filter(validName);
            }

            const titleEls = Array.from(document.querySelectorAll('span[title], [title]'))
                .filter(el => validName(el.getAttribute('title') || el.innerText || ''));

            let candidates = [];

            for (const sp of titleEls) {
                let n = sp;

                for (let i = 0; i < 8 && n; i++) {
                    const names = teamTitles(n);
                    const txt = (n.innerText || '').trim();

                    if (
                        names.length >= 2 &&
                        visible(n) &&
                        txt.length < 1200
                    ) {
                        candidates.push(n);
                        break;
                    }

                    n = n.parentElement;
                }
            }

            candidates = [...new Set(candidates)];

            // Büyük kapsayıcıları at, en küçük gerçek kart kalsın
            candidates = candidates.filter(el => {
                return !candidates.some(other => other !== el && el.contains(other));
            });

            return candidates.slice(0, 1000);
        """)

        return cards or []

    except Exception:
        return []

def debug_sayfa(driver):
    try:
        print("      🌍 URL:", driver.current_url)
    except Exception:
        pass

    try:
        print("      🧾 TITLE:", driver.title)
    except Exception:
        pass

    try:
        body = driver.find_element(By.TAG_NAME, "body").text
        print("      📄 Body ilk 700 karakter:")
        print(body[:700])
    except Exception:
        pass

    try:
        driver.save_screenshot("debug_iddaa.png")
        print("      📸 Screenshot kaydedildi: debug_iddaa.png")
    except Exception:
        pass

    try:
        with open("debug_iddaa.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("      🧩 HTML kaydedildi: debug_iddaa.html")
    except Exception:
        pass

def selector_debug(driver):
    try:
        info = driver.execute_script("""
            const txt = document.body.innerText || '';
            const times = txt.match(/\\b\\d{1,2}:\\d{2}\\b/g) || [];

            const els = Array.from(document.querySelectorAll('div, a, li, button, span, section, article'));
            const timeEls = els
                .filter(el => /\\b\\d{1,2}:\\d{2}\\b/.test(el.innerText || ''))
                .slice(0, 50)
                .map(el => ({
                    tag: el.tagName,
                    cls: el.className ? String(el.className) : '',
                    txt: (el.innerText || '').trim().slice(0, 350)
                }));

            return {
                timeCount: times.length,
                times: times.slice(0, 30),
                elems: timeEls
            };
        """)

        print(f"      ⏱ Sayfadaki saat sayısı: {info.get('timeCount')}")
        print(f"      ⏱ İlk saatler: {info.get('times')}")

        print("      🔍 Saat içeren elementler:")
        for i, r in enumerate(info.get("elems") or [], 1):
            print(f"      #{i} <{r.get('tag')}> class='{r.get('cls')}'")
            print("        " + r.get("txt", "").replace("\n", " | "))

    except Exception as e:
        print("      ⚠️ selector_debug hata:", e)

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
        window.scrollBy({
          top: px,
          left: 0,
          behavior: 'smooth'
        });
      }
    """, px)


# =========================
# MAÇ KART OKUMA & LİG ÇEKME
# =========================
def parse_card(card_or_text, current_date):
    """
    Hem Selenium WebElement hem düz text kabul eder.
    """
    try:
        if hasattr(card_or_text, "text"):
            txt = (card_or_text.text or "").strip()
        else:
            txt = (str(card_or_text) if card_or_text is not None else "").strip()
    except Exception:
        return None

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

        # oran satırlarını atla
        if ODD_RE.match(x.replace(",", ".")):
            continue

        # kısa kodları atla
        if re.fullmatch(r"[A-Z]{2,8}", x):
            continue

        # gereksiz menü yazılarını atla
        low = x.lower()
        if low in (
            "bülten", "canlı sonuçlar", "yazar yorumları",
            "popüler bahisler", "kolay kuponlar", "lig analiz",
            "giriş", "üye ol", "beni hatırla", "şifremi göster",
            "unuttum", "bugün", "yarın"
        ):
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
        "lig": "",
        "ev_sahibi": ev,
        "deplasman": dep,
        "durum": "baslamadi",
        "skor_ev": 0,
        "skor_dep": 0,
        "skor_1y_ev": 0,
        "skor_1y_dep": 0,
        "oranlar": {},
        "kaynak": "iddaa.com"
    }

def extract_visible(driver, current_date):
    out = []
    seen = set()

    expected_day = ""
    if current_date == bugunun_tarihi():
        expected_day = "Bugün"
    elif current_date == yarinin_tarihi():
        expected_day = "Yarın"

    cards = find_match_cards(driver)

    for c in cards:
        try:
            info = driver.execute_script("""
                const card = arguments[0];

                function validName(t) {
                    t = (t || '').trim();
                    if (!t) return false;
                    if (/^\\d+$/.test(t)) return false;
                    if (t.length < 2 || t.length > 70) return false;

                    const bad = ['1', '0', '2', 'x', 'h', 'alt', 'üst', 'ust', 'var', 'yok'];
                    if (bad.includes(t.toLowerCase())) return false;

                    return /[A-Za-zÇĞİÖŞÜçğıöşü]/.test(t);
                }

                function getTeams(card) {
                    const names = Array.from(card.querySelectorAll('span[title], [title]'))
                        .map(s => (s.getAttribute('title') || s.innerText || '').trim())
                        .filter(validName);

                    const uniq = [];
                    for (const n of names) {
                        if (!uniq.includes(n)) uniq.push(n);
                    }

                    if (uniq.length >= 2) {
                        return [uniq[0], uniq[1]];
                    }

                    return ['', ''];
                }

                function cleanLeague(t) {
                    return (t || '')
                        .replace('Bugün', '')
                        .replace('Yarın', '')
                        .replace('Today', '')
                        .replace('Tomorrow', '')
                        .trim();
                }

                function findHeader(card) {
                    let n = card;

                    while (n) {
                        let p = n.previousElementSibling;

                        while (p) {
                            const txt = p.innerText || '';

                            if (p.hasAttribute && p.hasAttribute('data-lh')) {
                                const em = p.querySelector('em');
                                return {
                                    lig: cleanLeague(txt),
                                    gun: em ? (em.innerText || '').trim() : ''
                                };
                            }

                            if (p.querySelector && p.querySelector('img.flag')) {
                                const em = p.querySelector('em');
                                return {
                                    lig: cleanLeague(txt),
                                    gun: em ? (em.innerText || '').trim() : ''
                                };
                            }

                            // Canlı başlığını yakala
                            if ((txt || '').includes('CANLI MAÇLAR')) {
                                return {
                                    lig: '',
                                    gun: 'CANLI'
                                };
                            }

                            p = p.previousElementSibling;
                        }

                        n = n.parentElement;
                    }

                    return {lig: '', gun: ''};
                }

                function findTime(card, ev, dep) {
                    const timeRe = /\\b\\d{1,2}:\\d{2}\\b/;

                    // Çok büyük parenta çıkma, yoksa sayfa saati 13:02 yakalanır
                    let n = card;

                    for (let i = 0; i < 7 && n; i++) {
                        const txt = n.innerText || '';

                        if (
                            txt.includes(ev) &&
                            txt.includes(dep) &&
                            txt.length < 1500
                        ) {
                            const m = txt.match(timeRe);
                            if (m) return m[0];
                        }

                        n = n.parentElement;
                    }

                    let p = card.previousElementSibling;

                    for (let i = 0; i < 10 && p; i++) {
                        const txt = p.innerText || '';

                        if ((txt || '').includes('CANLI MAÇLAR')) {
                            return '';
                        }

                        const m = txt.match(timeRe);
                        if (m) return m[0];

                        p = p.previousElementSibling;
                    }

                    return '';
                }

                function isLiveCard(card) {
                    const txt = card.innerText || '';

                    // 90+, 94', devre, canlı skor gibi şeyler varsa canlı olabilir
                    if (/\\b\\d{1,3}\\+?('|’)?\\b/.test(txt) && !/\\b\\d{1,2}:\\d{2}\\b/.test(txt)) {
                        return true;
                    }

                    let n = card;
                    for (let i = 0; i < 6 && n; i++) {
                        let p = n.previousElementSibling;
                        for (let j = 0; j < 8 && p; j++) {
                            const pt = p.innerText || '';
                            if (pt.includes('CANLI MAÇLAR')) return true;
                            if (p.hasAttribute && p.hasAttribute('data-lh')) return false;
                            if (p.querySelector && p.querySelector('img.flag')) return false;
                            p = p.previousElementSibling;
                        }
                        n = n.parentElement;
                    }

                    return false;
                }

                const teams = getTeams(card);
                const ev = teams[0];
                const dep = teams[1];
                const header = findHeader(card);
                const saat = findTime(card, ev, dep);

                return {
                    ev: ev,
                    dep: dep,
                    saat: saat,
                    lig: header.lig || '',
                    gun: header.gun || '',
                    live: isLiveCard(card)
                };
            """, c)

            ev = (info.get("ev") or "").strip()
            dep = (info.get("dep") or "").strip()
            saat = (info.get("saat") or "").strip()
            lig = parse_league_text(info.get("lig") or "")
            gun = (info.get("gun") or "").strip()
            live = bool(info.get("live"))

            if not ev or not dep or ev == dep:
                continue

            if re.fullmatch(r"\d+", ev) or re.fullmatch(r"\d+", dep):
                continue

            # Canlı maçları alma
            if live or gun == "CANLI":
                continue

            # Saat yoksa alma. Canlı maçlarda zaten saat olmaz.
            # Sayfa saati 13:02 gibi yanlış saatleri de böyle azaltıyoruz.
            if not TIME_RE.match(saat):
                continue

            # Tarih, tıklanan sekmeden geliyor.
            # Header içindeki Bugün/Yarın bilgisine göre filtreleme yapma.
            m = {
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
                "kaynak": "iddaa.com"
            }

            k = (m["tarih"], m["ev_sahibi"], m["deplasman"])

            if k in seen:
                continue

            seen.add(k)
            out.append(m)

        except Exception:
            pass

    return out

# =========================
# DEEP HARVEST (BUGÜN + YARIN BUTONLARI)
# =========================
def gun_sec(driver, gun_adi):
    """
    Tarih filtresinde yalnızca istenen günü seçili bırakır.

    Bugün seçilecekse:
        - Yarın seçiliyse kapatır
        - Bugün seçili değilse açar

    Yarın seçilecekse:
        - Bugün seçiliyse kapatır
        - Yarın seçili değilse açar
    """
    try:
        print(f"      🔎 Yalnızca '{gun_adi}' seçilecek...")

        # Tarih menüsünü aç
        try:
            tarih_acildi = driver.execute_script("""
                const spans = Array.from(
                    document.querySelectorAll('span[data-selected="colorChange"], span')
                );

                const tarih = spans.find(el => {
                    const text = (el.textContent || '').trim();
                    return text === 'Tarih';
                });

                if (!tarih) return false;

                tarih.click();
                return true;
            """)

            if tarih_acildi:
                time.sleep(1)
        except Exception:
            pass

        diger_gun = "Yarın" if gun_adi == "Bugün" else "Bugün"

        def durum_oku(gun):
            return driver.execute_script("""
                const hedef = arguments[0];

                function text(el) {
                    return (el.textContent || '')
                        .replace(/\\s+/g, ' ')
                        .trim();
                }

                function labelBul() {
                    const labels = Array.from(document.querySelectorAll('label'));

                    return labels.find(label => {
                        if (label.closest('[data-lh]')) return false;

                        const items = Array.from(
                            label.querySelectorAll('i, span, em')
                        );

                        return (
                            text(label) === hedef ||
                            items.some(el => text(el) === hedef)
                        );
                    });
                }

                function seciliMi(label) {
                    if (!label) return false;

                    const input = label.querySelector(
                        'input[type="checkbox"], input[type="radio"]'
                    );

                    if (input && input.checked) {
                        return true;
                    }

                    const elements = [
                        label,
                        ...Array.from(label.querySelectorAll('*'))
                    ];

                    for (const el of elements) {
                        const ariaChecked = el.getAttribute('aria-checked');
                        const ariaSelected = el.getAttribute('aria-selected');
                        const dataState = el.getAttribute('data-state');
                        const dataChecked = el.getAttribute('data-checked');
                        const dataSelected = el.getAttribute('data-selected');

                        if (ariaChecked === 'true') return true;
                        if (ariaSelected === 'true') return true;
                        if (dataState === 'checked') return true;
                        if (dataChecked === 'true') return true;

                        if (
                            dataSelected &&
                            dataSelected !== 'false' &&
                            dataSelected !== 'colorChange'
                        ) {
                            return true;
                        }

                        const cls = String(el.className || '').toLowerCase();

                        if (
                            cls.includes('checked') ||
                            cls.includes('selected') ||
                            cls.includes('active')
                        ) {
                            return true;
                        }
                    }

                    /*
                    Özel checkbox yapılarında tik genellikle label içindeki
                    SVG veya check ikonuyla gösterilir.
                    */
                    const tik = label.querySelector(
                        'svg[data-checked="true"], ' +
                        '[data-state="checked"], ' +
                        '[aria-checked="true"], ' +
                        'svg[class*="check"], ' +
                        '[class*="checkmark"]'
                    );

                    return Boolean(tik);
                }

                const label = labelBul();

                return {
                    bulundu: Boolean(label),
                    secili: seciliMi(label),
                    text: label ? text(label) : '',
                    html: label ? label.outerHTML.slice(0, 1000) : ''
                };
            """, gun)

        def tikla(gun):
            return driver.execute_script("""
                const hedef = arguments[0];

                function text(el) {
                    return (el.textContent || '')
                        .replace(/\\s+/g, ' ')
                        .trim();
                }

                const labels = Array.from(document.querySelectorAll('label'));

                const label = labels.find(el => {
                    if (el.closest('[data-lh]')) return false;

                    const items = Array.from(
                        el.querySelectorAll('i, span, em')
                    );

                    return (
                        text(el) === hedef ||
                        items.some(item => text(item) === hedef)
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
            """, gun)

        # Önce diğer günü kapat
        diger_durum = durum_oku(diger_gun)

        print(
            f"      🔎 {diger_gun}: "
            f"bulundu={diger_durum.get('bulundu')} "
            f"seçili={diger_durum.get('secili')}"
        )

        if diger_durum.get("bulundu") and diger_durum.get("secili"):
            print(f"      🔄 '{diger_gun}' seçimi kaldırılıyor...")

            if tikla(diger_gun):
                time.sleep(2)
            else:
                print(f"      ⚠️ '{diger_gun}' kapatılamadı")

        # Hedef günün güncel durumunu oku
        hedef_durum = durum_oku(gun_adi)

        print(
            f"      🔎 {gun_adi}: "
            f"bulundu={hedef_durum.get('bulundu')} "
            f"seçili={hedef_durum.get('secili')}"
        )

        if not hedef_durum.get("bulundu"):
            print(f"      ❌ '{gun_adi}' label bulunamadı")
            return False

        # Hedef seçili değilse aç
        if not hedef_durum.get("secili"):
            print(f"      🔄 '{gun_adi}' seçiliyor...")

            if not tikla(gun_adi):
                print(f"      ❌ '{gun_adi}' tıklanamadı")
                return False

            time.sleep(3)
        else:
            print(f"      ℹ️ '{gun_adi}' zaten seçili")

        # Son durumları kontrol et
        hedef_son = durum_oku(gun_adi)
        diger_son = durum_oku(diger_gun)

        print(
            f"      ✅ Son durum | "
            f"{gun_adi}: {hedef_son.get('secili')} | "
            f"{diger_gun}: {diger_son.get('secili')}"
        )

        # Bazı özel tasarımlarda seçili durumu okunamayabilir.
        # Tıklama başarılıysa devam et.
        if diger_son.get("secili"):
            print(
                f"      ⚠️ '{diger_gun}' hâlâ seçili görünüyor. "
                f"Bir kez daha kapatılıyor..."
            )
            tikla(diger_gun)
            time.sleep(2)

        return True

    except Exception as e:
        print(f"      ⚠️ gun_sec hata: {str(e)[:200]}")
        return False

def sayfayi_scroll_et(driver, hedef_tarih, max_step=MAX_SCROLL_STEPS):
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
            k = (m["tarih"], m["ev_sahibi"], m["deplasman"])
            if k not in seen:
                seen.add(k)
                maclar.append(m)

        if len(maclar) > last_total:
            print(f"      📈 Step {step}: +{len(maclar) - last_total} maç | Toplam {len(maclar)}")
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

        if gun_adi == "Yarın":
            print("      🔄 Bugün filtresi kapatılıp Yarın seçilecek...")

            try:
                driver.execute_script("""
                    function text(el) {
                        return (el.textContent || '')
                            .replace(/\\s+/g, ' ')
                            .trim();
                    }

                    const label = Array.from(
                        document.querySelectorAll('label')
                    ).find(el => {
                        if (el.closest('[data-lh]')) return false;

                        return Array.from(
                            el.querySelectorAll('i, span, em')
                        ).some(item => text(item) === 'Bugün');
                    });

                    if (label) {
                        label.click();
                        return true;
                    }

                    return false;
                """)
                time.sleep(2)
            except Exception:
                pass

        tiklandi = gun_sec(driver, gun_adi)

        if not tiklandi:
            print(f"      ❌ '{gun_adi}' butonu bulunamadı")
            continue

        time.sleep(8)

        try:
            reset_scroll_top(driver)
            time.sleep(1)
        except Exception:
            pass

        print(f"      ✅ '{gun_adi}' seçildi")

        try:
            ilk_kart = len(find_match_cards(driver))
            print(f"      🔎 Seçim sonrası görünen kart: {ilk_kart}")
        except Exception:
            pass

        maclar = sayfayi_scroll_et(driver, gun_tarih)

        for m in maclar:
            k = (m["tarih"], m["ev_sahibi"], m["deplasman"])

            if k not in hset:
                hset.add(k)
                harvest.append(m)

        bugun_adet = sum(1 for h in harvest if h["tarih"] == bugun)
        yarin_adet = sum(1 for h in harvest if h["tarih"] == yarin)

        print(
            f"      📊 {len(maclar)} maç çekildi | "
            f"Toplam: {len(harvest)} "
            f"(Bugün:{bugun_adet} Yarın:{yarin_adet})"
        )

    bugun_adet = sum(1 for m in harvest if m["tarih"] == bugun)
    yarin_adet = sum(1 for m in harvest if m["tarih"] == yarin)

    print(
        f"\n   🎯 Toplam: {len(harvest)} maç "
        f"(Bugün: {bugun_adet}, Yarın: {yarin_adet})"
    )

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
        for c in find_match_cards(driver):
            t = c.text
            if ev in t and dep in t:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", c
                )
                ActionChains(driver).move_to_element(c).pause(0.2).click().perform()
                return True

        clear_and_type(inp, dep[:22])
        time.sleep(0.8)
        for c in find_match_cards(driver):
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
        for c in find_match_cards(driver):
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
# JSON KAYDET (AKILLI BİRLEŞTİRME)
# =========================
def mac_json_kaydet(yeni_maclar):
    data = {"version": 2, "updated": "", "matches": []}
    
    # 1. Önce mevcut dosyayı oku (Eski maçların silinmesini önler)
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

    # Var olan maçları sözlüğe aktar
    var = {key(m): m for m in data.get("matches", [])}

    # 2. Yeni maçları mevcutlarla akıllıca birleştir
    for m in yeni_maclar:
        k = key(m)
        if k in var:
            eski = var[k]
            
            # Lig bilgisi boş veya "Bilinmeyen Lig" geldiyse eskini koru
            yeni_lig = m.get("lig", "").strip()
            eski_lig = eski.get("lig", "").strip()
            if (not yeni_lig or yeni_lig == "Bilinmeyen Lig") and eski_lig and eski_lig != "Bilinmeyen Lig":
                m["lig"] = eski_lig
                
            # Oranlar boş geldiyse ve eskide oran varsa eskini koru
            if not m.get("oranlar") and eski.get("oranlar"):
                m["oranlar"] = eski["oranlar"]
                
        var[k] = m

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

        driver, ok = guvenli_yukle(driver, URL)

        if not ok:
            print("❌ İlk yükleme başarısız")
            return

        if not wait_initial(driver):
            print("❌ İçerik yüklenemedi")
            return

        print("\n⬇️ Maçlar ve ligler çekiliyor...")
        harvested = deep_harvest(driver)
        toplam = len(harvested)
        print(f"\n📋 {toplam} maç bulundu")

        print("\n🔽 Oranlar alınıyor...")
        for idx, m in enumerate(harvested[:MAX_SCRAPE], 1):
            print(
                f"[{idx}/{toplam}] {m['tarih']} {m['saat']} | ({m['lig']}) | "
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

                driver, ok = guvenli_yukle(driver, URL)

                if not ok:
                    print("   ❌ Sayfa yüklenemedi")
                    time.sleep(5)
                    try:
                        driver.get(URL)
                        time.sleep(10)
                    except Exception:
                        pass

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

        input("Çıkmak için Enter tuşuna basın...")

if __name__ == "__main__":
    main()