import json
import datetime
from pathlib import Path

# ================= AYARLAR =================
KAYNAK_DOSYA = Path(r"C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json")

BASLANGIC = "2026-10-01"   # dahil
BITIS     = "2026-11-01"   # dahil

# Çıktı dosyaları (kaynak dosyanın yanına yazılır)
ARALIK_DOSYA = KAYNAK_DOSYA.parent / "gecmis_maclar_ekim.json"
KALAN_DOSYA  = KAYNAK_DOSYA.parent / "gecmis_maclar_kalan.json"
# ===========================================

def tarih_parse(t):
    t = str(t).strip()[:10]
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d-%m-%Y", "%Y.%m.%d"):
        try:
            return datetime.datetime.strptime(t, fmt).date()
        except ValueError:
            continue
    return None

def kaydet(path, maclar, son_guncelleme):
    temp = path.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"matches": maclar, "son_guncelleme": son_guncelleme},
                  f, ensure_ascii=False, separators=(",", ":"))
    temp.replace(path)
    boyut = path.stat().st_size / (1024 * 1024)
    print(f"💾 {path.name}: {len(maclar)} maç | {boyut:.1f} MB")

if __name__ == "__main__":
    bas = tarih_parse(BASLANGIC)
    bit = tarih_parse(BITIS)

    print(f"📂 Okunuyor: {KAYNAK_DOSYA.name} ...")
    with open(KAYNAK_DOSYA, "r", encoding="utf-8") as f:
        data = json.load(f)

    maclar = data.get("matches", [])
    son_guncelleme = data.get("son_guncelleme", "")
    print(f"📊 Toplam: {len(maclar)} maç")

    aralik, kalan, tarihsiz = [], [], 0

    for mac in maclar:
        d = tarih_parse(mac.get("tarih", ""))
        if d is None:
            tarihsiz += 1
            kalan.append(mac)   # tarihi bozuk olanları kaybetme, kalanda tut
        elif bas <= d <= bit:
            aralik.append(mac)
        else:
            kalan.append(mac)

    print(f"\n✂️ {BASLANGIC} → {BITIS} aralığı: {aralik} maç yerine {len(aralik)} maç")
    print(f"📦 Aralık dışı: {len(kalan)} maç" + (f" ({tarihsiz} tarihsiz dahil)" if tarihsiz else ""))

    kaydet(ARALIK_DOSYA, aralik, son_guncelleme)
    kaydet(KALAN_DOSYA, kalan, son_guncelleme)

    print("\n✅ Bitti. Orijinal dosyaya DOKUNULMADI.")
    input("ENTER ile kapat...")