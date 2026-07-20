import json
import re
import shutil
import traceback
from pathlib import Path
import datetime

DOSYA = Path(r"C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json")


def normalize_key(key: str) -> str:
    k = key.strip()

    # Sayı formatlarını normalize et
    k = k.replace("0,5", "0.5")
    k = k.replace("1,5", "1.5")
    k = k.replace("2,5", "2.5")
    k = k.replace("3,5", "3.5")
    k = k.replace("4,5", "4.5")

    # Eski İY formatlarını yeni formata çevir
    # Örnek: "İY Alt/Üst 0.5_Alt" -> "İlk Yarı Altı/Üstü 0.5_Alt"
    k = re.sub(r"^İY\s+Alt(?:ı)?/Üst(?:ü)?\s+", "İlk Yarı Altı/Üstü ", k)

    # Eğer yanlışlıkla "İlk Yarı Alt/Üst" gelmişse onu da düzelt
    k = re.sub(r"^İlk Yarı\s+Alt/Üst\s+", "İlk Yarı Altı/Üstü ", k)

    return k


def main():
    if not DOSYA.exists():
        print(f"❌ Dosya bulunamadı: {DOSYA}")
        input("\nKapatmak için ENTER...")
        return

    # Yedek al
    yedek = DOSYA.with_name(DOSYA.name + ".bak")
    shutil.copy2(DOSYA, yedek)
    print(f"✅ Yedek alındı: {yedek}")

    try:
        with DOSYA.open("r", encoding="utf-8") as f:
            data = json.load(f)

        matches = data.get("matches", [])
        toplam_silinen = 0
        toplam_degisen = 0
        toplam_mac = 0

        for mac in matches:
            oranlar = mac.get("oranlar", {})
            if not isinstance(oranlar, dict):
                continue

            yeni_oranlar = {}
            mac_silinen = 0
            mac_degisen = 0

            for key, value in oranlar.items():
                k = key.strip()
                kl = k.lower()

                # İstenmeyen başlangıçlar
                if kl.startswith(("oyuncu", "takım", "100.00")):
                    mac_silinen += 1
                    toplam_silinen += 1
                    continue

                yeni_key = normalize_key(k)
                if yeni_key != k:
                    mac_degisen += 1
                    toplam_degisen += 1

                # Aynı key'e dönüşürse son yazan kazansın
                yeni_oranlar[yeni_key] = value

            if mac_silinen > 0 or mac_degisen > 0:
                mac["oranlar"] = yeni_oranlar
                toplam_mac += 1

        data["updated"] = datetime.datetime.now().isoformat()

        with DOSYA.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"🗑️ Silinen oran: {toplam_silinen}")
        print(f"✏️ Değişen key: {toplam_degisen}")
        print(f"⚽ Etkilenen maç: {toplam_mac}")
        print("💾 Geçmiş JSON düzeltildi ve kaydedildi")

    except Exception as e:
        print("❌ HATA OLUŞTU:")
        print(e)
        print("\n--- DETAY ---")
        traceback.print_exc()

    input("\nKapatmak için ENTER...")


if __name__ == "__main__":
    main()