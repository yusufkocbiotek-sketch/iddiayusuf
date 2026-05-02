import json
import os
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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
    print(f"   💾 mac.json güncellendi!")

def takim_eslesir_mi(ad1, ad2):
    # İddaa.com'un kendi sitesinden çektiğimiz için %100 aynı olacak.
    # Yine de boşlukları ve küçük/büyük harfleri koruyalım.
    return ad1.lower().strip() == ad2.lower().strip()

def iddaa_biten_skorlari_cek(driver):
    # İddaa.com'da maç sonuçları "canli-skor" sayfasının "bitenler" sekmesindedir.
    url = "https://www.iddaa.com/canli-skor/futbol"
    print(f"📡 {url} açılıyor...")
    driver.get(url)
    
    print("   ⏳ Sayfanın yüklenmesi bekleniyor (15 saniye)...")
    time.sleep(15)

    skorlar = []

    try:
        # "Bitenler" sekmesini bul ve tıkla
        sekme_tiklandi = False
        buttons = driver.find_elements(By.CSS_SELECTOR, "a, button, span, div")
        for btn in buttons:
            txt = btn.text.strip().lower()
            if txt == "bitenler" or "bitti" in txt or "bitmiş maçlar" in txt:
                print(f"   🖱️ '{btn.text.strip()}' sekmesi bulundu, tıklanıyor...")
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", btn)
                sekme_tiklandi = True
                time.sleep(8)
                break
                
        if not sekme_tiklandi:
            print("   ⚠️ 'Bitenler' sekmesi bulunamadı. Genel skorlara bakılacak.")
    except Exception as e:
        print(f"   ⚠️ Sekme tıklama hatası: {e}")

    # Sayfadaki maçları yüklemek için scroll yapalım
    print("   📜 Tüm sonuçlar yükleniyor (Aşağı kaydırılıyor)...")
    son_yukseklik = driver.execute_script("return document.body.scrollHeight")
    for s in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        yeni = driver.execute_script("return document.body.scrollHeight")
        if yeni == son_yukseklik:
            break
        son_yukseklik = yeni
    
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

    # İddaa.com canlı skor yapısı parse ediliyor
    print("   🔍 Sayfa içeriği analiz ediliyor...")
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        lines = [line.strip() for line in body.text.split("\n") if line.strip() != ""]
        
        # İddaa.com'da genelde: "Ev Sahibi", "2 - 1", "Deplasman" veya benzeri sıralamalar olur.
        # İddaa.com skor formatı: MS skoru genellikle '-' işaretli ve arada boşlukludur (Örn: 2 - 1)
        for i, line in enumerate(lines):
            # Eğer satır skor formatına benziyorsa (Örn: "2 - 1" veya "0 - 0")
            if "-" in line and len(line) <= 9 and any(c.isdigit() for c in line):
                try:
                    # Skoru parçala
                    s_ev, s_dep = map(int, line.replace(" ", "").split("-"))
                    
                    # Takım isimlerini yakala (İddaa.com'un HTML dizilimine göre takımlar ya skordan önce/sonra ya da alt alta olur)
                    # En mantıklı yaklaşım: Eğer etrafında saat veya lig ismi olmayan bir "metin" varsa o takımdır.
                    ev = lines[i-1] if i-1 >= 0 else ""
                    dep = lines[i+1] if i+1 < len(lines) else ""
                    
                    # İlk Yarı skoru genelde "(İY X-X)" veya alt satırda "X-X" şeklindedir
                    iy_ev, iy_dep = 0, 0
                    iy_line = lines[i+2] if i+2 < len(lines) else ""
                    if "-" in iy_line and any(c.isdigit() for c in iy_line):
                        try:
                            # Örn: (1-0) veya İY: 1-0
                            iy_temiz = ''.join(c for c in iy_line if c.isdigit() or c == '-')
                            iy_e, iy_d = map(int, iy_temiz.split("-"))
                            iy_ev, iy_dep = iy_e, iy_d
                        except:
                            pass
                    
                    if ev and dep and not ev.isdigit() and not dep.isdigit():
                        skorlar.append({
                            "ev": ev,
                            "dep": dep,
                            "skor_ev": s_ev,
                            "skor_dep": s_dep,
                            "skor_1y_ev": iy_ev,
                            "skor_1y_dep": iy_dep
                        })
                except Exception:
                    pass
    except Exception as e:
        print(f"   ⚠️ Parse hatası: {e}")

    print(f"   ✅ iddaa.com'dan {len(skorlar)} biten maç skoru okundu.")
    return skorlar

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
            if takim_eslesir_mi(mac["ev_sahibi"], skor["ev"]) and takim_eslesir_mi(mac["deplasman"], skor["dep"]):
                mac["durum"] = "bitti"
                mac["skor_ev"] = skor["skor_ev"]
                mac["skor_dep"] = skor["skor_dep"]
                mac["skor_1y_ev"] = skor["skor_1y_ev"]
                mac["skor_1y_dep"] = skor["skor_1y_dep"]
                guncellenen += 1
                bulundu = True
                print(f"   ✅ EŞLEŞTİ: (İddaa Bülten: {mac['ev_sahibi']} vs {mac['deplasman']}) <==> (İddaa Sonuç: {skor['ev']} {skor['skor_ev']}-{skor['skor_dep']} {skor['dep']})")
                break
        
        if not bulundu:
            bulunamayan += 1
            if mac["tarih"] < bugun_iso:
                eksik_gecmis_maclar.append(f"{mac['ev_sahibi']} vs {mac['deplasman']} ({mac['tarih']} {mac['saat']})")

    return guncellenen, bulunamayan, eksik_gecmis_maclar

def main():
    print("============================================================")
    print("⚽ Skor Güncelleyici (KAYNAK: IDDAA.COM CANLI SKOR)...")
    print("============================================================")
    
    print("📖 mac.json okunuyor...")
    data = mac_json_oku()
    maclar = data.get("matches", [])
    
    baslamadi = [m for m in maclar if m["durum"] == "baslamadi"]
    bitmis = [m for m in maclar if m["durum"] == "bitti"]
    
    print(f"   📊 Toplam: {len(maclar)} maç")
    print(f"   ⏳ Başlamadı: {len(baslamadi)} maç")
    print(f"   ✅ Biten: {len(bitmis)} maç")
    
    if not baslamadi:
        print("\n✅ Güncellenecek 'başlamadı' durumunda maç yok!")
        return

    driver = None
    try:
        driver = tarayici_baslat()
        skorlar = iddaa_biten_skorlari_cek(driver)
        
        print("\n📝 İddaa.com Sonuçları ile Bülten verileriniz eşleştiriliyor...")
        guncellenen, bulunamayan, eksik_liste = skorlari_guncelle(data, skorlar)
        
        print(f"\n{'='*60}")
        print(f"📊 SONUÇ")
        print(f"   ✅ Eşleşip Güncellenen: {guncellenen} maç")
        print(f"   ❌ Oynanmamış veya Eşleşemeyen: {bulunamayan} maç")
        print(f"{'='*60}")
        
        if eksik_liste:
            print("\n⚠️ Dün veya öncesine ait olup skoru bulunamayan takımlar (Maç iptal/ertelenmiş olabilir):")
            for e in eksik_liste[:15]:
                print(f"   - {e}")

        if guncellenen > 0:
            mac_json_kaydet(data)
            print(f"\n📌 Lütfen GitHub'a yükleyin: git add -A && git commit -m 'Skorlar guncellendi' && git push")
            
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()