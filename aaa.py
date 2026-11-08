import json
import datetime
from pathlib import Path

# ================= AYARLAR =================
KAYNAK_DOSYA = Path(r"C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json")

SINIR_TARIH = "2026-10-01"   # Bu tarih DAHİL kalır, sonrası silinir

# Silinenler buraya yedeklenir (istersen sonra geri alırsın)
YEDEK_DOSYA = KAYNAK_DOSYA.parent / "silinen_maclar_yedek.json"
# ===========================================

def tarih_parse(t):
    t = str(t).strip()[:10]
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d-%m-%Y", "%Y.%m.%d"):
        try:
            return datetime.datetime.strptime(t, fmt).date()
        except ValueError:
            continue
    return None

if __name__ == "__main__":
    sinir = tarih_parse(SINIR_TARIH)

    print(f"📂 Okunuyor: {KAYNAK_DOSYA.name} ...")
    with open(KAYNAK_DOSYA, "r", encoding="utf-8") as f:
        data = json.load(f)

    maclar = data.get("matches", [])
    print(f"📊 Toplam: {len(maclar)} maç")

    kalanlar, silinenler, tarihsiz = [], [], 0

    for mac in maclar:
        d = tarih_parse(mac.get("tarih", ""))
        if d is None:
            tarihsiz += 1
            kalanlar.append(mac)   # tarihi bozuk olanı silme, dursun
        elif d <= sinir:
            kalanlar.append(mac)
        else:
            silinenler.append(mac)

    print(f"\n✅ Kalan: {len(kalanlar)} maç" + (f" ({tarihsiz} tarihsiz dahil)" if tarihsiz else ""))
    print(f"🗑️ Silinen ({SINIR_TARIH} sonrası): {len(silinenler)} maç")

    # Önce yedeği yaz
    with open(YEDEK_DOSYA, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"matches": silinenler}, f, ensure_ascii=False, separators=(",", ":"))
    print(f"💾 Yedek: {YEDEK_DOSYA.name}")

    # Sonra ana dosyayı güncelle (temp üzerinden, yarım yazma riski yok)
    data["matches"] = kalanlar
    temp = KAYNAK_DOSYA.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    temp.replace(KAYNAK_DOSYA)

    boyut = KAYNAK_DOSYA.stat().st_size / (1024 * 1024)
    print(f"💾 Güncellendi: {KAYNAK_DOSYA.name} | {boyut:.1f} MB")
    input("\n✅ Bitti. ENTER ile kapat...")