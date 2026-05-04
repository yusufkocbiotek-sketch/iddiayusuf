import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def main():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.iddaa.com/")

        print("Chrome açıldı.")
        print("iddaa içinde skorların göründüğü sayfaya git.")
        print("Tarihi değiştir ve maç skorlarının ekranda göründüğünden emin ol.")
        input("Hazır olunca ENTER'a bas...")

        time.sleep(2)

        text = driver.find_element("tag name", "body").text

        with open("iddaa_sayfa_yazisi.txt", "w", encoding="utf-8") as f:
            f.write(text)

        print("✅ Sayfa yazısı iddaa_sayfa_yazisi.txt dosyasına kaydedildi.")
        print("Bu dosyadan skorların olduğu bölümü bana gönderebilirsin.")

        input("Kapatmak için ENTER'a bas...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()