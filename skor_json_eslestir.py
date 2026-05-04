import json
import os
import datetime
import time
import re
import difflib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

MAC_JSON = "public/data/mac.json"

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    options.add_argument("--disable-page-aligned-intervals")
    options.add_experimental_option("detach", False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome başlatıldı!")
    return driver

def mac_json_oku():
    if os.path.exists(MAC_JSON):
        try:
            with open(MAC_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ mac.json dosyası bozuk, yeni dosya oluşturuluyor.")
    return {"version": 2, "updated": "", "matches": []}

def mac_json_kaydet(data):
    data["updated"] = datetime.datetime.now().isoformat()
    os.makedirs(os.path.dirname(MAC_JSON), exist_ok=True)
    with open(MAC_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 mac.json güncellendi!")

def temizle_takim_adi(ad):
    if not ad:
        return ""
    ad = ad.lower().strip()
    tr_map = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'i': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u', 'æ': 'ae', 'œ': 'oe',
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n', 'ã': 'a',
        'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u', 'ý': 'y', 'å': 'a', 'ø': 'o'
    }
    for k, v in tr_map.items():
        ad = ad.replace(k, v)
    silinecekler = [
        " fc", "fc ", " f.c", "f.c.", " sk", "sk ", " s.k", "s.k.",
        " united", "utd", " utd", " city", " c", "c.",
        " as ", " ac ", " us ", " sc", " fk", " nk", " cs", " cd", 
        " deportivo", " club", " atletico", " atl.", "athletic",
        "spor", "kulubu", "takimi", "kulübü", "team", "fussball",
        "sk", "if", "ff", "bk", "gf", "gsk", "gb", "genclik",
        "al ", "al-", "el ", "el-", "bin ", "beni ", "abu ",
        "de ", "del ", "la ", "los ", "las ", "le ", "les ",
        "cf", "c.f.", "s.c.", "b.c.", "f.c.", " jr", "sr", 
        " ii", " iii", " iv", " v", " vii", " viii",
        "19", "20", "18", "17", "16", "15", "14", "13", "12", "11",
        "spor", "kulubu", "takımı", "kulübü", "resmi", "profesyonel"
    ]
    for s in silinecekler:
        ad = ad.replace(s, "")
    ad = re.sub(r'[^a-z]', '', ad)
    ad = re.sub(r'(.)\1{2,}', r'\1\1', ad)
    return ad if len(ad) >= 2 else ""

def takim_eslesir_mi(ad1, ad2):
    ad1_temiz = temizle_takim_adi(ad1)
    ad2_temiz = temizle_takim_adi(ad2)
    
    if not ad1_temiz or not ad2_temiz:
        return False
    
    if ad1_temiz == ad2_temiz:
        return True
    
    if len(ad1_temiz) > 2 and len(ad2_temiz) > 2:
        if ad1_temiz in ad2_temiz or ad2_temiz in ad1_temiz:
            return True
    
    if len(ad1_temiz) >=2 and len(ad2_temiz) >=2:
        if ad1_temiz[:2] == ad2_temiz[:2]:
            return True
    
    if len(ad1_temiz) >=2 and len(ad2_temiz) >=2:
        if ad1_temiz[-2:] == ad2_temiz[-2:]:
            return True
    
    benzerlik = difflib.SequenceMatcher(None, ad1_temiz, ad2_temiz).ratio()
    if benzerlik > 0.40:
        return True
    
    return False

def spordb_duz_metin_parse(text, aktif_tarih):
    skorlar = []
    lines = [line.strip() for line in text.split("\n") if line.strip() != ""]
    skor_kalibi = re.compile(r'(\d+)\s*-\s*(\d+)')
    
    for i, line in enumerate(lines):
        bulunan_skorlar = skor_kalibi.findall(line)
        if len(bulunan_skorlar) >= 2:
            try:
                parcalar = re.split(r'(\d+\s*-\s*\d+)', line)
                parcalar = [p.strip() for p in parcalar if p.strip()]
                
                ev_sahibi = parcalar[0]
                ms_skor = bulunan_skorlar[0]
                deplasman = parcalar[1]
                iy_skor = bulunan_skorlar[1]
                
                skor_ev, skor_dep = int(ms_skor[0]), int(ms_skor[1])
                skor_1y_ev, skor_1y_dep = int(iy_skor[0]), int(iy_skor[1])
                
                skorlar.append({
                    "ev": ev_sahibi, "dep": deplasman, "tarih": aktif_tarih,
                    "skor_ev": skor_ev, "skor_dep": skor_dep,
                    "skor_1y_ev": skor_1y_ev, "skor_1y_dep": skor_1y_dep
                })
            except Exception as e:
                continue
    return skorlar

def gunluk_menu_bul(driver):
    try:
        tum_selectler = driver.find_elements(By.TAG_NAME, "select")
        for select in tum_selectler:
            try:
                secenekler = select.find_elements(By.TAG_NAME, "option")
                if not secenekler:
                    continue
                if any(" - " in opt.text.strip() for opt in secenekler):
                    continue
                if any(re.match(r'^\d{2}\.\d{2}\.\d{4}', opt.text.strip()) for opt in secenekler):
                    return select
            except:
                continue
    except:
        pass
    return None

def spordb_skorlari_cek(driver, gunler):
    url = "https://www.spordb.com/iddaa-programi/"
    print(f"📡 {url} açılıyor...")
    driver.get(url)
    
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "select"))
        )
        print("✅ Sayfa tamamen yüklendi")
    except:
        print("⚠️ Sayfa zamanında yüklenemedi, yine de devam ediliyor...")
    time.sleep(3)
    
    tum_skorlar = []
    print(f"   📅 Kontrol edilecek günler: {', '.join(gunler)}")

    gunluk_menu = gunluk_menu_bul(driver)
    if not gunluk_menu:
        print("❌ Günlük menü bulunamadı!")
        return []
    print("✅ Günlük tarih menüsü bulundu!")

    for gun in gunler:
        print(f"\n   📅 {gun} tarihi aranıyor...")
        try:
            gunluk_menu = gunluk_menu_bul(driver)
            if not gunluk_menu:
                print(f"      ❌ Menü yeniden bulunamadı, bu günü atlıyorum...")
                continue
                
            secenekler = gunluk_menu.find_elements(By.TAG_NAME, "option")
            bulundu = False

            for opt in secenekler:
                opt_metin = opt.text.strip()
                if gun in opt_metin:
                    deger = opt.get_attribute("value")
                    secim = Select(gunluk_menu)
                    secim.select_by_value(deger)
                    print(f"      ✅ '{opt_metin}' seçildi, yükleniyor...")

                    eski_icerik = driver.find_element(By.TAG_NAME, "body").text
                    time.sleep(7)

                    yukleme_basladi = time.time()
                    while time.time() - yukleme_basladi < 20:
                        try:
                            yeni_icerik = driver.find_element(By.TAG_NAME, "body").text
                            if yeni_icerik != eski_icerik:
                                print(f"      ✅ İçerik güncellendi")
                                break
                        except:
                            pass
                        time.sleep(0.5)

                    gun_parcalari = gun.split(".")
                    iso_tarih = f"{gun_parcalari[2]}-{gun_parcalari[1]}-{gun_parcalari[0]}"

                    sayfa_icerigi = driver.find_element(By.TAG_NAME, "body").text
                    cekilen_skorlar = spordb_duz_metin_parse(sayfa_icerigi, iso_tarih)
                    tum_skorlar.extend(cekilen_skorlar)

                    print(f"      ✅ {gun} tarihinden {len(cekilen_skorlar)} maç skoru alındı")
                    bulundu = True
                    break

            if not bulundu:
                print(f"      ❌ {gun} menüde bulunamadı")

        except Exception as hata:
            print(f"      ❌ Hata: {str(hata)[:80]}...")
            continue

    print(f"\n   ✅ SporDB'den toplam {len(tum_skorlar)} bitmiş maç skoru okundu.")
    return tum_skorlar

