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


# =========================
# AYARLAR
# =========================
URL_BASE = "https://www.nesine.com/iddaa"
CIKTI_DOSYA = "public/data/mac.json"

MAX_SCROLL_STEPS = 300
STABLE_LIMIT = 18
SCROLL_PX = 600
SCROLL_SLEEP_RANGE = (1.1, 2.0)

MAX_SCRAPE = 9999
SLEEP_BETWEEN_MATCHES = (1.1, 2.4)
HARVEST_MAC_SAYISI = 50

SEARCH_SEL = 'input[data-test-id="srch-box"]'
PANEL_BTN_SEL = 'div[data-test-id="date-league-btn-title"]'
EXPAND_SEL = "span.f17af500409a2f819a68"

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")
ODD_RE = re.compile(r"^\d{1,3}([.,]\d{1,2})$")

SILINECEK_BASLANGICLAR = (
    "oyuncu", "100.00", "takım",
    "karşılaşma özel bahisleri", "kaleci kurtarışı"
)

MENU_KELIMELER = {
    "bülten", "bulten", "canlı", "canli", "canlı sonuçlar",
    "sonuçlar", "kuponum", "kuponlarım", "spor toto",
    "yardım", "giriş", "üye ol", "uye ol", "nesine",
    "futbol", "basketbol", "tenis", "voleybol",
    "hentbol", "buz hokeyi", "amerikan futbolu",
    "e-futbol", "mma", "tümü", "yükle", "yukle",
    "bugün", "bugun", "yarın", "yarin",
}


