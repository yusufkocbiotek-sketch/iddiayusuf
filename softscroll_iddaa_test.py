import json
import time
import random
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


# =======================
# AYARLAR
# =======================
URL = "https://www.iddaa.com/program/futbol"

USE_ULTRASURF_PROXY = False
ULTRASURF_PROXY = "http://127.0.0.1:9666"

# Senin mevcut DOM’unda çalışan match card selector
MATCH_CARD_SEL = ".i_tnw__t8AmC"

# Team span (title’dan okunur) — senin attığın HTML’e göre
TEAM_SPAN_SEL = "span[title][class*='i_tn__']"

TARGET_MATCHES = 30      # 20-30 için 30 iyi
MAX_SCROLL_STEPS = 2     # 1-2 scroll testi
SCROLL_PX = 1100
WAIT_AFTER_SCROLL = (1.4, 2.4)

OUTPUT = Path("softscroll_matches.json")


def build_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")

    # Çok agresif olmayan standart ayarlar
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if USE_ULTRASURF_PROXY:
        options.add_argument(f"--proxy-server={ULTRASURF_PROXY}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver


def wait_initial(driver, timeout=35):
    """İlk maç elementleri gelene kadar bekle."""
    start = time.time()
    last_cards = 0
    last_spans = 0

    while time.time() - start < timeout:
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL)
            spans = driver.find_elements(By.CSS_SELECTOR, TEAM_SPAN_SEL)
            last_cards = len(cards)
            last_spans = len(spans)

            if last_cards > 0 or last_spans >= 2:
                return last_cards, last_spans
        except Exception:
            pass
        time.sleep(1)

    return last_cards, last_spans


def init_scroll_target(driver):
    """İç scroll container varsa yakala (yoksa window)."""
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


def count_visible_matches(driver):
    """Maç sayısını öncelikle card sayısından, yoksa span/2’den tahmin eder."""
    cards = driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL)
    if len(cards) > 0:
        return len(cards)

    spans = driver.find_elements(By.CSS_SELECTOR, TEAM_SPAN_SEL)
    return len(spans) // 2


def extract_matches(driver, limit=60):
    """
    Önce card içinden 2 adet team span yakalamaya çalışır.
    Olmazsa global span’ları ikili eşler.
    """
    out = []
    seen = set()

    cards = driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL)
    if cards:
        for c in cards[:limit]:
            try:
                spans = c.find_elements(By.CSS_SELECTOR, TEAM_SPAN_SEL)
                if len(spans) >= 2:
                    ev = (spans[0].get_attribute("title") or spans[0].text or "").strip()
                    dep = (spans[1].get_attribute("title") or spans[1].text or "").strip()
                else:
                    # fallback: card text’inden iki satır
                    lines = [x.strip() for x in (c.text or "").split("\n") if x.strip() and x.strip() != "-"]
                    if len(lines) < 2:
                        continue
                    ev, dep = lines[0], lines[1]

                if not ev or not dep or ev == dep:
                    continue
                key = (ev, dep)
                if key in seen:
                    continue
                seen.add(key)
                out.append({"ev": ev, "dep": dep})
            except Exception:
                continue
        return out

    # card yoksa global span pairing
    spans = driver.find_elements(By.CSS_SELECTOR, TEAM_SPAN_SEL)
    titles = [(s.get_attribute("title") or s.text or "").strip() for s in spans]
    titles = [t for t in titles if t]

    for i in range(0, min(len(titles), limit * 2) - 1, 2):
        ev, dep = titles[i], titles[i + 1]
        if ev and dep and ev != dep:
            key = (ev, dep)
            if key in seen:
                continue
            seen.add(key)
            out.append({"ev": ev, "dep": dep})

    return out


def main():
    driver = None
    try:
        print("=" * 70)
        print("IDDAA SOFT-SCROLL TEST SCRAPER (1-2 scroll ile 20-30 maç hedefi)")
        print("=" * 70)

        driver = build_driver()
        print("✅ Chrome açıldı")

        print(f"📡 Açılıyor: {URL}")
        driver.get(URL)

        cards0, spans0 = wait_initial(driver)
        print(f"✅ İlk yük -> card: {cards0}, team-span: {spans0}, tahmini maç: {count_visible_matches(driver)}")

        init_scroll_target(driver)

        before = count_visible_matches(driver)

        for step in range(1, MAX_SCROLL_STEPS + 1):
            if before >= TARGET_MATCHES:
                break

            scroll_step(driver, SCROLL_PX)
            time.sleep(random.uniform(*WAIT_AFTER_SCROLL))

            after = count_visible_matches(driver)
            print(f"   ⬇️ Scroll {step}/{MAX_SCROLL_STEPS}: {before} -> {after}")

            if after <= before:
                # artmıyorsa çok zorlamayalım
                break

            before = after

        matches = extract_matches(driver, limit=80)
        print(f"\n📋 Çıkarılan maç: {len(matches)}")
        for i, m in enumerate(matches[:40], 1):
            print(f"  {i:02d}. {m['ev']} - {m['dep']}")
        if len(matches) > 40:
            print(f"  ... (+{len(matches)-40})")

        OUTPUT.write_text(json.dumps({
            "url": URL,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "visible_match_count": count_visible_matches(driver),
            "matches": matches
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"\n💾 Yazıldı: {OUTPUT.resolve()}")

    except Exception as e:
        print("❌ HATA:", e)
        traceback_path = Path("softscroll_error_page.html")
        try:
            traceback_path.write_text(driver.page_source, encoding="utf-8")
            print("🧾 Debug HTML:", traceback_path.resolve())
        except Exception:
            pass
    finally:
        if driver:
            try:
                driver.quit()
            except WebDriverException:
                pass


if __name__ == "__main__":
    main()