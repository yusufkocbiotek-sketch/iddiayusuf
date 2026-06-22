import json
import os
import re
import time
import datetime
import traceback
import subprocess
from pathlib import Path
from difflib import SequenceMatcher

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import *

# =========================
# ⚙️ AYARLAR
# =========================
BASLANGIC_TARIHI = "1u.06.2026"   # GG.AA.YYYY
BITIS_TARIHI = "20.06.2026"       # GG.AA.YYYY

BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
BASE_LINK = "https://www.mackolik.com/futbol/canli-sonuclar"
GIT_BRANCH_NAME = "main"

# Eşleştirme frenleri
TARIH_TOLERANSI_GUN = 15        # ±15 gün tolerans
GUCLU_TAKIM_ESIGI = 0.80       # En az bir takım bu kadar benzemeli
MIN_TOPLAM_PUAN = 1.30         # İki takımın toplam benzerlik alt sınırı (hayalet eşleşme freni)
MIN_TEK_TARAF = 0.50           # Bir taraf bundan düşükse farklı maçtır

# Performans (Lazy-load buffer)
SAYFA_YUKLEME_BEKLEME = 20
ADIM_KAYDIRMA_MIKTARI = 600
ADIMLAR_ARASI_BEKLEME = 1.2    # Mackolik lazy-load buffer
MAX_KAYDIRMA_ADIMI = 200

# =========================================================
# 🧠 İSİM HAFIZASI (TAKMA ADLAR)
# "kaynaktaki isim" : "standart isim"  (hepsi küçük harf)
# 🟡 YAKIN-ELENEN loglarını bana attıkça burayı büyüteceğiz.
# =========================================================
TAKIM_TAKMA_ADLAR = {
    # ====== GENEL / AVRUPA ======
    "psg": "paris saint germain",
    "paris sg": "paris saint germain",
    "man utd": "manchester united",
    "man city": "manchester city",
    "inter milan": "inter",
    "internazionale": "inter",
    "athletic club": "athletic bilbao",
    "sporting cp": "sporting lizbon",

    # ====== KAZAKİSTAN ======
    "k kyzylorda": "kaisar",
    "kaysar": "kaisar",
    "kaisar kyzylorda": "kaisar",
    "fc astana": "astana",
    "altay vko": "altay",
    "altay oskemen": "altay",
    "fc ordabasy": "ordabasy",
    "ordabasy shymkent": "ordabasy",

    # ====== PORTEKİZ ======
    "amarante fc": "amarante",
    "ud santarem": "santarem",
    "u.d. santarem": "santarem",

    # ====== ETİYOPYA ======
    "arba minch kenema": "arba minch",
    "arba minch city": "arba minch",
    "wolaita dicha sc": "wolaita dicha",
    "wolaitta dicha": "wolaita dicha",
    "bahir dar kenema fc": "bahir dar kenema",
    "bahir dar city": "bahir dar kenema",
    "welwalu adigrat": "welwalo adigrat",
    "welwalo adigrat university": "welwalo adigrat",

    # ====== ARJANTİN ======
    "argentinos j": "argentinos juniors",
    "argentinos jrs": "argentinos juniors",
    "ath lanus": "lanus",
    "ca lanus": "lanus",
    "ca acassuso": "acassuso",
    "ca defensores de belgrano": "defensores de belgrano",
    "def belgrano": "defensores de belgrano",
    "ca chaco for ever": "chaco for ever",
    "dep madryn": "deportivo madryn",

    # ====== MACARİSTAN ======
    "bfc siofok": "siofok",
    "erdi vse": "erd",
    "erd vse": "erd",

    # ====== ÇİN ======
    "pekin guoan": "beijing guoan",
    "shanghai sipg": "shanghai port",
    "shenzhen juniors fc": "shenzhen juniors",
    "shenzhen peng city": "shenzhen juniors",

    # ====== AVUSTRALYA ======
    "north eastern metrostars sc": "metrostars",
    "ne metrostars": "metrostars",
    "edgeworth fc": "edgeworth",
    "edgeworth eagles": "edgeworth",
    "maitland fc": "maitland",
    "para hills knights sc": "para hills knights",
    "para hills": "para hills knights",
    "fc bulleen lions": "bulleen lions",
    "bulleen": "bulleen lions",
    "melb. sharks": "melbourne sharks",
    "melb sharks": "melbourne sharks",
    "port melbourne sharks": "melbourne sharks",
    "magic united tfa": "magic united",
    "magic utd": "magic united",
    "adelaide city fc": "adelaide city",
    "white city fk beograd": "white city",
    "white city woodville": "white city",

    # ====== İSVİÇRE ======
    "sc bruhl st gallen": "sc bruhl",
    "sc brühl": "sc bruhl",
    "bruhl sg": "sc bruhl",
    "sc cham": "cham",
    "bsc young boys": "young boys",

    # ====== NORVEÇ / DANİMARKA ======
    "aasane fotball 2": "aasane 2",
    "asane 2": "aasane 2",
    "asane fotball 2": "aasane 2",
    "il gneist": "gneist",
    "nykoebing": "nykobing",
    "fa 2000 kobenhavn": "fa 2000",
    "nykobing fc": "nykobing",

    # ====== KANADA / ABD ======
    "atl ottawa": "atletico ottawa",
    "forge fc": "forge",
    "av alta fc": "av alta",
    "avs alta": "av alta",
    "new york cosmos": "ny cosmos",
    "n.y. cosmos": "ny cosmos",

    # ====== FAS ======
    "chabab atlas khenifra": "chabab khenifra",
    "cak khenifra": "chabab khenifra",

    # ====== PERU ======
    "asociacion deportiva tarma": "adt tarma",
    "adt": "adt tarma",
    "ad tarma": "adt tarma",

    # ====== GÜNEY AMERİKA ======
    "ldu": "ldu quito",
    "sao": "sao paulo",
    "san": "san lorenzo",

    # ====== HOLLANDA (Jong karışmasın!) ======
    "jong ajax": "ajax 2",
    "ajax amsterdam": "ajax",
    "jong utrecht": "utrecht 2",
    "fc utrecht": "utrecht",
    "jong psv": "psv 2",
    "jong az": "az 2",

    # ====== DİĞER ======
    "bfc": "bfc daugavpils",
    "ifk": "ifk mariehamn",
    "zrinjski": "zrinjski mostar",
    "saint": "saint etienne",

    # 👉 🟡 YAKIN-ELENEN loglarından buraya ekleyeceğiz...
}