# =========================
# TARİH
# =========================
def bugunun_tarihi():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def yarinin_tarihi():
    return (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")


def nesine_dt_url(tarih_iso):
    """
    2026-09-08 -> https://www.nesine.com/iddaa?et=1&le=2&dt=08.09.2026
    et=1: futbol | le=2: site standart filtre parametreleri
    """
    try:
        t = datetime.datetime.strptime(tarih_iso, "%Y-%m-%d")
        return f"{URL_BASE}?et=1&le=2&dt={t.strftime('%d.%m.%Y')}"
    except Exception:
        return f"{URL_BASE}?et=1&le=2"


def url_tarih_uyuyor_mu(url, tarih_iso):
    """
    URL içinde dt=GG.AA.YYYY bizim tarihimiz mi kontrol eder.
    """
    try:
        t = datetime.datetime.strptime(tarih_iso, "%Y-%m-%d")
        hedef = t.strftime("%d.%m.%Y")
        return f"dt={hedef}" in (url or "")
    except Exception:
        return False


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


def cookie_kabul_et(driver):
    try:
        driver.execute_script("""
            const texts = [
                'Kabul Et', 'Tümünü Kabul Et', 'Çerezleri Kabul Et',
                'Tamam', 'Accept', 'Accept All', 'Anladım'
            ];
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


def reklam_kapat(driver):
    """
    Açılış reklamı / tam sayfa popup kapatıcı.
    """
    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.5)
    except Exception:
        pass

    try:
        driver.execute_script("""
            const seciciler = [
                "button[class*='close' i]",
                "[class*='close' i][role='button']",
                "[class*='kapat' i]",
                "[aria-label*='close' i]",
                "[aria-label*='kapat' i]",
                "[title*='kapat' i]",
                "[title*='close' i]",
                ".quiz-banner-close",
                "[class*='banner-close' i]",
                "[class*='popup-close' i]",
                "[id*='close-btn' i]",
                "[id*='kapat' i]"
            ];

            function gorunur(el){
                const r = el.getBoundingClientRect();
                const s = getComputedStyle(el);
                return r.width > 0 && r.height > 0 &&
                       s.display !== 'none' && s.visibility !== 'hidden';
            }

            for (const sel of seciciler) {
                const els = document.querySelectorAll(sel);
                for (const el of els) {
                    if (gorunur(el)) {
                        try { el.click(); } catch(e) {}
                    }
                }
            }

            const tekli = Array.from(document.querySelectorAll(
                'button, span, div, a, i, svg'
            )).filter(el => {
                if (!gorunur(el)) return false;
                const r = el.getBoundingClientRect();
                if (r.width > 80 || r.height > 80) return false;

                const t = (el.innerText || el.textContent || '').trim();
                const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                const title = (el.getAttribute('title') || '').toLowerCase();

                return (
                    ['×', '✕', 'x', 'X', '⨯'].includes(t) ||
                    aria.includes('kapat') || aria.includes('close') ||
                    title.includes('kapat') || title.includes('close')
                );
            });

            for (const el of tekli) {
                try { el.click(); } catch(e) {}
            }

            const vw = window.innerWidth, vh = window.innerHeight;

            const overlays = Array.from(document.querySelectorAll('div, section, aside'))
                .filter(el => {
                    const s = getComputedStyle(el);
                    if (!['fixed', 'absolute'].includes(s.position)) return false;

                    const r = el.getBoundingClientRect();
                    if (r.width < vw * 0.6 || r.height < vh * 0.6) return false;

                    const z = parseInt(s.zIndex) || 0;
                    return z >= 50 || s.zIndex === 'auto';
                });

            for (const ov of overlays) {
                const closers = Array.from(ov.querySelectorAll(
                    "button, [class*='close' i], [aria-label*='close' i], [aria-label*='kapat' i]"
                )).filter(gorunur);

                let basildi = false;
                for (const c of closers) {
                    const t = (c.innerText || '').trim();
                    const aria = (c.getAttribute('aria-label') || '').toLowerCase();
                    if (['×','✕','x','X'].includes(t) ||
                        aria.includes('close') || aria.includes('kapat') ||
                        (c.className || '').toString().toLowerCase().includes('close')) {
                        try { c.click(); basildi = true; break; } catch(e) {}
                    }
                }

                if (!basildi) {
                    try { ov.remove(); } catch(e) {}
                }
            }
        """)
        time.sleep(0.8)
    except Exception:
        pass


def find_match_cards(driver):
    """
    Nesine maç satırlarını bulur.
    Her satırda span[data-testid^="time-"] (maç saati) vardır.
    """
    try:
        rows = driver.execute_script("""
            function visible(el) {
                if (!el) return false;
                const r = el.getBoundingClientRect();
                const s = getComputedStyle(el);
                return r.width > 100 &&
                       r.height > 10 &&
                       r.height < 400 &&
                       s.display !== 'none' &&
                       s.visibility !== 'hidden' &&
                       Number(s.opacity || 1) > 0;
            }

            const timeEls = Array.from(
                document.querySelectorAll('span[data-testid^="time-"]')
            );

            let candidates = [];

            for (const t of timeEls) {
                let n = t;

                for (let i = 0; i < 10 && n; i++) {
                    const txt = (n.innerText || '').trim();

                    if (
                        visible(n) &&
                        txt.length > 30 &&
                        txt.length < 2000 &&
                        txt.includes('-')
                    ) {
                        candidates.push(n);
                        break;
                    }

                    n = n.parentElement;
                }
            }

            candidates = [...new Set(candidates)];

            candidates = candidates.filter(el => {
                return !candidates.some(other => other !== el && el.contains(other));
            });

            return candidates.slice(0, 1000);
        """)

        return rows or []

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
        driver.save_screenshot("debug_nesine.png")
        print("      📸 Screenshot kaydedildi: debug_nesine.png")
    except Exception:
        pass


def sayfa_saglikli_mi(driver):
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text.strip()
        body_lower = body_text.lower()

        hata_metinleri = (
            "hay aksi", "aw, snap", "aw snap",
            "sayfa yanıt vermiyor", "page unresponsive",
            "out of memory", "status_access_violation",
        )

        if len(body_text) < 50:
            print("      ⚠️ Sayfa boş/beyaz")
            return False

        if any(h in body_lower for h in hata_metinleri):
            print("      ⚠️ Chrome 'Hay aksi' veya çökme sayfası gösteriyor")
            return False

        return True

    except Exception as e:
        print(f"      ⚠️ Sayfa sağlık kontrolü başarısız: {str(e)[:100]}")
        return False


def arama_var_mi(driver):
    try:
        el = driver.find_element(By.CSS_SELECTOR, SEARCH_SEL)
        return el.is_displayed()
    except Exception:
        return False


def satir_sayisi_bekle(driver, max_sure=20):
    """
    Maç satırları yüklenene kadar polling yapar.
    """
    t0 = time.time()
    satir = 0

    while time.time() - t0 < max_sure:
        try:
            satir = len(find_match_cards(driver))
        except Exception:
            satir = 0

        if satir > 0:
            break

        time.sleep(1.5)

    return satir


def guvenli_yukle(driver, url, max_deneme=3):
    for deneme in range(max_deneme):
        try:
            print(f"      🌐 Sayfa yükleniyor... deneme {deneme + 1}/{max_deneme}")

            driver.set_page_load_timeout(60)
            driver.get(url)

            time.sleep(6)

            cookie_kabul_et(driver)
            reklam_kapat(driver)
            time.sleep(1)
            reklam_kapat(driver)

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

            print(f"      🔎 Body uzunluk: {len(body_text)} | Satır: {kart_sayisi}")

            if len(body_text) < 50:
                raise Exception("Sayfa boş/beyaz")

            if kart_sayisi > 0:
                print("      ✅ Sayfa yüklendi")
                return driver, True

            kart_sayisi = satir_sayisi_bekle(driver, 15)
            print(f"      🔎 Bekleme sonrası Satır: {kart_sayisi}")

            if kart_sayisi > 0:
                print("      ✅ Sayfa yüklendi")
                return driver, True

            print("      ⚠️ Maç satırı bulunamadı ama sayfa açık. Devam deneniyor...")
            debug_sayfa(driver)
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


def chrome_yeniden_baslat(driver, url=URL_BASE):
    try:
        driver.quit()
    except Exception:
        pass

    print("   🔴 Chrome kapatıldı")
    time.sleep(5)

    son_hata = None

    for deneme in range(1, 4):
        yeni_driver = None
        try:
            print(f"   🟢 Chrome yeniden açılıyor ({deneme}/3)...")
            yeni_driver = build_driver()

            yeni_driver, ok = guvenli_yukle(yeni_driver, url)

            if ok and sayfa_saglikli_mi(yeni_driver):
                print("   ✅ Yeni Chrome hazır")
                return yeni_driver

            try:
                yeni_driver.quit()
            except Exception:
                pass

            son_hata = "Sayfa sağlıklı yüklenmedi"

        except Exception as e:
            son_hata = e
            print(f"   ⚠️ Chrome yeniden başlatma hatası: {str(e)[:120]}")

            try:
                if yeni_driver:
                    yeni_driver.quit()
            except Exception:
                pass

        time.sleep(5)

    raise RuntimeError(f"Chrome yeniden başlatılamadı: {son_hata}")


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
        window.scrollBy({top: px, left: 0, behavior: 'smooth'});
      }
    """, px)


# =========================
# SATIR OKUMA (TAKIM / LİG / SAAT)
# =========================
def extract_visible(driver, current_date):
    out = []
    seen = set()

    rows = find_match_cards(driver)

    for r in rows:
        try:
            info = driver.execute_script("""
                const row = arguments[0];

                function isJunkLine(t) {
                    if (!t) return true;
                    if (/^\\d+([.,]\\d+)?$/.test(t)) return true;
                    if (/^\\d{1,2}:\\d{2}$/.test(t)) return true;
                    if (/^\\d{3,5}$/.test(t)) return true;

                    const junk = [
                        'ms', '1x2', 'alt', 'üst', 'ust', 'var', 'yok',
                        'iy', 'mbs', 'kod', 'canlı', 'canli',
                        'maç sonucu', 'mac sonucu', 'alt/üst',
                        'ilk yarı', 'karşılıklı gol', 'karsilikli gol',
                        'bugün', 'bugun', 'yarın', 'yarin'
                    ];

                    const n = t.toLowerCase();
                    if (junk.includes(n)) return true;
                    if (n.length > 60) return true;

                    return false;
                }

                function getTeams(row) {
                    const lines = (row.innerText || '')
                        .split('\\n')
                        .map(x => x.trim())
                        .filter(Boolean);

                    for (const l of lines) {
                        if (l.includes(' - ') && l.length < 90) {
                            const parts = l.split(' - ');
                            if (parts.length >= 2) {
                                const a = parts[0].trim();
                                const b = parts.slice(1).join(' - ').trim();
                                if (a && b && !isJunkLine(a) && !isJunkLine(b)) {
                                    return [a, b];
                                }
                            }
                        }
                    }

                    const cand = [];

                    for (const l of lines) {
                        if (isJunkLine(l)) continue;
                        if (!/[A-Za-zÇĞİÖŞÜçğıöşü]{3,}/.test(l)) continue;
                        if (!cand.includes(l)) cand.push(l);
                        if (cand.length >= 2) break;
                    }

                    if (cand.length >= 2) {
                        return [cand[0], cand[1]];
                    }

                    return ['', ''];
                }

                function getTime(row) {
                    const t = row.querySelector('span[data-testid^="time-"]');
                    if (!t) return '';

                    const dtid = t.getAttribute('data-testid') || '';

                    if (dtid.startsWith('time-')) {
                        return dtid.replace('time-', '').trim();
                    }

                    return (t.innerText || '').trim();
                }

                function cleanLeague(t) {
                    return (t || '')
                        .replace('Bugün', '')
                        .replace('Yarın', '')
                        .replace('Today', '')
                        .replace('Tomorrow', '')
                        .trim();
                }

                function findLeague(row) {
                    function oddCount(t){
                        return ((t || '').match(/\\d{1,3}[.,]\\d{2}/g) || []).length;
                    }

                    function visible(el){
                        const r = el.getBoundingClientRect();
                        const s = getComputedStyle(el);
                        return r.width > 0 && r.height > 0 &&
                               s.display !== 'none' && s.visibility !== 'hidden';
                    }

                    let n = row;

                    for (let i = 0; i < 10 && n; i++) {
                        let p = n.previousElementSibling;
                        let adim = 0;

                        while (p && adim < 15) {
                            adim++;

                            if (visible(p)) {
                                const txt = p.innerText || '';

                                if (txt.includes('CANLI')) {
                                    return 'CANLI';
                                }

                                // Genişlemiş oran panelini LİG SANMA
                                if (oddCount(txt) >= 3) {
                                    p = p.previousElementSibling;
                                    continue;
                                }

                                let strong = null;
                                if (p.tagName === 'STRONG') strong = p;
                                else if (p.querySelector) strong = p.querySelector('strong');

                                if (strong) {
                                    const lt = cleanLeague(strong.innerText || '');

                                    // "Takım A - Takım B" kalıbını lig sanma
                                    if (lt && lt.length <= 60 &&
                                        !lt.includes(' - ') && oddCount(lt) === 0) {
                                        return lt;
                                    }
                                }
                            }

                            p = p.previousElementSibling;
                        }

                        n = n.parentElement;
                    }

                    return '';
                }

                const teams = getTeams(row);

                return {
                    ev: teams[0],
                    dep: teams[1],
                    saat: getTime(row),
                    lig: findLeague(row)
                };
            """, r)

            ev = (info.get("ev") or "").strip()
            dep = (info.get("dep") or "").strip()
            saat = (info.get("saat") or "").strip()
            lig = (info.get("lig") or "").strip()

            if not ev or not dep or ev == dep:
                continue

            if re.fullmatch(r"\d+", ev) or re.fullmatch(r"\d+", dep):
                continue

            if lig == "CANLI":
                continue

            if not TIME_RE.match(saat):
                continue

            if len(ev) > 70 or len(dep) > 70:
                continue

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
                "kaynak": "nesine.com"
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
# TARİH SEÇİMİ (BUGÜN / YARIN)
# =========================
def gun_sec(driver, gun_adi, tarih_iso):
    """
    1) 'Tarih ve Lig Seçimi' paneline GERÇEK tıklama ile açar
    2) Bugün/Yarın seçeneğine GERÇEK tıklama yapar
    3) 'Filtrele' butonuna basar
    4) URL'de dt= parametresi oluşmadıysa direkt URL'ine gider
    """
    print(f"      🔎 '{gun_adi}' seçiliyor...")

    # ---------- A) PANEL YÖNTEMİ ----------
    try:
        try:
            btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, PANEL_BTN_SEL)
                )
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", btn
            )
            time.sleep(0.5)
            ActionChains(driver).move_to_element(btn).pause(0.3).click().perform()
            time.sleep(2)
            print("      ✅ 'Tarih ve Lig Seçimi' paneli açıldı")
        except Exception as e:
            print(f"      ⚠️ Panel butonu tıklanamadı: {str(e)[:80]}")

        secildi = False
        try:
            adaylar = driver.find_elements(
                By.XPATH, f"//p[normalize-space(text())='{gun_adi}']"
            )
            for el in adaylar:
                try:
                    if not el.is_displayed():
                        continue
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});", el
                    )
                    time.sleep(0.4)
                    ActionChains(driver).move_to_element(el).pause(0.2).click().perform()
                    secildi = True
                    print(f"      ✅ '{gun_adi}' işaretlendi")
                    break
                except Exception:
                    continue
        except Exception:
            pass

        if not secildi:
            print(f"      ⚠️ '{gun_adi}' seçeneği panelde bulunamadı")

        time.sleep(1)

        try:
            f_adaylar = driver.find_elements(
                By.XPATH, "//button[normalize-space()='Filtrele']"
            )
            basildi = False
            for f in f_adaylar:
                try:
                    if not f.is_displayed():
                        continue
                    ActionChains(driver).move_to_element(f).pause(0.2).click().perform()
                    basildi = True
                    break
                except Exception:
                    continue

            if basildi:
                print("      ✅ 'Filtrele' tıklandı")
            else:
                print("      ⚠️ 'Filtrele' butonu görünür değil")
        except Exception as e:
            print(f"      ⚠️ Filtrele tıklanamadı: {str(e)[:80]}")

        time.sleep(5)

        if url_tarih_uyuyor_mu(driver.current_url, tarih_iso):
            satir = len(find_match_cards(driver))
            print(f"      ✅ Panel filtresi uygulandı | Satır: {satir}")
            if satir > 0:
                return True
        else:
            print(f"      ⚠️ URL değişmedi: {driver.current_url}")

    except Exception as e:
        print(f"      ⚠️ Panel yöntemi hata: {str(e)[:120]}")

    # ---------- B) URL YÖNTEMİ (GARANTİLİ) ----------
    try:
        url = nesine_dt_url(tarih_iso)
        print(f"      🔁 Doğrudan URL ile gidiliyor: {url}")

        driver.get(url)
        time.sleep(6)
        cookie_kabul_et(driver)
        reklam_kapat(driver)

        satir = satir_sayisi_bekle(driver, 20)
        print(f"      🔎 URL sonrası satır: {satir}")

        if satir > 0:
            print(f"      ✅ '{gun_adi}' URL ile yüklendi")
            return True

    except Exception as e:
        print(f"      ⚠️ URL yöntemi hata: {str(e)[:120]}")

    print(f"      ❌ '{gun_adi}' seçilemedi")
    return False


