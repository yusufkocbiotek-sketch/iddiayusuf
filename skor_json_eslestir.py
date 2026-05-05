import json
import os
import time
import re
import difflib
from datetime import datetime, timedelta  # ✅ DEĞİŞTİ: datetime modülünden direkt import
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

MAC_JSON = "public/data/mac.json"

def mac_json_oku():
    if os.path.exists(MAC_JSON):
        try:
            with open(MAC_JSON, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: pass
    return {"version": 2, "updated": "", "matches": []}

def mac_json_kaydet(data):
    os.makedirs(os.path.dirname(MAC_JSON), exist_ok=True)
    data["updated"] = datetime.now().isoformat()  # ✅ DEĞİŞTİ: datetime.datetime → datetime
    with open(MAC_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def metni_temizle(isim):
    if not isim: return ""
    isim = isim.lower().strip()
    tr_map = str.maketrans("çğıöşüâêîôû", "cgiosuaeiou")
    isim = isim.translate(tr_map)
    isim = re.sub(r'[^a-z0-9]', '', isim)
    return isim

def tarih_eslestir(tarih_json, tarih_site):
    if "-" in tarih_json and "." in tarih_site:
        try:
            y, a, g = tarih_json.split("-")
            return f"{g}.{a}.{y}" == tarih_site
        except Exception: pass
    return tarih_json == tarih_site

def spordb_veri_cek():
    print("🚀 Spordb 'İddaa Programı' sayfası açılıyor...")
    
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://www.spordb.com/iddaa-programi/")
        
        print("⏳ Tarih seçme menüsü bekleniyor...")
        
        # Sayfa ilk açıldığında menüyü bul
        dropdown_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "iddaa_dateselector"))
        )
        select = Select(dropdown_element)
        
        # Tüm tarihleri al
        tum_tarihler = [opt.get_attribute("value") for opt in select.options if opt.get_attribute("value") != "*"]
        
        # 🎯 KRİTİK DÜZELTME: Bugünden (6 Mayıs) geriye doğru son 3 günü hesapla
        bugun = datetime.now()  # ✅ DEĞİŞTİ: datetime.datetime → datetime
        hedef_tarihler = []
        
        for i in range(3):  # 0, 1, 2 (Bugün, dün, evvelsi gün)
            tarih_obj = bugun - timedelta(days=i)  # ✅ DEĞİŞTİ: datetime.timedelta → timedelta
            # Dropdown formatına çevir: "DD.MM.YYYY" (örn: "06.05.2026")
            tarih_str = tarih_obj.strftime("%Y-%m-%d")
            hedef_tarihler.append(tarih_str)
        
        # Dropdown'da olan tarihleri filtrele (eğer o gün maç yoksa listede olmayabilir)
        son_3_gun = [t for t in hedef_tarihler if t in tum_tarihler]
        
        # Eğer hesaplanan tarihlerden hiçbiri yoksa (çok nadir), mevcut son 3 günü al (yedek)
        if not son_3_gun:
            print(f"⚠️ {hedef_tarihler} tarihlerinde maç bulunamadı, mevcut son tarihler alınıyor...")
            son_3_gun = tum_tarihler[-3:] if len(tum_tarihler) >= 3 else tum_tarihler
            
        print(f"📅 Şu {len(son_3_gun)} gün taranacak: {son_3_gun}")
        
        cekilen_skorlar = []
        
        for i, gun in enumerate(son_3_gun):
            print(f"   🔎 {gun} tarihi seçiliyor...")
            
            # ⚠️ KRİTİK DÜZELTME: İlk tarihten sonra (i > 0) DOM yenilendiği için
            # Python'a "Hayalet menüyü bırak, git yenisini bul!" diyoruz.
            if i > 0:
                dropdown_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "iddaa_dateselector"))
                )
                select = Select(dropdown_element)

            # Tarihi seç
            select.select_by_value(gun)
            
            # Sitenin veriyi getirmesi için bekleme (4 saniye yeterli olacaktır)
            time.sleep(4) 
            
            # Sayfanın güncel halini al ve analiz et
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                eslesme = re.search(r'/(\d{2}-\d{2}-\d{4})-(.*?)-maci-(\d+)-(\d+)/', href)
                
                if eslesme:
                    tarih_ham = eslesme.group(1)      
                    takimlar_str = eslesme.group(2)   
                    skor_ev = int(eslesme.group(3))   
                    skor_dep = int(eslesme.group(4))  
                    
                    g, a, y = tarih_ham.split("-")
                    tarih = f"{g}.{a}.{y}"
                    
                    cekilen_skorlar.append({
                        "tarih": tarih,
                        "takimlar_url": takimlar_str,
                        "skor_ev": skor_ev,
                        "skor_dep": skor_dep
                    })
                    
        driver.quit()
        
        # Tekrarlayan maçları temizle
        benzersiz_skorlar = []
        for skor in cekilen_skorlar:
            if skor not in benzersiz_skorlar:
                benzersiz_skorlar.append(skor)
                
        print(f"✅ Son {len(son_3_gun)} günden toplam {len(benzersiz_skorlar)} maç skoru çekildi!")
        return benzersiz_skorlar

    except Exception as e:
        print(f"❌ Hata: {e}")
        print("💡 İpucu: Sayfa yapısı değişmiş veya internet yavaş olabilir.")
        return []