# =========================================================
# 🔍 İSİM NORMALİZE + BENZERLİK (KATEGORİ KORUMALI)
# =========================================================
def isim_normalize(s):
    """İsmi küçült, takma adlardan geçir. Genç/Rezerv/Kadın etiketlerini KORUR!"""
    if not s:
        return ""
    s = str(s).lower().strip()

    if s in TAKIM_TAKMA_ADLAR:
        s = TAKIM_TAKMA_ADLAR[s]

    # 🚨 KATEGORİ ETİKETLERİ: Silme → STANDARTLAŞTIR
    s = s.replace("(k)", " kadin ").replace("(w)", " kadin ")
    if s.startswith("jong "):                          # Jong Ajax → ajax 2
        s = s[5:].strip() + " 2"
    s = re.sub(r"\b(ii)\b", "2", s)                    # Luzern II → luzern 2
    s = re.sub(r"\b(genc|gencler|gençler|youth|u19|u20|u21|u23|junior|juniors)\b", "genc", s)
    s = re.sub(r"\b(kadin|kadın|women|ladies|fem|feminino)\b", "kadin", s)

    tr_map = str.maketrans("çğıöşü", "cgiosu")
    s = s.translate(tr_map)
    s = re.sub(r"[^a-z0-9\s]", "", s)

    # Sadece zararsız ekleri at
    for ek in [" fc", " fk", " sk", " jk", " cf", " sc", " club", " spor"]:
        if s.endswith(ek):
            s = s[: -len(ek)]
    for on_ek in ["fc ", "fk ", "sc ", "ca ", "cd ", "ud ", "il "]:
        if s.startswith(on_ek):
            s = s[len(on_ek):]
    s = re.sub(r"\s+", " ", s).strip()

    if s in TAKIM_TAKMA_ADLAR:
        s = TAKIM_TAKMA_ADLAR[s]

    return s

