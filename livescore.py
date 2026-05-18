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
    ElementClickInterceptedException, InvalidSelectorException,
    StaleElementReferenceException
)

# =============================================================================
# TAKIM İSMİ DÜZELTME & EŞLEŞTİRME
# =============================================================================
def clean_team_name(name):
    if not name:
        return ""
    n = name.lower().strip()
    n = n.replace(".", "").replace("-", " ").replace("'", "").replace("’", "").replace("(", "").replace(")", "")
    replacements = {
        "deportivo": "deport", "athletic": "athletic", "atletico": "atletico", "club": "",
        "ca ": "", " ca": "", "fc ": "", " fc": "", "ac ": "", " ac": "", "sc ": "", " sc": "",
        "us ": "", " us": "", "fk ": "", " fk": "", "sk ": "", " sk": "", "real ": "real",
        "sporting ": "sporting", "de ": "", "la ": "", "el ": "", "cf ": "", "cd ": "", "ud ": "",
        "vfb ": "", "vfl ": "", "fc ": "", "sv ": "", "spvgg ": "", "tsv ": "", "bvk ": ""
    }
    for key, val in replacements.items():
        if n.startswith(key + " "):
            n = val + n[len(key):]
        elif n.endswith(" " + key):
            n = n[:-(len(key)+1)] + (" " + val if val else "")
        elif n == key:
            n = val
    n = " ".join(n.split())
    return n.strip()

_TMAP = str.maketrans({"İ":"i","I":"ı","Ş":"s","ş":"s","Ğ":"g","ğ":"g","Ü":"u","ü":"u","Ö":"o","ö":"o","Ç":"c","ç":"c"})
_STOP = {"fk","fc","sk","jk","bk","ac","as","a.s","a.ş","spor","club","kulubu","kulübü",
         "u19","u20","u21","u23","women","reserves","b","ii","ca","cd","cf","sc","ud", "de", "la", "el"}

def _deaccent(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))

