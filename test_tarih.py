import json

data = json.load(open("public/data/mac.json", encoding="utf-8"))
gecmis = json.load(open("public/data/gecmis_maclar.json", encoding="utf-8"))

dun = "2026-05-01"
biten_dun = [m for m in data["matches"] if m["durum"] == "bitti" and m["tarih"] == dun]

print(f"📊 dün biten mac.json'da: {len(biten_dun)}\n")
for m in biten_dun:
    print(f"  {m['ev_sahibi']} vs {m['deplasman']}")

print(f"\n📊 dün biten gecmis_maclar.json'da:")
biten_g = [m for m in gecmis["matches"] if m["tarih"] == dun]
for m in biten_g[:10]:
    print(f"  {m['ev_sahibi']} vs {m['deplasman']} {m['skor_ev']}-{m['skor_dep']}")