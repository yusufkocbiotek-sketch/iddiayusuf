import json
import os
import datetime
import time
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

def takim_eslesir_mi(ad1, ad2):
    ad1 = ad1.lower().strip()
    ad2 = ad2.lower().strip()
    if ad1 == ad2:
        return True
    if ad1 in ad2 or ad2 in ad1:
        return True
    if len(ad1) >= 5 and len(ad2) >= 5 and ad1[:5] == ad2[:5]:
        return True
    return False

def spordb_skorlari_cek(driver):
    url = "https://www.spordb.com/iddaa-programi/"
    print(f"📡 {url} açılıyor...")
    driver.get(url)
    time.sleep(12)
    
    # Son 3 günü bul ve sırayla aç
    try:
        sel = driver.find_element(By.ID, "iddaa_dateselector")
        opts = sel.find_elements(By.TAG_NAME, "option")
        
        # Bugün ve geçmiş 2 gün = toplam 3 gün
        bugun = datetime.date.today()
        hedef_tarihler = []
        
        for i in range(3):
            tarih = bugun - datetime.timedelta(days=i)
            gunAyYil = tarih.strftime("%d.%m.%Y")
            hedef_tarihler.append(gunAyYil)
        
        print(f"   📅 Kontrollücek günler: {', '.join(hedef_tarihler)}")
        
        # Her günü aç
        skorlar = []
        for gun in hedef_tarihler:
            print(f"\n   📅 {gun} açılıyor...")
            
            # O günü seç
                                  # Selenium ile tarih seç ve elementleri yeniden bul
            opts = driver.find_elements(By.TAG_NAME, "option")
            bulundu = False
            for opt in opts:
                if opt.text.strip() == gun:
                    opt.click()
                    print(f"      ✅ {gun} seçildi")
                    time.sleep(10)
                    bulundu = True
                    break
            
            if not bulundu:
                print(f"      ⚠️ {gun} bulunamadı")
                continue
            
            # Elementleri yeniden bul (sayfa yenilendi)
            opts = driver.find_elements(By.TAG_NAME, "option")
            opts = driver.find_elements(By.TAG_NAME, "option")
            
            # Skorları çek
            try:
                table = driver.find_element(By.TAG_NAME, "table")
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                aktif_tarih = tarih.isoformat()
                
                for row in rows:
                    cells = row.find_elements(By.CSS_SELECTOR, "td")
                    
                    if len(cells) == 1:
                        txt = cells[0].text.strip()
                        if len(txt) >= 10 and txt[2] == "." and txt[5] == ".":
                            try:
                                p = txt[:10].split(".")
                                aktif_tarih = f"{p[2]}-{p[1]}-{p[0]}"
                            except:
                                pass
                        continue
                    
                    if len(cells) < 10:
                        continue
                    
                    try:
                        hucre = [c.text.strip() for c in cells]
                        saat = hucre[0]
                        if not saat or ":" not in saat:
                            continue
                        
                        ev = hucre[4] if len(hucre) > 4 else ""
                        skor_text = hucre[5] if len(hucre) > 5 else ""
                        dep = hucre[6] if len(hucre) > 6 else ""
                        iy_text = hucre[7] if len(hucre) > 7 else ""
                        
                        if not ev or not dep or not skor_text:
                            continue
                        
                        if "-" in skor_text and skor_text != "-":
                            try:
                                parcalar = skor_text.strip().split("-")
                                skor_ev = int(parcalar[0].strip())
                                skor_dep = int(parcalar[1].strip())
                                
                                iy_ev = 0
                                iy_dep = 0
                                if iy_text and "-" in iy_text and iy_text != "-":
                                    iy_parcalar = iy_text.strip().split("-")
                                    iy_ev = int(iy_parcalar[0].strip())
                                    iy_dep = int(iy_parcalar[1].strip())
                                
                                skorlar.append({
                                    "ev": ev,
                                    "dep": dep,
                                    "tarih": aktif_tarih,
                                    "saat": saat,
                                    "skor_ev": skor_ev,
                                    "skor_dep": skor_dep,
                                    "skor_1y_ev": iy_ev,
                                    "skor_1y_dep": iy_dep
                                })
                            except:
                                continue
                    except:
                        continue
            
            except Exception as e:
                print(f"      ⚠️ {gun} için hata: {e}")
                continue
        
        print(f"\n   ✅ Sonuç: {len(skorlar)} maç çekildi")
        return skorlar
    
    except Exception as e:
        print(f"   ❌ Hata: {e}")
        return []

