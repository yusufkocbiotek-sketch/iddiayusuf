import json
import os
import traceback

# Dosya yolları
KAYNAK_DOSYA = r"C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\mac.json"
HEDEF_DOSYA = r"C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\mac_filtreli.json"

# Alınacak oran anahtarları (HEPSİ olmak zorunda, yoksa maç atlanır)
ORAN_ANAHTARLARI = [
    "Maç Sonucu_1",
    "Maç Sonucu_0",
    "Maç Sonucu_2",
    "Alt/Üst 1.5_Alt",
    "Alt/Üst 1.5_Üst",
    "Alt/Üst 2.5_Alt",
    "Alt/Üst 2.5_Üst",
    "Alt/Üst 3.5_Alt",
    "Alt/Üst 3.5_Üst",
    "Ev Sahibi Alt/Üst 1.5_Alt",
    "Ev Sahibi Alt/Üst 1.5_Üst",
    "Deplasman Alt/Üst 1.5_Alt",
    "Deplasman Alt/Üst 1.5_Üst",
    "Her İki Yarıda da Alt 1.5_Evet",
    "Her İki Yarıda da Alt 1.5_Hayır",
    "Her İki Yarıda da Üst 1.5_Evet",
    "Her İki Yarıda da Üst 1.5_Hayır",
    "Karşılıklı Gol_Var",
    "Karşılıklı Gol_Yok",
    "Toplam Gol_0-1 gol",
    "Toplam Gol_2-3 gol",
    "Toplam Gol_4-5 gol",
    "Toplam Gol_6+ gol",
    "1. Yarı ve 2. Yarıda Karşılıklı Gol Olur_Hayır / Hayır",
    "1. Yarı ve 2. Yarıda Karşılıklı Gol Olur_Evet / Hayır",
    "1. Yarı ve 2. Yarıda Karşılıklı Gol Olur_Evet / Evet",
    "1. Yarı ve 2. Yarıda Karşılıklı Gol Olur_Hayır / Evet",
]

# Skor alanları da eksiksiz olmalı
SKOR_ALANLARI = ["skor_ev", "skor_dep", "skor_1y_ev", "skor_1y_dep"]


def mac_tam_mi(mac: dict) -> bool:
    """Maçta tüm oranlar ve skorlar eksiksiz mi kontrol eder."""
    oranlar = mac.get("oranlar", {})

    # Tüm oran anahtarları var mı ve değerleri None değil mi?
    for anahtar in ORAN_ANAHTARLARI:
        if anahtar not in oranlar or oranlar[anahtar] is None:
            return False

    # Skorlar dolu mu?
    for alan in SKOR_ALANLARI:
        if mac.get(alan) is None:
            return False

    return True


def mac_filtrele(mac: dict) -> dict:
    """Tek bir maç kaydından istenen alanları çıkarır."""
    oranlar = mac["oranlar"]

    return {
        "ev_sahibi": mac.get("ev_sahibi"),
        "deplasman": mac.get("deplasman"),
        "skor_ev": mac["skor_ev"],
        "skor_dep": mac["skor_dep"],
        "skor_1y_ev": mac["skor_1y_ev"],
        "skor_1y_dep": mac["skor_1y_dep"],
        "oranlar": {anahtar: oranlar[anahtar] for anahtar in ORAN_ANAHTARLARI},
    }


def main():
    if not os.path.exists(KAYNAK_DOSYA):
        print(f"HATA: Dosya bulunamadı -> {KAYNAK_DOSYA}")
        return

    with open(KAYNAK_DOSYA, "r", encoding="utf-8") as f:
        veri = json.load(f)

    if isinstance(veri, dict):
        for deger in veri.values():
            if isinstance(deger, list):
                veri = deger
                break
        else:
            veri = [veri]

    toplam = 0
    atlanan = 0
    sonuc = []

    for mac in veri:
        if not isinstance(mac, dict):
            continue
        toplam += 1
        if mac_tam_mi(mac):
            sonuc.append(mac_filtrele(mac))
        else:
            atlanan += 1

    with open(HEDEF_DOSYA, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)

    print(f"Toplam maç       : {toplam}")
    print(f"Eksik (atlanan)  : {atlanan}")
    print(f"Kaydedilen       : {len(sonuc)}")
    print(f"Dosya: {HEDEF_DOSYA}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("BİR HATA OLUŞTU:")
        traceback.print_exc()

    input("\nÇıkmak için Enter'a bas...")