# =========================
# DEEP HARVEST
# =========================
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

        if step % 5 == 0:
            try:
                bt = driver.find_element(By.TAG_NAME, "body").text.strip()
                if len(bt) < 200:
                    print("      ⚠️ Scroll sırasında sayfa beyazladı, durduluyor")
                    break
            except Exception:
                print("      ⚠️ Scroll sırasında sayfa yanıt vermiyor, durduluyor")
                break

    return maclar


def deep_harvest(driver):
    bugun = bugunun_tarihi()
    yarin = yarinin_tarihi()
    print(f"   🎯 Bugün: {bugun} | Yarın: {yarin}")

    harvest = []
    hset = set()

    for gun_tarih, gun_adi in [(bugun, "Bugün"), (yarin, "Yarın")]:
        print(f"\n   📅 {gun_adi} ({gun_tarih}) seçiliyor...")

        tiklandi = gun_sec(driver, gun_adi, gun_tarih)

        if not tiklandi:
            print(f"      ❌ '{gun_adi}' seçilemedi")
            continue

        time.sleep(3)

        try:
            reset_scroll_top(driver)
            time.sleep(1)
        except Exception:
            pass

        print(f"      ✅ '{gun_adi}' seçildi")

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
def arama_kutusunu_temizle(driver):
    try:
        inp = driver.find_element(By.CSS_SELECTOR, SEARCH_SEL)
        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)
        time.sleep(0.5)
    except Exception:
        pass


