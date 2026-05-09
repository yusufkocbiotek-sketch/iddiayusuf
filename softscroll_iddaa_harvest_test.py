import json
import time
import datetime
import random
import re
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


URL = "https://www.iddaa.com/program/futbol"

# Test hedefi
TARGET_UNIQUE = 30        # 20-30 için 30
MAX_SCROLL_STEPS = 6      # 1-2 istersen 2 yap; 30 için genelde 4-6 gerekir
SCROLL_PX = 1100
SLEEP_RANGE = (1.4, 2.4)

# Bu kadar maç açıp oran çekmeyi test et (0 yaparsan sadece liste toplar)
OPEN_FIRST_N = 3

# Selector'lar
MATCH_CARD_SEL = ".i_tnw__t8AmC"
TEAM_SPAN_SEL = "span[title][class*='i_tn__']"

OUTPUT = Path("softscroll_harvest.json")


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
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver


def wait_initial(driver, timeout=35):
    start = time.time()
    while time.time() - start < timeout:
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL)
            spans = driver.find_elements(By.CSS_SELECTOR, TEAM_SPAN_SEL)
            if len(cards) > 0 or len(spans) >= 2:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def init_scroll_target(driver):
    """İç container scroll varsa onu seçer; yoksa window."""
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


def extract_visible_matches(driver):
    """
    O an DOM'da görünen maçları çıkarır.
    Virtualize nedeniyle bu liste sürekli değişir, biz dışarıda set ile biriktireceğiz.
    """
    out = []
    seen = set()

    cards = driver.find_elements(By.CSS_SELECTOR, MATCH_CARD_SEL)
    for c in cards:
        try:
            spans = c.find_elements(By.CSS_SELECTOR, TEAM_SPAN_SEL)
            if len(spans) >= 2:
                ev = (spans[0].get_attribute("title") or spans[0].text or "").strip()
                dep = (spans[1].get_attribute("title") or spans[1].text or "").strip()
            else:
                # fallback: text
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


def xpath_literal(s: str) -> str:
    if "'" not in s:
        return f"'{s}'"
    if '"' not in s:
        return f'"{s}"'
    parts = s.split("'")
    return "concat(" + ", \"'\", ".join([f"'{p}'" for p in parts]) + ")"


def click_match(driver, ev: str, dep: str, max_find_scroll=8):
    """
    Sayfa virtualize ise maç ilk bakışta DOM'da olmayabilir.
    Bu fonksiyon sayfayı biraz scroll ederek maçı arar ve tıklar.
    """
    init_scroll_target(driver)

    x_ev = xpath_literal(ev)
    x_dep = xpath_literal(dep)

    # Öncelik: title span ile satır bul
    xp = f"//*[contains(@class,'i_tnw__')][.//span[@title={x_ev}] and .//span[@title={x_dep}]]"

    for _ in range(max_find_scroll):
        els = driver.find_elements(By.XPATH, xp)
        if els:
            el = els[0]
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                time.sleep(0.4)
                ActionChains(driver).move_to_element(el).pause(0.2).click().perform()
                return True
            except Exception:
                try:
                    driver.execute_script("arguments[0].click();", el)
                    return True
                except Exception:
                    pass

        scroll_step(driver, px=1200)
        time.sleep(1.0)

    return False


def wait_tumu(driver, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            txt = driver.find_element(By.TAG_NAME, "body").text
            if "Tümü" in txt:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def count_odds(body_text: str) -> int:
    # 1.23 gibi oranlar
    return len(re.findall(r"\b\d{1,2}[.,]\d{2}\b", body_text))


def main():
    driver = None
    harvested = []
    harvest_set = set()  # (ev, dep)

    try:
        print("=" * 70)
        print("IDDAA SOFT-SCROLL HARVEST TEST (unique biriktirerek 20-30 hedef)")
        print("=" * 70)

        driver = build_driver()
        print("✅ Chrome açıldı")

        print(f"📡 Açılıyor: {URL}")
        driver.get(URL)

        if not wait_initial(driver):
            print("❌ İlk içerik gelmedi (timeout).")
            return

        init_scroll_target(driver)

        # 0. adım: ilk görünenden ekle
        vis = extract_visible_matches(driver)
        for m in vis:
            k = (m["ev"], m["dep"])
            if k not in harvest_set:
                harvest_set.add(k)
                harvested.append(m)

        print(f"✅ İlk görünüm unique maç: {len(harvested)}")

        # scroll adımları: her adımda görünenleri set'e ekle
        for step in range(1, MAX_SCROLL_STEPS + 1):
            if len(harvested) >= TARGET_UNIQUE:
                break

            scroll_step(driver, SCROLL_PX)
            time.sleep(random.uniform(*SLEEP_RANGE))

            vis = extract_visible_matches(driver)
            before = len(harvested)
            for m in vis:
                k = (m["ev"], m["dep"])
                if k not in harvest_set:
                    harvest_set.add(k)
                    harvested.append(m)

            print(f"   ⬇️ Step {step}/{MAX_SCROLL_STEPS}: +{len(harvested)-before}  (toplam unique={len(harvested)})")

        # rapor
        print(f"\n📋 Toplam unique maç: {len(harvested)} (hedef {TARGET_UNIQUE})")
        for i, m in enumerate(harvested[:40], 1):
            print(f"  {i:02d}. {m['ev']} - {m['dep']}")
        if len(harvested) > 40:
            print(f"  ... (+{len(harvested)-40})")

        # İstersen ilk N maçı açıp oran testi
        opened = []
        if OPEN_FIRST_N > 0:
            print(f"\n🔎 İlk {OPEN_FIRST_N} maç için tıklama+oran testi:")
            for i, m in enumerate(harvested[:OPEN_FIRST_N], 1):
                ev, dep = m["ev"], m["dep"]
                print(f"   [{i}/{OPEN_FIRST_N}] {ev} vs {dep}")

                # sayfayı tazeleyip bulmak daha stabil
                driver.get(URL)
                time.sleep(4)

                ok = click_match(driver, ev, dep, max_find_scroll=18)
                if not ok:
                    print("      ❌ tıklanamadı")
                    opened.append({"ev": ev, "dep": dep, "clicked": False})
                    continue

                time.sleep(2.5)
                tumu = wait_tumu(driver, timeout=15)
                body = driver.find_element(By.TAG_NAME, "body").text
                odds = count_odds(body)
                print(f"      ✅ clicked | tumu={tumu} | odds_count={odds}")
                opened.append({"ev": ev, "dep": dep, "clicked": True, "tumu": tumu, "odds_count": odds})

        OUTPUT.write_text(json.dumps({
            "url": URL,
            "scraped_at": datetime.datetime.now().isoformat(),
            "target_unique": TARGET_UNIQUE,
            "max_scroll_steps": MAX_SCROLL_STEPS,
            "unique_count": len(harvested),
            "matches": harvested,
            "opened_test": opened,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"\n💾 Yazıldı: {OUTPUT.resolve()}")

    finally:
        if driver:
            try:
                driver.quit()
            except WebDriverException:
                pass


if __name__ == "__main__":
    main()