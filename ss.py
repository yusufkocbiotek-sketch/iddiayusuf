import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Temizlenecek dosyalar (olanlar işlenir, olmayanlar atlanır)
DOSYALAR = [
    BASE_DIR / "public" / "data" / "mac.json",
]

SILINECEK_ALANLAR = ["kaynak", "mac_kodu"]

def dosya_temizle(path):
    if not path.exists():
        print(f"⏭️  Atlandı (yok): {path.name}")
        return

    eski_boyut = path.stat().st_size / (1024 * 1024)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    maclar = data.get("matches", [])
    silinen = 0
    for mac in maclar:
        for alan in SILINECEK_ALANLAR:
            if alan in mac:
                del mac[alan]
                silinen += 1

    # Önce geçici dosyaya yaz, sorun yoksa üzerine taşı (yarım kayıt riski yok)
    temp_path = path.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    temp_path.replace(path)

    yeni_boyut = path.stat().st_size / (1024 * 1024)
    print(f"✅ {path.name}: {len(maclar)} maç | {silinen} alan silindi | "
          f"{eski_boyut:.1f} MB → {yeni_boyut:.1f} MB")

if __name__ == "__main__":
    for dosya in DOSYALAR:
        try:
            dosya_temizle(dosya)
        except Exception as e:
            print(f"❌ HATA ({dosya.name}): {e}")
    input("\n✅ Bitti. ENTER ile kapat...")