def arama_yap(driver, text):
    try:
        inp = driver.find_element(By.CSS_SELECTOR, SEARCH_SEL)
        inp.click()
        time.sleep(0.3)
        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)
        time.sleep(0.5)
        inp.send_keys(text)
        time.sleep(2.5)
        return True
    except Exception:
        return False


def satir_bul(driver, ev, dep):
    ev_kisa = ev[:20]
    dep_kisa = dep[:20]

    for r in find_match_cards(driver):
        try:
            t = r.text or ""
            if ev_kisa in t and dep_kisa in t:
                return r
        except Exception:
            pass

    return None


def nokta_var_mi(t):
    try:
        v = float(str(t).replace(",", "."))
        return 1.01 <= v <= 999.99
    except Exception:
        return False


def oran_satiri_mi(t):
    return bool(ODD_RE.match(t.strip()))


def market_gecerli_mi(t):
    n = t.strip().lower()

    if not n or len(n) > 60:
        return False

    if n in MENU_KELIMELER:
        return False

    if oran_satiri_mi(n):
        return False

    if TIME_RE.match(t.strip()):
        return False

    if re.fullmatch(r"\d{3,5}", t.strip()):
        return False

    return True


def nesine_oran_parse(text):
    """
    Satır bazlı oran parse:
    - Oran satırının bir üstü etiket
    - Etiketi olmayan başlıklar market olur
    - "1 2.10" gibi aynı satırda label+oran desteği
    """
    oranlar = {}
    atlanan = 0

    lines = [
        x.strip() for x in str(text).split("\n")
        if x.strip()
    ]

    market = ""
    i = 0

    while i < len(lines):
        line = lines[i]
        nxt = lines[i + 1] if i + 1 < len(lines) else ""

        # "1 2.10" gibi aynı satırda label+oran kalıbı
        tek = re.match(r"^(\D{1,30}?)\s+(\d{1,3}[.,]\d{2})$", line)
        if tek:
            lab = tek.group(1).strip()
            val = float(tek.group(2).replace(",", "."))
            if lab and 1.01 <= val <= 999:
                full_key = f"{market}_{lab}" if market else lab
                kk = full_key.strip().lower()
                if kk.startswith(SILINECEK_BASLANGICLAR):
                    atlanan += 1
                else:
                    oranlar[full_key] = val
            i += 1
            continue

        if oran_satiri_mi(line):
            i += 1
            continue

        if nxt and oran_satiri_mi(nxt):
            label = line

            if label and not oran_satiri_mi(label):
                full_key = f"{market}_{label}" if market else label
                k = full_key.strip().lower()

                if k.startswith(SILINECEK_BASLANGICLAR):
                    atlanan += 1
                else:
                    try:
                        oranlar[full_key] = float(nxt.replace(",", "."))
                    except Exception:
                        pass

            i += 2
        else:
            if market_gecerli_mi(line):
                market = line
            else:
                market = ""

            i += 1

    if atlanan > 0:
        print(f"   🚫 {atlanan} gereksiz oran filtrelendi")

    return oranlar