def skorlari_guncelle(data, skorlar):
    guncellenen = 0
    bulunamayan = 0
    eslesenler = []
    eslesmeyenler = []
    bugun_iso = datetime.date.today().isoformat()

    if "matches" not in data or not isinstance(data["matches"], list):
        print("❌ JSON verisinde 'matches' bölümü bulunamadı!")
        return 0, 0, []

    print("\n🔎 EŞLEŞTİRME SONUÇLARI:")
    print("-"*70)

    for mac in data["matches"]:
        if mac.get("durum", "baslamadi") != "baslamadi":
            continue
        
        bulundu = False
        mac_tarih = mac.get("tarih", "")
        mac_ev = mac.get("ev_sahibi", "")
        mac_dep = mac.get("deplasman", "")

        for skor in skorlar:
            if mac_tarih == skor["tarih"] and takim_eslesir_mi(mac_ev, skor["ev"]) and takim_eslesir_mi(mac_dep, skor["dep"]):
                mac["durum"] = "bitti"
                mac["skor_ev"] = skor["skor_ev"]
                mac["skor_dep"] = skor["skor_dep"]
                mac["skor_1y_ev"] = skor["skor_1y_ev"]
                mac["skor_1y_dep"] = skor["skor_1y_dep"]
                guncellenen += 1
                bulundu = True
                eslesenler.append(f"✅ {mac_ev} | {skor['ev']} -> {skor['skor_ev']}-{skor['skor_dep']} | {mac_dep} | {skor['dep']}")
                break
        
        if not bulundu:
            bulunamayan += 1
            if mac_tarih < bugun_iso:
                eslesmeyenler.append(f"❌ {mac_ev} vs {mac_dep} ({mac_tarih})")
    
    for eslesme in eslesenler:
        print(eslesme)
    
    print("-"*70)
    return guncellenen, bulunamayan, eslesmeyenler

