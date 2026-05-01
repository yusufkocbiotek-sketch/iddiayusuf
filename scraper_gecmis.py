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

CIKTI_DOSYA = "public/data/gecmis_maclar.json"

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

def veri_kaydet(maclar):
    data = {
        "version": 1,
        "updated": datetime.datetime.now().isoformat(),
        "kaynak": "spordb.com",
        "toplam_mac": len(maclar),
        "biten_mac": sum(1 for m in maclar if m["durum"] == "bitti"),
        "matches": maclar
    }
    os.makedirs(os.path.dirname(CIKTI_DOSYA), exist_ok=True)
    with open(CIKTI_DOSYA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"   💾 {len(maclar)} maç kaydedildi → {CIKTI_DOSYA}")

def skor_parse(skor_text):
    try:
        if not skor_text or skor_text.strip() == "-":
            return None, None
        parcalar = skor_text.strip().split("-")
        return int(parcalar[0].strip()), int(parcalar[1].strip())
    except:
        return None, None

def oran_parse(text):
    try:
        return float(text.strip())
    except:
        return None

def hafta_maclarini_cek(driver):
    maclar = []
    try:
        table = driver.find_element(By.CSS_SELECTOR, "table.datatable, table.ajaxtable, table")
        rows = table.find_elements(By.TAG_NAME, "tr")
    except:
        # Tablo bulunamazsa body text'ten parse et
        return maclar_body_parse(driver)

    aktif_tarih = datetime.date.today().isoformat()
    aktif_lig = ""

    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, "td")

        # Tek hücreli satır = tarih veya lig başlığı
        if len(cells) == 1:
            txt = cells[0].text.strip()
            # DD.MM.YYYY formatı
            if len(txt) >= 10 and txt[2] == "." and txt[5] == ".":
                try:
                    p = txt[:10].split(".")
                    aktif_tarih = f"{p[2]}-{p[1]}-{p[0]}"
                except:
                    pass
            elif len(txt) > 3 and not txt[0].isdigit():
                aktif_lig = txt
            continue

        if len(cells) < 10:
            continue

        try:
            hucre = [c.text.strip() for c in cells]
            saat = hucre[0]

            if not saat or ":" not in saat or len(saat) > 5:
                continue

            # Takım adlarını bul
            ev_sahibi = ""
            deplasman = ""
            skor_text = ""
            iy_skor_text = ""

            for j, h in enumerate(hucre):
                if " - " in h and any(c.isalpha() for c in h):
                    # Bu takım satırı: "Bolivar 2-0 Fluminense 1-0" veya "Bolivar - Fluminense"
                    # SporDB formatı: "Takım1 Skor Takım2 IYSkor"
                    pass

            # SporDB tablo yapısı (test_spordb2'den):
            # [0]=Saat, [2]=Lig, [3]=MBS, [4]=EvSahibi, [5]=Skor, [6]=Deplasman, [7]=IYSkor
            # [8]=MS1, [9]=MS0, [10]=MS2, [11]=AUAlt, [12]=AUUst
            # [13]=KGVar, [14]=KGYok, [15]=IY05Alt, [16]=IY05Ust, [17]=AU15Alt, [18]=AU15Ust

            lig = hucre[2] if len(hucre) > 2 else aktif_lig
            ev_sahibi = hucre[4] if len(hucre) > 4 else ""
            skor_text = hucre[5] if len(hucre) > 5 else ""
            deplasman = hucre[6] if len(hucre) > 6 else ""
            iy_skor_text = hucre[7] if len(hucre) > 7 else ""

            if not ev_sahibi or not deplasman:
                continue

            skor_ev, skor_dep = skor_parse(skor_text)
            iy_ev, iy_dep = skor_parse(iy_skor_text)

            durum = "bitti" if skor_ev is not None else "baslamadi"

            oranlar = {}
            ms1 = oran_parse(hucre[8]) if len(hucre) > 8 else None
            ms0 = oran_parse(hucre[9]) if len(hucre) > 9 else None
            ms2 = oran_parse(hucre[10]) if len(hucre) > 10 else None
            au_alt = oran_parse(hucre[11]) if len(hucre) > 11 else None
            au_ust = oran_parse(hucre[12]) if len(hucre) > 12 else None
            kg_var = oran_parse(hucre[13]) if len(hucre) > 13 else None
            kg_yok = oran_parse(hucre[14]) if len(hucre) > 14 else None
            iy05_alt = oran_parse(hucre[15]) if len(hucre) > 15 else None
            iy05_ust = oran_parse(hucre[16]) if len(hucre) > 16 else None
            au15_alt = oran_parse(hucre[17]) if len(hucre) > 17 else None
            au15_ust = oran_parse(hucre[18]) if len(hucre) > 18 else None

            if ms1: oranlar["Maç Sonucu_1"] = ms1
            if ms0: oranlar["Maç Sonucu_0"] = ms0
            if ms2: oranlar["Maç Sonucu_2"] = ms2
            if au_alt: oranlar["Alt/Üst 2.5_Alt"] = au_alt
            if au_ust: oranlar["Alt/Üst 2.5_Üst"] = au_ust
            if kg_var: oranlar["Karşılıklı Gol_Var"] = kg_var
            if kg_yok: oranlar["Karşılıklı Gol_Yok"] = kg_yok
            if iy05_alt: oranlar["İY Alt/Üst 0.5_Alt"] = iy05_alt
            if iy05_ust: oranlar["İY Alt/Üst 0.5_Üst"] = iy05_ust
            if au15_alt: oranlar["Alt/Üst 1.5_Alt"] = au15_alt
            if au15_ust: oranlar["Alt/Üst 1.5_Üst"] = au15_ust

            if not oranlar:
                continue

            maclar.append({
                "ev_sahibi": ev_sahibi,
                "deplasman": deplasman,
                "saat": saat,
                "tarih": aktif_tarih,
                "lig": lig if lig else aktif_lig,
                "durum": durum,
                "skor_ev": skor_ev if skor_ev is not None else 0,
                "skor_dep": skor_dep if skor_dep is not None else 0,
                "skor_1y_ev": iy_ev if iy_ev is not None else 0,
                "skor_1y_dep": iy_dep if iy_dep is not None else 0,
                "kaynak": "spordb.com",
                "oranlar": oranlar
            })

        except:
            continue

    return maclar

