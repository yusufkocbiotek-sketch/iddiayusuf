import json
import pandas as pd
import os

JSON_DOSYASI = "public/data/mac.json"
EXCEL_DOSYASI = "iddaa_bulten.xlsx"

print(f"'{JSON_DOSYASI}' okunuyor...")

# JSON dosyasını oku
with open(JSON_DOSYASI, "r", encoding="utf-8") as f:
    data = json.load(f)

maclar = data.get("matches", [])
print(f"{len(maclar)} maç bulundu.")

# Excel'e yazılacak veriyi hazırla
excel_verisi = []

for mac in maclar:
    # Temel bilgileri al
    satir = {
        "Tarih": mac.get("tarih", ""),
        "Saat": mac.get("saat", ""),
        "Lig": mac.get("lig", ""),
        "Ev Sahibi": mac.get("ev_sahibi", ""),
        "Deplasman": mac.get("deplasman", ""),
        "Durum": mac.get("durum", ""),
        "MS Skor": f"{mac.get('skor_ev', '')}-{mac.get('skor_dep', '')}" if mac.get("durum") == "bitti" else "-",
        "İY Skor": f"{mac.get('skor_1y_ev', '')}-{mac.get('skor_1y_dep', '')}" if mac.get("durum") == "bitti" else "-",
        "Kod": mac.get("mac_kodu", "")
    }
    
    # Tüm oranları satır olarak ekle
    if "oranlar" in mac:
        for oran_key, oran_value in mac["oranlar"].items():
            # Sütun adını daha okunaklı yapalım
            sutun_adi = oran_key.replace("_", " ")
            satir[sutun_adi] = oran_value
            
    excel_verisi.append(satir)

# Pandas DataFrame oluştur
df = pd.DataFrame(excel_verisi)

# Sütunları sırala (önemliler başta)
oncelikli_sutunlar = [
    "Tarih", "Saat", "Lig", "Ev Sahibi", "Deplasman", "Durum", "MS Skor", "İY Skor", "Kod",
    "Maç Sonucu 1", "Maç Sonucu 0", "Maç Sonucu 2",
    "Alt/Üst 2.5 Alt", "Alt/Üst 2.5 Üst",
    "Karşılıklı Gol Var", "Karşılıklı Gol Yok",
    "İlk Yarı Sonucu 1", "İlk Yarı Sonucu 0", "İlk Yarı Sonucu 2"
]

# Mevcut tüm sütunları al
tum_sutunlar = list(df.columns)

# Öncelikli olanları başa al, geri kalanları alfabetik sırala
sirali_sutunlar = []
for sutun in oncelikli_sutunlar:
    if sutun in tum_sutunlar:
        sirali_sutunlar.append(sutun)
        tum_sutunlar.remove(sutun)

# Kalan oranları da ekle
sirali_sutunlar.extend(sorted(tum_sutunlar))

df = df[sirali_sutunlar]

# Excel'e yaz
print(f"'{EXCEL_DOSYASI}' oluşturuluyor...")
df.to_excel(EXCEL_DOSYASI, index=False, engine='openpyxl')

print(f"\n✅ Başarılı! '{os.path.abspath(EXCEL_DOSYASI)}' dosyası oluşturuldu.")