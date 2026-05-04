import os
import json

KLASOR = "iddaa_responses"

ARANAN_KELIMELER = [
    "score",
    "skor",
    "result",
    "homeScore",
    "awayScore",
    "home_score",
    "away_score",
    "homeResult",
    "awayResult",
    "fullTime",
    "halfTime",
    "period",
    "periods",
    "status",
    "matchStatus",
    "currentScore",
    "eventScore",
    "homeTeam",
    "awayTeam",
    "competitors",
    "teams"
]


def json_icinde_ara(obj, yol=""):
    bulunanlar = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            yeni_yol = f"{yol}.{k}" if yol else k

            for kelime in ARANAN_KELIMELER:
                if kelime.lower() in str(k).lower():
                    bulunanlar.append((yeni_yol, v))

            bulunanlar.extend(json_icinde_ara(v, yeni_yol))

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            bulunanlar.extend(json_icinde_ara(item, f"{yol}[{i}]"))

    return bulunanlar


def main():
    if not os.path.exists(KLASOR):
        print(f"❌ {KLASOR} klasörü yok.")
        return

    dosyalar = [d for d in os.listdir(KLASOR) if d.endswith(".json")]

    if not dosyalar:
        print("❌ JSON dosyası bulunamadı.")
        return

    print(f"🔍 {len(dosyalar)} JSON dosyası taranıyor...\n")

    for dosya in dosyalar:
        yol = os.path.join(KLASOR, dosya)

        try:
            with open(yol, "r", encoding="utf-8") as f:
                veri = json.load(f)
        except Exception:
            continue

        bulunanlar = json_icinde_ara(veri)

        if bulunanlar:
            print("=" * 80)
            print(f"📄 DOSYA: {dosya}")
            print(f"🔎 Bulunan alan sayısı: {len(bulunanlar)}")

            for alan, deger in bulunanlar[:40]:
                deger_str = str(deger)
                if len(deger_str) > 120:
                    deger_str = deger_str[:120] + "..."
                print(f" - {alan}: {deger_str}")

            print("=" * 80)
            print()

    print("✅ Tarama bitti.")


if __name__ == "__main__":
    main()