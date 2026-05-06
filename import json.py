import json
import os
import time
import datetime
import re
import difflib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

MAC_JSON = "public/data/mac.json"

# ============================
# JSON İŞLEMLERİ
# ============================
def mac_json_oku():
    if os.path.exists(MAC_JSON):
        try:
            with open(MAC_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"version": 2, "updated": "", "matches": []}

def mac_json_kaydet(data):
    os.makedirs(os.path.dirname(MAC_JSON), exist_ok=True)
    data["updated"] = datetime.datetime.now().isoformat()
    with open(MAC_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============================
# TEMİZLEME VE EŞLEŞTİRME FONKSİYONLARI
# ============================
def metni_temizle(isim):
    if not isim: return ""
    isim = isim.lower().strip()
    # Türkçe karakterleri İngilizceye çevir
    tr_map = str.maketrans("çğıöşüâêîôû", "cgiosuaeiou")
    isim = isim.translate(tr_map)
    # Sadece harf ve rakam bırak (boşluk, tire, nokta vs. hepsi silinir)
    isim = re.sub(r'[^a-z0-9]', '', isim)
    return isim

def tarih_eslestir(tarih_json, tarih_site):
    # JSON dosyasındaki 2026-04-28 formatını 28.04.2026 formatına çevir
    if "-" in tarih_json and "." in tarih_site:
        try:
            y, a, g = tarih_json.split("-")
            cevrilmis_tarih = f"{g}.{a}.{y}"
            return cevrilmis_tarih == tarih_site
        except:
            pass
    return tarih_json == tarih_site

# ============================
# SPORDB VERİ ÇEKME (AKILLI LİNK OKUYUCU)
# ============================
def spordb_veri_cek():
    print("🚀 Spordb sayfası açılıyor ve Akıllı Link Okuyucu çalışıyor...")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://www.spordb.com/iddaa-programi/")
        time.sleep(8) 
        
        html = driver.page_source
        driver.quit()
        
        soup = BeautifulSoup(html, "html.parser")
        cekilen_skorlar = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            eslesme = re.search(r'/(\d{2}-\d{2}-\d{4})-(.*?)-maci-(\d+)-(\d+)/', href)
            
            if eslesme:
                tarih_ham = eslesme.group(1)      
                takimlar_str = eslesme.group(2)   
                skor_ev = int(eslesme.group(3))   
                skor_dep = int(eslesme.group(4))  
                
                # Tarihi DD.MM.YYYY formatına çevir
                g, a, y = tarih_ham.split("-")
                tarih = f"{g}.{a}.{y}"
                
                cekilen_skorlar.append({
                    "tarih": tarih,
                    "takimlar_url": takimlar_str,
                    "skor_ev": skor_ev,
                    "skor_dep": skor_dep
                })
                
        print(f"✅ Spordb'den toplam {len(cekilen_skorlar)} maç verisi linklerden başarıyla çekildi!")
        return cekilen_skorlar

    except Exception as e:
        print(f"❌ Tarayıcı Hatası: {e}")
        return []

# ============================
# SKORLARI EŞLEŞTİRME (BULANIK EŞLEŞTİRME İLE)
# ============================
def skorlari_eslestir(veri, cekilen_skorlar):
    guncellenen = 0
    mac_listesi = veri.get("matches", [])

    for mac in mac_listesi:
        # TEST İÇİN DURUM KONTROLÜNÜ KALDIRDIK! 
        # Gerçek kullanımda sadece başlamamış maçları güncellemek için alttaki satırı açabilirsin:
        # if mac.get("durum", "baslamadi") != "baslamadi": continue
        
        mac_ev_ham = mac.get("ev_sahibi", "")
        mac_dep_ham = mac.get("deplasman", "")
        mac_tarih = mac.get("tarih", "")
        
        # Takım isimlerini temizle (Boşluksuz, küçük harf)
        mac_ev_temiz = metni_temizle(mac_ev_ham)
        mac_dep_temiz = metni_temizle(mac_dep_ham)
        
        for skor in cekilen_skorlar:
            # 1. Tarih Eşleşmesi Kontrolü
            if tarih_eslestir(mac_tarih, skor["tarih"]):
                
                # Spordb linkindeki takımları temizle
                site_takimlar_temiz = metni_temizle(skor["takimlar_url"])
                
                # 2. Bulanık Takım İsmi Eşleşmesi (Difflib)
                # Ev sahibi ve Deplasman isimleri linkin içinde %60 ve üzeri benzerlikte geçiyor mu?
                benzerlik_ev = difflib.SequenceMatcher(None, mac_ev_temiz, site_takimlar_temiz).ratio()
                benzerlik_dep = difflib.SequenceMatcher(None, mac_dep_temiz, site_takimlar_temiz).ratio()
                
                # Eğer linkin içinde hem ev sahibi hem deplasman ismine benzeyen kısımlar varsa
                if mac_ev_temiz in site_takimlar_temiz and mac_dep_temiz in site_takimlar_temiz:
                    tam_eslesme = True
                elif benzerlik_ev > 0.45 and benzerlik_dep > 0.45:
                    tam_eslesme = True
                else:
                    tam_eslesme = False
                
                if tam_eslesme:
                    mac["durum"] = "bitti"
                    mac["skor_ev"] = skor["skor_ev"]
                    mac["skor_dep"] = skor["skor_dep"]
                    
                    guncellenen += 1
                    print(f"✅ BULUNDU! {mac_ev_ham} - {mac_dep_ham} ➜ {skor['skor_ev']} - {skor['skor_dep']}")
                    break
                
    return guncellenen

# ============================
# ANA ÇALIŞTIRMA
# ============================
def main():
    print("="*60)
    print("⚽ SPORDB AKILLI SKOR GÜNCELLEYİCİ (FİNAL)")
    print("="*60)
    
    mac_verisi = mac_json_oku()
    if not mac_verisi.get("matches"):
        print("⚠️ mac.json dosyasında güncellenecek maç bulunamadı!")
        return

    cekilenler = spordb_veri_cek()
    
    if cekilenler:
        guncel_sayi = skorlari_eslestir(mac_verisi, cekilenler)
        if guncel_sayi > 0:
            mac_json_kaydet(mac_verisi)
            print(f"\n🎉 İŞLEM BAŞARIYLA TAMAMLANDI! {guncel_sayi} maçın skoru dosyaya yazıldı.")
        else:
            print("\n⚠️ Maçlar çekildi ancak dosyadaki tarihlerle Spordb'deki tarihler aynı gün değil.")
    else:
        print("\n⚠️ Spordb'den hiç skor çekilemedi.")

if __name__ == "__main__":
    main()