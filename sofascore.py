import json, os, re, time, datetime, traceback, shutil, unicodedata, subprocess
from pathlib import Path
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException

# =============================================================================
# TAKIM İSMİ DÜZELTME & EŞLEŞTİRME FONKSİYONLARI
# =============================================================================
def clean_team_name(name):
    if not name:
        return ""
    n = name.lower().strip()
    replacements = {
        "deportivo": "deport", "athletic": "athletic", "atletico": "atletico", "club": "",
        "ca ": "", " ca": "", "fc ": "", " fc": "", "ac ": "", " ac": "", "sc ": "", " sc": "",
        "us ": "", " us": "", "fk ": "", " fk": "", "sk ": "", " sk": "", "real ": "real", 
        "sporting ": "sporting", "de ": "", "la ": "", "el ": "", "cf ": "", "cd ": "", "ud ": ""
    }
    for key, val in replacements.items():
        if n.startswith(key + " "): n = val + n[len(key):]
        elif n.endswith(" " + key): n = n[:-len(key)-1] + (" " + val if val else "")
        elif n == key: n = val
    n = " ".join(n.split())
    n = n.replace(".", "").replace("-", " ").replace("'", "").replace("’", "")
    return n.strip()

_TMAP = str.maketrans({"İ":"i","I":"i","ı":"i","Ş":"s","ş":"s","Ğ":"g","ğ":"g","Ü":"u","ü":"u","Ö":"o","ö":"o","Ç":"c","ç":"c"})
_STOP = {"fk","fc","sk","jk","bk","ac","as","a.s","a.ş","spor","club","kulubu","kulübü",
         "u19","u20","u21","u23","women","reserves","b","ii","ca","cd","cf","sc","ud", "de", "la", "el"}

def _deaccent(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))

def norm_team(s: str) -> str:
    s = (s or "").strip()
    s = _deaccent(s).translate(_TMAP).lower()
    s = re.sub(r"[’'`´]", "", s)
    s = re.sub(r"\d+", " ", s)
    s = re.sub(r"[^a-z0-9\s-]", " ", s).replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip()
    parts = [p for p in s.split(" ") if p and p not in _STOP and len(p) > 1]
    return " ".join(parts)

def seq_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def token_dice(a: str, b: str) -> float:
    A = set(a.split()); B = set(b.split())
    if not A or not B: return 0.0
    return (2 * len(A & B)) / (len(A) + len(B))

def team_sim(a: str, b: str) -> float:
    a = norm_team(a); b = norm_team(b)
    if not a or not b: return 0.0
    if a == b: return 1.0
    if a in b or b in a: return 0.95
    return max(token_dice(a, b), seq_ratio(a, b))

def match_score(local_home, local_away, sp_home, sp_away):
    l_home = clean_team_name(local_home)
    l_away = clean_team_name(local_away)
    s_home = clean_team_name(sp_home)
    s_away = clean_team_name(sp_away)
    score = 0
    if l_home == s_home: score += 50
    elif l_home in s_home or s_home in l_home: score += 25
    if l_away == s_away: score += 50
    elif l_away in s_away or s_away in l_away: score += 25
    return score

def match_uid(tarih: str, ev: str, dep: str) -> str:
    a = norm_team(ev); b = norm_team(dep)
    x, y = sorted([a, b])
    return f"{tarih}|{x}|{y}"

# =============================================================================
# SOFASCORE AYARLARI
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
GECMIS_JSON_PATH = BASE_DIR / "public" / "data" / "gecmis_maclar.json"
OUTPUT_SKOR_JSON = BASE_DIR / "public" / "data" / "skorlar_sofascore.json"

SOFASCORE_URL = "https://www.sofascore.com/tr"

DAYS_BACK_FINISHED = 7     
INCLUDE_TODAY = True       

UPDATE_MAC_JSON = True
UPDATE_GECMIS_JSON = True
ADD_MISSING_MATCHES = True

