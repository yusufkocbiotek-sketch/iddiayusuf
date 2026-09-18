import time
import json
import shutil
import subprocess
import traceback
import re
from datetime import date, timedelta, datetime
from pathlib import Path
from difflib import SequenceMatcher

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


# ============================================================
# AYARLAR
# ============================================================

URL = "https://www.iddaa.com/program/futbol"

OUT_DIR = Path(r"C:\Users\YUSUF\OneDrive\Desktop\iddaa_scraper_output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# GG/AA/YYYY formatında yazın
BASLANGIC_TARIHI = "01/09/2026"
BITIS_TARIHI = "16/09/2026"

# Takım adı benzerlik eşleşme ayarları
ESLESME_TOLERANSI_GUN = 15
BENZERLIK_ESIK = 0.60

# Sayfa yüklenme/bekleme süreleri
SAYFA_BEKLEME_SURESI = 4
ELEMENT_BEKLEME_SURESI = 15


# ============================================================
# TARİH / İSİM YARDIMCI FONKSİYONLARI
# ============================================================

def temiz_isim(text):
    """Takım isimlerini fuzzy eşleşme için normalize eder."""
    text = str(text or "").lower().strip()

    # Türkçe karakterleri koruyarak özel karakterleri temizle
    text = re.sub(r"[^a-z0-9çğıöşü ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def benzerlik(a, b):
    """0 ile 1 arasında isim benzerliği döndürür."""
    return SequenceMatcher(None, temiz_isim(a), temiz_isim(b)).ratio()


def parse_tarih(tarih_degeri):
    """
    Birden fazla tarih formatını date nesnesine çevirmeye çalışır.

    Desteklenen örnekler:
    - 2026-09-17
    - 17.09.2026
    - 17/09/2026
    - 2026-09-17T12:00:00
    """
    if not tarih_degeri:
        return None

    tarih_str = str(tarih_degeri).strip()

    # ISO datetime varsa sadece tarih tarafını kullan
    tarih_str = tarih_str.split("T")[0].split(" ")[0]

    formats = [
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(tarih_str, fmt).date()
        except ValueError:
            pass

    return None


def tarih_farki(t1, t2):
    """İki tarih arasındaki gün farkını döndürür."""
    d1 = parse_tarih(t1)
    d2 = parse_tarih(t2)

    if not d1 or not d2:
        return 999

    return abs((d1 - d2).days)


def tarih_araligi_olustur(baslangic, bitis):
    """
    GG/AA/YYYY formatındaki başlangıç-bitiş tarihleri arasındaki
    tüm günleri listeler.
    """
    bas = datetime.strptime(baslangic, "%d/%m/%Y").date()
    son = datetime.strptime(bitis, "%d/%m/%Y").date()

    if bas > son:
        raise ValueError("BASLANGIC_TARIHI, BITIS_TARIHI'nden büyük olamaz.")

    tarihler = []

    while bas <= son:
        tarihler.append(bas)
        bas += timedelta(days=1)

    return tarihler


# ============================================================
# DOSYA YOLU BULMA
# ============================================================

def get_mac_json_path():
    """mac.json dosyasını olası klasörlerde bulur."""

    olasi_yollar = [
        Path(r"C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main\public\data\mac.json"),
        Path(r"C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\mac.json"),
    ]

    for path in olasi_yollar:
        if path.exists():
            return path

    # Script'in bulunduğu konumdan yukarı doğru arama yap
    try:
        current = Path(__file__).resolve().parent

        for _ in range(8):
            test_path = current / "public" / "data" / "mac.json"

            if test_path.exists():
                return test_path

            if current.parent == current:
                break

            current = current.parent

    except Exception:
        pass

    # Bulunamazsa varsayılan yolu döndürür
    return olasi_yollar[0]


MAC_JSON_PATH = get_mac_json_path()


# ============================================================
# SELENIUM / TARAYICI
# ============================================================

def build_driver():
    """Chrome WebDriver oluşturur."""

    options = Options()

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    options.add_experimental_option(
        "useAutomationExtension",
        False
    )

    driver = webdriver.Chrome(options=options)

    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    driver.set_page_load_timeout(60)

    return driver


def dismiss_cookies(driver):
    """Çerez popup'ı çıkarsa kapatmayı dener."""

    cookie_xpaths = [
        "//button[contains(translate(., 'KABUL', 'kabul'), 'kabul')]",
        "//button[contains(translate(., 'ACCEPT', 'accept'), 'accept')]",
        "//button[contains(., 'Tümünü Kabul Et')]",
        "//button[@id='onetrust-accept-btn-handler']",
        "//button[contains(@id, 'accept')]",
    ]

    for xpath in cookie_xpaths:
        try:
            buttons = driver.find_elements(By.XPATH, xpath)

            for button in buttons:
                if button.is_displayed():
                    driver.execute_script(
                        "arguments[0].click();",
                        button
                    )
                    time.sleep(1)
                    print("🍪 Çerez bildirimi kapatıldı.")
                    return True

        except Exception:
            pass

    return False


def sayfada_mac_icerigi_var_mi(driver):
    """
    Bulunulan sayfa/iframe içinde maç içeriği olabilecek elemanların
    olup olmadığını kontrol eder.
    """

    selectors = [
        "h3[data-testid='tournament-name-link']",
        ".rounded-match__score",
        "[role='row']",
        ".truncate",
    ]

    for selector in selectors:
        try:
            if driver.find_elements(By.CSS_SELECTOR, selector):
                return True
        except Exception:
            pass

    return False


def mac_icerik_contextine_gec(driver):
    """
    Maç listesi ana sayfadaysa ana sayfada kalır.
    Maç listesi iframe içindeyse uygun iframe'e geçer.

    Başarılı olursa driver doğru context içinde kalır.
    """

    driver.switch_to.default_content()

    # Önce ana sayfada ara
    if sayfada_mac_icerigi_var_mi(driver):
        return True

    # Sonra iframe'lerde ara
    iframes = driver.find_elements(By.TAG_NAME, "iframe")

    for index, iframe in enumerate(iframes):
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(iframe)

            time.sleep(0.5)

            if sayfada_mac_icerigi_var_mi(driver):
                print(f"🖼️ Maç içeriği iframe içinde bulundu. iframe no: {index}")
                return True

        except Exception:
            pass

    driver.switch_to.default_content()
    return False


def sayfa_yuklenmesini_bekle(driver, timeout=20):
    """document.readyState complete olana kadar bekler."""

    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )
        return True
    except Exception:
        return False


def mac_elemanlarini_bekle(driver, timeout=ELEMENT_BEKLEME_SURESI):
    """Sayfada maç/lig elemanları görünene kadar bekler."""

    try:
        WebDriverWait(driver, timeout).until(
            lambda d: (
                len(
                    d.find_elements(
                        By.CSS_SELECTOR,
                        "h3[data-testid='tournament-name-link'], "
                        ".rounded-match__score, "
                        ".truncate, "
                        "[role='row']"
                    )
                ) > 0
            )
        )
        return True

    except Exception:
        return False


# ============================================================
# MAÇ VERİSİ ÇEKME
# ============================================================

def extract_matches_with_js(driver, target_date_str):
    """
    Sayfadaki maçları JavaScript ile çeker.

    target_date_str:
        mac.json için ISO formatında tarih: YYYY-MM-DD
    """

    try:
        driver.execute_script("""
            window.scrollTo(0, document.body.scrollHeight);
        """)
        time.sleep(2)

        driver.execute_script("""
            window.scrollTo(0, 0);
        """)
        time.sleep(1)

    except Exception:
        pass

    js_code = r"""
        const results = [];
        const processedRows = new Set();

        let currentLeague = "Bilinmeyen Lig";

        const allElements = document.querySelectorAll(
            "h3[data-testid='tournament-name-link'], " +
            ".rounded-match__score, " +
            "div.w-6, " +
            "[role='row']"
        );

        allElements.forEach(el => {

            // Lig başlığı
            if (
                el.tagName === "H3" &&
                el.getAttribute("data-testid") === "tournament-name-link"
            ) {
                let leagueText = (el.innerText || el.textContent || "")
                    .replace(/\n/g, " ")
                    .replace(/\s+/g, " ")
                    .trim();

                leagueText = leagueText
                    .replace(/Favorilere ekle/gi, "")
                    .replace(/\bMS\b/gi, "")
                    .replace(/\bİY\b/gi, "")
                    .replace(/\bIY\b/gi, "")
                    .replace(/arrow/gi, "")
                    .trim();

                if (leagueText) {
                    currentLeague = leagueText;
                }

                return;
            }

            // Maç satırını bulmaya çalış
            let row =
                el.closest("[role='row']") ||
                el.closest(".rounded-match") ||
                el.closest("[data-testid*='match']") ||
                el.parentElement?.parentElement;

            if (!row || processedRows.has(row)) {
                return;
            }

            let truncates = Array.from(
                row.querySelectorAll(".truncate")
            )
            .map(item => (item.innerText || item.textContent || "").trim())
            .filter(text => {
                if (!text || text.length < 2) return false;

                return !/Favorilere|arrow|MS|İY|IY/i.test(text);
            });

            // Takım adları minimum iki adet olmalı
            if (truncates.length < 2) {
                return;
            }

            const home = truncates[0];
            const away = truncates[1];

            // Çok kısa / anlamsız satırları ele
            if (
                home.length < 2 ||
                away.length < 2 ||
                home === away
            ) {
                return;
            }

            processedRows.add(row);

            // Skor kutularından sadece sayıları al
            let scoreBoxes = Array.from(
                row.querySelectorAll(".rounded-match__score, div.w-6")
            );

            let numbers = [];

            scoreBoxes.forEach(box => {
                let value = (box.innerText || box.textContent || "")
                    .trim();

                if (/^\d+$/.test(value)) {
                    numbers.push(value);
                }
            });

            let msScore = "-";
            let iyHome = "-";
            let iyAway = "-";

            // İlk iki sayı: maç sonu skoru
            if (numbers.length >= 2) {
                msScore = numbers[0] + "-" + numbers[1];
            }

            // Sonraki iki sayı: ilk yarı skoru varsayımı
            if (numbers.length >= 4) {
                iyHome = numbers[2];
                iyAway = numbers[3];
            }

            const rowText = (row.innerText || row.textContent || "");
            const lines = rowText
                .split("\n")
                .map(line => line.trim())
                .filter(line => line.length > 0);

            const statusRegex =
                /^(\d{1,3}['’.]?|\d{1,2}:\d{2}|MS|İY|IY|Bitti|Canlı|Başlamadı|ERT|TAT)$/i;

            let status = lines.find(line => statusRegex.test(line)) || "MS";

            if (!status || status === "-") {
                status = "MS";
            }

            results.push({
                tarih: arguments[0],
                league: currentLeague,
                home: home,
                away: away,
                score: msScore,
                iy_home: iyHome,
                iy_away: iyAway,
                status: status
            });
        });

        // Aynı maçın tekrar gelmesini engelle
        const unique = [];
        const seen = new Set();

        results.forEach(match => {
            const key =
                match.tarih + "|" +
                match.home.toLowerCase() + "|" +
                match.away.toLowerCase();

            if (!seen.has(key)) {
                seen.add(key);
                unique.push(match);
            }
        });

        return unique;
    """

    try:
        matches = driver.execute_script(js_code, target_date_str)
        return matches or []

    except Exception as exc:
        print(f"❌ JavaScript maç çekme hatası: {exc}")
        return []


# ============================================================
# MAC.JSON GÜNCELLEME
# ============================================================

def update_mac_json_safely(scraped_matches):
    """
    mac.json dosyasını yedek alarak günceller.
    Takım isimleri fuzzy eşleşme + tarih toleransı ile karşılaştırılır.
    """

    print("\n" + "=" * 75)
    print("🔄 MAC.JSON GÜNCELLEME BAŞLIYOR")
    print("=" * 75)
    print(f"📁 mac.json yolu: {MAC_JSON_PATH}")

    if not MAC_JSON_PATH.exists():
        print("❌ mac.json bulunamadı.")
        return 0

    # Yedek al
    backup_name = f"mac_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    backup_path = OUT_DIR / backup_name

    try:
        shutil.copy2(MAC_JSON_PATH, backup_path)
        print(f"💾 Yedek oluşturuldu: {backup_path}")
    except Exception as exc:
        print(f"❌ Yedek alınamadı: {exc}")
        return 0

    # JSON dosyasını oku
    try:
        with open(MAC_JSON_PATH, "r", encoding="utf-8") as file:
            original_data = json.load(file)

    except Exception as exc:
        print(f"❌ mac.json okunamadı: {exc}")
        return 0

    def clean_name(name):
        return temiz_isim(name)

    # Geçerli skor içeren çekilmiş maçlar
    valid_scraped_matches = []

    for match in scraped_matches:
        home = clean_name(
            match.get("home") or match.get("ev_sahibi") or ""
        )
        away = clean_name(
            match.get("away") or match.get("deplasman") or ""
        )

        score = str(match.get("score", "")).strip()

        if not home or not away:
            continue

        if "-" not in score:
            continue

        try:
            score_parts = score.split("-")

            if len(score_parts) != 2:
                continue

            int(score_parts[0].strip())
            int(score_parts[1].strip())

            valid_scraped_matches.append(match)

        except Exception:
            continue

    print(f"📊 Geçerli skor içeren çekilmiş maç sayısı: {len(valid_scraped_matches)}")

    updated_count = 0
    checked_count = 0
    matched_scraped_keys = set()

    def update_match_obj(obj):
        nonlocal updated_count, checked_count

        if not isinstance(obj, dict):
            return

        home = clean_name(
            obj.get("home") or
            obj.get("ev_sahibi") or
            obj.get("ev") or
            obj.get("homeTeam") or ""
        )

        away = clean_name(
            obj.get("away") or
            obj.get("deplasman") or
            obj.get("dep") or
            obj.get("awayTeam") or ""
        )

        if not home or not away or home == "?" or away == "?":
            return

        checked_count += 1

        json_tarih = (
            obj.get("tarih") or
            obj.get("date") or
            ""
        )

        best_match = None
        best_total_score = 0
        best_home_score = 0
        best_away_score = 0

        # En iyi fuzzy eşleşmeyi bul
        for scraped in valid_scraped_matches:
            scraped_home = clean_name(scraped.get("home", ""))
            scraped_away = clean_name(scraped.get("away", ""))
            scraped_tarih = scraped.get("tarih", "")

            # Tarihler varsa tolerans kontrolü yap
            if json_tarih and scraped_tarih:
                gun_farki = tarih_farki(json_tarih, scraped_tarih)

                if gun_farki > ESLESME_TOLERANSI_GUN:
                    continue

            home_score = benzerlik(home, scraped_home)
            away_score = benzerlik(away, scraped_away)

            # Her iki takım da eşik üstünde olmalı
            if home_score < BENZERLIK_ESIK:
                continue

            if away_score < BENZERLIK_ESIK:
                continue

            total_score = home_score + away_score

            # İlk uygun olanı değil, en iyi eşleşmeyi seç
            if total_score > best_total_score:
                best_total_score = total_score
                best_match = scraped
                best_home_score = home_score
                best_away_score = away_score

        if not best_match:
            return

        score = str(best_match.get("score", "")).strip()

        try:
            new_home_score, new_away_score = map(
                int,
                score.split("-")
            )
        except Exception:
            return

        iy_home_raw = str(best_match.get("iy_home", "")).strip()
        iy_away_raw = str(best_match.get("iy_away", "")).strip()

        new_iy_home = int(iy_home_raw) if iy_home_raw.isdigit() else 0
        new_iy_away = int(iy_away_raw) if iy_away_raw.isdigit() else 0

        # Önceki değerleri al
        old_home_score = obj.get("skor_ev")
        old_away_score = obj.get("skor_dep")
        old_status = obj.get("durum")

        # Verileri güncelle
        obj["skor_ev"] = new_home_score
        obj["skor_dep"] = new_away_score
        obj["skor_1y_ev"] = new_iy_home
        obj["skor_1y_dep"] = new_iy_away
        obj["durum"] = "bitti"
        obj["kaynak"] = "iddaa.com"
        obj["cekme_zamani"] = datetime.now().isoformat()

        scraped_key = (
            f"{best_match.get('tarih')}|"
            f"{clean_name(best_match.get('home'))}|"
            f"{clean_name(best_match.get('away'))}"
        )

        matched_scraped_keys.add(scraped_key)

        # Gerçekten veri değiştiyse sayaç artır
        if (
            old_home_score != new_home_score or
            old_away_score != new_away_score or
            old_status != "bitti"
        ):
            updated_count += 1

            print(
                f"✅ EŞLEŞTİ / GÜNCELLENDİ: "
                f"{obj.get('ev_sahibi', obj.get('home', '?'))} vs "
                f"{obj.get('deplasman', obj.get('away', '?'))} | "
                f"MS: {new_home_score}-{new_away_score} | "
                f"İY: {new_iy_home}-{new_iy_away} | "
                f"Benzerlik: Ev={best_home_score:.2f}, Dep={best_away_score:.2f}"
            )

    def traverse_and_update(data):
        """JSON içindeki tüm dict/list elemanlarını dolaşır."""

        if isinstance(data, dict):
            update_match_obj(data)

            for value in data.values():
                traverse_and_update(value)

        elif isinstance(data, list):
            for item in data:
                traverse_and_update(item)

    traverse_and_update(original_data)

    # Güncellenmiş JSON'u yaz
    try:
        with open(MAC_JSON_PATH, "w", encoding="utf-8") as file:
            json.dump(
                original_data,
                file,
                ensure_ascii=False,
                indent=2
            )

    except Exception as exc:
        print(f"❌ mac.json yazılamadı: {exc}")
        return 0

    # Eşleşmeyen çekilmiş maçları bul
    unmatched_scraped = []

    for scraped in valid_scraped_matches:
        key = (
            f"{scraped.get('tarih')}|"
            f"{clean_name(scraped.get('home'))}|"
            f"{clean_name(scraped.get('away'))}"
        )

        if key not in matched_scraped_keys:
            unmatched_scraped.append(scraped)

    print("\n" + "=" * 75)
    print("✅ MAC.JSON GÜNCELLEME TAMAMLANDI")
    print("=" * 75)
    print(f"📌 Kontrol edilen mac.json maç kaydı: {checked_count}")
    print(f"✅ Güncellenen maç sayısı: {updated_count}")
    print(f"⚠️ Eşleşmeyen çekilmiş maç sayısı: {len(unmatched_scraped)}")

    if unmatched_scraped:
        unmatched_file = OUT_DIR / (
            f"unmatched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        unmatched_file.write_text(
            json.dumps(
                unmatched_scraped,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print(f"📋 Eşleşmeyenler kaydedildi: {unmatched_file}")

    return updated_count


# ============================================================
# GIT COMMIT / PUSH
# ============================================================

def auto_git_commit_and_push(updated_count):
    """mac.json değiştiyse Git add, commit ve push yapar."""

    if updated_count <= 0:
        print("\nℹ️ Güncellenen maç olmadığı için Git işlemi atlandı.")
        return

    print("\n" + "=" * 75)
    print("🚀 GIT OTOMASYONU BAŞLIYOR")
    print("=" * 75)

    try:
        # mac.json -> data -> public -> repo dizini
        fallback_repo_dir = MAC_JSON_PATH.parent.parent.parent

        # Daha güvenli Git repo kökü bulma
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=fallback_repo_dir,
            capture_output=True,
            text=True,
            check=True
        )

        repo_dir = Path(result.stdout.strip())

        relative_file_path = MAC_JSON_PATH.relative_to(repo_dir)

        print(f"📁 Repo klasörü: {repo_dir}")
        print(f"📄 Güncellenecek dosya: {relative_file_path}")

        # Sadece mac.json dosyasını stage'e ekle
        subprocess.run(
            ["git", "add", str(relative_file_path)],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )

        # Stage edilmiş değişiklik var mı?
        diff_result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )

        # returncode 0 = fark yok
        if diff_result.returncode == 0:
            print("ℹ️ Git commit gerektiren yeni değişiklik bulunamadı.")
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        commit_message = (
            f"Otomatik skor güncellemesi: "
            f"{updated_count} maç güncellendi ({now})"
        )

        print(f"📝 Commit mesajı: {commit_message}")

        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )

        print("☁️ Git push yapılıyor...")

        push_result = subprocess.run(
            ["git", "push"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )

        if push_result.returncode == 0:
            print("✅ Git push başarılı.")
        else:
            print("⚠️ Commit atıldı fakat push başarısız oldu.")
            print(push_result.stderr)

    except FileNotFoundError:
        print("❌ Git bulunamadı. Git PATH'e ekli olmayabilir.")

    except subprocess.CalledProcessError as exc:
        print("❌ Git komutu hata verdi.")
        print(exc.stderr)

    except Exception as exc:
        print(f"❌ Git işlemi sırasında beklenmeyen hata: {exc}")


# ============================================================
# ANA PROGRAM
# ============================================================

def main():
    driver = None

    try:
        print("=" * 75)
        print("🌐 İDDAA FUTBOL MAÇ SKOR SCRAPER BAŞLATILIYOR")
        print("=" * 75)

        print("📆 Tarih aralığı hazırlanıyor...")

        dates_to_fetch = tarih_araligi_olustur(
            BASLANGIC_TARIHI,
            BITIS_TARIHI
        )

        print(
            f"📅 Tarih aralığı: {BASLANGIC_TARIHI} -> {BITIS_TARIHI}"
        )
        print(f"📌 Toplam gün sayısı: {len(dates_to_fetch)}")

        print("\n🌐 Chrome tarayıcı başlatılıyor...")
        driver = build_driver()

        all_scraped_matches = []

        for target_date in dates_to_fetch:
            # mac.json eşleşmesi için ISO tarih
            iso_date_str = target_date.strftime("%Y-%m-%d")

            # iddaa URL'si için GG.AA.YYYY formatı
            iddaa_date_str = target_date.strftime("%d.%m.%Y")

            # Örnek:
            # https://www.iddaa.com/program/futbol?date=17.09.2026
            date_url = f"{URL}?date={iddaa_date_str}"

            print("\n" + "=" * 90)
            print(f"📅 TARİH İŞLENİYOR: {iso_date_str}")
            print(f"🌐 URL: {date_url}")
            print("=" * 90)

            try:
                # Önceki iframe contextinden çık
                driver.switch_to.default_content()

                # Takvim kullanmadan direkt ilgili güne git
                driver.get(date_url)

                sayfa_yuklenmesini_bekle(driver, timeout=25)
                time.sleep(SAYFA_BEKLEME_SURESI)

                # Cookie tekrar görünürse kapat
                dismiss_cookies(driver)

                # Maçlar ana sayfada mı iframe içinde mi bul
                context_found = mac_icerik_contextine_gec(driver)

                if not context_found:
                    print("⚠️ Maç içerik alanı bulunamadı.")
                    print("⚠️ Bu tarihte maç olmayabilir veya site HTML yapısı değişmiş olabilir.")
                    continue

                # Dinamik verilerin yüklenmesini bekle
                elements_found = mac_elemanlarini_bekle(driver)

                if not elements_found:
                    print("⚠️ Maç elemanları beklenen sürede yüklenmedi.")
                    print("⚠️ Buna rağmen veri çekme işlemi denenecek.")

                time.sleep(2)

                matches = extract_matches_with_js(
                    driver,
                    iso_date_str
                )

                all_scraped_matches.extend(matches)

                print(f"\n✅ {iso_date_str} için çekilen maç sayısı: {len(matches)}")

                if matches:
                    print(f"\n📋 [{iso_date_str}] MAÇ LİSTESİ")
                    print("-" * 115)

                    for index, match in enumerate(matches, start=1):
                        league = match.get("league", "Bilinmeyen Lig")
                        home = match.get("home", "?")
                        away = match.get("away", "?")
                        score = match.get("score", "-")
                        iy_home = match.get("iy_home", "-")
                        iy_away = match.get("iy_away", "-")
                        status = match.get("status", "MS")

                        iy_score = (
                            f"{iy_home}-{iy_away}"
                            if iy_home != "-" and iy_away != "-"
                            else "-"
                        )

                        print(
                            f"[{index:02d}] "
                            f"🏆 {league[:25]:<25} | "
                            f"⚽ {home[:20]:<20} vs {away[:20]:<20} | "
                            f"🏁 MS: {score:<7} | "
                            f"⏱️ İY: {iy_score:<7} | "
                            f"📌 {status}"
                        )

                    print("-" * 115)

                else:
                    print(f"ℹ️ {iso_date_str} tarihinde maç verisi bulunamadı.")

            except Exception as exc:
                print(f"❌ {iso_date_str} tarihi işlenirken hata oluştu: {exc}")
                traceback.print_exc()

        # Tüm tarihlerin özeti
        print("\n" + "=" * 90)
        print("🎉 TARİH TARAMASI TAMAMLANDI")
        print("=" * 90)
        print(f"📊 Toplam çekilen maç sayısı: {len(all_scraped_matches)}")

        if not all_scraped_matches:
            print("⚠️ Hiç maç verisi çekilemedi.")
            return

        # Ham veriyi kaydet
        output_file = OUT_DIR / (
            f"matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        output_file.write_text(
            json.dumps(
                all_scraped_matches,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print(f"💾 Ham çekilen veri kaydedildi: {output_file}")

        # mac.json güncelle
        updated_count = update_mac_json_safely(all_scraped_matches)

        # Git commit / push
        auto_git_commit_and_push(updated_count)

    except KeyboardInterrupt:
        print("\n⚠️ İşlem kullanıcı tarafından durduruldu.")

    except Exception:
        print("\n❌ KRİTİK HATA OLUŞTU:")
        traceback.print_exc()

    finally:
        if driver:
            try:
                driver.quit()
                print("\n🧹 Tarayıcı kapatıldı.")
            except Exception:
                pass

        print("\n" + "=" * 75)

        try:
            input("Çıkmak için Enter tuşuna basın...")
        except EOFError:
            pass


if __name__ == "__main__":
    main()