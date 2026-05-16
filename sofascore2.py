import json, os, re, time, datetime, traceback, shutil, unicodedata, subprocess
from pathlib import Path
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException,
    ElementClickInterceptedException, InvalidSelectorException
)

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
        if n.startswith(key + " "):
            n = val + n[len(key):]
        elif n.endswith(" " + key):
            n = n[:-len(key)-1] + (" " + val if val else "")
        elif n == key:
            n = val
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
    A, B = set(a.split()), set(b.split())
    if not A or not B: return 0.0
    return (2 * len(A & B)) / (len(A) + len(B))

def team_sim(a: str, b: str) -> float:
    a, b = norm_team(a), norm_team(b)
    if not a or not b: return 0.0
    if a == b: return 1.0
    if a in b or b in a: return 0.95
    return max(token_dice(a, b), seq_ratio(a, b))

def match_score(local_home, local_away, sp_home, sp_away):
    l_home, l_away = clean_team_name(local_home), clean_team_name(local_away)
    s_home, s_away = clean_team_name(sp_home), clean_team_name(sp_away)
    score = 0
    if l_home == s_home: score += 50
    elif l_home and s_home and (l_home in s_home or s_home in l_home): score += 25
    if l_away == s_away: score += 50
    elif l_away and s_away and (l_away in s_away or s_away in l_away): score += 25
    return score

def match_uid(tarih: str, ev: str, dep: str) -> str:
    a, b = norm_team(ev), norm_team(dep)
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

# ✅ SABİT AYAR: Son 3 gün verisi çekilir
TARGET_DAYS = 3
INCLUDE_TODAY = True

UPDATE_MAC_JSON = True
UPDATE_GECMIS_JSON = True
ADD_MISSING_MATCHES = True

PAGE_LOAD_TIMEOUT = 60
WAIT_LONG = 45
SCROLL_PAUSE_TIME = 1.2
MAX_LOAD_MORE = 5  # ✅ En fazla 5 kere "Daha fazla" yükle, sonsuz kaydırma engeli

# ✅ SEÇİCİLER — OK İKONU ÖZEL + BOŞ LİG KONTROLÜ
MATCH_ROW_SELECTOR = "div[class*='eventRow'], div.d_flex.jc_space-between"
LEAGUE_GROUP_SELECTOR = "div[class*='leagueGroup']" # Lig kapsayıcı div
HOME_TEAM_SELECTOR = "div.d_flex.flex-d_column.ai_center.pos_absolute.top_\\[56px\\] > bdi, span.textStyle_display\\.micro"
AWAY_TEAM_SELECTOR = "div.d_flex.flex-d_row-reverse.gap_sm.pos_relative div.d_flex.flex-d_column.ai_center > bdi, span.textStyle_display\\.micro"
HOME_SCORE_SELECTOR = "span.score, span.textStyle_body\\.medium.score"
AWAY_SCORE_SELECTOR = "div.d_flex.flex-d_row-reverse ~ div span.score, div.d_flex.flex-d_row-reverse ~ div span.textStyle_body\\.medium.score"
HALF_SCORE_SELECTOR = "span.textStyle_display\\.small.c_neutrals\\.nLv3.mt_sm.ta_center.d_block"
TIME_SELECTOR = "span.textStyle_display\\.large, span.textStyle_body\\.medium.c_neutrals\\.nLv3"
HOME_IMG_SELECTOR = "div.h_4xl > img"
# ✅ Sizin verdiğiniz OK İKONU'NA ÖZEL SEÇİCİ
ARROW_ICON_SELECTOR = "svg path[d='M11.99 18 4 9.942 5.42 8.51l6.57 6.636 6.6-6.646L20 9.922z']"
DATE_BUTTONS_XPATH = "//span[contains(text(), 'Bugün') or contains(text(), 'Dün') or contains(text(), 'Evvelsi') or contains(text(), '2 gün önce')]"
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
    options.add_argument("--enable-javascript")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

