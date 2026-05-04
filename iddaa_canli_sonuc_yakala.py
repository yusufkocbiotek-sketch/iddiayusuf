import os
import re
import json
import time
import base64

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


KAYIT_KLASORU = "iddaa_skor_adaylari"


GEREKSIZ_DOMAINLER = [
    "clarity.ms",
    "google",
    "googletagmanager",
    "analytics",
    "doubleclick",
    "facebook",
    "sentry",
    "cookielaw",
    "dengage",
    "hotjar",
    "collect",
    "envelope"
]


def guvenli_dosya_adi(url):
    return re.sub(r"[^a-zA-Z0-9_-]", "_", url)[:170]


def gereksiz_url_mu(url):
    url = url.lower()
    return any(x in url for x in GEREKSIZ_DOMAINLER)


def json_mu(text):
    if not text:
        return False
    t = text.strip()
    return (t.startswith("{") and t.endswith("}")) or (t.startswith("[") and t.endswith("]"))


def skor_izi_var_mi(text):
    t = text.lower()
    aranacaklar = [
        "score",
        "skor",
        "result",
        "homeScore".lower(),
        "awayScore".lower(),
        "halfTime".lower(),
        "period",
        "periods",
        "status",
        "matchStatus".lower(),
        "homeTeam".lower(),
        "awayTeam".lower(),
        "eventName".lower(),
        "teams",
        "winner",
        "ended",
        "finished",
        "ms",
        "iy"
    ]
    return any(x in t for x in aranacaklar)


def oran_verisi_mi(text):
    """
    Sadece odd/market verisi olan JSON'ları elemek için.
    """
    t = text.lower()

    oran_izleri = [
        '"odd"',
        '"webodd"',
        '"currentodd"',
        '"marketid"',
        '"marketname"',
        '"outcomeno"',
        '"mbs"'
    ]

    skor_izleri = [
        '"score"',
        '"result"',
        '"homescore"',
        '"awayscore"',
        '"periods"',
        '"matchstatus"'
    ]

    return any(x in t for x in oran_izleri) and not any(x in t for x in skor_izleri)


def linke_tikla(driver):
    """
    Ana sayfadaki Canlı Sonuçlar Futbol linkini bulup tıklamaya çalışır.
    Bulamazsa direkt muhtemel URL'lere gider.
    """

    print("🔎 Canlı Sonuçlar Futbol linki aranıyor...")

    link_textleri = [
        "Canlı Sonuçlar Futbol",
        "CANLI SONUÇLAR FUTBOL",
        "Canlı Sonuçlar"
    ]

    for txt in link_textleri:
        try:
            elemanlar = driver.find_elements(By.PARTIAL_LINK_TEXT, txt)
            for e in elemanlar:
                href = e.get_attribute("href")
                text = e.text.strip()
                print(f"   Link bulundu: {text} -> {href}")
                if href:
                    driver.get(href)
                else:
                    e.click()
                time.sleep(5)
                return True
        except Exception:
            pass

    print("⚠️ Link bulunamadı, muhtemel URL'ler deneniyor...")

    muhtemel_urller = [
        "https://www.iddaa.com/canli-sonuclar/futbol",
        "https://www.iddaa.com/canli-sonuclar",
        "https://www.iddaa.com/canli-sonuclar/futbol/",
        "https://www.iddaa.com/canli-sonuc/futbol"
    ]

    for url in muhtemel_urller:
        print(f"🌐 Deneniyor: {url}")
        driver.get(url)
        time.sleep(5)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        if "Futbol" in body_text or "Canlı Sonuçlar" in body_text:
            return True

    return False


