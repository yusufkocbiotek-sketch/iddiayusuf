import json
import pandas as pd
import re
import os

# -------------------- AYARLAR --------------------
JSON_DOSYASI = "mac.json"
EXCEL_DOSYASI = "sonuc_kesin_cozum.xlsx"
# -------------------------------------------------

if not os.path.exists(JSON_DOSYASI):
    print("Hata: JSON dosyasi bulunamadi.")
    exit()

try:
    print("JSON dosyasi okunuyor, akilli ayiklama yapiliyor...")

    # Tum dosyayi tek parca olarak oku
    with open(JSON_DOSYASI, "r", encoding="utf-8", errors="ignore") as f:
        icerik = f.read()

    # >>> EN GUCLU COZUM BASLIYOR <<<
    # Regex ile dosyanin icindeki her bir { ... } yapisini yakala
    # Bu yontem ne virgul ne de satir sonu umursamaz, sadece nesneleri ceker
    nesneler = re.findall(r'\{.*?\}', icerik, re.DOTALL)
    print("Bulunan ham veri sayisi: " + str(len(nesneler)))

    gecerli_veriler = []
    sayac = 0

    # Her bir bulunan nesneyi kontrol et, sadece duzgun olanlari al
    for nesne_metin in nesneler:
        try:
            # JSON olarak yuklemeyi dene
            veri = json.loads(nesne_metin)
            gecerli_veriler.append(veri)
            sayac += 1
        except:
            # Bozuk olanlari atla
            continue

    if len(gecerli_veriler) == 0:
        print("Hata: Gecerli veri bulunamadi.")
        exit()

    print("Basariyla dogrulanan veri sayisi: " + str(sayac))

    # DataFrame'e cevir
    df = pd.DataFrame(gecerli_veriler)
    print("Veri Boyutu: " + str(df.shape[0]) + " satir, " + str(df.shape[1]) + " sutun")

    # Excel sutun siniri kontrolu (16384 sutun gecmemeli)
    if df.shape[1] > 16000:
        print("Uyari: Veri cok genis, satir ve sutunlar yer degistiriliyor...")
        df = df.transpose().reset_index()
        print("Yeni Boyut: " + str(df.shape[0]) + " satir, " + str(df.shape[1]) + " sutun")

    # Excel'e yaz
    print("Excel dosyasi olusturuluyor...")
    with pd.ExcelWriter(EXCEL_DOSYASI, engine="openpyxl") as yazici:
        df.to_excel(yazici, index=False, sheet_name="Veriler")

    print("ISLEM TAMAMLANDI!")
    print("Olusturulan dosya: " + EXCEL_DOSYASI)
    print("Bu yontemle bozuk kisimlar otomatik olarak atlanip sadece saglam veriler alindi.")

except Exception as e:
    print("SON HATA: " + str(e))