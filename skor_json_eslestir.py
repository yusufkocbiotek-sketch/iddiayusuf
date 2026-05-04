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
from webdriver_manager.chrome import ChromeDriverManager

MAC_JSON = "public/data/mac.json"

def tarayici_baslat():
    print("🌐 Chrome başlatılıyor...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome başlatıldı!")
    return driver

def mac_json_oku():
    if os.path.exists(MAC_JSON):
        with open(MAC_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": 2, "updated": "", "matches": []}

def mac_json_kaydet(data):
    data["updated"] = datetime.datetime.now().isoformat()
    with open(MAC_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 mac.json güncellendi!")

def temizle_takim_adi(ad):
    ad = ad.lower().strip()
    tr_map = {'ç':'c', 'ğ':'g', 'ı':'i', 'i':'i', 'ö':'o', 'ş':'s', 'ü':'u'}
    for k, v in tr_map.items():
        ad = ad.replace(k, v)
    silinecekler = [
        " fc", "fc ", " united", " utd", " city", " as ", " ac ", " us ", " sc", 
        " fk", " nk", " cs", " cd", " deportivo", " club", " atletico", " atl.",
        " athletic", " 1911", " 1919", " 1908", " 1912", " 2000", "spor"
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
    if len(ad1_temiz) > 4 and len(ad2_temiz) > 4:
        if ad1_temiz in ad2_temiz or ad2_temiz in ad1_temiz:
            return True
        if ad1_temiz[:5] == ad2_temiz[:5]:
            return True
    benzerlik = difflib.SequenceMatcher(None, ad1_temiz, ad2_temiz).ratio()
    if benzerlik > 0.70:
        return True
    return False

def spordb_duz_metin_parse(text, aktif_tarih):
    skorlar = []
    lines = [line.strip() for line in text.split("\n") if line.strip() != ""]
    for i, line in enumerate(lines):
        if line.count("-") >= 2 and any(char.isdigit() for char in line):
            parts = line.split()
            skor_indexleri = [idx for idx, part in enumerate(parts) if "-" in part and part.replace("-","").isdigit()]
            if len(skor_indexleri) >= 2:
                ms_idx = skor_indexleri[0]
                iy_idx = skor_indexleri[1]
                ev_sahibi = " ".join(parts[:ms_idx])
                ms_skor_txt = parts[ms_idx]
                deplasman = " ".join(parts[ms_idx+1:iy_idx])
                iy_skor_txt = parts[iy_idx]
                try:
                    skor_ev, skor_dep = map(int, ms_skor_txt.split("-"))
                    skor_1y_ev, skor_1y_dep = map(int, iy_skor_txt.split("-"))
                    skorlar.append({
                        "ev": ev_sahibi, "dep": deplasman, "tarih": aktif_tarih,
                        "skor_ev": skor_ev, "skor_dep": skor_dep,
                        "skor_1y_ev": skor_1y_ev, "skor_1y_dep": skor_1y_dep
                    })
                except Exception:
                    pass
    return skorlar

def spordb_skorlari_cek(driver, gunler):
    url = "https://www.spordb.com/iddaa-programi/"
    print(f"📡 {url} açılıyor...")
    driver.get(url)
    time.sleep(10)
    tum_skorlar = []
    print(f"   📅 Kontrol edilecek günler: {', '.join(gunler)}")
    for gun in gunler:
        print(f"\n   📅 {gun} tarihi spordb'de aranıyor...")
        try:
            selects = driver.find_elements(By.TAG_NAME, "select")
            hedef_select = None
            for sel in selects:
                opts = sel.find_elements(By.TAG_NAME, "option")
                if any("." in opt.text for opt in opts) and not any("Hafta" in opt.text for opt in opts):
                    hedef_select = sel
                    break
            if not hedef_select:
                print("   ⚠️ Tarih dropdown'ı bulunamadı.")
                continue
            opts = hedef_select.find_elements(By.TAG_NAME, "option")
            tiklandi = False
            for opt in opts:
                if gun in opt.text:
                    hedef_deger = opt.get_attribute("value")
                    s = Select(hedef_select)
                    s.select_by_value(hedef_deger)
                    print(f"      ✅ {gun} seçildi, yükleniyor...")
                    time.sleep(10)
                    p = gun.split(".")
                    iso_tarih = f"{p[2]}-{p[1]}-{p[0]}"
                    body_text = driver.find_element(By.TAG_NAME, "body").text
                    cekilen = spordb_duz_metin_parse(body_text, iso_tarih)
                    tum_skorlar.extend(cekilen)
                    tiklandi = True
                    break
            if not tiklandi:
                print(f"      ⚠️ {gun} listede bulunamadı.")
        except Exception as e:
            print(f"      ⚠️ Hata: {e}")
    print(f"\n   ✅ SporDB'den toplam {len(tum_skorlar)} bitmiş maç skoru okundu.")
    return tum_skorlar

def skorlari_guncelle(data, skorlar):
    guncellenen = 0
    bulunamayan = 0
    eksik_gecmis_maclar = []
    bugun_iso = datetime.date.today().isoformat()
    for mac in data["matches"]:
        if mac["durum"] != "baslamadi":
            continue
        bulundu = False
        for skor in skorlar:
            if mac["tarih"] == skor["tarih"] and takim_eslesir_mi(mac["ev_sahibi"], skor["ev"]) and takim_eslesir_mi(mac["deplasman"], skor["dep"]):
                mac["durum"] = "bitti"
                mac["skor_ev"] = skor["skor_ev"]
                mac["skor_dep"] = skor["skor_dep"]
                mac["skor_1y_ev"] = skor["skor_1y_ev"]
                mac["skor_1y_dep"] = skor["skor_1y_dep"]
                guncellenen += 1
                bulundu = True
                print(f"   ✅ EŞLEŞTİ: (İddaa: {mac['ev_sahibi']}) <==> (SporDB: {skor['ev']} {skor['skor_ev']}-{skor['skor_dep']})")
                break
        if not bulundu:
            bulunamayan += 1
            if mac["tarih"] < bugun_iso:
                eksik_gecmis_maclar.append(f"{mac['ev_sahibi']} vs {mac['deplasman']} ({mac['tarih']})")
    return guncellenen, bulunamayan, eksik_gecmis_maclar

def main():
    print("============================================================")
    print("⚽ Skor Güncelleyici (Akıllı Eşleştirme v6.0)...")
    print("============================================================")
    data = mac_json_oku()
    maclar = data.get("matches", [])
    baslamadi = [m for m in maclar if m["durum"] == "baslamadi"]
    if not baslamadi:
        print("\n✅ Güncellenecek maç yok!")
        return
    
    # Son 3 günün tarihlerini otomatik al
    bugun = datetime.date.today()
    aranacak_gunler = [
        (bugun - datetime.timedelta(days=i)).strftime("%d.%m.%Y") for i in range(3)
    ]
    
    driver = None
    try:
        driver = tarayici_baslat()
        skorlar = spordb_skorlari_cek(driver, aranacak_gunler)
        print("\n📝 Skorlar eşleştiriliyor...")
        guncellenen, bulunamayan, eksik_liste = skorlari_guncelle(data, skorlar)
        print(f"\n{'='*60}")
        print(f"📊 SONUÇ")
        print(f"   ✅ Güncellenen: {guncellenen} maç")
        print(f"   ❌ Bulunamayan: {bulunamayan} maç")
        print(f"{'='*60}")
        if eksik_liste:
            print("\n⚠️ Eşleşmeyen geçmiş maçlar:")
            for e in eksik_liste[:15]:
                print(f"   - {e}")
        if guncellenen > 0:
            mac_json_kaydet(data)
            print(f"\n📌 GitHub'a yükleyin: git add -A && git commit -m 'Skorlar guncellendi' && git push")
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()