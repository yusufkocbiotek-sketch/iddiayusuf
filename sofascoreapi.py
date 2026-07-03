import requests
import datetime
import time
import json


# =========================
# AYARLAR
# =========================
BASLANGIC_TARIHI = "01.07.2026"
BITIS_TARIHI     = "02.07.2026"

API_URL = "https://api.sofascore.com/api/v1/sport/football/scheduled-events/"


# =========================
# TARİH
# =========================
def parse_date(s):
    return datetime.datetime.strptime(s, "%d.%m.%Y").date()

def gun_listesi_olustur(bas, bit):
    gunler = []
    aktif = bas
    while aktif <= bit:
        gunler.append(aktif)
        aktif += datetime.timedelta(days=1)
    return gunler


# =========================
# MAÇ ÇEK
# =========================
def maclari_cek(tarih):

    tarih_str = tarih.strftime("%Y-%m-%d")
    url = API_URL + tarih_str

    print(f"\n🌐 API çağrılıyor: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print("❌ API hata:", r.status_code)
        return []

    data = r.json()

    mac_listesi = []

    for event in data.get("events", []):

        try:
            ev = event["homeTeam"]["name"]
            dep = event["awayTeam"]["name"]

            lig = event["tournament"]["uniqueTournament"]["name"]

            durum_kod = event.get("status", {}).get("type", "")

            # Maç sonucu
            skor_ev = event.get("homeScore", {}).get("current", 0)
            skor_dep = event.get("awayScore", {}).get("current", 0)

            # İlk yarı
            iy_ev = event.get("homeScore", {}).get("period1", 0)
            iy_dep = event.get("awayScore", {}).get("period1", 0)

            durum = "baslamadi"

            if durum_kod == "finished":
                durum = "bitti"
            elif durum_kod == "inprogress":
                durum = "canli"

            mac_listesi.append({
                "tarih": tarih_str,
                "lig": lig,
                "ev_sahibi": ev,
                "deplasman": dep,
                "skor_ev": skor_ev,
                "skor_dep": skor_dep,
                "skor_1y_ev": iy_ev,
                "skor_1y_dep": iy_dep,
                "durum": durum
            })

            print(f"✅ {lig} | {ev} - {dep} | {skor_ev}-{skor_dep} | İY {iy_ev}-{iy_dep}")

        except:
            continue

    return mac_listesi


# =========================
# ANA
# =========================
if __name__ == "__main__":

    print("="*60)
    print("🚀 SOFASCORE API SKOR ÇEKİCİ")
    print("="*60)

    bas = parse_date(BASLANGIC_TARIHI)
    bit = parse_date(BITIS_TARIHI)

    gunler = gun_listesi_olustur(bas, bit)

    tum_maclar = []

    for gun in gunler:
        print("\n" + "="*50)
        print("📆", gun)
        print("="*50)

        maclar = maclari_cek(gun)
        tum_maclar.extend(maclar)

        time.sleep(1)  # rate limit güvenlik

    print("\n📊 TOPLAM MAÇ:", len(tum_maclar))

    # JSON kaydetmek istersen:
    with open("maclar.json", "w", encoding="utf-8") as f:
        json.dump(tum_maclar, f, ensure_ascii=False, indent=2)

    print("✅ maclar.json kaydedildi")