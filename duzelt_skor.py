import json
import datetime

DOSYA = "public/data/mac.json"

with open(DOSYA, "r", encoding="utf-8") as f:
    data = json.load(f)

duzeldi = 0

for m in data.get("matches", []):
    ev = m.get("ev_sahibi", "").lower()
    dep = m.get("deplasman", "").lower()
    tarih = m.get("tarih", "")

    if tarih == "2026-05-01" and "rizespor" in ev and "konyaspor" in dep:
        m["durum"] = "bitti"
        m["skor_ev"] = 3
        m["skor_dep"] = 2
        m["skor_1y_ev"] = 1
        m["skor_1y_dep"] = 1
        m["skor_duzeltme"] = "manuel"
        m["skor_duzeltme_zamani"] = datetime.datetime.now().isoformat()
        duzeldi += 1
        print(f"✅ Düzeltildi: {m['ev_sahibi']} 3-2 {m['deplasman']} | İY 1-1")

with open(DOSYA, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nToplam düzeltilen maç: {duzeldi}")