# =============================================================================
# ✅ GELİŞMİŞ LİG AÇMA - BOŞ OLANLARI ATLA
# =============================================================================
def open_all_leagues(driver):
    print("🔓 Lig grupları kontrol ediliyor ve açılıyor...")
    try:
        # Tüm lig gruplarını bul
        leagues = driver.find_elements(By.CSS_SELECTOR, LEAGUE_GROUP_SELECTOR)
        acilan = 0
        kapatilan_bos = 0

        for league in leagues:
            try:
                # Önce bu ligde maç var mı kontrol et
                mac_sayisi = len(league.find_elements(By.CSS_SELECTOR, MATCH_ROW_SELECTOR))
                if mac_sayisi == 0:
                    # İçinde maç yoksa zaten boş, atla/kapat
                    try:
                        arrow = league.find_element(By.CSS_SELECTOR, ARROW_ICON_SELECTOR)
                        if arrow:
                            parent_btn = arrow.find_element(By.XPATH, "./../..")
                            # Eğer açıksa kapat, kapalıysa dokunma
                            if "expanded" in parent_btn.get_attribute("class") or "rotate" in arrow.get_attribute("style"):
                                driver.execute_script("arguments[0].click();", parent_btn)
                                kapatilan_bos +=1
                    except:
                        pass
                    continue # Boş ligi geç

                # Maç varsa aç
                arrow = league.find_element(By.CSS_SELECTOR, ARROW_ICON_SELECTOR)
                if arrow.is_displayed():
                    parent_btn = arrow.find_element(By.XPATH, "./../..")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'start'});", parent_btn)
                    time.sleep(0.1)
                    # Kapalıysa aç
                    if "expanded" not in parent_btn.get_attribute("class") and "rotate" not in arrow.get_attribute("style"):
                        driver.execute_script("arguments[0].click();", parent_btn)
                        acilan += 1
                        time.sleep(0.25)

            except Exception as e:
                continue

        print(f"✅ {acilan} DOLU lig açıldı | ⏭️ {kapatilan_bos} BOŞ lig kapatıldı/atlandı.")
    except Exception as e:
        print(f"⚠️ Lig açma hatası: {e}")

# =============================================================================
# ✅ SINIRLANDIRILMIŞ KAYDIRMA - SONSUZA KADAR DEĞİL
# =============================================================================
def deep_slow_scroll(driver):
    print("🔄 Sayfa kaydırılıyor (sınırlı mod)...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    same_count = 0
    iteration = 0
    load_more_count = 0 # Kaç kere daha fazla yüklendi sayacı

    while True:
        iteration += 1
        print(f"   ↳ Adım: {iteration}")

        # Yavaşça kaydır
        for i in range(0, last_height, 400):
            driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(0.15)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

        # Daha fazla yükle butonu - SINIRLA
        try:
            if load_more_count >= MAX_LOAD_MORE:
                print(f"⏹️ Maksimum yükleme sayısına ({MAX_LOAD_MORE}) ulaşıldı, duruluyor.")
                break

            load_more_btn = driver.find_element(By.XPATH, LOAD_MORE_XPATH)
            if load_more_btn.is_displayed() and load_more_btn.is_enabled():
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_btn)
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", load_more_btn)
                load_more_count += 1
                print(f"   ➕ Daha fazla yüklendi ({load_more_count}/{MAX_LOAD_MORE})...")
                time.sleep(1.5)
                open_all_leagues(driver) # Yeni gelenleri kontrol et
        except:
            pass

        # Sonu geldi mi kontrol
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            same_count += 1
            if same_count >= 2:
                print("✅ Sayfa sonuna ulaşıldı.")
                break
        else:
            same_count = 0
            last_height = new_height

    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

