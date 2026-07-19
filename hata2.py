import json
import shutil
import traceback

dosya = r"C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\mac.json"

try:
    SILINECEK_BASLANGICLAR = ("oyuncu", "100.00", "takım")

    # yedek al
    shutil.copy(dosya, dosya + ".yedek")
    print("✅ Yedek alındı")

    with open(dosya, "r", encoding="utf-8") as f:
        data = json.load(f)

    silinen_toplam = 0
    etkilenen_mac = 0

    for mac in data.get("matches", []):
        oranlar = mac.get("oranlar", {})
        yeni_oranlar = {}
        silinen_bu_mac = 0

        for key, value in oranlar.items():
            k = key.strip().lower()

            if k.startswith(SILINECEK_BASLANGICLAR):
                silinen_bu_mac += 1
                silinen_toplam += 1
                continue

            yeni_oranlar[key] = value

        if silinen_bu_mac > 0:
            mac["oranlar"] = yeni_oranlar
            etkilenen_mac += 1

    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"🗑️ Toplam silinen oran: {silinen_toplam}")
    print(f"⚽ Etkilenen maç: {etkilenen_mac}")
    print("💾 Dosya temizlenip kaydedildi")

except Exception as e:
    print("❌ HATA OLUŞTU:")
    print(e)
    print("\n--- DETAY ---")
    traceback.print_exc()

input("\nKapatmak için ENTER...")