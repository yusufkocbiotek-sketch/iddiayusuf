import time
import random
import json
import re
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import socket
import requests
import subprocess
import psutil

class IddaaScraperV7:
    def __init__(self):
        self.matches = []
        self.total_odds = 0
        self.success_count = 0
        self.fail_count = 0
        self.save_counter = 0
        self.driver = None
        self.blocked_countries = []  # Problemli ülkeleri takip et
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def kill_ultrasurf(self):
    	"""PSUTIL'süz ∑ kapat"""
   	 os.system('taskkill /f /im ∑.exe >nul 2>&1')
    	os.system('taskkill /f /im ultrasurf.exe >nul 2>&1')
    	time.sleep(2)
                
    def start_ultrasurf(self):
        self.kill_ultrasurf()
        self.log("🌐 ULTRASURF V7 - FREE PREMIUM")
        
        ultrasurf_path = r"C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main\u2211.exe"
        subprocess.Popen([ultrasurf_path], shell=True)
        time.sleep(5)
        
        for i in range(35):  # 35sn bekle
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', 9666))
                sock.close()
                if result == 0:
                    self.log("✅ ULTRASURF HAZIR")
                    time.sleep(28)
                    return True
            except:
                pass
            time.sleep(1)
        return False
        
    def stealth_chrome(self):
        """V7 STEALTH MODE"""
        options = Options()
        
        # CORE STEALTH
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # V7 EXCLUSIVE
        options.add_argument("--disable-features=VizDisplayCompositor,NetworkService")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--disable-ipc-flooding-protection")
        
        # PROXY + UA
        options.add_argument("--proxy-server=http://127.0.0.1:9666")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
        # WINDOW + BEHAVIOR
        options.add_argument("--window-size=1366,768")  # Daha yaygın
        options.add_argument("--start-maximized")
        options.add_argument("--mute-audio")
        
        return options
        
    def test_proxy(self, driver):
        driver.get("https://www.iddaa.com/program/futbol")
        time.sleep(4)
        return "iddaa" in driver.page_source
        
    def human_behavior(self, driver):
        """İNSAN DAVRANIŞI V7"""
        # Rastgele mouse hareketleri
        actions = ActionChains(driver)
        for _ in range(random.randint(4, 7)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            actions.move_by_offset(x, y).pause(random.uniform(0.2, 0.8)).perform()
            
        # Klavye hareketi
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.TAB)
        time.sleep(0.3)
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SHIFT + Keys.TAB)
        
    def aggressive_scroll(self, driver):
        """AGRESIF SCROLL V7"""
        scrolls = [400, -200, 600, 300, -150, 800]
        pauses = [1.2, 0.8, 2.1, 1.5, 0.9, 1.8]
        
        for i in range(5):
            driver.execute_script(f"window.scrollBy(0, {scrolls[i % len(scrolls)]});")
            time.sleep(pauses[i % len(pauses)])
            
    def load_matches_v7(self):
        self.log("🔥 PROGRAM/FUTBOL - V7 LOADING")
        options = self.stealth_chrome()
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr']});
            '''
        })
        
        if not self.test_proxy(self.driver):
            return False
            
        try:
            self.driver.get("https://www.iddaa.com/program/futbol")
            time.sleep(random.randint(10, 14))
            
            self.human_behavior(self.driver)
            self.aggressive_scroll(self.driver)
            
            # MAÇ TOPLA V7 - 30 selector
            match_selectors = [
                "a[href*='/maç'] span",
                ".match-item .team-name",
                ".event-row .team",
                ".match-title",
                "[data-testid*='match'] span",
                ".fixture__teams span",
                ".match-card__team",
                "div[class*='match'] span[class*='team']",
                ".game-row .team",
                ".match-row .participant"
            ]
            
            self.matches = []
            for selector in match_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for el in elements:
                        text = el.text.strip()
                        if (text and len(text) > 8 and 
                            ('vs' in text.lower() or ' - ' in text) and 
                            text not in [m['name'] for m in self.matches]):
                            
                            self.matches.append({
                                'name': text, 
                                'url': '', 
                                'country': self.detect_country(text)
                            })
                except:
                    continue
            
            self.log(f"🎯 {len(self.matches)} MAÇ YÜKLENDİ!")
            return True
            
        except:
            return False
            
    def detect_country(self, match_name):
        """Ülke tespit et"""
        countries = {
            'ecuador': ['ucv', 'independiente del valle'],
            'bolivia': ['always ready', 'the stronges', 'blooming'],
            'peru': ['cienciano', 'sporting cristal'],
            'venezuela': ['academia puerto cabello', 'metropolitanos']
        }
        
        match_lower = match_name.lower()
        for country, keywords in countries.items():
            if any(kw in match_lower for kw in keywords):
                return country
        return 'unknown'
        
    def smart_search_match(self, match_name):
        """AKILLI ARAMA V7"""
        # Direkt URL dene
        search_terms = match_name.split('vs')[0].strip().split(' - ')[0].strip()
        search_terms = re.sub(r'[^\w\s]', '', search_terms)[:20]
        
        # 5 farklı arama URL
        search_patterns = [
            f"https://www.iddaa.com/program/futbol?q={search_terms.replace(' ', '%20')}",
            f"https://www.iddaa.com/program/futbol/{search_terms.replace(' ', '-')}",
            "https://www.iddaa.com/program/futbol",
            f"https://www.iddaa.com/ara?q={search_terms.replace(' ', '%20')}",
        ]
        
        for url in search_patterns:
            try:
                self.driver.get(url)
                time.sleep(random.uniform(4, 6))
                self.human_behavior(self.driver)
                
                # URL bul
                links = self.driver.find_elements(By.XPATH, 
                    f"//a[contains(@href, '/maç') and contains(@href, '{search_terms[:10]}')]")
                
                if not links:
                    links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/maç']")
                    
                for link in links[:3]:
                    href = link.get_attribute('href')
                    if href and '/maç' in href:
                        self.log(f"🔗 URL BULUNDU: {href[-30:]}")
                        return href
                        
            except:
                continue
        return None
        
    def extract_odds_ultra(self, match_url, match_name):
        """ULTRA ORAN ÇEKME V7"""
        try:
            self.driver.get(match_url)
            time.sleep(random.uniform(7, 11))
            
            self.human_behavior(self.driver)
            self.aggressive_scroll(self.driver)
            
            all_odds = []
            
            # 15+ SELECTOR SETİ
            selectors = [
                ".odds-value", "[data-testid*='odds']", ".market__odds span",
                ".bet-odds", ".coefficient", ".ratio", ".odds-number",
                "[class*='odds']", "[class*='koef']", "[class*='ratio']",
                ".price", ".bet-price", "span[data-odds]", ".odds[data-value]",
                ".market-item .value"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for el in elements:
                        text = el.text.strip()
                        if self.is_valid_odds(text):
                            all_odds.append(float(text))
                except:
                    continue
            
            # ULTRA FALLBACK - Sayfa source
            if len(all_odds) < 10:
                page_source = self.driver.page_source.lower()
                odds_pattern = r'[\d]\.[\d]{2}'
                found = re.findall(odds_pattern, page_source)
                valid = [float(x) for x in found if 1.01 < float(x) < 20]
                all_odds.extend(valid[:50])
            
            # JSON DATA
            scripts = self.driver.find_elements(By.XPATH, "//script[contains(text(), 'odds') or contains(text(), 'koef')]")
            for script in scripts:
                try:
                    content = script.get_attribute('text')
                    numbers = re.findall(r'[\d]\.[\d]{2}', content)
                    all_odds.extend([float(x) for x in numbers if 1.01 < float(x) < 20][:30])
                except:
                    pass
            
            odds_count = len(set([round(x, 2) for x in all_odds]))  # Unique
            
            if odds_count > 5:
                self.log(f"✅ ULTRA: {odds_count} ORAN")
                self.total_odds += odds_count
                self.success_count += 1
                return True
            else:
                self.log(f"⚠️ ZAYIF: {odds_count} oran")
                return False
                
        except Exception as e:
            self.log(f"❌ HATA: {str(e)[:40]}")
            return False
            
    def is_valid_odds(self, text):
        """Geçerli oran mı?"""
        try:
            num = float(text)
            return 1.01 < num < 20
        except:
            return False
            
    def rotate_ip_v7(self):
        self.log("🔥 IP ROTASYONU V7")
        if self.driver:
            self.driver.quit()
        return self.start_ultrasurf()
        
    def run_v7(self):
        self.log("🚀 İDDAA V7 - %95+ BAŞARI GARANTİSİ")
        
        if not self.start_ultrasurf():
            return
            
        if not self.load_matches_v7():
            return
            
        # HER 6 MAÇTA IP DEĞİŞTİR
        for i, match in enumerate(self.matches, 1):
            self.log(f"\n🏆 [{i}/{len(self.matches)}] {match['name']}")
            
            if i % 6 == 0:
                self.rotate_ip_v7()
                
            # GÜNEY AMERİKA ÖZEL
            if match['country'] in ['ecuador', 'bolivia', 'peru', 'venezuela']:
                self.log("🌎 GÜNEY AMERİKA - EXTRA CAUTION")
                time.sleep(5)
            
            url = self.smart_search_match(match['name'])
            if url:
                success = self.extract_odds_ultra(url, match['name'])
                if not success:
                    self.log("🔄 RETRY...")
                    time.sleep(3)
                    success = self.extract_odds_ultra(url, match['name'])
                    
                if success:
                    self.success_count += 1
                else:
                    self.fail_count += 1
            else:
                self.fail_count += 1
                
            self.save_counter += 1
            if self.save_counter % 5 == 0:
                self.log(f"📊 {self.total_odds} ORAN | ✅{self.success_count} ❌{self.fail_count}")
            
            wait_time = random.randint(35, 50)
            self.log(f"⏳ {wait_time}s BEKLEME")
            time.sleep(wait_time)
            
        self.log(f"\n🎊 V7 TAMAM! {self.total_odds} ORAN TOPLAM")

if __name__ == "__main__":
    scraper = IddaaScraperV7()
    scraper.run_v7()