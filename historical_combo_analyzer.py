import json
import os
import shutil
import datetime
from pathlib import Path
from collections import defaultdict

# ============================
# YOLLAR
# ============================
BASE_DIR = Path(__file__).resolve().parent
MAC_JSON = BASE_DIR / "public" / "data" / "mac.json"
GECMIS_JSON = BASE_DIR / "public" / "data" / "gecmis_maclar.json"

# ============================
# YARDIMCI FONKSİYONLAR
# ============================
def get_oran_bucket(oran_str):
    """Oranı 0.10'luk aralıklara böler (Örn: 1.55 -> '1.50-1.59')"""
    try:
        oran = float(oran_str)
        if oran < 1.01 or oran > 20.0: return None
        lower = round(int(oran * 10) / 10, 2)
        upper = round(lower + 0.09, 2)
        return f"{lower:.2f}-{upper:.2f}"
    except:
        return None

def evaluate_actual_result(mac):
    """Geçmiş maçın gerçek skoruna göre 6'lı kombinasyon sonuçlarını döner"""
    try:
        ev = int(mac.get("skor_ev", 0))
        dep = int(mac.get("skor_dep", 0))
    except:
        return None

    total_goals = ev + dep
    
    # İstenen 6 Kombinasyonun Gerçekleşme Durumları
    return {
        "MS1_MS0": ev >= dep,           # 1X (Çifte Şans)
        "MS1_MS2": ev != dep,           # 12 (Çifte Şans)
        "MS1_ALT25": ev > dep and total_goals <= 2,  # MS1 ve 2.5 Alt
        "MS1_UST25": ev > dep and total_goals >= 3,  # MS1 ve 2.5 Üst
        "MS1_KGVAR": ev > dep and ev > 0 and dep > 0,# MS1 ve KG Var
        "MS1_KGYOK": ev > dep and dep == 0           # MS1 ve KG Yok
    }

# ============================
# ANA ANALİZ MOTORU
# ============================
def build_historical_stats():
    print("📚 Geçmiş maç verileri okunuyor (Güvenli Mod)...")
    
    if not GECMIS_JSON.exists():
        print("❌ gecmis_maclar.json bulunamadı!")
        return {}

    with open(GECMIS_JSON, "r", encoding="utf-8") as f:
        gecmis_data = json.load(f)
    
    gecmis_maclar = gecmis_data.get("matches", [])
    
    # İstatistik havuzu
    stats = defaultdict(lambda: {"total": 0, "hits": defaultdict(int)})
    
    analyzed_count = 0
    for mac in gecmis_maclar:
        if mac.get("durum") != "bitti": continue
        
        actual = evaluate_actual_result(mac)
        if not actual: continue
        
        oranlar = mac.get("oranlar", {})
        ms1_oran = get_oran_bucket(oranlar.get("Maç Sonucu_1"))
        
        if ms1_oran:
            key = f"MS1_{ms1_oran}"
            stats[key]["total"] += 1
            
            # 6 kombinasyonun her birini kontrol et
            for combo_key, is_hit in actual.items():
                if is_hit:
                    stats[key]["hits"][combo_key] += 1
                    
            analyzed_count += 1

    print(f"✅ {analyzed_count} geçmiş maç analiz edildi.")
    return stats

def apply_stats_to_today(stats):
    print("🎯 Bugünün bültenine detaylı kombinasyonlar ekleniyor...")
    
    if not MAC_JSON.exists():
        print("❌ mac.json bulunamadı!")
        return

    # GÜVENLİK: İşlem öncesi yedek al
    backup_path = MAC_JSON.with_suffix(".json.bak")
    shutil.copy2(MAC_JSON, backup_path)
    print(f"💾 Güvenlik yedeği alındı: {backup_path.name}")

    with open(MAC_JSON, "r", encoding="utf-8") as f:
        mac_data = json.load(f)
    
    maclar = mac_data.get("matches", [])
    updated_count = 0
    
    # İstenen 6 Kombinasyon Listesi
    COMBO_KEYS = ["MS1_MS0", "MS1_MS2", "MS1_ALT25", "MS1_UST25", "MS1_KGVAR", "MS1_KGYOK"]
    COMBO_NAMES = {
        "MS1_MS0": "MS1-MS0 (1X)",
        "MS1_MS2": "MS1-MS2 (12)",
        "MS1_ALT25": "MS1 & 2.5 ALT",
        "MS1_UST25": "MS1 & 2.5 ÜST",
        "MS1_KGVAR": "MS1 & KG VAR",
        "MS1_KGYOK": "MS1 & KG YOK"
    }
    
    for mac in maclar:
        oranlar = mac.get("oranlar", {})
        ms1_oran_str = oranlar.get("Maç Sonucu_1")
        ms1_bucket = get_oran_bucket(ms1_oran_str)
        
        detayli_kombinasyonlar = {}
        
        if ms1_bucket:
            key = f"MS1_{ms1_bucket}"
            total_matches = stats[key]["total"] if key in stats else 0
            
            for combo_key in COMBO_KEYS:
                if total_matches >= 5: # En az 5 maçlık veri varsa hesapla
                    hits = stats[key]["hits"][combo_key]
                    yuzde = round((hits / total_matches) * 100)
                    
                    # Renk belirleme
                    if yuzde >= 70: renk = "yesil"
                    elif yuzde >= 50: renk = "sari"
                    else: renk = "kirmizi"
                    
                    detayli_kombinasyonlar[combo_key] = {
                        "ad": COMBO_NAMES[combo_key],
                        "tutan": hits,
                        "toplam": total_matches,
                        "yuzde": yuzde,
                        "renk": renk
                    }
                else:
                    # Veri yoksa veya yetersizse "-" göster
                    detayli_kombinasyonlar[combo_key] = {
                        "ad": COMBO_NAMES[combo_key],
                        "yuzde": "-",
                        "renk": "gri"
                    }
        
        # MEVCUT VERİYE DOKUNMADAN SADECE YENİ ANAHTARI EKLE
        if detayli_kombinasyonlar:
            mac["detayli_kombinasyonlar"] = detayli_kombinasyonlar
            updated_count += 1

    # GÜVENLİ KAYDETME (Atomic Write)
    tmp_path = MAC_JSON.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(mac_data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, MAC_JSON)
        
    print(f"✅ {updated_count} maça 'detayli_kombinasyonlar' eklendi.")

def main():
    print("=" * 60)
    print("🧠 DETAYLI KOMBİNASYON ANALİZİ (GÜVENLİ MOD)")
    print("=" * 60)
    
    stats = build_historical_stats()
    if stats:
        apply_stats_to_today(stats)
        
    print("\n🎉 İşlem Tamamlandı! (Geri almak isterseniz .bak dosyasını kullanın)")

if __name__ == "__main__":
    main()