# =============================================================================
# VERİ ÇEKME & PARSE ETME
# =============================================================================
def parse_match_row(row_element, hedef_tarih_bilgisi):
    try:
        # Bitti durumu kontrolü
        try:
            bitti_kontrol = row_element.find_element(By.XPATH, ".//*[contains(text(), 'Bitti')]")
            if not bitti_kontrol.is_displayed():
                return None
        except:
            return None

        # 1. TAKIM İSİMLERİ
        try:
            ev_sahibi_elem = row_element.find_element(By.CSS_SELECTOR, HOME_TEAM_SELECTOR)
            ev_sahibi = ev_sahibi_elem.get_attribute('innerHTML').strip()
        except NoSuchElementException:
            try:
                ev_sahibi_elem = row_element.find_element(By.CSS_SELECTOR, HOME_TEAM_SELECTOR.replace("bdi", "span"))
        try:
            deplasman_elem = row_element.find_element(By.CSS_SELECTOR, AWAY_TEAM_SELECTOR)
            deplasman = deplasman_elem.get_attribute('innerHTML').strip()
        except NoSuchElementException:
            try:
                deplasman_elem = row_element.find_element(By.CSS_SELECTOR, AWAY_TEAM_SELECTOR.replace("bdi", "span"))
                deplasman = deplasman_elem.text.strip()
            except:
                deplasman = ""

        if not ev_sahibi or not deplasman:
            return None

        # 2. SKORLAR
        ev_skor = 0; dep_skor = 0
        try:
            ev_skor_txt = row_element.find_element(By.CSS_SELECTOR, HOME_SCORE_SELECTOR).text.strip()
            dep_skor_txt = row_element.find_element(By.CSS_SELECTOR, AWAY_SCORE_SELECTOR).text.strip()
            ev_skor = int(ev_skor_txt) if ev_skor_txt.isdigit() else 0
            dep_skor = int(dep_skor_txt) if dep_skor_txt.isdigit() else 0
        except: pass

        # 3. İLK YARI SKORLARI
        iy_ev = 0; iy_dep = 0
        try:
            iy_text = row_element.find_element(By.CSS_SELECTOR, HALF_SCORE_SELECTOR).text.strip()
            rakamlar = re.findall(r"(\d+)", iy_text)
            if len(rakamlar) >= 2:
                iy_ev, iy_dep = int(rakamlar[0]), int(rakamlar[1])
        except: pass

        # 4. SAAT BİLGİSİ
        saat_metni = ""
        try:
            saat_eleman = row_element.find_element(By.CSS_SELECTOR, TIME_SELECTOR)
            saat_metni = saat_eleman.text.strip()
            if not re.match(r"\d{2}:\d{2}", saat_metni):
                saat_bul = re.search(r"\d{2}:\d{2}", saat_metni)
                if saat_bul:
                    saat_metni = saat_bul.group()
        except NoSuchElementException:
            try:
                saat_eleman = row_element.find_element(By.XPATH, ".//span[contains(@class, 'textStyle_display') or contains(@class, 'c_neutrals')]")
                saat_metni = saat_eleman.text.strip()
                if not re.match(r"\d{2}:\d{2}", saat_metni):
                    saat_bul = re.search(r"\d{2}:\d{2}", saat_metni)
                    if saat_bul:
                        saat_metni = saat_bul.group()
            except:
                saat_metni = ""
        except:
            saat_metni = ""

        # ✅ TARİH: DIŞARIDAN GELEN DEĞER KULLANILIR
        tarih = hedef_tarih_bilgisi

        # 5. MAÇ ID'Sİ
        sofascore_id = "0"
        try:
            img_elem = row_element.find_element(By.CSS_SELECTOR, HOME_IMG_SELECTOR)
            src_link = img_elem.get_attribute("src")
            id_match = re.search(r"/team/(\d+)/|image/(\d+)", src_link)
            if id_match:
                if id_match.group(1):
                    sofascore_id = id_match.group(1)
                elif id_match.group(2):
                    sofascore_id = id_match.group(2)
        except:
            pass

        # 6. VERİYİ DÖNDÜR
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
            "durum": "bitti",
            "cekme_zamani": datetime.datetime.now().isoformat()
        }

    except Exception as e:
        return None

