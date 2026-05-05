import time
import random
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

class IddaaScraperV7NoProxy:
    def __init__(self):
        self.matches = []
        self.total_odds = 0
        self.success_count = 0
        self.fail_count = 0
        self.driver = None
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def stealth_chrome(self):
        """NO PROXY - DIRECT STEALTH"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # ULTRA STEALTH V7
        options.add_argument("--disable-features=VizDisplayCompositor,NetworkServiceInProcess")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        options.add_argument("--window-size=1366,768")
        options.add_argument("--start-maximized")
        
        return options
        
    def human_mouse(self, driver):
        """İnsan mouse hareketi"""
        actions = ActionChains(driver)
        moves = [(200,150), (300,250), (-100,100), (150,-50)]
        for x, y in moves:
            actions.move_by_offset(x, y).pause(random.uniform(0.4, 1.2)).perform()
            
    def smart_scroll(self, driver):
        """Akıllı scroll"""
        scrolls = [350, 500, -200, 400, 300]
        for scroll in scrolls:
            driver.execute_script(f"window.scrollBy(0,{scroll});")
            time.sleep(random.uniform(1.5, 2.5))
            
    def load_matches_direct(self):
        """Direkt maç yükle"""
        self.log("🔥 DIRECT MODE - PROXY YOK")
        options = self.stealth_chrome()
        self.driver = webdriver.Chrome(options=options)
        
        # STEALTH INJECTION
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
                Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR','tr']});
                window.chrome = {runtime: {}};
            '''
        })
        
        self.driver.get("https://www.iddaa.com/program/futbol")
        time.sleep(12)
        
        self.human_mouse(self.driver)
        self.smart_scroll(self.driver)
        
        # 25+ MATCH SELECTOR
        match_selectors = [
            "a[href*='/maç'] span",
            ".match-item .team-name",
            ".event-row .team",
            ".match-title span",
            "[data-testid*='match'] span",
            ".fixture__teams span",
            ".match-card span",
            ".game-row .participant",
            ".match-row .team"
        ]
        
        self.matches = []
        for selector in match_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    text = el.text.strip()
                    if (len(text) > 10 and 
                        any(sep in text.lower() for sep in ['vs', ' - ', ' @ ']) and
                        text not in [m['name'] for m in self.matches]):
                        
                        self.matches.append({'name': text[:60]})
            except:
                continue
        
        self.log(f"✅ {len(self.matches)} MAÇ HAZIR!")
        return len(self.matches) > 0
        
    def direct_match_search(self, match_name):
        """Direkt arama"""
        # URL tahminleri
        team1 = match_name.split('vs')[0].strip()[:15].replace(' ', '-').lower()
        search_urls = [
            f"https://www.iddaa.com/program/futbol?q={team1.replace('-', '%20')}",
            "https://www.iddaa.com/program/futbol"
        ]
        
        for url in search_urls:
            try:
                self.driver.get(url)
                time.sleep(4)
                self.human_mouse(self.driver)
                
                # Link bul
                links = self.driver.find_elements(By.CSS_SELECTOR, 
                    "a[href*='/maç'], a[href*='match']")
                
                for link in links[:5]:
                    href = link.get_attribute('href')
                    if href and '/maç' in href and len(href) > 40:
                        return href
            except:
                continue
        return None
        
    def mega_odds_extract(self, url):
        """MEGA oran çekme"""
        try:
            self.driver.get(url)
            time.sleep(8)
            self.human_mouse(self.driver)
            self.smart_scroll(self.driver)
            
            all_odds = []
            
            # 18 SELECTOR KÜMESİ
            selectors = [
                ".odds", ".koef", ".ratio", ".price", ".bet-odds",
                ".odds-value", ".market span", ".coefficient",
                "[data-odds]", "[class*='odds']", "[class*='koef']",
                ".bet-value", ".odds-number", ".market__odds"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for el in elements:
                        text = el.text.strip()
                        if self.is_odds(text):
                            all_odds.append(float(text))
                except:
                    pass
            
            # REGEX ULTIMATE
            source = self.driver.page_source
            patterns = [r'\b\d+\.\d{2}\b', r'data-odds="([\d.]+)"']
            for pattern in patterns:
                matches = re.findall(pattern, source)
                for match in matches:
                    try:
                        num = float(match)
                        if 1.01 < num < 20:
                            all_odds.append(num)
                    except:
                        pass
            
            unique_odds = len(set([round(o, 2) for o in all_odds]))
            
            if unique_odds > 5:
                self.log(f"✅ MEGA: {unique_odds} ORAN")
                self.total_odds += unique_odds
                self.success_count += 1
                return True
            else:
                self.log(f"⚠️ {unique_odds} oran")
                return False
                
        except Exception as e:
            self.log(f"❌ {str(e)[:30]}")
            return False
            
    def is_odds(self, text):
        try:
            num = float(text)
            return 1.01 < num < 20
        except:
            return False
            
    def run_direct(self):
        self.log("🎯 NO PROXY DIRECT MODE")
        
        if not self.load_matches_direct():
            self.log("❌ Maç yüklenemedi")
            return
            
        # 50 MAÇ SINIRI (TEST)
        for i, match in enumerate(self.matches[:50], 1):
            self.log(f"\n[{i}/50] {match['name']}")
            
            url = self.direct_match_search(match['name'])
            if url:
                success = self.mega_odds_extract(url)
                if success:
                    self.success_count += 1
                else:
                    self.fail_count += 1
            else:
                self.fail_count += 1
                
            # Rate limit
            wait = random.randint(40, 60)
            self.log(f"⏳ {wait}s")
            time.sleep(wait)
            
            if i % 10 == 0:
                self.log(f"📊 {self.total_odds} ORAN | ✅{self.success_count} ❌{self.fail_count}")
        
        self.log(f"\n🎉 DIRECT MODE BİTTİ!")
        self.log(f"📈 TOPLAM: {self.total_odds} ORAN")

if __name__ == "__main__":
    scraper = IddaaScraperV7NoProxy()
    scraper.run_direct()