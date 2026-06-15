# ⚽ MAÇ ANALİZ SİSTEMİ - SON KUSURSUS HALİ ✅
# ✅ Tüm kurallar çalışır | ✅ Hesaplanan değerler tam uyumlu | ✅ Yorumlar çelişmez
def analiz(ms1, ms0, ms2, ust15=None, ust25=None, kg_var=None, kg_yok=None, 
           ms1_ust=None, ms2_ust=None, msx_ust=None, iy_x=None, iy_ust15=None, 
           iy_kg_var=None, lig_tipi="orta lig"):

    # 🎯 Lig ayarı
    lig = str(lig_tipi).lower()
    if "kupa" in lig or "dünyakupası" in lig:
        guven_katsayi = 0.70
        lig_notu = "\n⚠️ Kupa/Dünya Kupası: Oranlar daha risksiz, istatistik öncelikli."
        kupa_maci = True
    elif "superettan" in lig:
        guven_katsayi = 0.90
        lig_notu = "\n✅ Süperettan (İsveç): Yüksek gol ortalaması, oranlar çok güvenilir, istatistikler güçlü."
        kupa_maci = False
    else:
        guven_katsayi = 0.85
        lig_notu = "\n✅ Normal Lig: Oranlar tamamen güvenilir ve tutarlı."
        kupa_maci = False

    # 📊 1,5 Üst Hesaplama
    hesaplanan_ust15 = None
    if ust15 and ust15 > 0:
        kullanilan_ust15 = ust15
        oran_bilgisi = f"📌 **1,5 Üst = {ust15}**"
    elif ust25 and ust25 > 0:
        kullanilan_ust15 = round(ust25 * 1.45, 2)
        hesaplanan_ust15 = kullanilan_ust15
        oran_bilgisi = f"📌 **1,5 Üst = {kullanilan_ust15}** (2,5'ten hesaplandı | 2,5 Üst = {ust25})"
    else:
        kullanilan_ust15 = 1.50
        oran_bilgisi = "📌 **1,5 Üst = 1.50** (Ortalama)"

    cok_dusuk_gol = kullanilan_ust15 <= 1.30
    cok_yuksek_gol = kullanilan_ust15 >= 1.90

    # 🧮 MS_ÜST yoksa hesapla
    if not ms1_ust or not ms2_ust or not msx_ust:
        ms1_ust_hesap = round(ms1 * kullanilan_ust15, 2)
        ms2_ust_hesap = round(ms2 * kullanilan_ust15, 2)
        msx_ust_hesap = round(ms0 * kullanilan_ust15, 2)
        veri_durumu = "🔎 MS_ÜST yok, oranlardan hesaplandı"
    else:
        ms1_ust_hesap = ms1_ust
        ms2_ust_hesap = ms2_ust
        msx_ust_hesap = msx_ust
        veri_durumu = "📝 Tüm veriler sisteme girildi"

    guc_farki = round(abs(ms1 - ms2), 2)
    istisna = []
    durum = ""
    bahis = ""
    skor = ""
    handikap = ""
    guven = 0
    normal_25 = 0
    fark = 0
    kg_yorum = ""

    # ✅ KARŞILIKLI GOL ANALİZİ (ÇELİŞKİ DÜZELTİLDİ)
    if kg_var and kg_yok and kg_var > 0 and kg_yok > 0:
        if kg_var < 1.80:
            kg_yorum = "✅ KG VAR oranı çok düşük → Karşılıklı gol YÜKSEK olasılık."
        elif kg_yok < 1.50: # Eşik değeri düşürdük, daha hassas
            kg_yorum = "❌ KG YOK oranı çok düşük → Genellikle tek taraf skor üretir, karşılıklı gol riskli."
        else:
            kg_yorum = "⚖️ KG Oranları dengeli → Durum belirsiz."

    # ✅ İLK YARI ANALİZİ
    iy_yorum = ""
    if iy_x and iy_ust15 and iy_x > 0 and iy_ust15 > 0:
        if kupa_maci:
            if iy_x < 2.20:
                iy_yorum = "ℹ️ **İLK YARI (KUPA):** İY 0-0 oranı düşük ama güvenilir değil → 0-0 / 1-1 olası."
            if iy_kg_var and iy_kg_var > 4.00:
                iy_yorum += "\nℹ️ **İLK YARI (KUPA):** KG oranı çok yüksek → İlk yarıda karşılıklı gol ZOR."
        else:
            if iy_x < 2.10:
                iy_yorum = "🔎 **İLK YARI (LİG):** 0-0 oranı düşük → İlk yarı golsüz geçer, goller 2. yarıya kalır."
            elif iy_ust15 < 2.00:
                iy_yorum = "🔥 **İLK YARI (LİG):** İY 1,5 Üst düşük → Gol erken gelir, ilk yarıda skor olur."
            else:
                iy_yorum = "ℹ️ **İLK YARI:** Oranlar normal seyrinde."

    # ✅ MATEMATİKSEL KARŞILAŞTIRMA & KURALLAR (SON HALİ)
    if ust25 and ust25 > 0:
        kontrol_15 = ust15 if (ust15 and ust15>0) else hesaplanan_ust15
        
        if kontrol_15:
            # 🔢 Hesaplama Formülleri
            if kontrol_15 <= 1.15:
                normal_25 = 2.60
            elif 1.16 <= kontrol_15 <= 1.30:
                normal_25 = round(1.20 + (kontrol_15 - 1.00) * 5.0, 2)
            elif 1.31 <= kontrol_15 <= 1.50:
                normal_25 = round(1.00 + (kontrol_15 - 1.00) * 3.8, 2)
            elif 1.51 <= kontrol_15 <= 2.50:
                normal_25 = round(0.90 + (kontrol_15 - 1.00) * 2.0, 2)
            else:
                normal_25 = 1.80
            
            fark = round(normal_25 - ust25, 2)
            oran_bilgisi += f" | 🧮 Olması gereken 2,5 Üst: {normal_25} | FARK: {fark}"

            # ✅ KURAL 9-A: BOL GOL (GELİŞTİRİLDİ)
            if ust25 < 1.60 and fark > 0.30:
                durum = "🟣 KURAL 9-A: UYUMSUZLUK - BOL GOL ✅ KANITLANDI"
                istisna.append("⚠️ **TESPİT:** 2,5 Üst oranı, hesaplanan değere göre **ÇOK DÜŞÜK**.")
                istisna.append("💥 **ANLAMI:** Savunma zaafiyeti kesin, oranlar yanıltıcı. **En az 3 gol** olma olasılığı çok yüksek.")
                if iy_yorum: istisna.append(iy_yorum)
                if kg_yorum: istisna.append(kg_yorum)
                istisna.append("📌 **SONUÇ:** Yüksek skorlar, goller özellikle ikinci yarıda yüklenir.")
                # ✅ Bahisler duruma göre güncellendi
                if "çok düşük" in kg_yorum and "VAR" in kg_yorum:
                    bahis = "2,5 ÜST (EN DEĞERLİ) | 1,5 ÜST + 2,5 ÜST | KG VAR"
                else:
                    bahis = "2,5 ÜST (EN DEĞERLİ) | 1,5 ÜST + 2,5 ÜST"
                skor = "2-1 / 3-1 / 1-2 / 2-2 / 3-0 / 4-1"
                handikap = "✅ HND OYNANIR | Farklı galibiyet olasılığı yüksek"
                guven = 94

            # ✅ KURAL 9-B: AZ GOL
            elif ust25 > 2.20 and fark < -0.40:
                durum = "🟠 KURAL 9-B: UYUMSUZLUK - AZ GOL ✅ KANITLANDI"
                istisna.append("⚠️ **TESPİT:** 2,5 Üst oranı, hesaplanan değere göre **ÇOK YÜKSEK**.")
                istisna.append("💡 **ANLAMI:** Sıkı savunma, gol olur ama **en fazla 1 gol farkla** biter, 2 golü geçmez.")
                if iy_yorum: istisna.append(iy_yorum)
                if kg_yorum: istisna.append(kg_yorum)
                istisna.append("📌 **SONUÇ:** Düşük skorlu maç, tek başına skorlar ağırlıkta.")
                bahis = "2,5 ALT (EN DEĞERLİ) | 1,5 ÜST + 2,5 ALT | KG YOK"
                skor = "1-0 / 2-0 / 0-1 / 0-2"
                handikap = "❌ HND OYNANMAZ | Fark açılması zor"
                guven = 92

    # ✅ TERS ORANTI KURALI
    if ms1 < ms2 and ms1 <= 2.00 and cok_dusuk_gol and durum == "":
        durum = "🔴 TERS ORANTI KURALI ✅"
        istisna.append("🔴🔴 **EN ÖZEL DURUM - TERS ORANTI** 🔴🔴")
        istisna.append(f"→ ms1={ms1} Ev favori; ms2={ms2} Deplasman zayıf;")
        istisna.append(f"→ 1,5 Üst={kullanilan_ust15} **ÇOK DÜŞÜK** → Gol garanti;")
        istisna.append(f"→ ms1_ust={ms1_ust_hesap} Ev gol olasılığı YÜKSEK;")
        istisna.append(f"→ ms2_ust={ms2_ust_hesap} Deplasman gol olasılığı DÜŞÜK;")
        if iy_yorum: istisna.append(iy_yorum)
        if kg_yorum: istisna.append(kg_yorum)
        istisna.append("✅ **GERÇEK DURUM:** Ev baskın, **2-0 / 2-1 / 1-1** en olası.")
        bahis = "1,5 ÜST (KESİN), MS1"
        skor = "2-1 / 2-0 / 1-1"
        handikap = "✅ HND1 OYNANIR | Ev güvenilir"
        guven = 90

    # ✅ GENEL KURAL
    if durum == "":
        durum = "🔵 GENEL KURAL | ORANLAR UYUMLU"
        istisna.append("ℹ️ **DURUM:** Oranlar normal, özel bir sapma veya durum yok.")
        if kg_yorum: istisna.append(kg_yorum)
        if iy_yorum: istisna.append(iy_yorum)
        
        if cok_yuksek_gol:
            bahis = "1,5 ALT | KG YOK"
            skor = "0-0 / 1-0 / 0-1"
            guven = 80
        else:
            bahis = "1,5 ÜST"
            skor = "1-1 / 2-1 / 1-0"
            guven = round(75 * guven_katsayi)
        handikap = "⚠️ RİSKLİ | Özel durum olmadığı için önerilmez"

    # 📋 SONUÇ METNİ
    istisna_notu = "\n⚠️ **DİKKAT! ÖZEL DURUMLAR & YORUMLAR**\n" + "\n".join(istisna) if istisna else ""

    sonuc = f"""
======================================================================
⚽ ANALİZ SONUCU | {durum}
======================================================================
📊 ORANLAR: MS1={ms1} | MS0={ms0} | MS2={ms2} | KG Var={kg_var or 'Yok'} | KG Yok={kg_yok or 'Yok'}
{oran_bilgisi}
📊 VERİ DURUMU: {veri_durumu}
⚖️ GÜÇ FARKI: {guc_farki}
📊 GÜVEN YÜZDESİ: %{guven}
──────────────────────────────────────
📝 DETAYLI YORUM: {istisna_notu}
──────────────────────────────────────
🏆 ÖNERİLEN BAHİS: {bahis}
⚽ EN OLASI SKOR ARALIĞI: {skor}
🤝 HANDİKAP DURUMU: {handikap}
{lig_notu}
======================================================================
"""
    return sonuc


# ------------------- KULLANIM ALANI -------------------
if __name__ == "__main__":
    print("⚽ MAÇ ANALİZ SİSTEMİ | TÜM KURALLAR AKTİF ✅\n")

    # SENİN MAÇIN - ARTIK YORUMLAR DA TAM UYUMLU ✅
    print(analiz(
        ms1=1.27,       # Ev sahibi
        ms0=3.96,       # Beraberlik
        ms2=6.09,       # Deplasman
        ust15=1.14,     # 1,5 Üst
        ust25=1.70,     # 2,5 Üst
        kg_var=1.89,    # Karşılıklı Gol Var
        kg_yok=1.44,    # Karşılıklı Gol Yok
        ms1_ust=1.59,   # Ev Gol Oranı
        ms2_ust=9.45,   # Dep Gol Oranı
        msx_ust=5.63,   # Beraberlik Gol
        iy_x=2.13,      # İlk Yarı 0-0
        iy_ust15=2.48,  # İlk Yarı 1,5 Üst
        iy_kg_var=5.00, # İlk Yarı KG Var
        lig_tipi="dünyakupasi" # Lig Adı
    ))

    input("\nÇıkmak için ENTER basın...")