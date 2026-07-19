import json

dosya = r"C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\mac.json"

# ❌ Silinecek kategoriler (başlangıç eşleşmesi)
SILINECEK = [
    "Oyuncu Gol Atar",
    "Oyuncu",
    "100.00",
    "Takım",
    "Oyuncu İlk Golü Atar",
    "Oyuncu Son Golü Atar",
    "Oyuncu 2+ Gol Atar",
    "Oyuncu 3+ Gol Atar",
    "Oyuncu Asist Yapar",
    "Oyuncu Ceza Sahası",
    "Oyuncu Gol Atar Ve Takımı",
    "Oyuncu Frikikten",
    "Oyuncu Hat-trick",
    "Oyuncu Her Iki Yarı",
    "Oyuncu Gol Atar veya Asist",
    "Oyuncu Kaleyi Bulan",
    "Oyuncu Kart Görür",
    "Oyuncu Şut",
    "Oyuncu İsabetli Şut",
    "Karşılaşma Özel Bahisleri",
    "Kaleci Kurtarışı",
    "Takım Şut",
    "Takım İsabetli Şut",
    "Takım Faul",
    "Takım Ofsayt",
    "Takım Korner",
    "Takım Kart",
    "Oyuncu Gol Yemeden Maç",
    "Oyuncu Penaltı",
    "Oyuncu Kendi Kalesine",
    "Oyuncu Maçın İlk Dakikasında",
    "Oyuncu Maçın Son Dakikasında",
]

# Yedek al
import shutil
shutil.copy(dosya, dosya + ".yedek")
print("✅ Yedek alindi")

# Oku
with open(dosya, "r", encoding="utf-8") as f:
    data = json.load(f)

# Her maçın oranlarını temizle
silinen_toplam = 0
for mac in data.get("matches", []):
    oranlar = mac.get("oranlar", {})
    yeni_oranlar = {}
    silinen = 0
    
    for key, value in oranlar.items():
        sil = False
        for kategori in SILINECEK:
            if key.lower().startswith(kategori.lower()):
                sil = True
                break
        if not sil:
            yeni_oranlar[key] = value
        else:
            silinen += 1
    
    if silinen > 0:
        mac["oranlar"] = yeni_oranlar
        silinen_toplam += silinen

print(f"🗑️ {silinen_toplam} gereksiz oran silindi")

# Kaydet
with open(dosya, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"💾 Kaydedildi: {len(data['matches'])} maç")