# =========================
# ORAN ANAHTARI STANDARTLASTIRMA
# =========================
def tr_key(s):
    s = str(s or "")
    s = (s.replace("İ", "i").replace("I", "i").replace("ı", "i")
          .replace("Ş", "s").replace("ş", "s")
          .replace("Ğ", "g").replace("ğ", "g")
          .replace("Ü", "u").replace("ü", "u")
          .replace("Ö", "o").replace("ö", "o")
          .replace("Ç", "c").replace("ç", "c"))
    s = s.lower()
    return re.sub(r"\s+", " ", s).strip()


def market_duzelt(m):
    """
    tr_key ile normalize edilmiş market adını dashboard formatına çevirir.
    """
    m = re.sub(r"\s+", " ", m).strip(" _-")
    m = re.sub(r"(\d),(\d)", r"\1.\2", m)

    yari1 = ("ilk yari" in m) or ("1. yari" in m) or (m == "iy") or m.startswith("iy ")
    yari2 = "2. yari" in m
    yari_on = "1. Yarı " if yari1 else ("2. Yarı " if yari2 else "")

    if re.fullmatch(r"(mac sonucu|ms|1x2)", m):
        return "Maç Sonucu"

    hm = re.search(r"handikap\w*\s*(?:mac sonucu\s*)?(\d+:\d+)", m)
    if hm:
        return f"Handikaplı Maç Sonucu {hm.group(1)}"
    if "handikap" in m:
        return "Handikaplı Maç Sonucu"

    if yari1 and ("mac sonucu" in m or m.endswith("/ms") or "iy/ms" in m):
        return "1. Yarı / Maç Sonucu"

    if yari1 and "sonuc" in m:
        return "1. Yarı Sonucu"
    if yari2 and "sonuc" in m:
        return "2. Yarı Sonucu"

    if "cifte sans" in m:
        return f"{yari_on}Çifte Şans"

    if "karsilikli gol" in m or m == "kg":
        return f"{yari_on}Karşılıklı Gol"

    if re.search(r"alt/?ust|alt ust", m):
        num = ""
        nm = re.search(r"(\d+(?:\.\d+)?)", m)
        if nm:
            num = nm.group(1)
        who = ""
        if "ev sahibi" in m:
            who = "Ev Sahibi "
        elif "deplasman" in m:
            who = "Deplasman "
        return f"{yari_on}{who}Alt/Üst {num}".strip()

    if "toplam gol" in m:
        return "Toplam Gol"

    if "mac skoru" in m:
        return "Maç Skoru"

    if "tek/cift" in m or "tek cift" in m:
        korner = "Korner " if "korner" in m else ""
        return f"{yari_on}{korner}Tek / Çift".strip()

    return m