def maclar_body_parse(driver):
    """Tablo bulunamazsa body text'ten parse et"""
    maclar = []
    body = driver.find_element(By.TAG_NAME, "body")
    text = body.text
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    aktif_tarih = datetime.date.today().isoformat()
    i = 0

    while i < len(lines):
        line = lines[i]

        # Tarih satırı (DD.MM.YYYY)
        if len(line) >= 10 and line[2] == "." and line[5] == ".":
            try:
                p = line[:10].split(".")
                aktif_tarih = f"{p[2]}-{p[1]}-{p[0]}"
            except:
                pass
            i += 1
            continue

        # Saat satırı (HH:MM)
        if len(line) == 5 and line[2] == ":" and line[:2].isdigit():
            saat = line

            # Sonraki satırlarda takım + skor + oranlar olmalı
            # SporDB body formatı:
            # "Takım1 Skor Takım2 IYSkor Oran1 Oran2 Oran3..."
            if i + 1 < len(lines):
                mac_line = lines[i + 1]
                # "Bolivar 2-0 Fluminense 1-0 1.72 2.98 3.50 1.47 1.91 1.74 1.59 2.35 1.28 2.68 1.21"
                parts = mac_line.split()

                # Skor bul (X-Y formatında)
                skor_idx = -1
                for pi, p in enumerate(parts):
                    if "-" in p and len(p) <= 5:
                        try:
                            a, b = p.split("-")
                            int(a)
                            int(b)
                            skor_idx = pi
                            break
                        except:
                            continue

                if skor_idx > 0:
                    ev = " ".join(parts[:skor_idx])
                    skor_text = parts[skor_idx]

                    # Deplasman ve IY skoru bul
                    kalan = parts[skor_idx + 1:]
                    dep_parts = []
                    iy_skor = ""
                    oranlar_list = []

                    for kp in kalan:
                        try:
                            float(kp)
                            oranlar_list.append(float(kp))
                        except:
                            if "-" in kp and len(kp) <= 5:
                                try:
                                    a, b = kp.split("-")
                                    int(a)
                                    int(b)
                                    iy_skor = kp
                                except:
                                    dep_parts.append(kp)
                            else:
                                dep_parts.append(kp)

                    dep = " ".join(dep_parts)
                    skor_ev, skor_dep = skor_parse(skor_text)
                    iy_ev, iy_dep = skor_parse(iy_skor)

                    if ev and dep:
                        oranlar = {}
                        if len(oranlar_list) > 0: oranlar["Maç Sonucu_1"] = oranlar_list[0]
                        if len(oranlar_list) > 1: oranlar["Maç Sonucu_0"] = oranlar_list[1]
                        if len(oranlar_list) > 2: oranlar["Maç Sonucu_2"] = oranlar_list[2]
                        if len(oranlar_list) > 3: oranlar["Alt/Üst 2.5_Alt"] = oranlar_list[3]
                        if len(oranlar_list) > 4: oranlar["Alt/Üst 2.5_Üst"] = oranlar_list[4]
                        if len(oranlar_list) > 5: oranlar["Karşılıklı Gol_Var"] = oranlar_list[5]
                        if len(oranlar_list) > 6: oranlar["Karşılıklı Gol_Yok"] = oranlar_list[6]
                        if len(oranlar_list) > 7: oranlar["İY Alt/Üst 0.5_Alt"] = oranlar_list[7]
                        if len(oranlar_list) > 8: oranlar["İY Alt/Üst 0.5_Üst"] = oranlar_list[8]
                        if len(oranlar_list) > 9: oranlar["Alt/Üst 1.5_Alt"] = oranlar_list[9]
                        if len(oranlar_list) > 10: oranlar["Alt/Üst 1.5_Üst"] = oranlar_list[10]

                        if oranlar:
                            durum = "bitti" if skor_ev is not None else "baslamadi"
                            maclar.append({
                                "ev_sahibi": ev,
                                "deplasman": dep,
                                "saat": saat,
                                "tarih": aktif_tarih,
                                "lig": "",
                                "durum": durum,
                                "skor_ev": skor_ev if skor_ev is not None else 0,
                                "skor_dep": skor_dep if skor_dep is not None else 0,
                                "skor_1y_ev": iy_ev if iy_ev is not None else 0,
                                "skor_1y_dep": iy_dep if iy_dep is not None else 0,
                                "kaynak": "spordb.com",
                                "oranlar": oranlar
                            })
                i += 2
                continue

        i += 1

    return maclar