def main():
    print("============================================================")
    print("⚽ Skor Güncelleyici (SporDB Kaynağı - Son Sürüm)")
    print("============================================================")
    
    data = mac_json_oku()
    maclar = data.get("matches", [])
    baslamadi_maclar = [m for m in maclar if m.get("durum", "baslamadi") == "baslamadi"]
    
    if not baslamadi_maclar:
        print("\n✅ Güncellenecek başlama/bitmemiş maç yok!")
        return

    bugun = datetime.date.today()
    aranacak_gunler = [
        (bugun - datetime.timedelta(days=i)).strftime("%d.%m.%Y") 
        for i in range(7)
    ]

    tarayici = None
    try:
        tarayici = tarayici_baslat()
        bulunan_skorlar = spordb_skorlari_cek(tarayici, aranacak_gunler)
        
        guncellenen_sayi, bulunamayan_sayi, eslesmeyenler = skorlari_guncelle(data, bulunan_skorlar)

        print(f"\n{'='*60}")
        print(f"📊 İŞLEM SONUCU")
        print(f"   ✅ Güncellenen maç sayısı : {guncellenen_sayi}")
        print(f"   ❌ Eşleşmeyen maç sayısı : {bulunamayan_sayi}")
        print(f"{'='*60}")

        if eslesmeyenler:
            print("\n⚠️ Skoru bulunamayan geçmiş maçlar (ilk 15):")
            for i, mac_bilgisi in enumerate(eslesmeyenler[:15], 1):
                print(f"   {i}. {mac_bilgisi}")

        if guncellenen_sayi > 0:
            mac_json_kaydet(data)
            print(f"\n📌 Değişiklikleri depoya kaydetmek için:")
            print(f"   git add -A && git commit -m 'Skorlar güncellendi: {datetime.date.today()}' && git push")
        else:
            print(f"\nℹ️ Hiçbir maç eşleştirilemedi. Bunun nedenleri:")
            print(f"   - Takım isimleri çok farklı yazılıyor")
            print(f"   - Maç tarihleri kontrol edilen gün aralığında değil")
            print(f"   - SporDB'de henüz bu maçların skoru girilmemiş")
            
            # Her durumda komutu göster - TAM DÜZELTİLDİ
            print(f"\n📌 Depoya gönderme komutu:")
            print(f"   git add -A && git commit -m 'Kontrol: {datetime.date.today()}' && git push")

    except Exception as ana_hata:
        print(f