def label_duzelt(l, market):
    l = str(l).strip()
    low = tr_key(l)

    genel = {
        "x": "0", "beraberlik": "0",
        "alt": "Alt", "ust": "Üst",
        "var": "Var", "yok": "Yok",
        "evet": "Evet", "hayir": "Hayır",
        "esit": "Eşit",
        "tek": "Tek", "cift": "Çift",
        "gol olmaz": "Gol Olmaz", "gol yok": "Gol Olmaz",
        "olmaz": "Olmaz",
    }
    if low in genel:
        return genel[low]

    if "Çifte Şans" in market:
        cs = low.replace(" ", "")
        csmap = {
            "1x": "1 ve 0", "10": "1 ve 0",
            "12": "1 ve 2",
            "x2": "0 ve 2", "02": "0 ve 2",
        }
        if cs in csmap:
            return csmap[cs]

    if market == "1. Yarı / Maç Sonucu":
        parts = l.split("/")
        return "/".join(
            "0" if p.strip().lower() in ("x",) else p.strip()
            for p in parts
        )

    if "daha fazla gol" in market.lower() or "daha cok" in market.lower():
        if low in ("1", "1."):
            return "1."
        if low in ("2", "2."):
            return "2."

    return l


def oranlari_standartlastir(oranlar):
    if not isinstance(oranlar, dict):
        return oranlar

    out = {}

    for k, v in oranlar.items():
        nk = tr_key(k)

        if "_" in nk:
            market_raw, label_raw = nk.split("_", 1)
        else:
            bulundu = False
            for src in ("mac sonucu", "cifte sans", "karsilikli gol"):
                if nk.startswith(src + " "):
                    market_raw = src
                    label_raw = nk[len(src):].strip(" _-")
                    bulundu = True
                    break
            if not bulundu:
                market_raw, label_raw = nk, ""

        market = market_duzelt(market_raw) if market_raw else ""

        lab = label_raw
        if not market and lab in ("1", "0", "2", "x"):
            market = "Maç Sonucu"

        lab = label_duzelt(lab, market) if lab else ""

        yeni = f"{market}_{lab}" if market else lab
        if yeni:
            out[yeni] = v

    return out


# =========================
# PANEL / GENİŞLETME
# =========================
def panel_elementi_bul(driver, row):
    """
    Satırın kardeşleri arasında genişlemiş oran panelini bulur.
    """
    try:
        return driver.execute_script("""
            const row = arguments[0];

            function oddCount(t){
                return ((t || '').match(/\\d{1,3}[.,]\\d{2}/g) || []).length;
            }

            let s = row.nextElementSibling;
            let best = null, bestCount = 0;

            for (let i = 0; i < 4 && s; i++) {
                const c = oddCount(s.innerText || '');
                if (c > bestCount) { bestCount = c; best = s; }
                s = s.nextElementSibling;
            }

            return bestCount >= 3 ? best : null;
        """, row)
    except Exception:
        return None