def gecmis_cek(driver, kac_hafta=25):
    url = "https://www.spordb.com/iddaa-programi/"

    print(f"📡 {url} açılıyor...")
    driver.get(url)
    time.sleep(10)

    # Hafta dropdown'ını bul
    selects = driver.find_elements(By.TAG_NAME, "select")
    hafta_select = None

    for sel in selects:
        opts = sel.find_elements(By.TAG_NAME, "option")
        if len(opts) > 10:
            first_text = opts[0].text.strip() if opts else ""
            if "202" in first_text:
                hafta_select = sel
                break

    if not hafta_select:
        print("❌ Hafta dropdown bulunamadı!")
        return []

    options = hafta_select.find_elements(By.TAG_NAME, "option")
    print(f"📅 {len(options)} hafta bulundu")

    tum_maclar = []

    for hafta_idx in range(min(kac_hafta, len(options))):
        try:
            # Sayfayı yeniden yükle
            driver.get(url)
            time.sleep(5)

            # Dropdown tekrar bul
            selects = driver.find_elements(By.TAG_NAME, "select")
            for sel in selects:
                opts = sel.find_elements(By.TAG_NAME, "option")
                if len(opts) > 10:
                    first_text = opts[0].text.strip() if opts else ""
                    if "202" in first_text:
                        hafta_select = sel
                        break

            options = hafta_select.find_elements(By.TAG_NAME, "option")

            if hafta_idx >= len(options):
                break

            opt = options[hafta_idx]
            hafta_text = opt.text.strip()
            hafta_value = opt.get_attribute("value")

            print(f"\n{'='*60}")
            print(f"📅 [{hafta_idx+1}/{kac_hafta}] {hafta_text}")
            print(f"{'='*60}")

            Select(hafta_select).select_by_value(hafta_value)
            time.sleep(8)

            # Sayfayı kaydır
            for s in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)

            # Maçları çek
            maclar = hafta_maclarini_cek(driver)

            biten = sum(1 for m in maclar if m["durum"] == "bitti")
            print(f"   📋 {len(maclar)} maç ({biten} biten)")

            if maclar:
                tum_maclar.extend(maclar)
                veri_kaydet(tum_maclar)

        except Exception as e:
            print(f"   ⚠️ Hafta hatası: {str(e)[:60]}")
            continue

    return tum_maclar

def main():
    driver = None
    baslangic = datetime.datetime.now()

    try:
        driver = tarayici_baslat()
        KAC_HAFTA = 25
        maclar = gecmis_cek(driver, KAC_HAFTA)

        bitis = datetime.datetime.now()
        sure = bitis - baslangic

        biten = sum(1 for m in maclar if m["durum"] == "bitti")
        toplam_oran = sum(len(m["oranlar"]) for m in maclar)

        print(f"\n{'='*60}")
        print(f"📊 FİNAL SONUÇ")
        print(f"   ⚽ Toplam maç: {len(maclar)}")
        print(f"   ✅ Biten: {biten}")
        print(f"   📊 Toplam oran: {toplam_oran}")
        print(f"   ⏱️ Süre: {sure}")
        print(f"   📁 Dosya: {CIKTI_DOSYA}")
        print(f"{'='*60}")

        if maclar:
            veri_kaydet(maclar)
            print("\n🎉 Geçmiş maçlar başarıyla çekildi!")

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if driver:
            input("\n⏸️ Enter'a basın Chrome kapansın...")
            driver.quit()

if __name__ == "__main__":
    print("⚽ SporDB Geçmiş Maç Çekici")
    print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"🌐 Kaynak: spordb.com")
    print(f"⚠️ Mevcut sisteme DOKUNMAZ!")
    print("=" * 60)
    main()