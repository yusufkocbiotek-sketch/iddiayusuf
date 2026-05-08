import json
import os
import datetime
import time
import shutil
import subprocess
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

CIKTI_DOSYA = "public/data/mac.json"

# =========================
# GIT OTOMATİK COMMIT/PUSH
# =========================
ENABLE_GIT_AUTOPUSH = True          # İstemezsen False yap
GIT_STAGE_FILES = [CIKTI_DOSYA]     # Sadece mac.json stage edilecek

REPO_ROOT = Path(__file__).resolve().parent  # scriptin bulunduğu klasör (repo kökü varsayımı)

def _find_git_exe():
    exe = shutil.which("git")
    if exe:
        return exe

    candidates = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def _run_git(args, cwd=None):
    git_exe = _find_git_exe()
    if not git_exe:
        raise RuntimeError("Git bulunamadı. Git for Windows kur veya PATH'e ekle.")
    return subprocess.run([git_exe, *args], cwd=cwd, text=True, capture_output=True)

def _turkce_gun_kisa(dt: datetime.datetime) -> str:
    # Monday=0 .. Sunday=6
    mapping = ["Pts", "Sal", "Çar", "Per", "Cum", "Cts", "Paz"]
    return mapping[dt.weekday()]

def _format_commit_msg(dt: datetime.datetime) -> str:
    # ör: "Otomatik hizli guncelleme Per 07.05.2026 06:33:35,94"
    cs = int(dt.microsecond / 10000)  # centisecond 0-99
    return f"Otomatik hizli guncelleme {_turkce_gun_kisa(dt)} {dt.strftime('%d.%m.%Y %H:%M:%S')},{cs:02d}"

def git_add_commit_pull_push():
    if not ENABLE_GIT_AUTOPUSH:
        return

    if not (REPO_ROOT / ".git").exists():
        print("⚠️ Git: .git yok, repo değil. Otomatik push atlandı.")
        return

    try:
        # add (sadece hedef dosyalar)
        r = _run_git(["add", *GIT_STAGE_FILES], cwd=str(REPO_ROOT))
        if r.returncode != 0:
            print("⚠️ git add hata:", (r.stderr or r.stdout).strip())
            return

        # staged değişiklik var mı?
        r = _run_git(["diff", "--cached", "--quiet"], cwd=str(REPO_ROOT))
        if r.returncode == 0:
            print("ℹ️ Git: Değişiklik yok -> commit/push yapılmadı.")
            return

        # commit
        msg = _format_commit_msg(datetime.datetime.now())
        r = _run_git(["commit", "-m", msg], cwd=str(REPO_ROOT))
        if r.returncode != 0:
            print("⚠️ git commit hata:", (r.stderr or r.stdout).strip())
            return
        print(f"✅ Git commit: {msg}")

        # pull --rebase (push reddini engellemek için)
        r = _run_git(["pull", "--rebase", "--autostash"], cwd=str(REPO_ROOT))
        if r.returncode != 0:
            print("⚠️ git pull --rebase hata:", (r.stderr or r.stdout).strip())
            print("💡 Çakışma olabilir. Manuel düzeltip push atman gerekebilir.")
            return

        # push
        r = _run_git(["push"], cwd=str(REPO_ROOT))
        if r.returncode != 0:
            print("⚠️ git push hata:", (r.stderr or r.stdout).strip())
            print("💡 Kimlik doğrulama/remote sorunu olabilir. Manuel push deneyin.")
            return

        print("✅ Git push tamamlandı.")

    except Exception as e:
        print(f"⚠️ Git otomasyon hatası: {e}")

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # --- BOT KORUMASI AŞMA AYARLARI ---
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    # ---------------------------------

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Tarayıcıya "Ben bir bot değilim" sinyalini ver (webdriver özelliğini sil)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    print("✅ Chrome başlatıldı!")
    return driver