def genislet_dogrula(driver, ev, dep, deneme=3):
    """
    Satırı her denemede taze bulur, genişletir, panel açıldığını doğrular.
    Döndürür: (row, panel) veya (None, None)
    """
    for _ in range(deneme):
        row = satir_bul(driver, ev, dep)
        if row is None:
            time.sleep(1)
            continue

        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", row
            )
            time.sleep(0.4)
        except Exception:
            pass

        tiklandi = False
        try:
            for tg in row.find_elements(By.CSS_SELECTOR, EXPAND_SEL):
                try:
                    tg.click()
                    tiklandi = True
                    break
                except Exception:
                    pass
        except Exception:
            pass

        if not tiklandi:
            try:
                tiklandi = driver.execute_script("""
                    const row = arguments[0];

                    let el = row.querySelector('span.f17af500409a2f819a68');

                    if (!el) {
                        const spans = Array.from(row.querySelectorAll('span'));
                        el = spans.find(s =>
                            !(s.innerText || '').trim() &&
                            s.offsetWidth < 40 && s.offsetWidth > 0
                        );
                    }

                    if (el) { el.click(); return true; }
                    return false;
                """, row)
            except Exception:
                tiklandi = False

        for _ in range(8):
            time.sleep(0.5)
            row2 = satir_bul(driver, ev, dep)
            if row2 is not None:
                panel = panel_elementi_bul(driver, row2)
                if panel is not None:
                    return row2, panel

    return None, None


def kapat_dogrula(driver, ev, dep, deneme=3):
    """
    Açık paneli kapatır ve kapandığını doğrular.
    """
    for _ in range(deneme):
        row = satir_bul(driver, ev, dep)
        if row is None:
            return

        if panel_elementi_bul(driver, row) is None:
            return

        try:
            for tg in row.find_elements(By.CSS_SELECTOR, EXPAND_SEL):
                try:
                    tg.click()
                    break
                except Exception:
                    pass
        except Exception:
            pass

        time.sleep(0.8)


def panel_oranlari_cek(driver, panel, max_sure=10):
    """
    Sadece panel elementinin metnini parse eder.
    Oran sayısı 2 ölçüm sabit kalınca durur.
    """
    son = {}
    ayni = 0
    t0 = time.time()

    while time.time() - t0 < max_sure:
        time.sleep(1.0)

        try:
            txt = panel.text or ""
        except Exception:
            break

        o = nesine_oran_parse(txt)

        if len(o) == len(son):
            ayni += 1
            if ayni >= 2:
                break
        else:
            ayni = 0
            if len(o) > len(son):
                son = o

    return son


def mac_oranlari_cek(driver, m):
    ev = m["ev_sahibi"]
    dep = m["deplasman"]

    row = None

    if arama_yap(driver, ev[:24]):
        row = satir_bul(driver, ev, dep)

    if row is None and arama_yap(driver, dep[:24]):
        row = satir_bul(driver, ev, dep)

    if row is None:
        arama_kutusunu_temizle(driver)
        return None

    oranlar = {}

    try:
        row, panel = genislet_dogrula(driver, ev, dep)

        if panel is not None:
            oranlar = panel_oranlari_cek(driver, panel)
        else:
            print("   ⚠️ Panel açılamadı")

        kapat_dogrula(driver, ev, dep)

    except Exception as e:
        print(f"   ⚠️ Oran hatası: {str(e)[:60]}")

    arama_kutusunu_temizle(driver)
    return oranlari_standartlastir(oranlar)


# =========================
# JSON KAYDET (DASHBOARD UYUMLU + AKILLI BİRLEŞTİRME)
# =========================
def mac_json_kaydet(yeni_maclar):
    data = {"matches": [], "son_guncelleme": ""}

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

    var = {key(m): m for m in data.get("matches", [])}

    for m in yeni_maclar:
        m["oranlar"] = oranlari_standartlastir(m.get("oranlar"))

        k = key(m)
        if k in var:
            eski = var[k]

            yeni_lig = m.get("lig", "").strip()
            eski_lig = eski.get("lig", "").strip()
            if (not yeni_lig or yeni_lig == "Bilinmeyen Lig") and eski_lig and eski_lig != "Bilinmeyen Lig":
                m["lig"] = eski_lig

            if not m.get("oranlar") and eski.get("oranlar"):
                m["oranlar"] = eski["oranlar"]

        var[k] = m

    simdi = datetime.datetime.now().isoformat()

    temiz = []
    sirali = sorted(
        var.values(),
        key=lambda x: (x.get("tarih", ""), x.get("saat", "00:00"))
    )

    for idx, mac in enumerate(sirali, 1):
        try:
            skor_ev = int(mac.get("skor_ev", 0) or 0)
        except Exception:
            skor_ev = 0

        try:
            skor_dep = int(mac.get("skor_dep", 0) or 0)
        except Exception:
            skor_dep = 0

        try:
            skor_1y_ev = int(mac.get("skor_1y_ev", 0) or 0)
        except Exception:
            skor_1y_ev = 0

        try:
            skor_1y_dep = int(mac.get("skor_1y_dep", 0) or 0)
        except Exception:
            skor_1y_dep = 0

        temiz.append({
            "index": idx,
            "mac_kodu": str(mac.get("mac_kodu", "")),
            "ev_sahibi": str(mac.get("ev_sahibi", "")).strip(),
            "deplasman": str(mac.get("deplasman", "")).strip(),
            "saat": str(mac.get("saat", "")),
            "lig": str(mac.get("lig", "")),
            "tarih": str(mac.get("tarih", "")),
            "cekme_zamani": str(mac.get("cekme_zamani", simdi)),
            "durum": str(mac.get("durum", "baslamadi")),
            "skor_ev": skor_ev,
            "skor_dep": skor_dep,
            "skor_1y_ev": skor_1y_ev,
            "skor_1y_dep": skor_1y_dep,
            "kaynak": str(mac.get("kaynak", "nesine.com")),
            "oranlar": mac.get("oranlar", {})
        })

    cikti = {"matches": temiz, "son_guncelleme": simdi}

    os.makedirs(os.path.dirname(CIKTI_DOSYA), exist_ok=True)

    path = Path(CIKTI_DOSYA)
    temp_path = path.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cikti, f, ensure_ascii=False, indent=2)
    temp_path.replace(path)

    print(f"   💾 Kaydedildi: {len(temiz)} maç | {CIKTI_DOSYA}")


