import time
import json
import shutil
import subprocess
import traceback
import os
import re
from datetime import date, timedelta, datetime
from pathlib import Path
from difflib import SequenceMatcher

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

# ✅ DİNAMİK TARİH ARALIĞI
BASLANGIC_TARIHI = "14/08/2026"
BITIS_TARIHI     = "23/08/2026"

# ✅ FUZZY EŞLEŞTİRME AYARLARI
ESLESME_TOLERANSI_GUN = 15
BENZERLIK_ESIK = 0.60

# --- YARDIMCI FONKSİYONLAR ---
def temiz_isim(s):
    s = str(s).lower().strip()
    s = re.sub(r'[^a-z0-9çğıöşü ]', '', s)
    return s

def benzerlik(a, b):
    return SequenceMatcher(None, temiz_isim(a), temiz_isim(b)).ratio()

def tarih_farki(t1, t2):
    try:
        d1 = datetime.strptime(t1, "%Y-%m-%d").date()
        d2 = datetime.strptime(t2, "%Y-%m-%d").date()
        return abs((d1 - d2).days)
    except:
        return 999

def tarih_araligi_olustur(bas, bit):
    g1, a1, y1 = map(int, bas.split("/"))
    g2, a2, y2 = map(int, bit.split("/"))
    d1 = date(y1, a1, g1)
    d2 = date(y2, a2, g2)
    out = []
    while d1 <= d2:
        out.append(d1)
        d1 += timedelta(days=1)
    return out

# GÜNCELLENECEK ANA DOSYA (Otomatik bulma özelliği)
def get_mac_json_path():
    p1 = Path(r"C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main\public\data\mac.json")
    if p1.exists(): return p1
    p2 = Path(r"C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\mac.json")
    if p2.exists(): return p2

    current = Path(__file__).resolve()
    for _ in range(5):
        test_path = current / "public" / "data" / "mac.json"
        if test_path.exists(): return test_path
        current = current.parent

    return p1

MAC_JSON_PATH = get_mac_json_path()

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
    for xp in [
        "//button[contains(.,'Kabul')]",
        "//button[contains(.,'Accept')]",
        "//button[@id='onetrust-accept-btn-handler']"
    ]:
        try:
            for b in driver.find_elements(By.XPATH, xp):
                if b.is_displayed():
                    driver.execute_script("arguments[0].click();", b)
                    time.sleep(1)
                    return
        except:
            pass

def switch_to_iframe(driver):
    for iframe in driver.find_elements(By.TAG_NAME, "iframe"):
        try:
            driver.switch_to.frame(iframe)
            if driver.find_elements(By.XPATH, "//button[@aria-label='Takvim' or contains(@aria-label, 'Takvim')]"):
                return True
        except:
            pass
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

def extract_matches_with_js(driver, target_date_str):
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    except:
        pass

    js_code = """
    let results = [];
    let currentLeague = "Bilinmeyen Lig";
    let processedRows = new Set();
    let elements = document.querySelectorAll('h3[data-testid="tournament-name-link"], .rounded-match__score, div.w-6');

    elements.forEach(el => {
        if (el.tagName === 'H3' && el.getAttribute('data-testid') === 'tournament-name-link') {
            let text = el.innerText || el.textContent || "";
            currentLeague = text.replace(/\\n/g, ' ').replace(/\\s+/g, ' ').trim()
                .replace(/Favorilere ekle|MS|İY|arrow/gi, '').replace(/\\|$/, '').trim();
        } else {
            let row = el.closest('[role="row"]') || el.parentElement.parentElement;
            if (!row || processedRows.has(row)) return;

            let truncates = Array.from(row.querySelectorAll('.truncate'))
                .map(e => (e.innerText || e.textContent || "").trim())
                .filter(t => t.length > 1 && !/Favorilere|arrow|MS|İY/i.test(t));

            if (truncates.length >= 2) {
                processedRows.add(row);

                let scoreBoxes = Array.from(row.querySelectorAll('.rounded-match__score, div.w-6'));
                let nums = [];
                scoreBoxes.forEach(b => {
                    let t = (b.innerText || b.textContent || "").trim();
                    if (/^\\d+$/.test(t)) nums.push(t);
                });

                let ms_score = "-";
                let iy_h = "-";
                let iy_a = "-";

                if (nums.length >= 2) {
                    ms_score = nums[0] + "-" + nums[1];
                }
                if (nums.length >= 4) {
                    iy_h = nums[2];
                    iy_a = nums[3];
                }

                let text = row.innerText || row.textContent || "";
                let lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                let statusRegex = /^(\\d{1,3}[''.']?|\\d{1,2}:\\d{2}|MS|IY|İY|Bitti|Canlı|Başlamadı|ERT|TAT)$/i;

                let status = lines.find(l => statusRegex.test(l) && !/^\\d$/.test(l)) || "MS";
                if (status === "-" || /^\\d$/.test(status)) status = "MS";

                results.push({
                    tarih: arguments[0],
                    league: currentLeague,
                    home: truncates[0],
                    away: truncates[1],
                    score: ms_score,
                    iy_home: iy_h,
                    iy_away: iy_a,
                    status: status
                });
            }
        }
    });
    return results;
    """

    try:
        return driver.execute_script(js_code, target_date_str) or []
    except Exception as e:
        print(f"❌ JS çalıştırma hatası: {e}")
        return []

