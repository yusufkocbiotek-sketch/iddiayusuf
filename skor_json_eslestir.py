import json
import os
import datetime
import re
import difflib

MAC_JSON = "public/data/mac.json"
GECMIS_JSON = "public/data/gecmis_maclar.json"

def json_oku(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def json_kaydet(path, data):
    data["updated"] = datetime.datetime.now().isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def temizle_takim_adi(ad):
    if not ad:
        return ""

    ad = ad.lower().strip()

    tr_map = {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u"
    }

    for k, v in tr_map.items():
        ad = ad.replace(k, v)

    silinecekler = [
        " fc", "fc ",
        " fk", "fk ",
        " sk", "sk ",
        " sc", "sc ",
        " ac", "ac ",
        " as", "as ",
        " cf", "cf ",
        " cd", "cd ",
        " afc", "afc ",
        " utd",
        " united",
        " city",
        " town",
        " club",
        " deportivo",
        " atletico",
        " athletic",
        " real ",
        "spor",
        " 1908",
        " 1911",
        " 1912",
        " 1919",
        " 1929",
        " 2000"
    ]

    for s in silinecekler:
        ad = ad.replace(s, " ")

    ad = re.sub(r"[^a-z0-9]", "", ad)

    manuel = {
        "indmendoza": "independienterivadavia",
        "independientemendoza": "independienterivadavia",
        "deplagua": "deportivolaguaira",
        "deportivolagua": "deportivolaguaira",
        "catigre": "atleticotigre",
        "tigre": "atleticotigre",
        "penaroluru": "penarol",
        "capenarol": "penarol",
        "americadecali": "americadecali",
        "velezsarsfield": "velezsarsfield",
        "gimnasiaytirodesalta": "gimnasiaytirodesalta",
        "ofkbaniklehotapodvtacnikom": "baniklehotapodvtacnikom",
        "baniklehotapodvtacnikom": "baniklehotapodvtacnikom",
        "shanghaishenhua": "shanghaishenhua",
        "chengdurongcheng": "chengdurongcheng",
        "vanersborgsfk": "vanersborgs",
        "vanersborgsif": "vanersborgs",
        "kuchingfa": "kuching",
        "terengganu": "terengganu",
        "fcsudtirol": "sudtirol",
        "sudtirol": "sudtirol",
        "sscbari": "bari",
        "bari": "bari",
        "lask": "lasklinz",
        "paideflora": "paidelinnamee",
        "tartujktam": "tammekatartu",
        "throtturv": "throttur",
        "haukarhafnarfjordur": "haukar",
        "acpisa": "pisa",
        "pisa": "pisa",
        "lecce": "lecce",
        "girona": "girona",
        "mallorca": "mallorca",
        "leeds": "leeds",
        "leedsunited": "leeds",
        "burnley": "burnley",
        "gaziantepfk": "gaziantep",
        "gaziantep": "gaziantep",
        "besiktas": "besiktas",
        "rizes": "rizespor",
        "rizespor": "rizespor",
        "caykurrizespor": "rizespor",
        "konyaspor": "konyaspor"
    }

    if ad in manuel:
        ad = manuel[ad]

    return ad


def benzerlik(a, b):
    a = temizle_takim_adi(a)
    b = temizle_takim_adi(b)

    if not a or not b:
        return 0

    if a == b:
        return 1.0

    if len(a) >= 4 and len(b) >= 4:
        if a in b or b in a:
            return 0.95

    return difflib.SequenceMatcher(None, a, b).ratio()

def takimlar_eslesiyor_mu(mac_ev, mac_dep, gecmis_ev, gecmis_dep):
    ev_oran = benzerlik(mac_ev, gecmis_ev)
    dep_oran = benzerlik(mac_dep, gecmis_dep)

    return ev_oran >= 0.70 and dep_oran >= 0.70

def en_iyi_eslesme_bul(mac, gecmis_maclar):
    adaylar = []

    for g in gecmis_maclar:
        if g.get("durum") != "bitti":
            continue

        # Tarih aynı olmalı
        if g.get("tarih") != mac.get("tarih"):
            continue

        ev_oran = benzerlik(mac["ev_sahibi"], g["ev_sahibi"])
        dep_oran = benzerlik(mac["deplasman"], g["deplasman"])

        ort = (ev_oran + dep_oran) / 2

        if ev_oran >= 0.70 and dep_oran >= 0.70:
            adaylar.append((ort, g, ev_oran, dep_oran))

    if not adaylar:
        return None

    adaylar.sort(key=lambda x: x[0], reverse=True)
    return adaylar[0]

def main():
    print("============================================================")
    print("⚽ JSON Skor Eşleştirici")
    print("============================================================")

    if not os.path.exists(MAC_JSON):
        print(f"❌ {MAC_JSON} bulunamadı")
        return

    if not os.path.exists(GECMIS_JSON):
        print(f"❌ {GECMIS_JSON} bulunamadı")
        print("Önce şunu çalıştırın:")
        print("python scraper_gecmis.py")
        return

    mac_data = json_oku(MAC_JSON)
    gecmis_data = json_oku(GECMIS_JSON)

    maclar = mac_data.get("matches", [])
    gecmis_maclar = gecmis_data.get("matches", [])

    print(f"📊 mac.json maç sayısı: {len(maclar)}")
    print(f"📊 gecmis_maclar.json maç sayısı: {len(gecmis_maclar)}")

    baslamadi = [m for m in maclar if m.get("durum") == "baslamadi"]
    bitti = [m for m in maclar if m.get("durum") == "bitti"]

    print(f"⏳ Başlamadı: {len(baslamadi)}")
    print(f"✅ Bitti: {len(bitti)}")

    guncellenen = 0
    eslesmeyen_gecmis = []
    eslesmeyen_gelecek = []

    bugun = datetime.date.today().isoformat()

    for mac in maclar:
        if mac.get("durum") != "baslamadi":
            continue

        sonuc = en_iyi_eslesme_bul(mac, gecmis_maclar)

        if sonuc:
            ort, g, ev_oran, dep_oran = sonuc

            mac["durum"] = "bitti"
            mac["skor_ev"] = g.get("skor_ev", 0)
            mac["skor_dep"] = g.get("skor_dep", 0)
            mac["skor_1y_ev"] = g.get("skor_1y_ev", 0)
            mac["skor_1y_dep"] = g.get("skor_1y_dep", 0)
            mac["skor_kaynak"] = "gecmis_maclar.json"
            mac["skor_eslesme_orani"] = round(ort, 3)

            guncellenen += 1

            print(
                f"✅ {mac['ev_sahibi']} {mac['skor_ev']}-{mac['skor_dep']} {mac['deplasman']} "
                f"<=> {g['ev_sahibi']} - {g['deplasman']} "
                f"(eşleşme: %{round(ort * 100, 1)})"
            )

        else:
            if mac.get("tarih", "") < bugun:
                eslesmeyen_gecmis.append(mac)
            else:
                eslesmeyen_gelecek.append(mac)

    print("\n============================================================")
    print("📊 SONUÇ")
    print(f"✅ Güncellenen maç: {guncellenen}")
    print(f"❌ Geçmiş tarihli ama eşleşmeyen: {len(eslesmeyen_gecmis)}")
    print(f"⏳ Gelecek/bugün henüz bitmemiş olabilir: {len(eslesmeyen_gelecek)}")
    print("============================================================")

    if eslesmeyen_gecmis:
        print("\n⚠️ Geçmiş tarihli olup eşleşmeyen ilk 30 maç:")
        for m in eslesmeyen_gecmis[:30]:
            print(f"- {m['tarih']} {m.get('saat','')} | {m['ev_sahibi']} vs {m['deplasman']}")

    if guncellenen > 0:
        json_kaydet(MAC_JSON, mac_data)
        print("\n💾 mac.json güncellendi.")
        print("\nGitHub'a yüklemek için:")
        print("git add -A")
        print('git commit -m "Skorlar json ile eslestirildi"')
        print("git push")
    else:
        print("\n⚠️ Güncellenecek yeni eşleşme bulunamadı.")

if __name__ == "__main__":
    main()