PAGE_LOAD_TIMEOUT = 60
WAIT_LONG = 35

# SENİN BULDUĞUN CLASSLARLA UYUMLU SEÇİCİLER
MATCH_ROW_SELECTOR = "div.d_flex.jc_space-between.h_\\[86px\\].py_sm.px_md.md\\:px_xs"
HOME_TEAM_SELECTOR = "div.d_flex.flex-d_column.ai_center.pos_absolute.top_\\[56px\\] > bdi.textStyle_display\\.micro"
AWAY_TEAM_SELECTOR = "div.d_flex.flex-d_row-reverse.gap_sm.pos_relative div.d_flex.flex-d_column.ai_center.pos_absolute.top_\\[56px\\] > bdi.textStyle_display\\.micro"
HOME_SCORE_SELECTOR = "span.textStyle_body\\.medium.c_neutrals\\.nLv1.pos_relative.min-w_lg.ta_end.score"
AWAY_SCORE_SELECTOR = "span.textStyle_body\\.medium.c_neutrals\\.nLv1.pos_relative.min-w_lg.ta_start.score"
HALF_SCORE_SELECTOR = "span.textStyle_display\\.small.c_neutrals\\.nLv3.mt_sm.ta_center.d_block"
DATE_TEXT_SELECTOR = "span.textStyle_body\\.medium.c_neutrals\\.nLv3.ta_center.d_block"
TIME_SELECTOR = "span.textStyle_display\\.large.c_neutrals\\.nLv1.d_block.ta_center"
HOME_IMG_SELECTOR = "div.h_4xl > img"
AWAY_IMG_SELECTOR = "div.d_flex.flex-d_row-reverse.gap_sm.pos_relative img"

LOAD_MORE_XPATH = "//button[contains(., 'Daha fazla') or contains(., 'Yükle') or contains(@class, 'loadMore')]"

THRESH_OK = 0.80
THRESH_MAYBE = 0.65
MIN_GAP = 0.06

# =============================================================================
# JSON OKUMA / YAZMA
# =============================================================================
def load_json_safe(path: Path):
    if not path.exists():
        return {"version": 2, "updated": "", "matches": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"⚠️ JSON Okuma Hatası ({path.name}): {e}")
        return {"version": 2, "updated": "", "matches": []}

def save_json_atomic(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    if path.exists():
        bak = path.with_suffix(path.suffix + f".bak.{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")
        try: shutil.copy2(path, bak)
        except: pass
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, path)
    print(f"💾 Kaydedildi: {path.name}")

# =============================================================================
# TARAYICI AYARLARI
# =============================================================================
def build_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--lang=tr-TR")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

# =============================================================================
# SAYFA YÜKLEME & KAYDIRMA
# =============================================================================
def deep_scroll_collect(driver, max_steps=100):
    last = 0; stable = 0
    for _ in range(max_steps):
        try:
            btns = driver.find_elements(By.XPATH, LOAD_MORE_XPATH)
            btn = next((b for b in btns if b.is_displayed() and b.is_enabled()), None)
            if btn:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                time.sleep(0.3)
                btn.click()
                time.sleep(1.5)
        except: pass
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.2)
        try:
            n = len(driver.find_elements(By.CSS_SELECTOR, MATCH_ROW_SELECTOR))
            if n > last: 
                last = n; stable = 0
            else:
                stable += 1
                if stable >= 10: break
        except: pass
    return last

