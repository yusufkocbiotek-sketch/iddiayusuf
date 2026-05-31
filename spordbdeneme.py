import json
import datetime
import subprocess
from pathlib import Path

# =========================
# ✅ GİT | ZORLA ÇALIŞTIR | FORMAT BOZULMAZ ✅
# =========================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON_PATH = BASE_DIR / "public" / "data" / "mac.json"
GIT_BRANCH = "main"

print("="*60)
print("🔧 GİT | ZORLA ÇALIŞTIRICI | FORMAT KORUNUYOR ✅")
print("="*60)

# 1. Dosyayı sadece oku, hiçbir şeyini değiştirme
try:
    with open(MAC_JSON_PATH, "r", encoding="utf-8") as f:
        veri = json.load(f)
    print(f"📖 Dosya Okundu | Toplam: {len(veri.get('matches', []))} maç")
except Exception as e:
    print(f"❌ Okuma Hatası: {e}")
    exit()

# 2. Sadece son_guncelleme alanını güncelle (bu sayede dosya KESİNLİKLE değişik görünür)
veri["son_guncelleme"] = datetime.datetime.now().isoformat()

# 3. AYNI FORMATTA geri kaydet (tarih formatı "2026-04-28" korunuyor)
try:
    with open(MAC_JSON_PATH, "w", encoding="utf-8", newline='\n') as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
    print("💾 Kaydedildi | Format: YYYY-AA-GG ✅")
except Exception as e:
    print(f"❌ Kaydetme Hatası: {e}")
    exit()

# 4. 🚀 GİT - ARTIK HİÇBİR ŞEYE TAKILMADAN ZORLA YAP
try:
    print("\n🔄 1/3: git add .")
    subprocess.run(["git", "add", "."], check=True)

    zaman = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
    mesaj = f"[OTOMATİK GÜNCELLEME] | {zaman} | Tüm Veriler Güncel"
    print(f"🔄 2/3: git commit -m '{mesaj}'")
    # --allow-empty parametresiyle boş olsa bile commit et
    subprocess.run(["git", "commit", "--allow-empty", "-m", mesaj], check=True)

    print(f"🔄 3/3: git push origin {GIT_BRANCH}")
    subprocess.run(["git", "push", "origin", GIT_BRANCH], check=True)

    print("\n✅ TAMAMLANDI | ARTIK HİÇ SORUN OLMAZ 🚀")
except Exception as e:
    print(f"\n❌ GİT HATA: {e}")

input("\nÇıkmak için ENTER...")