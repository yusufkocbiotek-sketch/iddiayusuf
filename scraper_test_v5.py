import json
import os
import datetime
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

CIKTI_DOSYA = "public/data/mac.json"

def rastgele_bekle(min_sn=3, max_sn=7):
    sure = random.uniform(min_sn, max_sn)
    time.sleep(sure)
    return sure

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en-US', 'en']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
        """
    })
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
    guncel_dict = {}
    for m in data.get("matches", []):
        key = m['tarih'] + "_" + m['ev_sahibi'] + "_" + m['deplasman']
        guncel_dict[key] = m
    for ym in yeni_maclar:
        key = ym['tarih'] + "_" + ym['ev_sahibi'] + "_" + ym['deplasman']
        guncel_dict[key] = ym
    yeni_liste = sorted(guncel_dict.values(), key=lambda x: (x["tarih"], x.get("saat", "")))
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

def sayi_mi(text):
    try:
        float(text.replace(",", "."))
        return True
    except:
        return False

def nokta_var_mi(text):
    try:
        if "." not in text:
            return False
        val = float(text)
        return 1.01 <= val <= 99.99
    except:
        return False

SAHTE = ["Tarih", "Oyun Türü", "Lig Seçimi", "Tarihe Göre", "Maç Sonucu",
         "İlk Yarı", "Handikap", "Alt/Üst", "Karşılıklı", "Bugün", "Yarın",
         "ÖNE ÇIKAN", "CANLI", "FUTBOL", "BASKETBOL", "TENİS"]

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
    sekmeler = ["Kim Kazanır", "Alt/Üst", "Goller", "Skor", "Diğer",
                "Oyuncu", "Özel", "Kombo", "Korner/Kart", "Korner",
                "Kart", "Handikap", "Yarı", "Dakika", "Asist",
                "Toplam", "İstatistik", "Kombine"]
    while i < len(lines) and lines[i] in sekmeler:
        i += 1
    dur = ["Bugün", "Yarın", "Yardım", "Hakkımızda", "İletişim",
           "Gizlilik", "Popüler Bahisler", "Kolay Kuponlar", "Spor Toto",
           "Bülten", "Canlı Sonuçlar", "Yazar Yorumları"]
    aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
             "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
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
                key = current_market + "_" + outcome if current_market else outcome
                oranlar[key] = oran
                i += 2
                continue
        if not nokta_var_mi(line):
            current_market = line
        i += 1
    return oranlar

def rastgele_mouse_hareketi(driver):
    try:
        for _ in range(random.randint(2, 4)):
            x = random.randint(100, 1800)
            y = random.randint(100, 900)
            driver.execute_script(
                "var event = new MouseEvent('mousemove', {clientX: " + str(x) +
                ", clientY: " + str(y) + ", bubbles: true}); document.dispatchEvent(event);"
            )
            time.sleep(random.uniform(0.2, 0.5))
    except:
        pass

def insans_scroll(driver):
    try:
        for _ in range(random.randint(1, 3)):
            miktar = random.randint(100, 400)
            yon = random.choice([-1, 1])
            driver.execute_script("window.scrollBy({top: " + str(miktar * yon) + ", behavior: 'smooth'});")
            time.sleep(random.uniform(0.5, 1.5))
    except:
        pass

def insani_tiklama(driver, element):
    rastgele_mouse_hareketi(driver)
    actions = ActionChains(driver)
    actions.move_to_element(element)
    time.sleep(random.uniform(0.3, 0.8))
    actions.click()
    actions.perform()
    time.sleep(random.uniform(0.5, 1.0))

def tum_maclari_topla(driver):
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    toplanan = {}
    bos_sayaci = 0
    adim = 0
    while bos_sayaci < 20:
        adim += 1
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            lines = [l.strip() for l in body.text.split("\n") if l.strip()]
        except:
            time.sleep(2)
            continue
        yeni = 0
        for i in range(len(lines)):
            line = lines[i].strip()
            if line in ["-", "–", "—"]:
                if i >= 2 and i + 1 < len(lines):
                    ev = lines[i - 1].strip()
                    dep = lines[i + 1].strip()
                    if (len(ev) >= 2 and len(dep) >= 2 and
                        not sayi_mi(ev) and not sayi_mi(dep) and
                        not any(kw in ev for kw in SAHTE) and
                        not any(kw in dep for kw in SAHTE)):
                        saat = ""
                        for j in range(max(0, i - 3), i):
                            if saat_mi(lines[j].strip()):
                                saat = lines[j].strip()
                                break
                        key = ev.lower().strip() + "_vs_" + dep.lower().strip()
                        if key not in toplanan:
                            toplanan[key] = {"saat": saat, "ev": ev, "dep": dep}
                            yeni += 1
        if yeni > 0:
            bos_sayaci = 0
            print(f"   ⬇️ Adım {adim}: +{yeni} yeni maç | Toplam: {len(toplanan)}")
        else:
            bos_sayaci += 1
        driver.execute_script("window.scrollBy({top: 300, behavior: 'smooth'});")
        time.sleep(4)
    return list(toplanan.values())

def mac_detay_cek(driver, url, mac, mac_index):
    temel_oranlar = {}
    detay_oranlar = {}
    mac_saat = ""
    mac_kodu = ""

    for deneme in range(2):
        try:
            driver.get(url)
            rastgele_bekle(5, 8)

            body = driver.find_element(By.TAG_NAME, "body")
            lines = [l.strip() for l in body.text.split("\n") if l.strip()]

            for li in range(len(lines) - 15):
                if (lines[li + 2] == mac['ev'] and
                    lines[li + 4] == mac['dep'] and
                    lines[li + 3] == "-"):
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

            insans_scroll(driver)
            rastgele_bekle(1, 2)
            driver.execute_script("window.scrollTo(0, 0);")
            rastgele_bekle(1, 2)

            mac_bulundu = False
            for kaydir in range(15):
                takim_els = driver.find_elements(By.CSS_SELECTOR, ".i_tnw__t8AmC")
                for ta in takim_els:
                    ta_text = ta.text.strip()
                    if mac['ev'] in ta_text and mac['dep'] in ta_text:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ta)
                            rastgele_bekle(1, 2)
                            insani_tiklama(driver, ta)
                            rastgele_bekle(4, 7)
                            driver.execute_script("window.scrollTo(0, 600);")
                            rastgele_bekle(1, 2)
                            driver.execute_script("window.scrollTo(0, 1200);")
                            rastgele_bekle(1, 2)
                            driver.execute_script("window.scrollTo(0, 0);")
                            rastgele_bekle(1, 2)
                            if tumu_bekle(driver, 15):
                                detay_oranlar = detay_parse(driver)
                            mac_bulundu = True
                        except Exception as e:
                            print(f"         ⚠️ Tıklama Hatası: {str(e)[:40]}")
                        break
                if mac_bulundu:
                    break
                driver.execute_script("window.scrollBy({top: 400, behavior: 'smooth'});")
                rastgele_bekle(2, 3)

            if not mac_bulundu:
                print(f"      ⚠️ Maç listede bulunamadı")

            if len(detay_oranlar) > 0:
                break
            elif deneme == 0:
                print(f"      ⏳ Deneme 1 başarısız, tekrar deneniyor...")
                rastgele_bekle(8, 12)

        except Exception as e:
            print(f"      ⚠️ Hata: {str(e)[:50]}")
            if deneme == 0:
                rastgele_bekle(8, 12)

    return {
        "mac_saat": mac_saat,
        "mac_kodu": mac_kodu,
        "oranlar": {**temel_oranlar, **detay_oranlar},
        "detay_sayisi": len(detay_oranlar)
    }

def iddaa_cek(driver):
    bugun = datetime.date.today()
    url = "https://www.iddaa.com/program/futbol"

    print(f"📡 {url}")
    driver.get(url)
    rastgele_bekle(8, 12)

    mac_listesi = tum_maclari_topla(driver)

    if not mac_listesi:
        print("   ❌ Maç bulunamadı!")
        return []

    print(f"\n   📋 {len(mac_listesi)} maç bulundu!")
    print(f"   ⏱️ Tahmini süre: {len(mac_listesi) * 35 // 60} dakika")
    print(f"\n🔽 Maç detayları çekiliyor...\n")

    maclar = []
    basarili = 0
    basarisiz = 0

    for idx, mac in enumerate(mac_listesi):
        print(f"   [{idx + 1}/{len(mac_listesi)}] {mac['ev']} vs {mac['dep']}")

        # 🔑 HER 10 MAÇTA BİR 2 DAKİKA MOLA
        if idx > 0 and idx % 10 == 0:
            print(f"      ☕ Uzun mola: 120 saniye...")
            time.sleep(120)

        sonuc = mac_detay_cek(driver, url, mac, idx)

        if sonuc["detay_sayisi"] > 0:
            basarili += 1
            print(f"      ✅ {sonuc['detay_sayisi']} detay oran çekildi")
        else:
            basarisiz += 1

        tum_oranlar = sonuc.get("oranlar", {})

        maclar.append({
            "index": 0,
            "mac_kodu": sonuc.get("mac_kodu", ""),
            "ev_sahibi": mac['ev'],
            "deplasman": mac['dep'],
            "saat": sonuc.get("mac_saat", mac.get("saat", "")),
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

        print(f"      📊 Toplam {len(tum_oranlar)} oran | ✅{basarili} ❌{basarisiz}")

        # Her 10 maçta bir kayıt et
        if (idx + 1) % 10 == 0:
            mac_json_kaydet(maclar)
            print(f"   💾 Ara kayıt: {len(maclar)} maç")

        # 🔑 HER MAÇTAN SONRA 30 SANİYE BEKLE
        print(f"      ⏳ 30 saniye bekleniyor...")
        time.sleep(30)

    return maclar

def mac_cek():
    driver = None
    baslangic = datetime.datetime.now()
    try:
        driver = tarayici_baslat()
        maclar = iddaa_cek(driver)
        sure = datetime.datetime.now() - baslangic

        print(f"\n{'='*60}")
        print(f"📊 FİNAL SONUÇ")
        print(f"   ⚽ Toplam maç: {len(maclar)}")
        if maclar:
            toplam_oran = sum(len(m["oranlar"]) for m in maclar)
            basarili = sum(1 for m in maclar if len(m["oranlar"]) > 14)
            print(f"   📊 Toplam oran: {toplam_oran}")
            print(f"   ✅ Detaylı: {basarili}")
        print(f"   ⏱️ Süre: {sure}")
        print(f"{'='*60}")

        if maclar:
            mac_json_kaydet(maclar)
            print("\n🎉 İşlem tamamlandı!")
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print("⚽ İddaa Oran Çekici - SABİT BEKLEMELİ MOD")
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)
    mac_cek()