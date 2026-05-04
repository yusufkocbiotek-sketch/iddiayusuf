import os
import re
import json
import time
import base64

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


KAYIT_KLASORU = "iddaa_responses"


def guvenli_dosya_adi(url):
    ad = re.sub(r"[^a-zA-Z0-9_-]", "_", url)
    return ad[:180]


def json_olabilir_mi(text):
    if not text:
        return False

    text_strip = text.strip()

    return (
        text_strip.startswith("{") and text_strip.endswith("}")
    ) or (
        text_strip.startswith("[") and text_strip.endswith("]")
    )


def skor_izi_var_mi(text):
    text_kucuk = text.lower()

    aranacaklar = [
        "home",
        "away",
        "result",
        "teams",
        "status",
        "periods",
        "score",
        "match",
        "matches",
        "event",
        "events",
        "galatasaray",
        "fenerbahçe",
        "fenerbahce",
        "beşiktaş",
        "besiktas",
        "trabzon",
        "başakşehir",
        "basaksehir"
    ]

    return any(kelime in text_kucuk for kelime in aranacaklar)


def main():
    os.makedirs(KAYIT_KLASORU, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    # Chrome performans/network loglarını açıyoruz
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    print("🌐 Chrome açılıyor...")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Network takibini aktif et
        driver.execute_cdp_cmd("Network.enable", {})

        print("🌐 iddaa.com açılıyor...")
        driver.get("https://www.iddaa.com/")

        print("\n✅ Tarayıcı açıldı.")
        print("Şimdi iddaa sitesinde futbol / sonuçlar / maçlar bölümüne git.")
        print("Önceki gün, Bugün veya Takvim ile tarihi değiştir.")
        print("Maçların ekranda yüklendiğinden emin ol.")

        input("\nTarihi değiştirip maçlar yüklendikten sonra ENTER'a bas...")

        print("\n🔍 Network cevapları inceleniyor...")

        logs = driver.get_log("performance")

        bulunan = 0
        gorulen_requestler = set()

        for log in logs:
            try:
                mesaj = json.loads(log["message"])["message"]
            except Exception:
                continue

            method = mesaj.get("method")
            params = mesaj.get("params", {})

            if method != "Network.responseReceived":
                continue

            response = params.get("response", {})
            request_id = params.get("requestId")
            url = response.get("url", "")
            mime_type = response.get("mimeType", "")

            if not request_id or not url:
                continue

            if request_id in gorulen_requestler:
                continue

            gorulen_requestler.add(request_id)

            url_lower = url.lower()

            # İlgili olabilecek istekleri filtreliyoruz
            aday_url = any(k in url_lower for k in [
                "gismo",
                "match",
                "matches",
                "sport",
                "result",
                "event",
                "events",
                "unified",
                "fixture",
                "football",
                "coupon",
                "bulletin"
            ])

            aday_mime = (
                "json" in mime_type.lower()
                or "javascript" not in mime_type.lower()
            )

            if not aday_url and not aday_mime:
                continue

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

            if not body:
                continue

            if not json_olabilir_mi(body):
                continue

            if not skor_izi_var_mi(body):
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

            print("\n✅ Aday JSON bulundu")
            print(f"#{bulunan}")
            print(f"URL: {url}")
            print(f"Dosya: {yol}")

        print("\n" + "=" * 70)
        print(f"Toplam aday JSON sayısı: {bulunan}")
        print("=" * 70)

        if bulunan == 0:
            print("⚠️ Hiç aday JSON bulunamadı.")
            print("Şunları dene:")
            print("1. Sayfa açıkken tarihi tekrar değiştir.")
            print("2. Maçlar tamamen yüklensin.")
            print("3. Sonra tekrar ENTER'a basarak scripti yeniden çalıştır.")
        else:
            print(f"📁 JSON dosyaları kaydedildi: {KAYIT_KLASORU}")
            print("Bu klasördeki içinde maç isimleri/skorlar olan JSON'u bana gönder.")

        input("\nTarayıcıyı kapatmak için ENTER'a bas...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()