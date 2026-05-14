import time
import json
import shutil
import subprocess
import traceback
from datetime import date, timedelta, datetime
from pathlib import Path

time.sleep(2) 

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- YOLLAR ---
URL = "https://www.iddaa.com/canli-skor/futbol"
OUT_DIR = Path(r"C:\Users\YUSUF\OneDrive\Desktop\iddaa_scraper_output")
OUT_DIR.mkdir(exist_ok=True)

# GÜNCELLENECEK ANA DOSYA
MAC_JSON_PATH = Path(r"C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main\public\data\mac.json")

def build_driver():
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    d = webdriver.Chrome(options=opts) 
    d.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    d.set_page_load_timeout(60)
    return d

def dismiss_cookies(driver):
    for xp in ["//button[contains(.,'Kabul')]", "//button[contains(.,'Accept')]", "//button[@id='onetrust-accept-btn-handler']"]:
        try:
            for b in driver.find_elements(By.XPATH, xp):
                if b.is_displayed():
                    driver.execute_script("arguments[0].click();", b)
                    time.sleep(1)
                    return
        except: pass

def switch_to_iframe(driver):
    for iframe in driver.find_elements(By.TAG_NAME, "iframe"):
        try:
            driver.switch_to.frame(iframe)
            if driver.find_elements(By.XPATH, "//button[@aria-label='Takvim' or contains(@aria-label, 'Takvim')]"):
                return True
        except: pass
        driver.switch_to.default_content()
    return False

def select_date(driver, target_date_str):
    try:
        cal_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Takvim' or contains(@aria-label, 'Takvim')]"))
        )
        driver.execute_script("arguments[0].click();", cal_btn)
        time.sleep(1.5)
        
        try:
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
        except:
            driver.switch_to.default_content()
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))

        cells = driver.find_elements(By.CSS_SELECTOR, f"td[data-day='{target_date_str}']")
        month_clicks = 0
        
        while not cells and month_clicks < 2:
            prev_btns = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Previous') or @name='previous-month']")
            if prev_btns:
                driver.execute_script("arguments[0].click();", prev_btns[0])
                time.sleep(0.5)
                cells = driver.find_elements(By.CSS_SELECTOR, f"td[data-day='{target_date_str}']")
                month_clicks += 1
            else:
                break
                
        if cells:
            btns = cells[0].find_elements(By.TAG_NAME, "button")
            if btns:
                driver.execute_script("arguments[0].click();", btns[0])
            else:
                driver.execute_script("arguments[0].click();", cells[0])
            time.sleep(3)
            return True
    except Exception as e:
        print(f"⚠️ Tarih seçimi hatası ({target_date_str}): {e}")
    return False

def extract_matches_with_js(driver):
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    except: pass

    js_code = """
    let results = [];
    let currentLeague = "Bilinmeyen Lig";
    let processedRows = new Set();
    let elements = document.querySelectorAll('h3[data-testid="tournament-name-link"], .rounded-match__score');

    elements.forEach(el => {
        if (el.tagName === 'H3' && el.getAttribute('data-testid') === 'tournament-name-link') {
            let text = el.innerText || el.textContent || "";
            currentLeague = text.replace(/\\n/g, ' ').replace(/\\s+/g, ' ').trim().replace(/Favorilere ekle|MS|İY|arrow/gi, '').replace(/\\|$/, '').trim();
        } 
        else if (el.classList && el.classList.contains('rounded-match__score')) {
            let row = el.parentElement;
            for (let i = 0; i < 6; i++) {
                if (!row) break;
                let scores = row.querySelectorAll('.rounded-match__score');
                let truncates = Array.from(row.querySelectorAll('.truncate'))
                    .map(e => (e.innerText || e.textContent || "").trim())
                    .filter(t => t.length > 1 && !/Favorilere|arrow|MS|İY/i.test(t));
                
                if (scores.length >= 2 && truncates.length >= 2) {
                    if (!processedRows.has(row)) {
                        processedRows.add(row);
                        let text = row.innerText || row.textContent || "";
                        let statusRegex = /^(\\d{1,3}['’\\.]?|\\d{1,2}:\\d{2}|MS|IY|İY|Bitti|Canlı|Başlamadı|İlk Yarı|İkinci Yarı|ERT|TAT)$/i;
                        let status = text.split('\\n').map(l=>l.trim()).find(l => statusRegex.test(l)) || "?";

                        results.push({
                            league: currentLeague,
                            home: truncates[0],
                            away: truncates[1],
                            score: (scores[0].innerText || scores[0].textContent || "").trim() + "-" + (scores[1].innerText || scores[1].textContent || "").trim(),
                            status: status
                        });
                    }
                    break; 
                }
                row = row.parentElement;
            }
        }
    });
    return results;
    """
    
    try:
        return driver.execute_script(js_code) or []
    except Exception as e:
        return []