def skorlari_eslestir(veri, cekilen_skorlar):
    guncellenen = 0
    mac_listesi = veri.get("matches", [])

    for mac in mac_listesi:
        if mac.get("durum", "baslamadi") != "baslamadi":
            continue
        
        mac_ev_temiz = metni_temizle(mac.get("ev_sahibi", ""))
        mac_dep_temiz = metni_temizle(mac.get("deplasman", ""))
        mac_tarih = mac.get("tarih", "")
        
        for skor in cekilen_skorlar:
            if tarih_eslestir(mac_tarih, skor["tarih"]):
                site_takimlar_temiz = metni_temizle(skor["takimlar_url"])
                
                benzerlik_ev = difflib.SequenceMatcher(None, mac_ev_temiz, site_takimlar_temiz).ratio()
                benzerlik_dep = difflib.SequenceMatcher(None, mac_dep_temiz, site_takimlar_temiz).ratio()
                
                if (mac_ev_temiz in site_takimlar_temiz and mac_dep_temiz in site_takimlar_temiz) or \
                   (benzerlik_ev > 0.45 and benzerlik_dep > 0.45):
                    
                    mac["durum"] = "bitti"
                    mac["skor_ev"] = skor["skor_ev"]
                    mac["skor_dep"] = skor["skor_dep"]
                    
                    guncellenen += 1
                    print(f"✅ BULUNDU! {mac.get('ev_sahibi')} - {mac.get('deplasman')} ➜ {skor['skor_ev']} - {skor['skor_dep']}")
                    break
                
    return guncellenen

def main():
    print("="*60)
    print("⚽ SPORDB OTOMATİK SKOR GÜNCELLEYİCİ (V3.2)")
    print("="*60)
    
    mac_verisi = mac_json_oku()
    if not mac_verisi.get("matches"):
        print("⚠️ mac.json dosyasında maç bulunamadı!")
        return

    cekilenler = spordb_veri_cek()
    
    if cekilenler:
        guncel_sayi = skorlari_eslestir(mac_verisi, cekilenler)
        if guncel_sayi > 0:
            mac_json_kaydet(mac_verisi)
            print(f"\n🎉 İŞLEM TAMAMLANDI! {guncel_sayi} maçın skoru başarıyla güncellendi.")
        else:
            print("\n⚠️ Bekleyen maçlar arasında yeni biten bir eşleşme bulunamadı.")
    else:
        print("\n⚠️ Veri çekilemedi.")

if __name__ == "__main__":
    main()