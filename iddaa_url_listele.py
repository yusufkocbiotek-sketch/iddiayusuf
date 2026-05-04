import json
import base64

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def main():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.execute_cdp_cmd("Network.enable", {})

        print("🌐 iddaa.com açılıyor...")
        driver.get("https://www.iddaa.com/")

        print("\n✅ Chrome açıldı.")
        print("Şimdi iddaa sitesinde SKORLARIN göründüğü sayfaya git.")
        print("Örneğin: Canlı Sonuçlar > Futbol")
        print("Sonra tarihi değiştir: Önceki gün / Bugün / Takvim")
        print("Ekranda biten maç skorları görünsün.")
        input("\nSkorlar ekranda göründükten sonra ENTER'a bas...")

        logs = driver.get_log("performance")

        print("\n🔍 Network URL'leri taranıyor...\n")

        bulunan = []
        gorulen = set()

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

            url_lower = url.lower()
            mime_lower = mime.lower()

            ilgili = any(k in url_lower for k in [
                "iddaa",
                "contentv2",
                "event",
                "events",
                "match",
                "matches",
                "result",
                "results",
                "score",
                "scores",
                "sport",
                "sports",
                "live",
                "football",
                "program",
                "coupon",
                "bulletin"
            ])

            if not ilgili and "json" not in mime_lower:
                continue

            body = ""

            try:
                body_data = driver.execute_cdp_cmd(
                    "Network.getResponseBody",
                    {"requestId": request_id}
                )

                body = body_data.get("body", "")

                if body_data.get("base64Encoded"):
                    body = base64.b64decode(body).decode("utf-8", errors="ignore")

            except Exception:
                pass

            body_short = body[:500].replace("\n", " ").replace("\r", " ")

            bulunan.append({
                "url": url,
                "mime": mime,
                "body_start": body_short
            })

        with open("iddaa_url_listesi.txt", "w", encoding="utf-8") as f:
            for i, item in enumerate(bulunan, 1):
                f.write("=" * 100 + "\n")
                f.write(f"#{i}\n")
                f.write(f"MIME: {item['mime']}\n")
                f.write(f"URL: {item['url']}\n")
                f.write(f"BODY_START: {item['body_start']}\n\n")

        print(f"✅ Toplam {len(bulunan)} ilgili URL bulundu.")
        print("📄 iddaa_url_listesi.txt dosyasına yazıldı.")
        print("\nBu dosyanın içeriğini veya özellikle içinde result/score/match geçen URL'leri bana gönder.")

        input("\nTarayıcıyı kapatmak için ENTER'a bas...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()