# =============================================================================
# TARİH SİSTEMİ
# =============================================================================
def get_data_for_all_days(driver):
    all_collected_data = []
    bugun = datetime.date.today()

    target_dates = [
        ("Bugün", bugun.isoformat()),
        ("Dün", (bugun - datetime.timedelta(days=1)).isoformat()),
        ("Evvelsi Gün", (bugun - datetime.timedelta(days=2)).isoformat()),
        ("2 gün önce", (bugun - datetime.timedelta(days=2)).isoformat())
    ]

    print("\n🗓️  TARANACAK TARİHLER:")
    for ad, tar in target_dates[:3]:
        print(f"   ➤ {ad}: {tar}")
    print("-" * 50)

    islenen_tarihler = set()

    for gun_ismi, gunun_tarihi in target_dates:
        if gunun_tarihi in islenen_tarihler:
            continue

        print(f"\n🔘 {gun_ismi} işlemi başlıyor — Hedef: {gunun_tarihi}")

        try:
            date_buttons = driver.find_elements(By.XPATH, DATE_BUTTONS_XPATH)
            tiklandi = False

            for btn in date_buttons:
                if btn.is_displayed and gun_ismi.lower() in btn.text.lower():
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                    time.sleep(0.3)
                    try:
                        btn.click()
                    except ElementClickInterceptedException:
                        driver.execute_script("arguments[0].click();", btn)
                    print(f"✅ '{gun_ismi}' butonuna basıldı.")
                    tiklandi = True
                    time.sleep(WAIT_LONG / 3)
                    break

            if not tiklandi:
                print(f"⚠️ '{gun_ismi}' butonu bulunamadı, atlanıyor.")
                continue

            # ✅ GELİŞMİŞ AÇMA: Sadece dolu ligleri açar, boş olanları kapatır
            open_all_leagues(driver)

            # ✅ SINIRLI KAYDIRMA: En fazla 5 kez "Daha fazla" yükler, sonsuz döngü engellendi
            deep_slow_scroll(driver)

            rows = driver.find_elements(By.CSS_SELECTOR, MATCH_ROW_SELECTOR)
            print(f"📋 {gun_ismi}: {len(rows)} satır bulundu, filtreleniyor...")

            kontrol_seti = set()
            for row in rows:
                veri = parse_match_row(row, gunun_tarihi)
                if veri:
                    essiz_id = f"{veri['tarih']}|{veri['sp_home']}|{veri['sp_away']}"
                    if essiz_id not in kontrol_seti:
                        kontrol_seti.add(essiz_id)
                        all_collected_data.append(veri)
                        print(f"   ✅ Alındı: {veri['sp_home']} - {veri['sp_away']} | Skor: {veri['skor1']}-{veri['skor2']}")

            islenen_tarihler.add(gunun_tarihi)
            print(f"✅ {gun_ismi} tamamlandı.")

        except Exception as e:
            print(f"❌ Hata ({gun_ismi}): {str(e)}")
            continue

    return all_collected_data