def update_mac_json_safely(scraped_matches):
    print(f"\n🔄 {MAC_JSON_PATH.name} dosyası GÜVENLİ şekilde güncelleniyor...")
    
    if not MAC_JSON_PATH.exists():
        print("⚠️ mac.json bulunamadı. İşlem iptal edildi.")
        return 0

    backup_path = MAC_JSON_PATH.with_name("mac_backup.json")
    shutil.copy2(MAC_JSON_PATH, backup_path)
    print(f"💾 Güvenlik yedeği alındı: {backup_path.name}")

    with open(MAC_JSON_PATH, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    def clean_name(name): return str(name).strip().lower()

    scraped_lookup = {}
    for m in scraped_matches:
        h = clean_name(m.get('home') or m.get('ev_sahibi'))
        a = clean_name(m.get('away') or m.get('deplasman'))
        if h and a and h != "?" and a != "?":
            key = f"{h}||{a}"
            scraped_lookup[key] = m

    updated_count = 0

def update_mac_json_safely(scraped_matches):
    print(f"\n🔄 {MAC_JSON_PATH.name} dosyası GÜVENLİ şekilde güncelleniyor...")
    
    if not MAC_JSON_PATH.exists():
        print("⚠️ mac.json bulunamadı. İşlem iptal edildi.")
        return 0

    # Yedek Al
    backup_path = MAC_JSON_PATH.with_name("mac_backup.json")
    shutil.copy2(MAC_JSON_PATH, backup_path)
    print(f"💾 Güvenlik yedeği alındı: {backup_path.name}")

    # Mevcut Veriyi Oku
    with open(MAC_JSON_PATH, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    # İsim Temizleme Fonksiyonu (Yerel tanımlama)
    def clean_name(name): 
        return str(name).strip().lower()

    # Eşleştirme Sözlüğü Oluştur
    scraped_lookup = {}
    for m in scraped_matches:
        h = clean_name(m.get('home') or m.get('ev_sahibi'))
        a = clean_name(m.get('away') or m.get('deplasman'))
        
        if h and a and h != "?" and a != "?":
            key = f"{h}||{a}"
            scraped_lookup[key] = {
                'score': m['score'],
                'status': m['status'],
                'iy_home': m.get('iy_home', '0'),
                'iy_away': m.get('iy_away', '0'),
            }

    updated_count = 0  # Sayacı başlat

    # --- İÇ FONKSİYON: MAÇ GÜNCELLEME ---
    def update_match_obj(obj):
        nonlocal updated_count  # Üst fonksiyondaki sayacı kullan
        
        if not isinstance(obj, dict): 
            return

        h = clean_name(obj.get('home') or obj.get('ev_sahibi') or obj.get('ev') or obj.get('homeTeam') or "")
        a = clean_name(obj.get('away') or obj.get('deplasman') or obj.get('dep') or obj.get('awayTeam') or "")

        if h and a and h != "?" and a != "?":
            key = f"{h}||{a}"
            
        if key in scraped_lookup:
            new_data = scraped_lookup[key]
            
            # SPORDB'den gelen veriler
            sp_status = new_data.get('status', '')
            sp_score = new_data.get('score', '') # Örn: "2-3"
            
            # Skoru parçala (Sayıya çevir)
            new_ev, new_dep = 0, 0
            if '-' in sp_score:
                try:
                    new_ev, new_dep = map(int, sp_score.split('-'))
                except: 
                    pass
            
            # İY Skorlarını Hazırla
            new_iy_ev = 0
            new_iy_dep = 0
            if 'iy_home' in new_data:
                iy_h = new_data['iy_home']
                iy_d = new_data['iy_away']
                if isinstance(iy_h, str) and iy_h.isdigit(): new_iy_ev = int(iy_h)
                if isinstance(iy_d, str) and iy_d.isdigit(): new_iy_dep = int(iy_d)

            # ==========================================
            # 🚨 KRİTİK MANTIK: ZORLA GÜNCELLEME 🚨
            # ==========================================
            # Eğer SPORDB maçın "Bittiğini" söylüyorsa VE skor 0-0 değilse (veya gol varsa)
            # JSON'daki mevcut durum NE OLURSA OLSUN (başlamadi bile olsa) güncelle!
            
            is_finished_in_spordb = 'Bitti' in sp_status or 'Finished' in sp_status
            has_goals = (new_ev + new_dep) > 0
            
            if is_finished_in_spordb or has_goals:
                # Maç bitmiş kabul edilir, verileri zorla yaz
                obj['durum'] = 'bitti'
                obj['skor_ev'] = new_ev
                obj['skor_dep'] = new_dep
                
                # İY Skorlarını da yaz
                obj['skor_1y_ev'] = new_iy_ev
                obj['skor_1y_dep'] = new_iy_dep
                
                # Kaynağı güncelle
                obj['kaynak'] = 'spordb.com'
                
                updated_count += 1
                print(f"✅ ZORLA GÜNCELLENDİ: {obj.get('ev_sahibi')} vs {obj.get('deplasman')} -> MS: {new_ev}-{new_dep} | İY: {new_iy_ev}-{new_iy_dep}")
            else:
                # Maç henüz bitmemişse, eski usül (sadece farklıysa) güncelle
                if obj.get('skor_ev') != new_ev or obj.get('skor_dep') != new_dep:
                    obj['skor_ev'] = new_ev
                    obj['skor_dep'] = new_dep
                    # Durumu da güncellemeye çalış (Canlı vs)
                    if 'Canlı' in sp_status: obj['durum'] = 'canli'
                    updated_count += 1
            # ==========================================

    # --- İÇ FONKSİYON: AĞAÇTA GEZİNME ---
    def traverse_and_update(data):
        if isinstance(data, dict):
            update_match_obj(data)
            for v in data.values(): 
                traverse_and_update(v)
        elif isinstance(data, list):
            for item in data: 
                traverse_and_update(item)

    # --- İŞLEMİ BAŞLAT ---
    traverse_and_update(original_data)

    # --- KAYDET ---
    with open(MAC_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(original_data, f, ensure_ascii=False, indent=2)

    print(f"✅ GÜVENLİ GÜNCELLEME BAŞARILI! {updated_count} maçın skoru/durumu güncellendi.")
    return updated_count

def auto_git_commit_and_push(updated_count):
    """Değişiklik varsa otomatik Git add, commit ve push yapar."""
    if updated_count == 0:
        print("\nℹ️ Güncellenen maç yok, Git commit işlemi atlanıyor.")
        return

    print("\n🚀 Git otomasyonu başlatılıyor...")
    try:
        # Proje kök dizinini bul (iddiayusuf-main)
        repo_dir = MAC_JSON_PATH.parent.parent.parent 
        
        # DOSYA YOLU DÜZELTİLDİ: Kök dizine göre göreceli yolu bul (public/data/mac.json)
        relative_file_path = MAC_JSON_PATH.relative_to(repo_dir)
        
        # 1. Git Add (Doğru yol ile)
        print(f"📦 Git add yapılıyor: {relative_file_path}...")
        subprocess.run(["git", "add", str(relative_file_path)], cwd=repo_dir, check=True, capture_output=True, text=True)
        
        # 2. Değişiklik var mı kontrol et
        status_result = subprocess.run(["git", "status", "--porcelain"], cwd=repo_dir, check=True, capture_output=True, text=True)
        if not status_result.stdout.strip():
            print("ℹ️ Git'te commit edilecek yeni değişiklik bulunamadı.")
            return

        # 3. Git Commit
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"🤖 Otomatik Güncelleme: {updated_count} maç skoru/durumu güncellendi ({now})"
        print(f"📝 Commit atılıyor: {commit_msg}")
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_dir, check=True, capture_output=True, text=True)
        
        # 4. Git Push
        print("☁️ GitHub/GitLab'a pushlanıyor...")
        push_result = subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True, text=True)
        
        if push_result.returncode == 0:
            print("✅ Git push başarılı! Veriler depoya yüklendi.")
        else:
            print(f"⚠️ Git push başarısız (Commit yapıldı ama push edilemedi). Hata: {push_result.stderr}")
            
    except FileNotFoundError:
        print("❌ Git yüklü değil veya sistem PATH'ine eklenmemiş.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git komutu hatası: {e.stderr}")
    except Exception as e:
        print(f"❌ Git işlemi sırasında beklenmeyen hata: {e}")

def main():
    driver = None
    try:
        print("🌐 Tarayıcı başlatılıyor...")
        driver = build_driver()
        driver.get(URL)
        time.sleep(4)
        
        dismiss_cookies(driver)
        in_iframe = switch_to_iframe(driver)
        
        dates_to_fetch = [
            date.today(),
            date.today() - timedelta(days=1),
            date.today() - timedelta(days=2)
        ]
        
        all_scraped_matches = []
        
        for target_date in dates_to_fetch:
            date_str = target_date.strftime("%Y-%m-%d")
            print(f"\n{'='*50}")
            print(f"📅 Tarih İşleniyor: {date_str}")
            print(f"{'='*50}")
            
            success = select_date(driver, date_str)
            if success:
                matches = extract_matches_with_js(driver)
                all_scraped_matches.extend(matches)
                print(f"✅ {date_str} için {len(matches)} maç çekildi.")
            else:
                print(f"⚠️ {date_str} seçilemedi, atlanıyor.")

        print(f"\n🎉 TOPLAM {len(all_scraped_matches)} MAÇ ÇEKİLDİ (Son 3 Gün)!")
        
        if all_scraped_matches:
            out_file = OUT_DIR / f"matches_3days_{date.today().strftime('%Y%m%d_%H%M%S')}.json"
            out_file.write_text(json.dumps(all_scraped_matches, ensure_ascii=False, indent=2), encoding="utf-8")
            
            updated_count = update_mac_json_safely(all_scraped_matches)
            auto_git_commit_and_push(updated_count)
        else:
            print("\n⚠️ Hiç maç verisi çekilemedi.")
            
    except Exception as e:
        print(f"\n❌ KRİTİK HATA:")
        traceback.print_exc() 
    finally:
        if driver:
            try: driver.quit()
            except: pass
        
        print("\n" + "="*50)
        input("Çıkmak için Enter tuşuna basın...")

if __name__ == "__main__":
    main()