def benzerlik(a, b):
    a_n = isim_normalize(a)
    b_n = isim_normalize(b)
    if not a_n or not b_n:
        return 0.0

    # 🛡️ KATEGORİ KORUMASI: Biri genç/rezerv/kadın, diğeri A takımsa → İMKANSIZ
    for etiket in ["2", "genc", "kadin"]:
        a_var = etiket in a_n.split()
        b_var = etiket in b_n.split()
        if a_var != b_var:
            return 0.10

    if a_n == b_n:
        return 1.0
    if a_n in b_n or b_n in a_n:
        return 0.90
    return SequenceMatcher(None, a_n, b_n).ratio()

# =========================
# 📅 TARİH FONKSİYONLARI
# =========================
def esnek_tarih_parse(t):
    """Hem YYYY-MM-DD hem DD.MM.YYYY formatını çözer."""
    t = str(t).strip()[:10]
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d-%m-%Y", "%Y.%m.%d"):
        try:
            return datetime.datetime.strptime(t, fmt).date()
        except:
            continue
    return None

def dates_close(t1, t2):
    d1 = esnek_tarih_parse(t1)
    d2 = esnek_tarih_parse(t2)
    if not d1 or not d2:
        return False
    return abs((d1 - d2).days) <= TARIH_TOLERANSI_GUN

def parse_date(s):
    try:
        return datetime.datetime.strptime(s, "%d.%m.%Y").date()
    except:
        return None

def gun_listesi_olustur(bas, bit):
    gunler = []
    aktif = bas
    while aktif <= bit:
        gunler.append(aktif)
        aktif += datetime.timedelta(days=1)
    return gunler

# =========================
# 📂 JSON İŞLEMLERİ (FORMATIN AYNISI)
# =========================
def load_json_safe(path):
    try:
        if not path.exists():
            return {"matches": [], "son_guncelleme": ""}
        with open(path, "r", encoding="utf-8") as f:
            veri = json.load(f)
            if "matches" not in veri or not isinstance(veri["matches"], list):
                veri["matches"] = []
            return veri
    except Exception as e:
        print(f"⚠️ JSON OKUMA HATASI: {e}")
        return {"matches": [], "son_guncelleme": ""}

def save_json_safe(data, path):
    try:
        temiz_mac_listesi = []
        for idx, mac in enumerate(data.get("matches", []), 1):
            ev_sahibi = str(mac.get("ev_sahibi", "")).strip()
            deplasman = str(mac.get("deplasman", "")).strip()

            if ev_sahibi and deplasman:
                temiz_mac = {
                    "index": idx,
                    "mac_kodu": str(mac.get("mac_kodu", "")),
                    "ev_sahibi": ev_sahibi,
                    "deplasman": deplasman,
                    "saat": str(mac.get("saat", "")),
                    "lig": str(mac.get("lig", "")),
                    "tarih": str(mac.get("tarih", "")),
                    "cekme_zamani": str(mac.get("cekme_zamani", datetime.datetime.now().isoformat())),
                    "durum": str(mac.get("durum", "baslamadi")),
                    "skor_ev": int(mac.get("skor_ev", 0)),
                    "skor_dep": int(mac.get("skor_dep", 0)),
                    "skor_1y_ev": int(mac.get("skor_1y_ev", 0)),
                    "skor_1y_dep": int(mac.get("skor_1y_dep", 0)),
                    "kaynak": str(mac.get("kaynak", "spordb.com")),
                    "oranlar": mac.get("oranlar", {})
                }
                temiz_mac_listesi.append(temiz_mac)

        data["son_guncelleme"] = datetime.datetime.now().isoformat()
        cikti_verisi = {"matches": temiz_mac_listesi, "son_guncelleme": data["son_guncelleme"]}

        temp_path = path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8", newline='\n') as f:
            json.dump(cikti_verisi, f, ensure_ascii=False, indent=2)

        temp_path.replace(path)
        print(f"💾 KAYIT BAŞARILI: {path.name} | Toplam: {len(temiz_mac_listesi)} maç")
        return True
    except Exception as e:
        print(f"❌ KAYIT HATASI: {e}")
        return False

