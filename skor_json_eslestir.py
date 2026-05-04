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
    # Tarayıcı penceresinin otomatik kapanmasını engelle
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
    # Klasör yoksa oluştur
    os.makedirs(os.path.dirname(MAC_JSON), exist_ok=True)
    with open(MAC_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 mac.json güncellendi!")

def temizle_takim_adi(ad):
    if not ad:
        return ""
    ad = ad.lower().strip()
    # Türkçe karakter dönüşümü düzeltildi
    tr_map = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'i': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u', 'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u'}
    for k, v in tr_map.items():
        ad = ad.replace(k, v)
    silinecekler = [
        " fc", "fc ", " united", " utd", " city", " as ", " ac ", " us ", " sc", 
        " fk", " nk", " cs", " cd", " deportivo", " club", " atletico", " atl.",
        " athletic", " 1911", " 1919", " 1908", " 1912", " 2000", "spor", "kulubu", "sk"
    ]
    for s in silinecekler:
        ad = ad.replace(s, "")
    ad = re.sub(r'[^a-z0-9]', '', ad)
    return ad

def takim_eslesir_mi(ad1, ad2):
    ad1_temiz = temizle_takim_adi(ad1)
    ad2_temiz = temizle_takim_adi(ad2)
    if not ad1_temiz or not ad2_temiz:
        return False
    if ad1_temiz == ad2_temiz:
        return True
    if len(ad1_temiz) > 3 and len(ad2_temiz) > 3:
        if ad1_temiz in ad2_temiz or ad2_temiz in ad1_temiz:
            return True
        if ad1_temiz[:4] == ad2_temiz[:4]:
            return True
    benzerlik = difflib.SequenceMatcher(None, ad1_temiz, ad2_temiz).ratio()
    if benzerlik > 0.70:
        return True
    return False

def spordb_duz_metin_parse(text, aktif_tarih):
    skorlar = []
    lines = [line.strip() for line in text.split("\n") if line.strip() != ""]
    
    # Skor kalıbı: en az bir rakam, tire, en az bir rakam şeklinde
    skor_kalibi = re.compile(r'(\d+)\s*-\s*(\d+)')
    
    for i, line in enumerate(lines):
        # İki farklı skor olmalı (maç skoru ve ilk yarı skoru)
        bulunan_skorlar = skor_kalibi.findall(line)
        if len(bulunan_skorlar) >= 2:
            try:
                # Parçaları ayır
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
                print(f"⚠️ Satır ayrıştırılamadı: {line} | Hata: {str(e)}")
                continue
    return skorlar

def spordb_skorlari_cek(driver, gunler):
    url = "https://www.spordb.com/iddaa-programi/"
    print(f"📡 {url} açılıyor...")
    driver.get(url)
    # Sayfanın tamamen yüklenmesini bekle
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "select"))
        )
    except:
        print("⚠️ Sayfa zamanında yüklenemedi, devam ediliyor...")
    time.sleep(5)
    
    tum_skorlar = []
    print(f"   📅 Kontrol edilecek günler: {', '.join(gunler)}")

    for gun in gunler:
        print(f"\n   📅 {gun} tarihi spordb'de aranıyor...")
        try:
            # Tüm açılır menüleri al
            selectler = driver.find_elements(By.TAG_NAME, "select")
            hedef_select = None
            
            for sel in selectler:
                try:
                    secenekler = sel.find_elements(By.TAG_NAME, "option")
                    # Sadece tarih içeren ve hafta bilgisi olmayan menüyü seç
                    if secenekler and any(re.search(r'\d{2}\.\d{2}\.\d{4}', opt.text.strip()) for opt in secenekler):
                        hedef_select = sel
                        break
                except:
                    continue
            
            if not hedef_select:
                print("   ⚠️ Tarih seçim menüsü bulunamadı.")
                continue
            
            secenekler = hedef_select.find_elements(By.TAG_NAME, "option")
            secildi_mi = False
            
            for opt in secenekler:
                opt_metin = opt.text.strip()
                if gun in opt_metin:
                    deger = opt.get_attribute("value")
                    secim_nesnesi = Select(hedef_select)
                    secim_nesnesi.select_by_value(deger)
                    print(f"      ✅ {gun} seçildi, yükleniyor...")
                    # Verilerin yüklenmesi için yeterli süre bekle
                    time.sleep(15)
                    
                    # Tarih formatını ISO'ya çevir
                    gun_parcalari = gun.split(".")
                    iso_tarih = f"{gun_parcalari[2]}-{gun_parcalari[1]}-{gun_parcalari[0]}"
                    
                    sayfa_icerigi = driver.find_element(By.TAG_NAME, "body").text
                    cekilen_skorlar = spordb_duz_metin_parse(sayfa_icerigi, iso_tarih)
                    tum_skorlar.extend(cekilen_skorlar)
                    
                    secildi_mi = True
                    break
            
            if not secildi_mi:
                print(f"      ⚠️ {gun} seçeneği listede bulunamadı.")
        
        except Exception as hata:
            print(f"      ⚠️ Tarih işlenirken hata: {str(hata)}")
    
    print(f"\n   ✅ SporDB'den toplam {len(tum_skorlar)} bitmiş maç skoru okundu.")
    return tum_skorlar