# =============================================================================
# VERİ ÇEKME & PARSE ETME
# =============================================================================
def parse_match_row(row_element):
    try:
        # 1. TAKIM İSİMLERİ
        try:
            ev_sahibi_elem = row_element.find_element(By.CSS_SELECTOR, HOME_TEAM_SELECTOR)
            ev_sahibi = ev_sahibi_elem.get_attribute('innerHTML').strip()
        except NoSuchElementException:
            try: 
                ev_sahibi_elem = row_element.find_element(By.CSS_SELECTOR, HOME_TEAM_SELECTOR.replace("bdi", "span"))
                ev_sahibi = ev_sahibi_elem.text.strip()
            except: ev_sahibi = ""

        try:
            deplasman_elem = row_element.find_element(By.CSS_SELECTOR, AWAY_TEAM_SELECTOR)
            deplasman = deplasman_elem.get_attribute('innerHTML').strip()
        except NoSuchElementException:
            try: 
                deplasman_elem = row_element.find_element(By.CSS_SELECTOR, AWAY_TEAM_SELECTOR.replace("bdi", "span"))
                deplasman = deplasman_elem.text.strip()
            except: deplasman = ""

        if not ev_sahibi or not deplasman:
            return None

        # 2. SKORLAR
        ev_skor = 0; dep_skor = 0
        try:
            ev_skor_txt = row_element.find_element(By.CSS_SELECTOR, HOME_SCORE_SELECTOR).text.strip()
            dep_skor_txt = row_element.find_element(By.CSS_SELECTOR, AWAY_SCORE_SELECTOR).text.strip()
            ev_skor = int(ev_skor_txt) if ev_skor_txt.isdigit() else 0
            dep_skor = int(dep_skor_txt) if dep_skor_txt.isdigit() else 0
        except Exception as e:
            pass

        # 3. İLK YARI SKORLARI
        iy_ev = 0; iy_dep = 0
        try:
            iy_text = row_element.find_element(By.CSS_SELECTOR, HALF_SCORE_SELECTOR).text.strip()
            rakamlar = re.findall(r"(\d+)", iy_text)
            if len(rakamlar) >= 2:
                iy_ev = int(rakamlar[0])
                iy_dep = int(rakamlar[1])
            elif ev_skor == 0 and dep_skor == 0 and len(rakamlar) == 2:
                iy_ev, iy_dep = int(rakamlar[0]), int(rakamlar[1])
        except:
            pass

        # 4. TARİH & SAAT
        tarih_metni = ""
        saat_metni = ""
        try:
            tarih_metni = row_element.find_element(By.CSS_SELECTOR, DATE_TEXT_SELECTOR).text.strip()
            saat_metni = row_element.find_element(By.CSS_SELECTOR, TIME_SELECTOR).text.strip()
        except:
            pass

        bugun = datetime.date.today()
        if "Bugün" in tarih_metni:
            tarih = bugun.isoformat()
        elif "Yarın" in tarih_metni:
            tarih = (bugun + datetime.timedelta(days=1)).isoformat()
        elif "Dün" in tarih_metni:
            tarih = (bugun - datetime.timedelta(days=1)).isoformat()
        else:
            if re.search(r"\d", tarih_metni):
                try:
                    tarih_obj = datetime.datetime.strptime(f"{tarih_metni} {bugun.year}", "%d %b %Y").date()
                    tarih = tarih_obj.isoformat()
                except:
                    tarih = bugun.isoformat()
            else:
                tarih = bugun.isoformat()

        # 5. MAÇ ID'Sİ
        sofascore_id = "0"
        try:
            img_elem = row_element.find_element(By.CSS_SELECTOR, HOME_IMG_SELECTOR)
            src_link = img_elem.get_attribute("src")
            id_match = re.search(r"/team/(\d+)/image", src_link)
            if id_match:
                sofascore_id = id_match.group(1)
        except:
            pass

        # 6. VERİLERİ DÖNDÜR
        return {
            "sofascore_id": sofascore_id,
            "tarih": tarih,
            "saat": saat_metni,
            "sp_home": ev_sahibi,
            "sp_away": deplasman,
            "skor1": ev_skor,
            "skor2": dep_skor,
            "iy_skor1": iy_ev,
            "iy_skor2": iy_dep,
            "cekme_zamani": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        return None

def collect_all_scores(driver):
    print("📋 Maç listesi yükleniyor ve veriler çekiliyor...")
    total_rows = deep_scroll_collect(driver)
    print(f"✅ Sayfada bulunan toplam satır: {total_rows}")

    rows = driver.find_elements(By.CSS_SELECTOR, MATCH_ROW_SELECTOR)
    all_scores = []
    seen_uids = set()

    bugun = datetime.date.today()
    if INCLUDE_TODAY:
        hedef_tarihler = [(bugun - datetime.timedelta(days=i)).isoformat() for i in range(DAYS_BACK_FINISHED)]
    else:
        hedef_tarihler = [(bugun - datetime.timedelta(days=i)).isoformat() for i in range(1, DAYS_BACK_FINISHED + 1)]

    print(f"📅 Filtrelenecek tarihler: {hedef_tarihler}")

    for index, row in enumerate(rows):
        try:
            veri = parse_match_row(row)
            if not veri:
                continue

            # Sadece istediğimiz tarihler arasındakileri al
            if veri["tarih"] not in hedef_tarihler:
                continue

            # Tekrar eden kayıtları engelle
            unique_id = f"{veri['tarih']}|{veri['sp_home']}|{veri['sp_away']}"
            if unique_id in seen_uids:
                continue
            seen_uids.add(unique_id)

            all_scores.append(veri)
            print(f"✅ Veri Alındı: {veri['sp_home']} - {veri['sp_away']} | Tarih: {veri['tarih']} | Saat: {veri.get('saat', '')}")

        except Exception as e:
            continue

    return all_scores

# =============================================================================
# VERİTABANI GÜNCELLEME & EŞLEŞTİRME
# =============================================================================
def update_db(db_data: dict, scores: list, today_iso: str):
    matches = db_data.get("matches", [])
    if not isinstance(matches, list):
        matches = []
        db_data["matches"] = matches

    # Mevcut verileri tarihe göre grupla
    uid_set = set()
    by_date = {}
    for m in matches:
        if m.get("tarih") and m.get("ev_sahibi") and m.get("deplasman"):
            uid_set.add(match_uid(m["tarih"], m["ev_sahibi"], m["deplasman"]))
            by_date.setdefault(m["tarih"], []).append(m)

    # İstatistik sayaçları
    matched = updated = noop = added = skipped = not_matched = 0

    # Gelen her Sofascore verisini kontrol et
    for sp in scores:
        cands = by_date.get(sp["tarih"], [])
        best = None
        best_sc = -1.0
        second_sc = -1.0

        # En iyi eşleşmeyi bul
        for m in cands:
            sc = match_score(m.get("ev_sahibi", ""), m.get("deplasman", ""), sp["sp_home"], sp["sp_away"])
            if sc > best_sc:
                second_sc = best_sc
                best_sc = sc
                best = m
            elif sc > second_sc:
                second_sc = sc

        # Eşleşme Kriterleri
        if best and best_sc >= THRESH_MAYBE and (best_sc - second_sc) >= MIN_GAP:
            if best_sc >= THRESH_OK:
                matched += 1

                # Takımların yer değiştirip değiştirilmediğini kontrol et
                s_direct = team_sim(best.get("ev_sahibi", ""), sp["sp_home"]) + team_sim(best.get("deplasman", ""), sp["sp_away"])
                s_swap = team_sim(best.get("ev_sahibi", ""), sp["sp_away"]) + team_sim(best.get("deplasman", ""), sp["sp_home"])

                # Skorları doğru tarafa ata
                if s_swap > s_direct:
                    skor_ev, skor_dep = sp["skor2"], sp["skor1"]
                    iy_ev, iy_dep = sp.get("iy_skor2", 0), sp.get("iy_skor1", 0)
                else:
                    skor_ev, skor_dep = sp["skor1"], sp["skor2"]
                    iy_ev, iy_dep = sp.get("iy_skor1", 0), sp.get("iy_skor2", 0)

                # Veri değişikliği var mı?
                changed = (
                    best.get("skor_ev") != skor_ev or
                    best.get("skor_dep") != skor_dep or
                    best.get("skor_1y_ev") != iy_ev or
                    best.get("skor_1y_dep") != iy_dep or
                    best.get("sofascore_id") != sp["sofascore_id"]
                )

                # Bilgileri güncelle
                best["skor_ev"] = skor_ev
                best["skor_dep"] = skor_dep
                best["skor_1y_ev"] = iy_ev
                best["skor_1y_dep"] = iy_dep
                best["durum"] = "bitti" if (skor_ev + skor_dep) > 0 else "bekliyor"
                best["sofascore_id"] = sp["sofascore_id"]
                best["kaynak"] = "sofascore.com"
                best["cekme_zamani"] = sp["cekme_zamani"]

                if changed:
                    updated += 1
                else:
                    noop += 1
                continue

            skipped += 1
            continue

        # Eşleşme bulunamadıysa ve ekleme özelliği açıksa yeni kayıt oluştur
        if ADD_MISSING_MATCHES:
            uid = match_uid(sp["tarih"], sp["sp_home"], sp["sp_away"])
            if uid not in uid_set:
                yeni_mac = {
                    "index": 0,
                    "mac_kodu": "",
                    "ev_sahibi": sp["sp_home"],
                    "deplasman": sp["sp_away"],
                    "saat": sp.get("saat", ""),
                    "lig": "",
                    "tarih": sp["tarih"],
                    "cekme_zamani": sp["cekme_zamani"],
                    "durum": "bitti" if (sp["skor1"] + sp["skor2"]) > 0 else "bekliyor",
                    "skor_ev": sp["skor1"],
                    "skor_dep": sp["skor2"],
                    "skor_1y_ev": sp.get("iy_skor1", 0),
                    "skor_1y_dep": sp.get("iy_skor2", 0),
                    "kaynak": "sofascore.com",
                    "sofascore_id": sp["sofascore_id"],
                    "oranlar": {}
                }
                matches.append(yeni_mac)
                uid_set.add(uid)
                added += 1
                print(f"➕ Yeni Maç Eklendi: {sp['sp_home']} - {sp['sp_away']}")
            else:
                not_matched += 1
        else:
            not_matched += 1

    # Listeyi sırala ve indexleri güncelle
    db_data["matches"] = sorted(matches, key=lambda x: (x.get("tarih", ""), x.get("saat", "00:00"), x.get("ev_sahibi", "")))
    for i, item in enumerate(db_data["matches"], 1):
        item["index"] = i

    db_data["updated"] = datetime.datetime.now().isoformat()
    return matched, updated, noop, added, skipped, not_matched

# =============================================================================
# ANA ÇALIŞTIRMA FONKSİYONU
# =============================================================================
def main():
    print("=" * 70)
    print("⚽ SOFASCORE VERİ ÇEKİCİ | GÜNCEL SÜRÜM")
    print("=" * 70)

    bugun_iso = datetime.date.today().isoformat()
    driver = None
    all_scores = []

    try:
        # Tarayıcıyı Başlat
        driver = build_driver()
        print(f"🌐 Adrese gidiliyor: {SOFASCORE_URL}")
        driver.get(SOFASCORE_URL)

        # Sayfanın ana elemanlarının yüklenmesini bekle
        try:
            WebDriverWait(driver, WAIT_LONG).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, MATCH_ROW_SELECTOR))
            )
            print("✅ Sayfa başarıyla yüklendi.")
        except TimeoutException:
            print("❌ HATA: Sayfa zaman aşımına uğradı veya maç listesi bulunamadı!")
            return

        time.sleep(3)

        # Verileri Çek
        all_scores = collect_all_scores(driver)
        print(f"\n📊 Toplam {len(all_scores)} adet maç verisi başarıyla çekildi.")

        # Ham veriyi JSON'a kaydet
        save_json_atomic({
            "olusturulma_tarihi": datetime.datetime.now().isoformat(),
            "kaynak": SOFASCORE_URL,
            "gun_geriye_donuk": DAYS_BACK_FINISHED,
            "bugun_dahil": INCLUDE_TODAY,
            "adet": len(all_scores),
            "veriler": all_scores
        }, OUTPUT_SKOR_JSON)

        # Ana Veritabanını Güncelle
        if UPDATE_MAC_JSON:
            print("\n🔄 Ana dosya (mac.json) güncelleniyor...")
            mac_veri = load_json_safe(MAC_JSON_PATH)
            istatistik = update_db(mac_veri, all_scores, bugun_iso)
            save_json_atomic(mac_veri, MAC_JSON_PATH)
            print(f"""
            📈 İŞLEM SONUÇLARI:
            ✅ Eşleşen: {istatistik[0]}
            ✏️ Güncellenen: {istatistik[1]}
            🟡 Değişmeyen: {istatistik[2]}
            ➕ Yeni Eklenen: {istatistik[3]}
            ⏭️ Atlanan: {istatistik[4]}
            ❌ Eşleşmeyen: {istatistik[5]}
            """)

        # Geçmiş Veritabanını Güncelle
        if UPDATE_GECMIS_JSON:
            print("\n🔄 Geçmiş dosya (gecmis_maclar.json) güncelleniyor...")
            gecmis_veri = load_json_safe(GECMIS_JSON_PATH)
            update_db(gecmis_veri, all_scores, bugun_iso)
            save_json_atomic(gecmis_veri, GECMIS_JSON_PATH)

    except Exception as genel_hata:
        print(f"❌ BEKLENMEDİK HATA: {genel_hata}")
        traceback.print_exc()

    finally:
        # Tarayıcıyı kapat
        if driver:
            try:
                driver.quit()
                print("🗑️ Tarayıcı kapatıldı.")
            except:
                pass

        # Otomatik Git Gönderimi
        try:
            if len(all_scores) > 0:
                print("\n🚀 Git deposuna gönderiliyor...")
                repo_yol = BASE_DIR
                dosyalar = [
                    "public/data/mac.json",
                    "public/data/gecmis_maclar.json",
                    "public/data/skorlar_sofascore.json"
                ]

                for dosya in dosyalar:
                    tam_yol = repo_yol / dosya
                    if tam_yol.exists():
                        subprocess.run(["git", "add", dosya], cwd=repo_yol, capture_output=True)

                durum = subprocess.run(["git", "status", "--porcelain"], cwd=repo_yol, capture_output=True, text=True)
                if durum.stdout.strip():
                    mesaj = f"🤖 Sofascore Otomatik Güncelleme | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} | Son {DAYS_BACK_FINISHED} Gün"
                    subprocess.run(["git", "commit", "-m", mesaj], cwd=repo_yol, capture_output=True)
                    subprocess.run(["git", "pull", "--rebase"], cwd=repo_yol, capture_output=True)
                    push_sonuc = subprocess.run(["git", "push"], cwd=repo_yol, capture_output=True, text=True)
                    if push_sonuc.returncode == 0:
                        print("✅ Depoya başarıyla yüklendi!")
                    else:
                        print(f"⚠️ Git Push Hatası: {push_sonuc.stderr}")
                else:
                    print("ℹ️ Değişiklik bulunamadı, gönderme yapılmadı.")
        except Exception as git_hata:
            print(f"⚠️ Git İşlem Hatası: {git_hata}")

    print("\n" + "="*60)
    print("          🎉 TÜM İŞLEMLER TAMAMLANDI 🎉")
    print("="*60)
    input("Çıkmak için herhangi bir tuşa basın...")

# Programı çalıştır
if __name__ == "__main__":
    main()