def update_mac_json_safely(scraped_matches):
    print(f"\n🔄 [{MAC_JSON_PATH}] dosyası GÜVENLİ şekilde güncelleniyor...")

    if not MAC_JSON_PATH.exists():
        print(f"⚠️ mac.json bulunamadı! Aranan yol: {MAC_JSON_PATH}")
        return 0

    backup_path = OUT_DIR / "mac_backup.json"
    shutil.copy2(MAC_JSON_PATH, backup_path)
    print(f"💾 Güvenlik yedeği alındı: {backup_path}")

    with open(MAC_JSON_PATH, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    def clean_name(name):
        return str(name).strip().lower()

    # Scraped verileri lookup tablosuna al
    scraped_lookup = {}
    for m in scraped_matches:
        h = clean_name(m.get('home') or m.get('ev_sahibi') or "")
        a = clean_name(m.get('away') or m.get('deplasman') or "")

        if h and a and h != "?" and a != "?":
            key = f"{h}||{a}"
            scraped_lookup[key] = m

    updated_count = 0
    unmatched_count = 0

    def update_match_obj(obj):
        nonlocal updated_count, unmatched_count
        if not isinstance(obj, dict):
            return

        h = clean_name(
            obj.get('home') or obj.get('ev_sahibi') or
            obj.get('ev') or obj.get('homeTeam') or ""
        )
        a = clean_name(
            obj.get('away') or obj.get('deplasman') or
            obj.get('dep') or obj.get('awayTeam') or ""
        )

        if not h or not a or h == "?" or a == "?":
            return

        matched = False  # ✅ Eşleşme kontrolü

        # ✅ FUZZY + TARİH TOLERANSLI EŞLEŞTİRME
        for scraped_key, new_data in scraped_lookup.items():
            sh, sa = scraped_key.split("||")

            # ✅ ±5 gün toleransı
            json_tarih = obj.get("tarih", "")
            scraped_tarih = new_data.get("tarih", "")

            if json_tarih and scraped_tarih:
                if tarih_farki(json_tarih, scraped_tarih) > ESLESME_TOLERANSI_GUN:
                    continue

            # ✅ Fuzzy eşleşme
            ev_oran = benzerlik(h, sh)
            dep_oran = benzerlik(a, sa)

            if ev_oran >= BENZERLIK_ESIK and dep_oran >= BENZERLIK_ESIK:

                sp_score = new_data.get('score', '')
                if '-' not in sp_score:
                    continue

                try:
                    new_ev, new_dep = map(int, sp_score.split('-'))
                except:
                    continue

                new_iy_ev = (
                    int(new_data.get("iy_home", 0))
                    if str(new_data.get("iy_home", "")).isdigit() else 0
                )
                new_iy_dep = (
                    int(new_data.get("iy_away", 0))
                    if str(new_data.get("iy_away", "")).isdigit() else 0
                )

                obj["skor_ev"]    = new_ev
                obj["skor_dep"]   = new_dep
                obj["skor_1y_ev"] = new_iy_ev
                obj["skor_1y_dep"]= new_iy_dep
                obj["durum"]      = "bitti"
                obj["kaynak"]     = "iddaa.com"
                obj["cekme_zamani"] = datetime.now().isoformat()

                updated_count += 1
                matched = True  # ✅ Eşleşti işaretle
                
                print(
                    f"✅ FUZZY ±{ESLESME_TOLERANSI_GUN}G EŞLEŞTİ: "
                    f"{obj.get('ev_sahibi')} vs {obj.get('deplasman')} "
                    f"-> MS: {new_ev}-{new_dep} | İY: {new_iy_ev}-{new_iy_dep} "
                    f"(Benzerlik: Ev={ev_oran:.2f}, Dep={dep_oran:.2f})"
                )
                break  # İlk eşleşmede dur
        
        # ✅ Eşleşmeyen maçları say
        if not matched:
            unmatched_count += 1

    def traverse_and_update(data):
        if isinstance(data, dict):
            update_match_obj(data)
            for v in data.values():
                traverse_and_update(v)
        elif isinstance(data, list):
            for item in data:
                traverse_and_update(item)

    traverse_and_update(original_data)

    with open(MAC_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(original_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ GÜVENLİ GÜNCELLEME BAŞARILI!")
    print(f"   ✅ Güncellenen maç: {updated_count}")
    print(f"   ⚠️ Eşleşmeyen çekilen maç: {unmatched_count}")
    
    # ✅ Eşleşmeyenleri rapor et
    if unmatched_count > 0:
        unmatched_file = OUT_DIR / f"unmatched_{date.today().strftime('%Y%m%d_%H%M%S')}.json"
        unmatched_file.write_text(
            json.dumps(scraped_matches, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"   📋 Eşleşmeyen maçlar kaydedildi: {unmatched_file}")
    
    return updated_count

def auto_git_commit_and_push(updated_count):
    if updated_count == 0:
        print("\nℹ️ Güncellenen maç yok, Git commit işlemi atlanıyor.")
        return

    print("\n🚀 Git otomasyonu başlatılıyor...")
    try:
        repo_dir = MAC_JSON_PATH.parent.parent.parent
        relative_file_path = MAC_JSON_PATH.relative_to(repo_dir)

        print(f"📦 Git add yapılıyor: {relative_file_path}...")
        subprocess.run(
            ["git", "add", str(relative_file_path)],
            cwd=repo_dir, check=True, capture_output=True, text=True
        )

        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_dir, check=True, capture_output=True, text=True
        )
        if not status_result.stdout.strip():
            print("ℹ️ Git'te commit edilecek yeni değişiklik bulunamadı.")
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = (
            f"🤖 Otomatik Güncelleme: {updated_count} maç skoru/durumu güncellendi ({now})"
        )
        print(f"📝 Commit atılıyor: {commit_msg}")
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=repo_dir, check=True, capture_output=True, text=True
        )

        print("☁️ GitHub/GitLab'a pushlanıyor...")
        push_result = subprocess.run(
            ["git", "push"],
            cwd=repo_dir, capture_output=True, text=True
        )

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

        # ✅ DİNAMİK TARİH ARALIĞI
        dates_to_fetch = tarih_araligi_olustur(BASLANGIC_TARIHI, BITIS_TARIHI)

        print(f"\n📆 Tarih aralığı: {BASLANGIC_TARIHI} → {BITIS_TARIHI} ({len(dates_to_fetch)} gün)")

        all_scraped_matches = []

        for target_date in dates_to_fetch:
            date_str = target_date.strftime("%Y-%m-%d")
            print(f"\n{'='*75}")
            print(f"📅 TARİH İŞLENİYOR: {date_str}")
            print(f"{'='*75}")

            success = select_date(driver, date_str)
            if success:
                matches = extract_matches_with_js(driver, date_str)
                all_scraped_matches.extend(matches)
                print(f"✅ {date_str} için toplam {len(matches)} maç çekildi.")

                print(f"\n📋 [{date_str}] TARİHLİ MAÇLARIN DETAYLI LİSTESİ:")
                print("-" * 95)
                for idx, m in enumerate(matches, 1):
                    lig    = m.get('league', 'Bilinmeyen Lig')
                    ev     = m.get('home', '?')
                    dep    = m.get('away', '?')
                    ms     = m.get('score', '?-?')
                    iy_ev  = m.get('iy_home', '-')
                    iy_dep = m.get('iy_away', '-')
                    iy_str = f"{iy_ev}-{iy_dep}" if iy_ev != "-" else "-"
                    durum  = m.get('status', 'MS')

                    print(
                        f" [{idx:02d}] 🏆 {lig[:18]:<18} | "
                        f"⚽ {ev:>15} vs {dep:<15} | "
                        f"🏁 MS: {ms:<5} | "
                        f"⏱️ İY: {iy_str:<5} | "
                        f"📌 {durum}"
                    )
                print("-" * 95)
            else:
                print(f"⚠️ {date_str} seçilemedi, atlanıyor.")

        print(f"\n🎉 TOPLAM {len(all_scraped_matches)} MAÇ ÇEKİLDİ!")

        if all_scraped_matches:
            out_file = OUT_DIR / f"matches_{date.today().strftime('%Y%m%d_%H%M%S')}.json"
            out_file.write_text(
                json.dumps(all_scraped_matches, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            print(f"💾 Ham veri kaydedildi: {out_file}")

            updated_count = update_mac_json_safely(all_scraped_matches)
            auto_git_commit_and_push(updated_count)
        else:
            print("\n⚠️ Hiç maç verisi çekilemedi.")

    except Exception as e:
        print(f"\n❌ KRİTİK HATA:")
        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

        print("\n" + "=" * 50)
        input("Çıkmak için Enter tuşuna basın...")

if __name__ == "__main__":
    main()