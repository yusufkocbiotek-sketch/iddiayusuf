import json

# İki JSON'u oku
data = json.load(open("public/data/mac.json", encoding="utf-8"))
gecmis = json.load(open("public/data/gecmis_maclar.json", encoding="utf-8"))

# Tüm takım adlarını topla
takimlar = {}

def ekle(ad, kaynak):
    ad = ad.strip()
    if not ad:
        return
    if ad not in takimlar:
        takimlar[ad] = set()
    takimlar[ad].add(kaynak)

for m in data["matches"]:
    ekle(m["ev_sahibi"], "mac.json")
    ekle(m["deplasman"], "mac.json")

for m in gecmis["matches"]:
    ekle(m["ev_sahibi"], "gecmis.json")
    ekle(m["deplasman"], "gecmis.json")

# Eşleşmeyenleri göster
print(f"📊 Toplam {len(takimlar)} farklı takım adı bulundu\n")

eslesmeyen = []
for takim, kaynaklar in takimlar.items():
    if len(kaynaklar) > 1:
        eslesmeyen.append((takim, kaynaklar))

print(f"❌ {len(eslesmeyen)} takım farklı yazımla bulunuyor:\n")
for takim, k in eslesmeyen[:30]:
    print(f"  '{takim}' → {', '.join(k)}")

# Normalizasyon kuralları
def normalize(ad):
    ad = ad.lower().strip()
    # Türkçe karakterler
    tr = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    ad = ad.translate(tr)
    # Nokta, virgül, slash kaldır
    ad = ad.replace(".", "").replace(",", "").replace("/", "").replace("-", " ")
    # Fazla boşluk
    ad = " ".join(ad.split())
    return ad

print("\n🔍 Normalizasyon testi (ilk 20 farklı yazım):\n")
ornekler = sorted(eslesmeyen, key=lambda x: len(x[0]))[:20]
for takim, _ in ornekler:
    print(f"  '{takim}' → '{normalize(takim)}'")

# İsim eşleşme tablosu oluştur
eslesme = {}
for takim in takimlar.keys():
    n = normalize(takim)
    if n not in eslesme:
        eslesme[n] = []
    eslesme[n].append(takim)

print(f"\n✅ {len(eslesme)} benzersiz (normalleşmiş) takım")
print(f"❌ {len(eslesmeyen)} çakışma var")