# =========================
# 🚀 DRIVER
# =========================
def build_driver():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--log-level=3")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)

    print("🔄 ChromeDriver hazırlanıyor...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.set_page_load_timeout(60)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("✅ Tarayıcı başarıyla başlatıldı")
    return driver

# =========================
# 🛠️ YARDIMCILAR
# =========================
def rakam_bul(text):
    if not text:
        return 0
    rakamlar = re.findall(r'\d+', str(text))
    return int(rakamlar[0]) if rakamlar else 0

# =========================================================
# 📅 MACKOLİK TAKVİM NAVİGASYONU
# =========================================================
def takvimde_gezin(driver, hedef_tarih):
    """Mackolik takviminde hedef tarihe gider (hedef_tarih: datetime.date)"""
    hedef_iso = hedef_tarih.strftime("%Y-%m-%d")
    print(f"   🔧 Takvim navigasyonu: {hedef_iso}")

    try:
        hedef_ay = hedef_tarih.month
        hedef_yil = hedef_tarih.year

        # 1️⃣ TAKVİMİ AÇ
        takvim_buton = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "widget-dateslider__datepicker-toggle")))
        driver.execute_script("arguments[0].click();", takvim_buton)
        print("   ✅ Takvim açıldı")
        time.sleep(2)

        # 🇹🇷 Türkçe kısaltmalar + İngilizce (her ihtimale karşı)
        AY_KISALTMA = {
            "oca": 1, "sub": 2, "şub": 2, "mar": 3, "nis": 4,
            "may": 5, "haz": 6, "tem": 7, "agu": 8, "ağu": 8,
            "eyl": 9, "eki": 10, "kas": 11, "ara": 12,
            "jan": 1, "feb": 2, "apr": 4, "jun": 6, "jul": 7,
            "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }

        def takvim_durumu_oku():
            """
            Tüm .widget-datepicker__value elemanlarını okur.
            Birinde ay kısaltması (Haz, May...), birinde yıl (2026) olur.
            Döner: (ay_no, ay_index, yil, yil_index)
            """
            ay_no, ay_idx, yil, yil_idx = None, None, None, None
            try:
                degerler = driver.find_elements(By.CLASS_NAME, "widget-datepicker__value")
                for i, el in enumerate(degerler):
                    metin = el.text.strip().lower()
                    if not metin:
                        continue
                    # Yıl mı? (4 haneli sayı)
                    yil_m = re.search(r"(\d{4})", metin)
                    if yil_m:
                        yil = int(yil_m.group(1))
                        yil_idx = i
                        continue
                    # Ay kısaltması mı?
                    metin_temiz = metin[:3]
                    if metin_temiz in AY_KISALTMA:
                        ay_no = AY_KISALTMA[metin_temiz]
                        ay_idx = i
            except Exception as e:
                print(f"   ⚠️ Takvim okuma hatası: {str(e)[:30]}")
            return ay_no, ay_idx, yil, yil_idx

        # 2️⃣ DOĞRU AY/YILA GİT
        # İki ayrı nav seti var: ay navları ve yıl navları.
        # value[i] hangi indexte ise, previous[i]/next[i] de ona aittir.
        for deneme in range(40):
            ay_no, ay_idx, yil, yil_idx = takvim_durumu_oku()

            if ay_no is None:
                print("   ⚠️ Ay okunamadı, tarih seçimine direkt geçiliyor...")
                break

            # Yıl okunamadıysa hedef yılla aynı varsay
            if yil is None:
                yil = hedef_yil

            print(f"   📍 Takvim şu an: Ay={ay_no}, Yıl={yil} | Hedef: Ay={hedef_ay}, Yıl={hedef_yil}")

            if ay_no == hedef_ay and yil == hedef_yil:
                print("   ✅ Hedef ay/yıla ulaşıldı")
                break

            prev_butonlar = driver.find_elements(
                By.CSS_SELECTOR, "div.widget-datepicker__nav.widget-datepicker__nav--previous")
            next_butonlar = driver.find_elements(
                By.CSS_SELECTOR, "div.widget-datepicker__nav.widget-datepicker__nav--next")

            try:
                # ÖNCE YILI DÜZELT (varsa ayrı yıl navı)
                if yil != hedef_yil and yil_idx is not None:
                    if yil > hedef_yil and len(prev_butonlar) > yil_idx:
                        driver.execute_script("arguments[0].click();", prev_butonlar[yil_idx])
                        print("   ⏪ Yıl geri")
                    elif yil < hedef_yil and len(next_butonlar) > yil_idx:
                        driver.execute_script("arguments[0].click();", next_butonlar[yil_idx])
                        print("   ⏩ Yıl ileri")
                    time.sleep(1.2)
                    continue

                # SONRA AYI DÜZELT
                # (Yıl navı yoksa ay navı yıl sınırını kendisi aşar varsayımıyla
                #  toplam fark üzerinden ilerle)
                toplam_fark = (hedef_yil - yil) * 12 + (hedef_ay - ay_no)
                if toplam_fark < 0 and len(prev_butonlar) > (ay_idx or 0):
                    driver.execute_script("arguments[0].click();", prev_butonlar[ay_idx or 0])
                    print("   ⏪ Ay geri")
                elif toplam_fark > 0 and len(next_butonlar) > (ay_idx or 0):
                    driver.execute_script("arguments[0].click();", next_butonlar[ay_idx or 0])
                    print("   ⏩ Ay ileri")
                else:
                    break
                time.sleep(1.2)

            except Exception as nav_hata:
                print(f"   ⚠️ Nav tıklama hatası: {str(nav_hata)[:30]}")
                break

        # 3️⃣ HEDEF GÜNÜ SEÇ
        tarih_secici = f'td.widget-datepicker__calendar-body-cell[data-date="{hedef_iso}"]'
        try:
            tarih_elemani = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, tarih_secici)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tarih_elemani)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", tarih_elemani)
            print(f"   ✅ TARİH SEÇİLDİ: {hedef_iso}")
            time.sleep(10)
            return True
        except Exception as e:
            print(f"   ❌ TARİH HÜCRESI BULUNAMADI: {str(e)[:40]}")
            # Debug: takvimde görünen tarihleri listele
            try:
                hucreler = driver.find_elements(
                    By.CSS_SELECTOR, "td.widget-datepicker__calendar-body-cell")
                ornekler = [h.get_attribute("data-date") for h in hucreler[:10] if h.get_attribute("data-date")]
                print(f"      Takvimde görünenler (ilk 10): {ornekler}")
            except:
                pass
            return False

    except Exception as e:
        print(f"   ❌ TAKVİM HATASI: {str(e)[:60]}")
        return False