def mac_json_kaydet(yeni_maclar):
    data = {"version": 2, "updated": "", "matches": []}
    if os.path.exists(CIKTI_DOSYA):
        try:
            with open(CIKTI_DOSYA, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            pass

    guncel_dict = {f"{m['tarih']}_{m['ev_sahibi']}_{m['deplasman']}": m for m in data.get("matches", [])}
    for ym in yeni_maclar:
        guncel_dict[f"{ym['tarih']}_{ym['ev_sahibi']}_{ym['deplasman']}"] = ym

    yeni_liste = sorted(guncel_dict.values(), key=lambda x: (x["tarih"], x["saat"]))
    for i, m in enumerate(yeni_liste, 1):
        m["index"] = i

    data["matches"] = yeni_liste
    data["updated"] = datetime.datetime.now().isoformat()

    os.makedirs(os.path.dirname(CIKTI_DOSYA), exist_ok=True)
    with open(CIKTI_DOSYA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"   💾 Toplam {len(yeni_liste)} maç kaydedildi")

def saat_mi(text):
    if len(text) == 5 and text[2] == ":":
        try:
            s, d = text.split(":")
            if 0 <= int(s) <= 23 and 0 <= int(d) <= 59:
                return True
        except:
            pass
    return False

def nokta_var_mi(text):
    try:
        if "." not in text:
            return False
        val = float(text)
        return 1.01 <= val <= 99.99
    except:
        return False

def tumu_bekle(driver, max_sure=20):
    for _ in range(max_sure):
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            if "Tümü" in body.text:
                return True
        except:
            pass
        time.sleep(1)
    return False

def detay_parse(driver):
    oranlar = {}
    body = driver.find_element(By.TAG_NAME, "body")
    text = body.text
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    tumu_idx = -1
    for i, line in enumerate(lines):
        if line == "Tümü":
            tumu_idx = i
            break
    if tumu_idx == -1:
        return oranlar
    i = tumu_idx + 1
    sekmeler = ["Kim Kazanır","Alt/Üst","Goller","Skor","Diğer",
                "Oyuncu","Özel","Kombo","Korner/Kart","Korner",
                "Kart","Handikap","Yarı","Dakika","Asist",
                "Toplam","İstatistik","Kombine"]
    while i < len(lines) and lines[i] in sekmeler:
        i += 1
    dur = ["Bugün","Yarın","Yardım","Hakkımızda","İletişim",
           "Gizlilik","Popüler Bahisler","Kolay Kuponlar","Spor Toto",
           "Bülten","Canlı Sonuçlar","Yazar Yorumları"]
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
             "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    current_market = ""
    while i < len(lines):
        line = lines[i]
        if line in dur:
            break
        if any(ay in line for ay in aylar) and any(c.isdigit() for c in line):
            break
        if saat_mi(line):
            break
        if line.isupper() and len(line) > 2:
            i += 1
            continue
        if i + 1 < len(lines):
            sonraki = lines[i + 1]
            if nokta_var_mi(sonraki):
                outcome = line
                oran = float(sonraki)
                key = f"{current_market}_{outcome}" if current_market else outcome
                oranlar[key] = oran
                i += 2
                continue
        if not nokta_var_mi(line):
            current_market = line
        i += 1
    return oranlar

def tum_maclari_yukle(driver, url):
    driver.get(url)
    print("   ⏳ Maçlar yükleniyor (max 30sn)...")
    for _ in range(30):
        maclar = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
        if len(maclar) > 0:
            print(f"   ✅ {len(maclar)} maç bulundu")
            return len(maclar)
        time.sleep(1)
    print("   ⚠️ Maç bulunamadı (timeout)")
    return 0

def iddaa_cek(driver):
    bugun = datetime.date.today()
    url = "https://www.iddaa.com/program/futbol"

    print(f"📡 {url}")
    toplam = tum_maclari_yukle(driver, url)

    if toplam == 0:
        print("   ❌ Maç bulunamadı!")
        return []

    print(f"\n🔍 Maç isimleri toplanıyor...")
    takim_adlari = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")

    mac_listesi = []
    for ta in takim_adlari:
        try:
            txt = ta.text.strip()
            parcalar = txt.split("\n")
            ev = ""
            dep = ""
            for p in parcalar:
                p = p.strip()
                if p and p != "-":
                    if not ev:
                        ev = p
                    elif not dep:
                        dep = p
            if ev and dep:
                mac_listesi.append({"ev": ev, "dep": dep})
        except:
            continue

    print(f"   📋 {len(mac_listesi)} maç bulundu:")
    for i, m in enumerate(mac_listesi):
        print(f"      {i+1}. {m['ev']} vs {m['dep']}")

    print(f"\n🔽 Maçlar tek tek açılıyor...\n")
    maclar = []
    basarili = 0
    basarisiz = 0

    for idx, mac in enumerate(mac_listesi):
        print(f"   [{idx+1}/{len(mac_listesi)}] {mac['ev']} vs {mac['dep']}")

        temel_oranlar = {}
        detay_oranlar = {}
        mac_saat = ""
        mac_kodu = ""

        for deneme in range(3):
            try:
                driver.get(url)
                time.sleep(5)

                body = driver.find_element(By.TAG_NAME, "body")
                lines = [l.strip() for l in body.text.split("\n") if l.strip()]

                # Temel oranlar
                for li in range(len(lines) - 15):
                    if lines[li + 2] == mac['ev'] and lines[li + 4] == mac['dep'] and lines[li + 3] == "-":
                        mac_saat = lines[li + 1] if saat_mi(lines[li + 1]) else ""
                        oran_start = li + 5
                        if lines[oran_start] == "Kral Oran":
                            oran_start = li + 7
                        if nokta_var_mi(lines[oran_start]):
                            try:
                                temel_oranlar = {
                                    "Maç Sonucu_1": float(lines[oran_start]),
                                    "Maç Sonucu_0": float(lines[oran_start + 1]),
                                    "Maç Sonucu_2": float(lines[oran_start + 2]),
                                    "İY Sonuç_1": float(lines[oran_start + 3]),
                                    "İY Sonuç_0": float(lines[oran_start + 4]),
                                    "İY Sonuç_2": float(lines[oran_start + 5]),
                                    "Handikap": lines[oran_start + 6],
                                    "Handikap_1": float(lines[oran_start + 7]),
                                    "Handikap_0": float(lines[oran_start + 8]),
                                    "Handikap_2": float(lines[oran_start + 9]),
                                    "Alt/Üst 2.5_Alt": float(lines[oran_start + 10]),
                                    "Alt/Üst 2.5_Üst": float(lines[oran_start + 11]),
                                    "Karşılıklı Gol_Var": float(lines[oran_start + 12]),
                                    "Karşılıklı Gol_Yok": float(lines[oran_start + 13]),
                                }
                                mac_kodu = lines[oran_start + 14]
                            except:
                                pass
                        break

                # Detay oranları için tıkla
                takim_els = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
                for ta in takim_els:
                    ta_text = ta.text.strip()
                    if mac['ev'] in ta_text and mac['dep'] in ta_text:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ta)
                            time.sleep(1)

                            actions = ActionChains(driver)
                            actions.move_to_element(ta).click().perform()
                            time.sleep(4)

                            driver.execute_script("window.scrollTo(0, 600);")
                            time.sleep(1)
                            driver.execute_script("window.scrollTo(0, 1200);")
                            time.sleep(1)
                            driver.execute_script("window.scrollTo(0, 0);")
                            time.sleep(2)

                            if tumu_bekle(driver, 15):
                                detay_oranlar = detay_parse(driver)
                            else:
                                print("      ⚠️ Detay paneli açılmadı.")
                        except Exception as click_err:
                            print(f"      ⚠️ Tıklama Hatası: {str(click_err)[:40]}")
                        break

                if len(detay_oranlar) > 0:
                    print(f"      ✅ {len(detay_oranlar)} detay oran çekildi")
                    break

                if deneme < 2:
                    print(f"      ⏳ Deneme {deneme+1} başarısız, 30sn sonra tekrar...")
                    time.sleep(30)
                else:
                    print("      ❌ 3 deneme de başarısız oldu")

            except Exception as e:
                print(f"      ⚠️ Hata: {str(e)[:60]}")
                if deneme < 2:
                    print(f"      ⏳ Hata sonrası 30sn bekleniyor...")
                    time.sleep(30)

        if len(detay_oranlar) > 0:
            basarili += 1
        else:
            basarisiz += 1

        tum_oranlar = {**temel_oranlar, **detay_oranlar}

        maclar.append({
            "index": 0,
            "mac_kodu": mac_kodu,
            "ev_sahibi": mac['ev'],
            "deplasman": mac['dep'],
            "saat": mac_saat,
            "lig": "",
            "tarih": bugun.isoformat(),
            "cekme_zamani": datetime.datetime.now().isoformat(),
            "durum": "baslamadi",
            "skor_ev": 0,
            "skor_dep": 0,
            "skor_1y_ev": 0,
            "skor_1y_dep": 0,
            "kaynak": "iddaa.com",
            "oranlar": tum_oranlar
        })

        print(f"      📊 Toplam {len(tum_oranlar)} oran")

        if (idx + 1) % 10 == 0:
            mac_json_kaydet(maclar)
            print(f"   💾 {len(maclar)} maç kaydedildi (✅{basarili} ❌{basarisiz})")

    return maclar

def mac_cek():
    driver = None
    baslangic = datetime.datetime.now()
    try:
        driver = tarayici_baslat()
        maclar = iddaa_cek(driver)
        bitis = datetime.datetime.now()
        sure = bitis - baslangic

        print(f"\n{'='*60}")
        print(f"📊 FİNAL SONUÇ")
        print(f"   ⚽ Toplam maç: {len(maclar)}")
        if maclar:
            toplam_oran = sum(len(m["oranlar"]) for m in maclar)
            basarili = sum(1 for m in maclar if len(m["oranlar"]) > 14)
            print(f"   📊 Toplam oran: {toplam_oran}")
            print(f"   📊 Ortalama: {toplam_oran // len(maclar)} oran/maç")
            print(f"   ✅ Detaylı: {basarili}")
        print(f"   ⏱️ Süre: {sure}")
        print(f"{'='*60}")

        if maclar:
            mac_json_kaydet(maclar)
            print("\n🎉 İşlem tamamlandı!")

            # ✅ OTOMATİK GIT ADD/COMMIT/PULL/PUSH
            git_add_commit_pull_push()

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

if __name__ == "__main__":
    print("⚽ İddaa Oran Çekici - BUGÜNÜN TÜM MAÇLARI")
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)
    mac_cek()