# =============================================================================
# VERİTABANI GÜNCELLEME
# =============================================================================
def update_db(db_data: dict, scores: list, today_iso: str):
    matches = db_data.get("matches", [])
    if not isinstance(matches, list):
        matches = []
        db_data["matches"] = []

    uid_set = set()
    by_date = {}
    for m in matches:
        if m.get("tarih") and m.get("ev_sahibi") and m.get("deplasman"):
            uid = match_uid(m["tarih"], m["ev_sahibi"], m["deplasman"])
            uid_set.add(uid)
            by_date.setdefault(m["tarih"], []).append(m)

    matched = updated = noop = added = skipped = not_matched = 0

    for sp in scores:
        cands = by_date.get(sp["tarih"], [])
        best_match = None
        best_score = -1.0
        second_best_score = -1.0

        for m in cands:
            sc = match_score(m.get("ev_sahibi", ""), m.get("deplasman", ""), sp["sp_home"], sp["sp_away"])
            if sc > best_score:
                second_best_score = best_score
                best_score = sc
                best_match = m
            elif sc > second_best_score:
                second_best_score = sc

        if best_match and best_score >= THRESH_MAYBE and (best_score - second_best_score) >= MIN_GAP:
            if best_score >= THRESH_OK:
                matched += 1

                s_direct = team_sim(best_match.get("ev_sahibi", ""), sp["sp_home"]) + team_sim(best_match.get("deplasman", ""), sp["sp_away"])
                s_swap = team_sim(best_match.get("ev_sahibi", ""), sp["sp_away"]) + team_sim(best_match.get("deplasman", ""), sp["sp_home"])

                if s_swap > s_direct:
                    skor_ev, skor_dep = sp["skor2"], sp["skor1"]
                    iy_ev, iy_dep = sp.get("iy_skor2", 0), sp.get("iy_skor1", 0)
                else:
                    skor_ev, skor_dep = sp["skor1"], sp["skor2"]
                    iy_ev, iy_dep = sp.get("iy_skor1", 0), sp.get("iy_skor2", 0)

                changed = (
                    best_match.get("skor_ev") != skor_ev or
                    best_match.get("skor_dep") != skor_dep or
                    best_match.get("skor_1y_ev") != iy_ev or
                    best_match.get("skor_1y_dep") != iy_dep or
                    best_match.get("sofascore_id") != sp["sofascore_id"]
                )

                best_match["skor_ev"] = skor_ev
                best_match["skor_dep"] = skor_dep
                best_match["skor_1y_ev"] = iy_ev
                best_match["skor_1y_dep"] = iy_dep
                best_match["durum"] = "bitti" if (skor_ev + skor_dep) > 0 else "bekliyor"
                best_match["sofascore_id"] = sp["sofascore_id"]
                best_match["kaynak"] = "sofascore.com"
                best_match["cekme_zamani"] = sp["cekme_zamani"]

                if changed:
                    updated += 1
                else:
                    noop += 1
                continue

            skipped += 1
            continue

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
            else:
                not_matched += 1
        else:
            not_matched += 1

    db_data["matches"] = sorted(matches, key=lambda x: (x.get("tarih", ""), x.get("saat", "00:00"), x.get("ev_sahibi", "")))
    for i, item in enumerate(db_data["matches"], 1):
        item["index"] = i

    db_data["updated"] = datetime.datetime.now().isoformat()
    return matched, updated, noop, added, skipped, not_matched

# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================
def main():
    print("=" * 70)
    print("⚽ SOFASCORE - TARİH SİSTEMİ SABİTLENDİ | SADECE BİTMİŞ MAÇLAR")
    print("=" * 70)
    print(f"⏩ Ayarlar: Son {TARGET_DAYS} Gün | Lig Açma: AKTİF | Kaydırma: SINIRLI (Max {MAX_LOAD_MORE})")
    print("📌 Sistem: O anki tarih baz alınır, sayfanın yazısı dikkate alınmaz!")
    print("📌 Filtre: Sadece 'Bitti' durumunda olan maçlar çekilir.")
    print("📌 Optimizasyon: Boş ligler otomatik kapatılır/atlanır.")
    print("-" * 70)

    bugun_iso = datetime.date.today().isoformat()
    driver = None
    all_scores = []

    try:
        driver = build_driver()
        print(f"🌐 Adrese gidiliyor: {SOFASCORE_URL}")
        driver.get(SOFASCORE_URL)

        try:
            WebDriverWait(driver, WAIT_LONG).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, MATCH_ROW_SELECTOR))
            )
            print("✅ Ana sayfa başarıyla yüklendi.")
        except TimeoutException:
            print("❌ HATA: Sayfa zaman aşımına uğradı veya maç listesi bulunamadı!")
            return

        time.sleep(3)
        all_scores = get_data_for_all_days(driver)

        print(f"\n📊 TOPLAMDA {len(all_scores)} adet maç verisi başarıyla çekildi!")

        save_json_atomic({
            "olusturulma_tarihi": datetime.datetime.now().isoformat(),
            "kaynak": SOFASCORE_URL,
            "gun_geriye_donuk": TARGET_DAYS,
            "veri": all_scores
        }, OUTPUT_SKOR_JSON)

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

        if UPDATE_GECMIS_JSON:
            print("\n🔄 Geçmiş dosya (gecmis_maclar.json) güncelleniyor...")
            gecmis_veri = load_json_safe(GECMIS_JSON_PATH)
            update_db(gecmis_veri, all_scores, bugun_iso)
            save_json_atomic(gecmis_veri, GECMIS_JSON_PATH)

    except Exception as genel_hata:
        print(f"❌ KRİTİK HATA: {genel_hata}")
        traceback.print_exc()

    finally:
        if driver:
            try:
                driver.quit()
                print("🗑️ Tarayıcı başarıyla kapatıldı.")