# =========================================================
# 🌐 MACKOLİK GÜNLÜK ÇEKİM (BUFFER'LI KAYDIRMA)
# =========================================================
def get_skorlar_tek_gun(driver, hedef_tarih):
    hedef_iso = hedef_tarih.strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"📅 İŞLENİYOR: {hedef_iso}")
    print(f"{'='*60}")

    skor_listesi = []
    gorulen = set()

    try:
        if not takvimde_gezin(driver, hedef_tarih):
            print("❌ Takvim navigasyonu başarısız, bu gün atlanıyor")
            return []

        print("🔧 Sayfa kaydırılıyor (lazy-load buffer aktif)...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(3)

        for adim in range(MAX_KAYDIRMA_ADIMI):
            driver.execute_script(f"window.scrollBy(0, {ADIM_KAYDIRMA_MIKTARI});")
            time.sleep(ADIMLAR_ARASI_BEKLEME)  # 1.2s buffer

            try:
                mac_satirlari = driver.find_elements(By.CSS_SELECTOR, "div.match-row")
            except:
                mac_satirlari = []

            for satir in mac_satirlari:
                try:
                    isimler = satir.find_elements(By.CSS_SELECTOR, "span.match-row__team-name-text")
                    if len(isimler) < 2:
                        continue

                    ev_isim = isimler[0].text.strip()
                    dep_isim = isimler[1].text.strip()
                    if not ev_isim or not dep_isim or ev_isim == dep_isim:
                        continue

                    kimlik = f"{isim_normalize(ev_isim)}|{isim_normalize(dep_isim)}"
                    if kimlik in gorulen or kimlik == "|":
                        continue
                    gorulen.add(kimlik)

                    # ─── ANA SKOR ───
                    s_ev, s_dep = 0, 0
                    try:
                        s_ev = rakam_bul(satir.find_element(
                            By.CSS_SELECTOR, "span.match-row__score-home").get_attribute("innerHTML"))
                    except: pass
                    try:
                        s_dep = rakam_bul(satir.find_element(
                            By.CSS_SELECTOR, "span.match-row__score-away").get_attribute("innerHTML"))
                    except: pass

                    if s_ev == 0 and s_dep == 0:
                        try:
                            skor_linki = satir.find_element(By.CSS_SELECTOR, "a.match-row__score")
                            spanlar = skor_linki.find_elements(By.TAG_NAME, "span")
                            if len(spanlar) >= 2:
                                s_ev = rakam_bul(spanlar[0].get_attribute("innerHTML"))
                                s_dep = rakam_bul(spanlar[1].get_attribute("innerHTML"))
                        except: pass

                    # ─── İLK YARI ───
                    iy_ev, iy_dep = 0, 0
                    try:
                        iy_metin = satir.find_element(
                            By.CSS_SELECTOR, "div.match-row__half-time-score").text.strip()
                        r = re.findall(r'\d+', iy_metin)
                        if len(r) == 2:
                            iy_ev, iy_dep = int(r[0]), int(r[1])
                    except: pass

                    # İY > MS mantık hatası → İY'yi sıfırla (yanlış veri yazmaktansa)
                    if iy_ev > s_ev or iy_dep > s_dep:
                        iy_ev, iy_dep = 0, 0

                    # ─── DURUM ───
                    durum = "baslamadi"
                    if s_ev > 0 or s_dep > 0 or iy_ev > 0 or iy_dep > 0:
                        durum = "bitti"

                    skor_listesi.append({
                        "tarih": hedef_iso,
                        "ev_sahibi": ev_isim,
                        "deplasman": dep_isim,
                        "skor_ev": s_ev,
                        "skor_dep": s_dep,
                        "skor_1y_ev": iy_ev,
                        "skor_1y_dep": iy_dep,
                        "durum": durum,
                        "kaynak": "mackolik.com"
                    })

                    print(f"   ✅ [{len(skor_listesi)}] {ev_isim} - {dep_isim} | MS:{s_ev}-{s_dep} | İY:{iy_ev}-{iy_dep}")

                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue

            # Sayfa sonu kontrolü
            try:
                son = driver.execute_script(
                    "return window.innerHeight + window.scrollY >= document.body.scrollHeight - 500;")
                if son:
                    print(f"🏁 Sayfa sonuna ulaşıldı! (Adım: {adim+1})")
                    break
            except:
                pass

        print(f"\n📊 {hedef_iso} ÖZET: {len(skor_listesi)} maç çekildi")

    except Exception as e:
        print(f"❌ ÇEKİM HATASI: {e}")
        traceback.print_exc()

    return skor_listesi

# =========================================================
# 🧠 EŞLEŞTİRME - ÇOKLU GÜNCELLEME (±3 GÜN | DUPLİKELER DAHİL)
# Frenleri geçen TÜM kayıtlara aynı skor yazılır.
# Yeni kayıt EKLEMEZ (Mackolik tamamlayıcı kaynak - JSON'u şişirmesin)
# =========================================================
def merge_data(mevcut, yeni):
    mac_listesi = mevcut.get("matches", [])
    guncelle_say = 0
    kopya_say = 0
    bulunamayan = 0
    print("\n🔎 EŞLEŞTİRME BAŞLADI (MACKOLİK | ±3 GÜN | DUPLİKELER DAHİL)...")

    for sp in yeni:
        sp_tarih = sp.get("tarih", "")
        sp_ev = sp.get("ev_sahibi", "")
        sp_dep = sp.get("deplasman", "")

        # Skoru olmayan (0-0 baslamadi) web verisini yazmaya değmez
        if sp.get("durum") == "baslamadi":
            continue

        # ─────────────────────────────────────────────
        # 1️⃣ FRENLERİ GEÇEN TÜM ADAYLARI TOPLA
        # ─────────────────────────────────────────────
        adaylar = []

        for idx, mevcut_mac in enumerate(mac_listesi):

            if not dates_close(mevcut_mac.get("tarih", ""), sp_tarih):
                continue

            oran_ev = benzerlik(mevcut_mac.get("ev_sahibi", ""), sp_ev)
            oran_dep = benzerlik(mevcut_mac.get("deplasman", ""), sp_dep)
            toplam = oran_ev + oran_dep

            # 🟡 DEDEKTÖR: Eşiğe yakın ama elenenler (isim avı için bana at!)
            if (0.90 <= toplam < MIN_TOPLAM_PUAN) or \
               (toplam >= MIN_TOPLAM_PUAN and min(oran_ev, oran_dep) < MIN_TEK_TARAF):
                print(f"🟡 YAKIN-ELENEN: WEB[{sp_ev} - {sp_dep}] ↔ "
                      f"JSON[{mevcut_mac.get('ev_sahibi','')} - {mevcut_mac.get('deplasman','')}] "
                      f"| ev:{oran_ev:.2f} dep:{oran_dep:.2f}")

            # 🛡️ FREN 1: Toplam alt sınır (hayalet eşleşme freni)
            if toplam < MIN_TOPLAM_PUAN:
                continue
            # 🛡️ FREN 2: En az bir takım güçlü olmalı
            if oran_ev < GUCLU_TAKIM_ESIGI and oran_dep < GUCLU_TAKIM_ESIGI:
                continue
            # 🛡️ FREN 3: Bir taraf zayıfsa farklı maçtır
            if min(oran_ev, oran_dep) < MIN_TEK_TARAF:
                continue

            puan = toplam
            d1 = esnek_tarih_parse(mevcut_mac.get("tarih", ""))
            d2 = esnek_tarih_parse(sp_tarih)
            if d1 and d2 and d1 == d2:
                puan += 0.50

            adaylar.append((idx, puan, f"ev:{oran_ev:.2f} dep:{oran_dep:.2f}"))

        # ─────────────────────────────────────────────
        # 2️⃣ TÜM ADAYLARI GÜNCELLE (DUPLİKELER DAHİL!)
        # ─────────────────────────────────────────────
        if adaylar:
            adaylar.sort(key=lambda x: x[1], reverse=True)

            for sira, (idx, puan, detay) in enumerate(adaylar):
                mevcut_mac = mac_listesi[idx]

                degisti_mi = False
                if mevcut_mac["skor_ev"] != sp["skor_ev"] or mevcut_mac["skor_dep"] != sp["skor_dep"]:
                    degisti_mi = True
                    mevcut_mac["skor_ev"] = sp["skor_ev"]
                    mevcut_mac["skor_dep"] = sp["skor_dep"]
                if mevcut_mac["skor_1y_ev"] != sp["skor_1y_ev"] or mevcut_mac["skor_1y_dep"] != sp["skor_1y_dep"]:
                    degisti_mi = True
                    mevcut_mac["skor_1y_ev"] = sp["skor_1y_ev"]
                    mevcut_mac["skor_1y_dep"] = sp["skor_1y_dep"]
                if mevcut_mac["durum"] != sp["durum"]:
                    degisti_mi = True
                    mevcut_mac["durum"] = sp["durum"]

                if degisti_mi:
                    mevcut_mac["cekme_zamani"] = datetime.datetime.now().isoformat()
                    if sira == 0:
                        guncelle_say += 1
                        print(f"🔄 GÜNCELLE [P:{puan:.2f} | {detay}]: "
                              f"{mevcut_mac['ev_sahibi']} - {mevcut_mac['deplasman']} | "
                              f"{sp['skor_ev']}-{sp['skor_dep']} (IY:{sp['skor_1y_ev']}-{sp['skor_1y_dep']})")
                    else:
                        kopya_say += 1
                        print(f"   👯 DUPLİKE DE GÜNCELLENDİ [P:{puan:.2f}] ({mevcut_mac.get('tarih','')}): "
                              f"{mevcut_mac['ev_sahibi']} - {mevcut_mac['deplasman']} | "
                              f"{sp['skor_ev']}-{sp['skor_dep']}")
        else:
            bulunamayan += 1
            # ❗ Mackolik tamamlayıcı kaynak: JSON'da yoksa EKLEMEYİZ (bülten dışı maçlarla şişmesin)

    mevcut["matches"] = mac_listesi

    # ═══════════════════════════════════════════
    # 📋 RAPOR: Aralıkta hâlâ "baslamadi" kalan maçlar
    # ═══════════════════════════════════════════
    web_tarihler = {sp.get("tarih", "") for sp in yeni}
    eksikler = []
    for mac in mac_listesi:
        if mac.get("durum") == "baslamadi":
            for wt in web_tarihler:
                if dates_close(mac.get("tarih", ""), wt):
                    eksikler.append(mac)
                    break

    if eksikler:
        print(f"\n⚠️ HÂLÂ GÜNCELLENMEYEN {len(eksikler)} MAÇ:")
        for m in eksikler:
            print(f"   ❓ {m.get('tarih','')} | {m['ev_sahibi']} - {m['deplasman']}")
        try:
            with open(BASE_DIR / "eksik_maclar.json", "w", encoding="utf-8") as f:
                json.dump(eksikler, f, ensure_ascii=False, indent=2)
            print("   💾 eksik_maclar.json dosyasına kaydedildi")
        except:
            pass

    print(f"\n📊 ÖZET: 🔄 {guncelle_say} ana güncelleme | 👯 {kopya_say} duplike senkronize | "
          f"❓ {len(eksikler)} hâlâ eksik")
    return mevcut, guncelle_say, kopya_say

# =========================
# 📤 GİT İŞLEMLERİ
# =========================
def git_islemleri():
    try:
        print("\n🔄 GİT İŞLEMLERİ BAŞLATILIYOR...")
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True, capture_output=True, text=True)
        zaman = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        commit_mesaji = f"Mackolik Skor Güncelleme | {zaman}"
        subprocess.run(["git", "commit", "--allow-empty", "-m", commit_mesaji],
                       cwd=BASE_DIR, capture_output=True, text=True)
        subprocess.run(["git", "push", "origin", GIT_BRANCH_NAME],
                       cwd=BASE_DIR, check=True, capture_output=True, text=True)
        print("✅ GİT BAŞARILI")
        return True
    except Exception as e:
        print(f"❌ GİT HATA: {e}")
        return False