def norm_team(s: str) -> str:
    s = (s or "").strip()
    s = _deaccent(s).translate(_TMAP).lower()
    s = re.sub(r"[’'`´]", "", s)
    s = re.sub(r"\d+", "", s)
    s = re.sub(r"[^a-zçşğüöıA-ZÇŞĞÜÖIİ0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    parts = [p for p in s.split() if p and p not in _STOP and len(p) > 1]
    return " ".join(parts)

def team_sim(a: str, b: str) -> float:
    a_orj = norm_team(a)
    b_orj = norm_team(b)
    if not a_orj or not b_orj: return 0.0
    if a_orj == b_orj: return 1.0
    if a_orj in b_orj or b_orj in a_orj: return 0.98
    a_kelimeler = a_orj.split()
    b_kelimeler = b_orj.split()
    ortak = 0
    for ak in a_kelimeler:
        for bk in b_kelimeler:
            if len(ak)>=3 and len(bk)>=3 and (ak in bk or bk in ak):
                ortak +=1
                break
    if ortak > 0: return 0.95 + (ortak * 0.02)
    return SequenceMatcher(None, a_orj, b_orj).ratio()

def match_score(local_home, local_away, sp_home, sp_away):
    sh = team_sim(local_home, sp_home)
    sa = team_sim(local_away, sp_away)
    sh_ters = team_sim(local_home, sp_away)
    sa_ters = team_sim(local_away, sp_home)
    return (sh + sa) * 50 if (sh + sa) >= (sh_ters + sa_ters) else (sh_ters + sa_ters) * 50

def match_uid(tarih: str, ev: str, dep: str) -> str:
    a, b = norm_team(ev), norm_team(dep)
    x, y = sorted([a, b])
    return f"{tarih}|{x}|{y}"

# =============================================================================
# AYARLAR - BURADAN DÜZENLEYEBİLİRSİN
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
GECMIS_JSON_PATH = BASE_DIR / "public" / "data" / "gecmis_maclar.json"
OUTPUT_SKOR_JSON = BASE_DIR / "public" / "data" / "skorlar_livescore.json"

# HANGİ TARİHİN VERİSİ ÇEKİLSİN?
# SEÇENEK 1: DÜN -> "https://www.livescore.bz/tr/yesterday/"
# SEÇENEK 2: BUGÜN -> "https://www.livescore.bz/tr/"
# SEÇENEK 3: TARİH -> "https://www.livescore.bz/tr/ended/?date=2026-05-16"
# SEÇİMİ BURADAN YAP:  
CEKILECEK_LINK = "https://www.livescore.bz/tr/" # DÜN İÇİN
# CEKILECEK_LINK = "https://www.livescore.bz/tr/"     # BUGÜN İÇİN
# CEKILECEK_LINK = "https://www.livescore.bz/tr/ended/?date=2026-05-16" # ÖZEL TARİH

UPDATE_MAC_JSON = True
UPDATE_GECMIS_JSON = True
ADD_MISSING_MATCHES = True

PAGE_LOAD_TIMEOUT = 45
WAIT_LONG = 20
SCROLL_PAUSE_TIME = 2.5  # ⏱️ ÇOK DAHA YAVAŞ! 2.5 saniye bekleyerek kesin yükleme
MAX_SCROLL_ATTEMPT = 50  # 🔁 En fazla 50 kere aşağı in (Çok uzun sayfalar için)

# =============================================================================
# JSON OKU / YAZ
# =============================================================================
def load_json_safe(path: Path):
    if not path.exists():
        print(f"ℹ️ {path.name} bulunamadı, yeni oluşturuluyor.")
        return {"version": 2, "updated": "", "matches": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ JSON Okuma Hatası: {e}")
        return {"version": 2, "updated": "", "matches": []}

def save_json_atomic(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        tmp.replace(path)
        print(f"💾 {path.name} kaydedildi.")
    except Exception as e:
        print(f"❌ Kaydetme Hatası: {e}")
        if tmp.exists(): tmp.unlink()

# =============================================================================
# TARAYICI
# =============================================================================
def build_driver():
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1366,768")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--lang=tr-TR")
    opts.add_argument("--enable-javascript")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
    except Exception:
        driver = webdriver.Chrome(options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver

# =============================================================================
# ✅ ÇOK YAVAŞ KAYDIRMA - TÜM VERİYİ KAÇIRMADAN ÇEK
# =============================================================================
def get_all_matches(driver):
    print("🔎 Veri çekme işlemi başladı...")
    tum_veriler = []

    try:
        # ✅ Belirlenen linke git
        print(f"🌐 Hedef sayfa açılıyor: {CEKILECEK_LINK}")
        driver.get(CEKILECEK_LINK)
        
        WebDriverWait(driver, WAIT_LONG).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)  # Sayfanın tam açılması için ekstra bekleme

        # =============================================================
        # 🔽 ÇOK YAVAŞÇA AŞAĞI KAYDIRMA
        # =============================================================
        print("🔽 Sayfa ÇOK YAVAŞ aşağı kaydırılıyor, tüm maçlar yükleniyor...")
        eski_yükseklik = -1
        deneme_sayisi = 0

        while deneme_sayisi < MAX_SCROLL_ATTEMPT:
            # Mevcut yüksekliği al
            yeni_yükseklik = driver.execute_script("return document.body.scrollHeight")
            
            # Eğer yükseklik değişmediyse sona ulaştık demektir
            if yeni_yükseklik == eski_yükseklik:
                print("✅ Sayfanın sonuna ulaşıldı, tüm veriler yüklendi.")
                break

            # Önceki yüksekliği güncelle
            eski_yükseklik = yeni_yükseklik

            # En aşağıya kaydır
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # ⏱️ UZUN BEKLEME SÜRESİ - Kesin yükleme için
            time.sleep(SCROLL_PAUSE_TIME)
            
            deneme_sayisi += 1
            print(f"⏳ Kaydırma {deneme_sayisi}/{MAX_SCROLL_ATTEMPT} | Yükseklik: {yeni_yükseklik}px")

        # En üste geri dön
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        # =============================================================
        # 📥 ARTIK TÜM SAYFA YÜKLENDİ, HEPSİNİ OKU
        # =============================================================
        print("🔍 Tüm maçlar okunuyor -> <a class='m ft modd'> yapısı...")
        
        # Sayfadaki BÜTÜN maç etiketlerini bul
        mac_etiketleri = driver.find_elements(By.CSS_SELECTOR, "a.m.ft.modd")
        
        if not mac_etiketleri:
            print("❌ Hiç maç etiketi bulunamadı!")
            return []

        print(f"📋 Toplam {len(mac_etiketleri)} adet maç bulundu, ayrıştırılıyor...")

        for idx, etiket in enumerate(mac_etiketleri):
            try:
                # İç elemanları al (sa, st, t1, sc, t2, ht)
                saat = etiket.find_element(By.CSS_SELECTOR, "sa").text.strip()
                durum = etiket.find_element(By.CSS_SELECTOR, "st").text.strip()
                ev_sahibi = etiket.find_element(By.CSS_SELECTOR, "t1 t").text.strip()
                skor = etiket.find_element(By.CSS_SELECTOR, "sc").text.strip()
                deplasman = etiket.find_element(By.CSS_SELECTOR, "t2 t").text.strip()
                
                # İlk yarı skoru (varsa)
                iy_skor = "0-0"
                try:
                    iy_skor = etiket.find_element(By.CSS_SELECTOR, "ht").text.strip()
                except:
                    pass

                # Skorları ayır (örn: "1 - 0" -> 1 ve 0)
                skorlar = re.findall(r"(\d+)", skor)
                if len(skorlar) < 2:
                    continue
                ev_gol = int(skorlar[0])
                dep_gol = int(skorlar[1])

                # İlk yarı skorlarını ayır
                iy_skorlar = re.findall(r"(\d+)", iy_skor)
                iy_ev, iy_dep = 0, 0
                if len(iy_skorlar) >= 2:
                    iy_ev = int(iy_skorlar[0])
                    iy_dep = int(iy_skorlar[1])

                # Benzersiz ID (mid)
                mac_id = etiket.get_attribute("mid")

                # ✅ VERİYİ OLUŞTUR
                veri = {
                    "sofascore_id": mac_id,
                    "tarih": datetime.date.today().isoformat() if "yesterday" not in CEKILECEK_LINK else (datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
                    "saat": saat,
                    "sp_home": ev_sahibi,
                    "sp_away": deplasman,
                    "skor1": ev_gol,
                    "skor2": dep_gol,
                    "iy_skor1": iy_ev,
                    "iy_skor2": iy_dep,
                    "durum": durum,
                    "cekme_zamani": datetime.datetime.now().isoformat()
                }
                tum_veriler.append(veri)
                print(f"✅ [{idx+1:3d}] {saat} {durum} | {ev_sahibi} {ev_gol}-{dep_gol} {deplasman} | İY: {iy_ev}-{iy_dep}")

            except Exception as oku_hata:
                print(f"⚠️ Okuma hatası ({idx+1}): {str(oku_hata)[:50]}...")
                continue

    except Exception as e:
        print(f"❌ Genel hata: {e}")

    if not tum_veriler:
        print("❌ VERİ YOK! Eskiler KORUNUYOR.")
    else:
        print(f"✅ İşlem tamamlandı! Toplam {len(tum_veriler)} maç verisi alındı.")

    return tum_veriler

# =============================================================================
# VERİ İŞLEME & KAYDETME
# =============================================================================
def collect_all_scores(driver):
    print("📋 Veriler düzenleniyor...")
    tum_veriler = get_all_matches(driver)
    temiz = []
    kontrol = set()
    for v in tum_veriler:
        if not v: continue
        uid = f"{v['tarih']}|{v['sp_home']}|{v['sp_away']}"
        if uid in kontrol: continue
        kontrol.add(uid)
        temiz.append(v)
    return temiz

def update_db(db_data: dict, scores: list, today_iso: str):
    if not scores:
        print("ℹ️ Yeni veri yok, değişiklik yapılmadı.")
        return 0,0,0,0,0,0

    matches = db_data.get("matches", [])
    if not isinstance(matches, list):
        matches = []
        db_data["matches"] = []

    mevcut_idler = set()
    gruplu = {}
    for m in matches:
        if m.get("tarih") and m.get("ev_sahibi") and m.get("deplasman"):
            uid = match_uid(m["tarih"], m["ev_sahibi"], m["deplasman"])
            mevcut_idler.add(uid)
            gruplu.setdefault(m["tarih"], []).append(m)

    eslesen = guncellenen = degismeyen = eklenen = atlanan = eslesmeyen = 0

    for sp in scores:
        adaylar = gruplu.get(sp["tarih"], [])
        en_iyi = None
        en_puan = -1
        ikincil = -1

        for a in adaylar:
            p = match_score(a["ev_sahibi"], a["deplasman"], sp["sp_home"], sp["sp_away"])
            if p > en_puan:
                ikincil = en_puan
                en_puan = p
                en_iyi = a
            elif p > ikincil:
                ikincil = p

        # Eşleşme yeterli mi?
        if en_iyi and en_puan >= 30 and (en_puan - ikincil) >= 10:
            if en_puan >= 60:
                eslesen += 1

                # Takımlar ters mi kontrol et
                düz = team_sim(en_iyi["ev_sahibi"], sp["sp_home"]) + team_sim(en_iyi["deplasman"], sp["sp_away"])
                ters = team_sim(en_iyi["ev_sahibi"], sp["sp_away"]) + team_sim(en_iyi["deplasman"], sp["sp_home"])

                if ters > düz:
                    sk1, sk2 = sp["skor2"], sp["skor1"]
                    iy1, iy2 = sp.get("iy_skor2", 0), sp.get("iy_skor1", 0)
                else:
                    sk1, sk2 = sp["skor1"], sp["skor2"]
                    iy1, iy2 = sp.get("iy_skor1", 0), sp.get("iy_skor2", 0)

                degisim = (
                    en_iyi.get("skor_ev") != sk1 or
                    en_iyi.get("skor_dep") != sk2 or
                    en_iyi.get("skor_1y_ev") != iy1 or
                    en_iyi.get("skor_1y_dep") != iy2 or
                    en_iyi.get("sofascore_id") != sp["sofascore_id"] or
                    en_iyi.get("durum") != sp["durum"]
                )

                # Güncelle
                en_iyi["skor_ev"] = sk1
                en_iyi["skor_dep"] = sk2
                en_iyi["skor_1y_ev"] = iy1
                en_iyi["skor_1y_dep"] = iy2
                en_iyi["durum"] = sp["durum"]
                en_iyi["sofascore_id"] = sp["sofascore_id"]
                en_iyi["kaynak"] = "livescore.bz"
                en_iyi["cekme_zamani"] = sp["cekme_zamani"]

                if degisim:
                    guncellenen += 1
                    print(f"✏️ Güncellendi: {en_iyi['ev_sahibi']} {sk1}-{sk2} {en_iyi['deplasman']}")
                else:
                    degismeyen += 1
            else:
                atlanan += 1
        else:
            # Yeni kayıt ekleme
            if ADD_MISSING_MATCHES:
                uid = match_uid(sp["tarih"], sp["sp_home"], sp["sp_away"])
                if uid not in mevcut_idler:
                    yeni = {
                        "index": 0,
                        "mac_kodu": sp.get("sofascore_id", ""),
                        "ev_sahibi": sp["sp_home"],
                        "deplasman": sp["sp_away"],
                        "saat": sp.get("saat", ""),
                        "lig": "",
                        "tarih": sp["tarih"],
                        "cekme_zamani": sp["cekme_zamani"],
                        "durum": sp.get("durum", "bitti"),
                        "skor_ev": sp["skor1"],
                        "skor_dep": sp["skor2"],
                        "skor_1y_ev": sp.get("iy_skor1", 0),
                        "skor_1y_dep": sp.get("iy_skor2", 0),
                        "kaynak": "livescore.bz",
                        "sofascore_id": sp.get("sofascore_id", ""),
                        "oranlar": {}
                    }
                    matches.append(yeni)
                    mevcut_idler.add(uid)
                    eklenen += 1
                    print(f"➕ Yeni eklendi: {sp['sp_home']} {sp['skor1']}-{sp['skor2']} {sp['sp_away']}")
                else:
                    eslesmeyen += 1
            else:
                eslesmeyen += 1

    # Sıralama ve indexleme
    db_data["matches"] = sorted(matches, key=lambda x: (x.get("tarih", ""), x.get("saat", "00:00"), x.get("ev_sahibi", "")))
    for i, item in enumerate(db_data["matches"], 1):
        item["index"] = i

    db_data["updated"] = datetime.datetime.now().isoformat()
    return eslesen, guncellenen, degismeyen, eklenen, atlanan, eslesmeyen


# =============================================================================
# ANA FONKSİYON
# =============================================================================
def main():
    print("======================================================================")
    print("⚽ LIVESCORE.BZ | DÜN + BUGÜN | ÇOK YAVAŞ KAYDIRMA MODU")
    print("======================================================================")
    print(f"🔗 Çekilecek Link: {CEKILECEK_LINK}")
    print(f"⏱️ Kaydırma Bekleme Süresi: {SCROLL_PAUSE_TIME}sn (Çok Yavaş)")
    print("----------------------------------------------------------------------")

    bugun_iso = datetime.date.today().isoformat()
    driver = None
    tum_veriler = []

    try:
        driver = build_driver()
        tum_veriler = collect_all_scores(driver)

        # Ham veriyi kaydet
        save_json_atomic({
            "olusturulma_tarihi": datetime.datetime.now().isoformat(),
            "kaynak": CEKILECEK_LINK,
            "veri": tum_veriler
        }, OUTPUT_SKOR_JSON)

        # Ana dosyayı güncelle
        if UPDATE_MAC_JSON:
            print("\n🔄 Ana veri dosyası (mac.json) güncelleniyor...")
            mac_veri = load_json_safe(MAC_JSON_PATH)
            istatistik = update_db(mac_veri, tum_veriler, bugun_iso)
            save_json_atomic(mac_veri, MAC_JSON_PATH)
            print(f"""
            📈 İŞLEM SONUÇLARI:
            ✅ Eşleşen Maç:      {istatistik[0]}
            ✏️ Güncellenen:      {istatistik[1]}
            🟡 Değişmeyen:      {istatistik[2]}
            ➕ Yeni Eklenen:     {istatistik[3]}
            ⏭️ Atlanan:          {istatistik[4]}
            ❌ Eşleşmeyen:       {istatistik[5]}
            """)

        # Geçmiş dosyayı güncelle
        if UPDATE_GECMIS_JSON:
            print("\n🔄 Geçmiş veri dosyası (gecmis_maclar.json) güncelleniyor...")
            gecmis_veri = load_json_safe(GECMIS_JSON_PATH)
            update_db(gecmis_veri, tum_veriler, bugun_iso)
            save_json_atomic(gecmis_veri, GECMIS_JSON_PATH)

    except Exception as genel_hata:
        print(f"❌ KRİTİK HATA: {genel_hata}")
        traceback.print_exc()

    finally:
        if driver:
            driver.quit()
            print("🗑️ Tarayıcı kapatıldı.")

        # Git işlemleri
        try:
            if len(tum_veriler) > 0:
                print("\n🚀 Git deposuna gönderiliyor...")
                repo_yol = BASE_DIR
                dosyalar = [
                    "public/data/mac.json",
                    "public/data/gecmis_maclar.json",
                    "public/data/skorlar_livescore.json"
                ]

                for dosya_yolu in dosyalar:
                    dp = repo_yol / dosya_yolu
                    if dp.exists():
                        subprocess.run(
                            ["git", "add", dosya_yolu],
                            cwd=repo_yol,
                            capture_output=True,
                            text=True
                        )

                durum = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=repo_yol,
                    capture_output=True,
                    text=True
                )

                if durum.stdout.strip():
                    zaman = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                    mesaj = f"🤖 {zaman} | {CEKILECEK_LINK.replace('https://www.livescore.bz/tr/', '')} | {len(tum_veriler)} maç çekildi"
                    subprocess.run(["git", "commit", "-m", mesaj], cwd=repo_yol, capture_output=True, text=True)
                    subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=repo_yol, capture_output=True, text=True)
                    subprocess.run(["git", "push", "origin", "main"], cwd=repo_yol, capture_output=True, text=True)
                    print("✅ Git işlemi tamamlandı!")
                else:
                    print("ℹ️ Değişiklik bulunamadı, Git'e gönderilmedi.")
            else:
                print("ℹ️ Veri bulunamadığı için Git işlemi yapılmadı.")
        except Exception as git_hata:
            print(f"⚠️ Git Hatası: {git_hata}")

    print("\n" + "============================================================")
    print("✅ TÜM İŞLEMLER TAMAMLANDI - HAZIR")
    print("============================================================")
    print(f"🔗 Kaynak: {CEKILECEK_LINK}")
    print(f"📊 Çekilen Toplam Maç: {len(tum_veriler)} adet")
    print(f"⚙️ Ayar: Çok Yavaş Kaydırma (Hiç veri kaçmaz)")
    print("============================================================")
    input("Çıkmak için herhangi bir tuşa bas...")


if __name__ == "__main__":
    main()