def skorlari_guncelle(data, skorlar):
    guncellenen = 0
    bulunamayan = 0
    
    for mac in data["matches"]:
        if mac["durum"] != "baslamadi":
            continue
        
        bulundu = False
        for skor in skorlar:
            if takim_eslesir_mi(mac["ev_sahibi"], skor["ev"]) and takim_eslesir_mi(mac["deplasman"], skor["dep"]):
                mac["durum"] = "bitti"
                mac["skor_ev"] = skor["skor_ev"]
                mac["skor_dep"] = skor["skor_dep"]
                mac["skor_1y_ev"] = skor["skor_1y_ev"]
                mac["skor_1y_dep"] = skor["skor_1y_dep"]
                guncellenen += 1
                bulundu = True
                print(f"   ✅ {mac['ev_sahibi']} {skor['skor_ev']}-{skor['skor_dep']} {mac['deplasman']}")
                break
        
        if not bulundu:
            bulunamayan += 1
    
    return guncellenen, bulunamayan

def main():
    print("📖 mac.json okunuyor...")
    data = mac_json_oku()
    maclar = data.get("matches", [])
    
    baslamadi = [m for m in maclar if m["durum"] == "baslamadi"]
    bitmis = [m for m in maclar if m["durum"] == "bitti"]
    
    print(f"   📊 Toplam: {len(maclar)} maç")
    print(f"   ⏳ Başlamadı: {len(baslamadi)} maç")
    print(f"   ✅ Biten: {len(bitmis)} maç")
    
    if not baslamadi:
        print("\n✅ Güncellenecek maç yok! Tümü zaten biten.")
        return
    
    tarihler = set(m["tarih"] for m in baslamadi)
    print(f"\n📅 Kontrol edilecek tarihler: {', '.join(sorted(tarihler))}")
    
    driver = None
    try:
        driver = tarayici_baslat()
        
        print("\n🔍 SporDB'den skorlar çekiliyor...")
        skorlar = spordb_skorlari_cek(driver)
        
        biten_skorlar = [s for s in skorlar if s["skor_ev"] is not None]
        print(f"   📊 SporDB'de {len(biten_skorlar)} biten maç bulundu")
        
        print(f"\n📝 Skorlar güncelleniyor...")
        guncellenen, bulunamayan = skorlari_guncelle(data, biten_skorlar)
        
        print(f"\n{'='*60}")
        print(f"📊 SONUÇ")
        print(f"   ✅ Güncellenen: {guncellenen} maç")
        print(f"   ❌ Bulunamayan: {bulunamayan} maç")
        print(f"{'='*60}")
        
        if guncellenen > 0:
            mac_json_kaydet(data)
            print(f"\n💾 mac.json güncellendi!")
            
            yeni_bitmis = [m for m in data["matches"] if m["durum"] == "bitti"]
            yeni_baslamadi = [m for m in data["matches"] if m["durum"] == "baslamadi"]
            print(f"   ✅ Biten: {len(yeni_bitmis)} maç")
            print(f"   ⏳ Başlamadı: {len(yeni_baslamadi)} maç")
            
            print(f"\n📌 GitHub'a yükleyin:")
            print(f"   git add -A")
            print(f'   git commit -m "Skorlar guncellendi"')
            print(f"   git push")
        else:
            print("\n⚠️ Güncellenecek skor bulunamadı.")
            print("   Muhtemelen maçlar henüz bitmemiş veya takım adları eşleşmiyor.")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            input("\n⏸️ Enter'a basın Chrome kapansın...")
            driver.quit()

if __name__ == "__main__":
    print("⚽ Skor Güncelleyici")
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"🌐 Kaynak: spordb.com")
    print("=" * 60)
    main()