def main():
    os.makedirs(KAYIT_KLASORU, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.execute_cdp_cmd("Network.enable", {})

        print("🌐 iddaa.com açılıyor...")
        driver.get("https://www.iddaa.com/")
        time.sleep(5)

        linke_tikla(driver)

        print("\n✅ Şimdi Chrome'da açılan sayfaya bak.")
        print("Eğer maç skorları görünmüyorsa:")
        print(" - Canlı Sonuçlar > Futbol'a elle gir")
        print(" - Tarihi değiştir")
        print(" - Maç skorları ekranda görünsün")
        input("\nMaç skorları ekranda görünüyorsa ENTER'a bas...")

        time.sleep(2)

        # Sayfa görüntüsü ve yazısını kaydet
        driver.save_screenshot("iddaa_canli_sonuc_ekran.png")

        body_text = driver.find_element(By.TAG_NAME, "body").text
        with open("iddaa_canli_sonuc_sayfa_yazisi.txt", "w", encoding="utf-8") as f:
            f.write(body_text)

        print("📸 Ekran görüntüsü kaydedildi: iddaa_canli_sonuc_ekran.png")
        print("📄 Sayfa yazısı kaydedildi: iddaa_canli_sonuc_sayfa_yazisi.txt")

        logs = driver.get_log("performance")

        bulunan = 0
        tum_url_sayisi = 0
        aday_url_sayisi = 0
        gorulen = set()

        with open("iddaa_network_url_listesi.txt", "w", encoding="utf-8") as url_file:
            for log in logs:
                try:
                    mesaj = json.loads(log["message"])["message"]
                except Exception:
                    continue

                if mesaj.get("method") != "Network.responseReceived":
                    continue

                params = mesaj.get("params", {})
                response = params.get("response", {})
                request_id = params.get("requestId")
                url = response.get("url", "")
                mime = response.get("mimeType", "")

                if not request_id or not url:
                    continue

                if request_id in gorulen:
                    continue

                gorulen.add(request_id)
                tum_url_sayisi += 1

                if gereksiz_url_mu(url):
                    continue

                url_lower = url.lower()

                ilgili_url = any(k in url_lower for k in [
                    "iddaa",
                    "contentv2",
                    "match",
                    "matches",
                    "result",
                    "results",
                    "score",
                    "scores",
                    "sport",
                    "event",
                    "events",
                    "live",
                    "gismo",
                    "unified",
                    "sportradar",
                    "fishnet",
                    "lmt",
                    "widgets",
                    "fn"
                ])

                if not ilgili_url and "json" not in mime.lower():
                    continue

                aday_url_sayisi += 1
                url_file.write("=" * 100 + "\n")
                url_file.write(f"URL: {url}\n")
                url_file.write(f"MIME: {mime}\n\n")

                try:
                    body_data = driver.execute_cdp_cmd(
                        "Network.getResponseBody",
                        {"requestId": request_id}
                    )
                except Exception:
                    continue

                body = body_data.get("body", "")

                if body_data.get("base64Encoded"):
                    try:
                        body = base64.b64decode(body).decode("utf-8", errors="ignore")
                    except Exception:
                        continue

                if not json_mu(body):
                    continue

                if not skor_izi_var_mi(body):
                    continue

                if oran_verisi_mi(body):
                    continue

                try:
                    veri = json.loads(body)
                except Exception:
                    continue

                bulunan += 1

                dosya_adi = f"{bulunan:02d}_{guvenli_dosya_adi(url)}.json"
                yol = os.path.join(KAYIT_KLASORU, dosya_adi)

                with open(yol, "w", encoding="utf-8") as f:
                    json.dump(veri, f, ensure_ascii=False, indent=2)

                print("\n✅ Skor adayı JSON bulundu")
                print(f"#{bulunan}")
                print(f"URL: {url}")
                print(f"Dosya: {yol}")

        print("\n" + "=" * 70)
        print("ÖZET")
        print("=" * 70)
        print(f"Toplam network response : {tum_url_sayisi}")
        print(f"İlgili aday URL         : {aday_url_sayisi}")
        print(f"Kaydedilen JSON adayı   : {bulunan}")
        print("=" * 70)

        print("\n📄 Tüm ilgili URL'ler şuraya yazıldı:")
        print("iddaa_network_url_listesi.txt")

        print("\n📁 Skor adayı JSON'lar şurada:")
        print(KAYIT_KLASORU)

        if bulunan == 0:
            print("\n⚠️ Skor JSON'u bulunamadı.")
            print("Ama şu dosyalara bak:")
            print("1. iddaa_canli_sonuc_ekran.png")
            print("2. iddaa_canli_sonuc_sayfa_yazisi.txt")
            print("3. iddaa_network_url_listesi.txt")
            print("\nEğer ekran görüntüsünde skor görünmüyorsa doğru sayfaya girilmemiştir.")

        input("\nTarayıcıyı kapatmak için ENTER'a bas...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()