def skorlari_guncelle(data, skorlar):
    guncellenen = 0
    bulunamayan = 0
    eksik_gecmis_maclar = []
    bugun_iso = datetime.date.today().isoformat()

    # Önce maç verisinin geçerliliğini kontrol et
    if "matches" not in data or not isinstance(data["matches"], list):
        return 0, 0, []

    for mac in data["matches"]:
        # Durum anahtarı yoksa varsayılan değer ata
        if mac.get("durum", "baslamadi") != "baslamadi":
            continue
        
        bulundu = False
        for skor in skorlar:
            if (mac.get("tarih") == skor["tarih"] and 
                takim_eslesir_mi(mac.get("ev_sahibi", ""), skor["ev"]) and 
                takim_eslesir_mi(mac.get("deplasman", ""), skor["dep"])):
                
                mac["durum"] = "bitti"
                mac["skor_ev"] = skor["skor_ev"]
                mac["skor_dep"] = skor["skor_dep"]
                mac["skor_1y_ev"] = skor["skor_1y_ev"]
                mac["skor_1y_dep"] = skor["skor_1y_dep"]
                guncellenen += 1
                bulundu = True
                print(f"   ✅ EŞLEŞTİ: {mac.get('ev_sahibi')} {skor['skor_ev']}-{skor['skor_dep']} {skor['dep']}")
                break
        
        if not bulundu:
            bulunamayan += 1
            if mac.get("tarih", "") < bugun_iso:
                ev = mac.get("ev_sahibi", "Bilinmeyen")
                dep = mac.get("deplasman", "Bilinmeyen")
                tar = mac.get("tarih", "Bilinmeyen Tarih")
                eksik_gecmis_maclar.append(f"{ev} vs {dep} ({tar})")
    
    return guncellenen, bulunamayan, eksik_gecmis_maclar

def main():
    print("============================================================")
    print("⚽ Skor Güncelleyici (Akıllı Eşleştirme v6.1)...")
    print("============================================================")
    
    data = mac_json_oku()
    maclar = data.get("matches", [])
    baslamadi_maclar = [m for m in maclar if m.get("durum", "baslamadi") == "baslamadi"]
    
    if not baslamadi_maclar:
        print("\n✅ Güncellenecek başlama/bitmemiş maç yok!")
        return

    # Son 3 günün tarihlerini gün.ay.yıl formatında al
    bugun = datetime.date.today()
    aranacak_gunler = [
        (bugun - datetime.timedelta(days=i)).strftime("%d.%m.%Y") 
        for i in range(3)
    ]

    tarayici = None
    try:
        tarayici = tarayici_baslat()
        bulunan_skorlar = spordb_skorlari_cek(tarayici, aranacak_gunler)
        
        print("\n📝 Skorlar maçlarla eşleştiriliyor...")
        guncellenen_sayi, bulunamayan_sayi, eksik_listesi = skorlari_guncelle(data, bulunan_skorlar)

        print(f"\n{'='*60}")
        print(f"📊 İŞLEM SONUCU")
        print(f"   ✅ Güncellenen maç sayısı : {guncellenen_sayi}")
        print(f"   ❌ Eşleşmeyen maç sayısı : {bulunamayan_sayi}")
        print(f"{'='*60}")

        if eksik_listesi:
            print("\n⚠️ Skoru bulunamayan geçmiş maçlar (ilk 15):")
            for mac_bilgisi in eksik_listesi[:15]:
                print(f"   - {mac_bilgisi}")

        if guncellenen_sayi > 0:
            mac_json_kaydet(data)
            print(f"\n📌 Değişiklikleri depoya kaydetmek için:")
            print(f"   git add -A && git commit -m 'Skorlar güncellendi: {datetime.date.today()}' && git push")

    except Exception as ana_hata:
        print(f"\n❌ GENEL HATA: {str(ana_hata)}")
    finally:
        if tarayici:
            print("\n🔒 Tarayıcı kapatılıyor...")
            tarayici.quit()

if __name__ == "__main__":
    main()