# =========================
# 🎯 ANA AKIŞ
# =========================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 MACKOLİK | TAMAMLAYICI SKOR ÇEKİCİ | ±3 GÜN + DUPLİKE ✅")
    print("=" * 60)

    bas_tar = parse_date(BASLANGIC_TARIHI)
    bit_tar = parse_date(BITIS_TARIHI)
    if not bas_tar or not bit_tar:
        print("❌ Tarih hatası! Format: GG.AA.YYYY")
        input("Devam...")
        exit()

    hedef_gunler = gun_listesi_olustur(bas_tar, bit_tar)
    print(f"📅 İşlenecek {len(hedef_gunler)} gün:")
    for g in hedef_gunler:
        print(f"   • {g.strftime('%d.%m.%Y')}")

    driver = None
    tum_yeni = []

    try:
        driver = build_driver()

        for gun_tarihi in hedef_gunler:
            print("\n" + "#" * 60)
            print(f"# 📅 GÜN: {gun_tarihi.strftime('%d.%m.%Y')}")
            print("#" * 60)

            try:
                driver.get(BASE_LINK)
                time.sleep(SAYFA_YUKLEME_BEKLEME)

                gunluk = get_skorlar_tek_gun(driver, gun_tarihi)
                tum_yeni.extend(gunluk)

            except Exception as gun_hata:
                print(f"❌ {gun_tarihi} işlenirken hata: {str(gun_hata)[:50]}")
                continue

        print(f"\n📊 TOPLAM ÇEKİLEN: {len(tum_yeni)} maç")

        if tum_yeni:
            mevcut_veri = load_json_safe(MAC_JSON_PATH)
            yeni_veri, guncelle, kopya = merge_data(mevcut_veri, tum_yeni)

            if save_json_safe(yeni_veri, MAC_JSON_PATH):
                print(f"\n🎉 İŞLEM TAMAMLANDI: {guncelle} Güncellendi | {kopya} Duplike Senkronize")
                git_islemleri()
        else:
            print("\n⚠️ Hiç veri çekilemedi, JSON'a dokunulmadı.")

    except Exception as err:
        print(f"\n❌ KRİTİK HATA: {err}")
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
        input("\n✅ TAMAMLANDI. Kapatmak için ENTER...")