import json, sys, os

path = "public/data/mac.json"

try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    matches = data.get("matches", [])
    print("✅ Kaydedilen mac.json kayıt sayısı:", len(matches))
    
    if matches:
        print("\n🔎 İlk 5 kayıt:")
        for i, m in enumerate(matches[:5]):
            print(f"  {i+1}. {m.get('ev_sahibi')} - {m.get('deplasman')} | {m.get('tarih')} {m.get('saat')} | durum={m.get('durum')}")
        print("\n🔎 Son 5 kayıt:")
        for i, m in enumerate(matches[-5:]):
            idx = len(matches)-2+i
            print(f"  {idx}. {m.get('ev_sahibi')} - {m.get('deplasman')} | {m.get('tarih')} {m.get('saat')} | durum={m.get('durum')}")
        
        # Bekleyen maçları da listele
        pending = [m for m in matches if m.get("durum") in ["baslamadi", "devam", None]]
        print(f"\n⏳ Bekleyen (pending) maç sayısı:", len(pending))
        if pending:
            print("🔎 İlk 5 bekleyen maç:")
            for i, m in enumerate(pending[:5]):
                print(f"  {i+1}. {m.get('ev_sahibi')} - {m.get('deplasman')} | {m.get('tarih')} {m.get('saat')}")
        else:
            print("⚠️ Bekleyen maç yok (tüm maçlar tamamlanmış gibi görünüyor).")
    
    else:
        print("⚠️ 'matches' listesi BOŞ! JSON yapısı farklı olabilir.")
        
except FileNotFoundError:
    print(f"❌ Dosya bulunamadı: {path}")
    print("   → Önce 'python scraper_gecmis.py' ile veriyi çektiğinden emin ol.")
except json.JSONDecodeError as e:
    print("❌ JSON geçersiz / okunamadı:", e)
except Exception as e:
    print("❌ Beklenmeyen hata:", e)
