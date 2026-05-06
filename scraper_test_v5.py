import os
import re
import time
import random
import socket
import subprocess
from datetime import datetime

import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class V7Killer:
    def __init__(self):
        self.driver = None
        self.matches = []
        self.total_odds = 0
        self.success = 0
        self.fail = 0
        self.processed_count = 0  # dongu disinda kullanmak icin guvenli sayac
        self.ultrasurf_port = 9666
        # <- BURAYI GERCEK ULTRASURF EXE YOLUNLA DEGISTIR
        self.ultrasurf_path = r"C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main\u2211.exe"

    # ---------------- LOGGING ----------------
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    # ---------------- ULTRASURF ----------------
    def kill_ultrasurf(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = (proc.info.get('name') or '').lower()
                if 'ultrasurf' in name:
                    self.log(f"Ultrasurf sonlandiriliyor (PID: {proc.info['pid']})")
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def is_proxy_port_open(self, host="127.0.0.1", port=9666, timeout=1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                res = sock.connect_ex((host, port))
                return res == 0
        except Exception:
            return False

    def start_ultrasurf(self):
        self.kill_ultrasurf()
        self.log("ULTRASURF PROXY BASLATILIYOR")

        if not os.path.exists(self.ultrasurf_path):
            self.log(f"HATA: Ultrasurf bulunamadi: {self.ultrasurf_path}")
            return False

        try:
            # shell=True KULLANMA
            subprocess.Popen([self.ultrasurf_path])
        except Exception as e:
            self.log(f"HATA: Ultrasurf baslatilamadi: {e}")
            return False

        # Proxy portunu bekle
        self.log("Proxy portu bekleniyor (35 saniye)")
        for _ in range(35):
            if self.is_proxy_port_open("127.0.0.1", self.ultrasurf_port, 1):
                self.log("ULTRASURF PROXY HAZIR")
                time.sleep(3)
                return True
            time.sleep(1)

        self.log("UYARI: Proxy portu acilmadi")
        return False

    # ---------------- SELENIUM ----------------
    def stealth_chrome_options(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-extensions")
        options.add_argument("--mute-audio")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1366,768")
        options.add_argument(f"--proxy-server=http://127.0.0.1:{self.ultrasurf_port}")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        )
        return options

    def init_driver(self):
        options = self.stealth_chrome_options()
        self.driver = webdriver.Chrome(options=options)
        # WebDriver gizleme
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
                    Object.defineProperty(navigator, 'languages', { get: () => ['tr-TR','tr','en-US','en'] });
                """
            },
        )
        return self.driver

    def quit_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    # ---------------- DAVRANIS (GUVENLI) ----------------
    def human_like(self, driver):
        """Guvenli, bot-tespitini azaltan hafif hareketler."""
        try:
            actions = ActionChains(driver)
            # Sayfada gorunen bazi elementlerin uzerine hafifce git
            selectors = ["a", "button", "nav a", "header a", ".match-item", ".event-row", ".fixture__teams"]
            for sel in selectors:
                elems = driver.find_elements(By.CSS_SELECTOR, sel)
                if elems:
                    el = random.choice(elems)
                    # Scroll into view + move to element (viewport icinde kalir)
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    time.sleep(0.25)
                    actions.move_to_element(el).pause(random.uniform(0.2, 0.6)).perform()
                    break
            # Kucuk klavye hareketi
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.TAB)
            time.sleep(0.15)
            body.send_keys(Keys.SHIFT + Keys.TAB)
        except Exception:
            pass

    def controlled_scroll(self, driver):
        """Kontrollu, viewport disina cikmayan scroll."""
        for _ in range(4):
            try:
                # viewport yuksekligine gore makul bir deger
                vh = driver.execute_script("return window.innerHeight;") or 768
                delta = random.randint(int(vh * 0.25), int(vh * 0.6))
                direction = random.choice([-1, 1])
                driver.execute_script(f"window.scrollBy(0, {direction * delta});")
                time.sleep(random.uniform(0.6, 1.1))
            except Exception:
                pass

    # ---------------- SITE / MAC LISTESI ----------------
    def load_all_matches(self):
        self.log("IDDAA PROGRAM/FUTBOL SAYFASI YUKLENIYOR")
        self.init_driver()

        try:
            # Sayfayi ac
            self.driver.get("https://www.iddaa.com/program/futbol")
            # Temel container'in yuklenmesini bekle (siteye gore en saglamini bulmak icin birkac alternatif)
            wait_selectors = [
                ".match-item",
                ".event-row",
                ".fixture__teams",
                "a[href*='/mac']",
                ".program-list",
                "body"
            ]
            loaded = False
            for sel in wait_selectors:
                try:
                    WebDriverWait(self.driver, 12).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                    )
                    loaded = True
                    break
                except TimeoutException:
                    continue

            if not loaded:
                self.log("UYARI: Sayfa icerigi beklenenden erken geldi, yine de devam ediliyor")

            time.sleep(random.uniform(2.5, 4.5))
            self.human_like(self.driver)
            self.controlled_scroll(self.driver)

            # Maclari topla (genis selector seti)
            match_selectors = [
                "a[href*='/mac'] span",
                ".match-item .team-name",
                ".event-row .team",
                ".match-title",
                "[data-testid*='match'] span",
                ".fixture__teams span",
                ".match-card__team",
                "div[class*='match'] span[class*='team']",
                ".game-row .team",
                ".match-row .participant",
            ]

            self.matches = []
            seen = set()
            for sel in match_selectors:
                try:
                    elems = self.driver.find_elements(By.CSS_SELECTOR, sel)
                    for el in elems:
                        txt = el.text.strip()
                        if txt and len(txt) > 6:
                            low = txt.lower()
                            if ("vs" in low or " - " in low):
                                key = low
                                if key not in seen:
                                    seen.add(key)
                                    self.matches.append({"name": txt, "url": ""})
                except Exception:
                    continue

            self.log(f"TOPLAM {len(self.matches)} MAC BULUNDU")
            return len(self.matches) > 0

        except Exception as e:
            self.log(f"HATA: Mac listesi yuklenemedi: {e}")
            self.quit_driver()
            return False

    # ---------------- ANA AKIS ----------------
    def attack(self):
        print("V7 KILLER BASLATILIYOR...")
        self.log("V7 KILLER ATTACK!")

        # Ultrasurf baslat
        if not self.start_ultrasurf():
            self.log("KRITIK: Ultrasurf baslatilamadi")
            return

        # Mac listesini yukle
        if not self.load_all_matches():
            self.log("KRITIK: Mac listesi bos veya yuklenemedi")
            # Hala devam etmek istersen burada return yerine kisa bir uyari birakabilirsin
            # return

        # Hedef sayi (istege gore)
        target = min(60, len(self.matches)) if self.matches else 0
        self.log(f"HEDEF: {target} MAC")

        # Maclari isle
        for i, match in enumerate(self.matches[:target], 1):
            self.processed_count = i  # disarida kullanmak icin
            self.log(f"ISLENIYOR [{i}/{target}]: {match['name']}")

            # Burada normalde URL bulma + oran cekme olur
            # Simdilik sadece bekleme + basari/hatayi say
            time.sleep(random.uniform(2.5, 4.5))
            # Ornek: rastgele basari
            if random.random() > 0.25:
                odds_found = random.randint(10, 80)
                self.total_odds += odds_found
                self.success += 1
                self.log(f"BASARILI: {odds_found} oran")
            else:
                self.fail += 1
                self.log("BASARISIZ: Oran bulunamadi")

            # Ara rapor
            if i % 5 == 0:
                self.log(
                    f"RAPOR: Toplam Oran={self.total_odds} | "
                    f"Basarili={self.success} | Basarisiz={self.fail}"
                )

            # Kisa bekleme
            time.sleep(random.uniform(25, 40))

        # SONUC (artik 'i' yerine self.processed_count kullaniliyor)
        self.log(
            f"GOREV TAMAMLANDI: Toplam Oran={self.total_odds} | "
            f"Basarili={self.success} | Islenen={self.processed_count}"
        )
        self.quit_driver()


if __name__ == "__main__":
    killer = V7Killer()
    killer.attack()