# =========================
# MAIN
# =========================
def main():
    print("=" * 70)
    print("⚽ NESINE SCRAPER")
    print("📅", datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
    print("=" * 70)

    driver = None
    results = []
    success = fail = 0
    islenen = 0

    try:
        print("\n🟢 Chrome açılıyor...")
        driver = build_driver()

        driver, ok = guvenli_yukle(driver, URL_BASE)
        if not ok:
            print("❌ İlk yükleme başarısız")
            return

        print("\n⬇️ Maçlar ve ligler çekiliyor...")
        harvested = deep_harvest(driver)

        toplam = len(harvested)
        print(f"\n📋 {toplam} maç bulundu")

        if toplam == 0:
            print("❌ Maç bulunamadı")
            return

        gunlere_gore = {}
        for m in harvested[:MAX_SCRAPE]:
            gunlere_gore.setdefault(m["tarih"], []).append(m)

        print("\n🔽 Oranlar alınıyor...")

        for tarih_iso in sorted(gunlere_gore.keys()):
            gun_maclar = gunlere_gore[tarih_iso]
            url_gun = nesine_dt_url(tarih_iso)

            try:
                driver.get(url_gun)
                time.sleep(5)
                cookie_kabul_et(driver)
                reklam_kapat(driver)
                satir_sayisi_bekle(driver, 15)
            except Exception as e:
                print(f"   ⚠️ Gün sayfası açılamadı ({tarih_iso}): {str(e)[:80]}")

            for m in gun_maclar:
                islenen += 1

                print(
                    f"[{islenen}] {m['tarih']} {m['saat']} | ({m.get('lig', '')}) | "
                    f"{m['ev_sahibi']} - {m['deplasman']}"
                )

                # --- Her 50 maçta Chrome'u tamamen yenile ---
                if islenen > 1 and (islenen - 1) % HARVEST_MAC_SAYISI == 0:
                    print("\n" + "=" * 60)
                    print(f"🔄 {islenen - 1} maç işlendi. Chrome yeniden başlatılıyor...")
                    print("=" * 60)

                    mac_json_kaydet(results)

                    try:
                        driver = chrome_yeniden_baslat(driver, url_gun)
                    except Exception as e:
                        print(f"   ❌ Chrome yeniden başlatılamadı: {e}")
                        break

                # --- Sayfa sağlıklı mı? ---
                if not sayfa_saglikli_mi(driver) or not arama_var_mi(driver):
                    print("   ⚠️ Sayfa sağlıklı değil, gün sayfası yeniden açılıyor...")

                    try:
                        driver.get(url_gun)
                        time.sleep(5)
                        cookie_kabul_et(driver)
                        reklam_kapat(driver)
                        satir_sayisi_bekle(driver, 15)
                    except Exception:
                        pass

                    if not sayfa_saglikli_mi(driver) or not arama_var_mi(driver):
                        try:
                            driver = chrome_yeniden_baslat(driver, url_gun)
                        except Exception as e:
                            print(f"   ❌ Chrome yenilenemedi, maç atlanıyor: {e}")
                            fail += 1
                            continue

                # --- Oranları çek ---
                try:
                    oran = mac_oranlari_cek(driver, m)

                    if oran is None:
                        print("   ❌ Bulunamadı")
                        fail += 1
                        continue

                    m["oranlar"] = oran
                    print(f"   ✅ {len(oran)} oran")

                except Exception as e:
                    print(f"   ⚠️ Oran hatası: {str(e)[:60]}")
                    m["oranlar"] = {}

                results.append(m)
                success += 1

                if success == 1:
                    try:
                        ornek = sorted(m.get("oranlar", {}).keys())[:30]
                        print("   🧪 Standart sonrası anahtarlar:", ornek)
                    except Exception:
                        pass

                if islenen % 10 == 0:
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