# ⚽ MAÇ ANALİZ SİSTEMİ - TAM EKSİKSİZ SON SÜRÜM ✅
# ✅ KG YOK < 1.50 Kuralı + ✅ FARK > 1.00 Kuralı + ✅ HAZIRLIK MAÇI KURALI
def analiz(ms1, ms0, ms2, ust15=None, ust25=None, kg_var=None, kg_yok=None, 
           ms1_ust=None, ms2_ust=None, msx_ust=None, iy_x=None, iy_ust15=None, 
           iy_kg_var=None, lig_tipi="orta lig"):

    # 🎯 Lig ayarı
    lig = str(lig_tipi).lower()
    if "kupa" in lig or "dünyakupası" in lig or "hazırlık" in lig:
        guven_katsayi = 0.70
        lig_notu = "\n⚠️ Kupa/Hazırlık: Oranlar sonuç odaklıdır, skor farkı olmayabilir."
        kupa_maci = True
    elif "superettan" in lig:
        guven_katsayi = 0.90
        lig_notu = "\n✅ Süperettan: Yüksek gol ortalaması, oranlar çok güvenilir."
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
    kg_kural_gecerli = False 
    hazirlik_durumu = False # 👈 EKSİK OLAN KISIM 1: Hazırlık durumu kontrolü

    # ✅ KARŞILIKLI GOL ANALİZİ - KRAL KURAL 👑
    kg_yorum = ""
    if kg_var and kg_yok and kg_var > 0 and kg_yok > 0:
        if kg_var < 1.80:
            kg_yorum = "✅ KG VAR oranı çok düşük → Karşılıklı gol YÜKSEK olasılık."
        elif kg_yok < 1.50: 
            kg_yorum = "❌ **KG YOK < 1.50 KURALI** ✅ → Karşılıklı gol **ASLA OLMAZ**, tek taraf atar veya golsüz biter."
            kg_kural_gecerli = True 
        else:
            kg_yorum = "⚖️ KG Oranları dengeli → Durum belirsiz."

    # ✅ İLK YARI ANALİZİ
    iy_yorum = ""
    if iy_x and iy_ust15 and iy_x > 0 and iy_ust15 > 0:
        if kupa_maci:
            if iy_x < 2.20:
                iy_yorum = "ℹ️ **İLK YARI:** İY 0-0 oranı düşük → Goller ikinci yarıya kalır."
        else:
            if iy_x < 2.10:
                iy_yorum = "🔎 **İLK YARI:** 0-0 oranı düşük → Goller ikinci yarıya kalır."
            elif iy_ust15 < 2.00:
                iy_yorum = "🔥 **İLK YARI:** Gol erken gelir."

    # ✅ MATEMATİKSEL KARŞILAŞTIRMA & KURALLAR
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

            # 🔴 EKSİK OLAN KISIM 2: FARK > 1.00 VE MS < 1.20 KONTROLÜ
            if fark > 1.00 and ms1 < 1.20:
                hazirlik_durumu = True
                istisna.append("⚠️ **ÖZEL DURUM TESPİT EDİLDİ** ✅")
                istisna.append(f"→ FARK = {fark} (1.00'den büyük) | MS1 = {ms1} (1.20'den küçük)")
                istisna.append("✅ **ANLAMI:** Bu maç HAZIRLIK/GÖSTERİ MAÇIDIR. Oranlar sadece SONUÇ garantisi verir, SKOR garantisi vermez.")
                istisna.append("✅ **KURAL:** Gol olabilir de olmayabilir de, takımlar istediği gibi oynar. Alt/Üst risklidir.")

            # ✅ KURAL 9-A: BOL GOL
            if ust25 < 1.60 and fark > 0.30:
                durum = "🟣 KURAL 9-A: UYUMSUZLUK - BOL GOL ✅ KANITLANDI"
                istisna.append("⚠️ **TESPİT:** 2,5 Üst oranı çok düşük → Gol potansiyeli yüksek.")
                
                # 🔴 EKSİK OLAN KISIM 3: Hazırlık durumu varsa yorum değiştir
                if hazirlik_durumu:
                    istisna.append("ℹ️ **DÜZELTME:** Hazırlık maçı olduğu için 'bol gol' değil 'gol HAKKI' demektir. En fazla 1-2 gol olur veya hiç olmaz.")
                    istisna.append("📌 **SONUÇ:** Sadece sonuç kesin, skor belirsiz.")
                else:
                    istisna.append("💥 **ANLAMI:** En az 2-3 gol beklenir, goller ikinci yarıya yığılır.")
                    istisna.append("📌 **SONUÇ:** Skorlar yüksek olabilir ama KG kuralı belirleyicidir.")

                if iy_yorum: istisna.append(iy_yorum)
                if kg_yorum: istisna.append(kg_yorum) 

                # 👇 SKOR VE BAHİS TÜM KURALLARA GÖRE ŞEKİLLENİR 👇
                if kg_kural_gecerli:
                    if hazirlik_durumu:
                        # Hazırlık + KG Yok = En güvenli skorlar
                        bahis = "MS1 | KG YOK (EN GÜVENLİ)"
                        skor = "0-0 / 1-0 / 2-0 / 0-1" # 👈 En olası gerçek skorlar
                        handikap = "❌ HND OYNANMAZ | Skor belirsiz"
                        guven = 75
                    else:
                        bahis = "2,5 ÜST (EN DEĞERLİ) | KG YOK"
                        skor = "2-0 / 3-0 / 0-2 / 0-3 / 4-0"
                        handikap = "✅ HND OYNANIR"
                        guven = 94
                else:
                    bahis = "2,5 ÜST | KG VAR"
                    skor = "2-1 / 3-1 / 2-2 / 3-2"
                    handikap = "✅ HND OYNANIR"
                    guven = 94

            # ✅ KURAL 9-B: AZ GOL
            elif ust25 > 2.20 and fark < -0.40:
                durum = "🟠 KURAL 9-B: UYUMSUZLUK - AZ GOL ✅ KANITLANDI"
                istisna.append("⚠️ **TESPİT:** 2,5 Üst oranı çok yüksek → Gol sınırlı kalır.")
                istisna.append("💡 **ANLAMI:** En fazla 1-2 gol olur, 2 golü geçmez.")
                if iy_yorum: istisna.append(iy_yorum)
                if kg_yorum: istisna.append(kg_yorum)
                istisna.append("📌 **SONUÇ:** Düşük skor, tek başına goller.")

                if kg_kural_gecerli:
                    bahis = "2,5 ALT (EN DEĞERLİ) | KG YOK"
                    skor = "1-0 / 2-0 / 0-1 / 0-0"
                else:
                    bahis = "2,5 ALT"
                    skor = "1-0 / 0-0 / 1-1"
                handikap = "❌ HND OYNANMAZ"
                guven = 92

    # ✅ TERS ORANTI KURALI
    if ms1 < ms2 and ms1 <= 2.00 and cok_dusuk_gol and durum == "":
        durum = "🔴 TERS ORANTI KURALI ✅"
        istisna.append("🔴🔴 **EN ÖZEL DURUM** 🔴🔴")
        istisna.append(f"→ ms1={ms1} Favori, ms2={ms2} Zayıf")
        istisna.append(f"→ 1,5 Üst={kullanilan_ust15} Çok düşük → Gol garanti")
        if kg_yorum: istisna.append(kg_yorum)

        if kg_kural_gecerli:
            if hazirlik_durumu:
                bahis = "MS1 | KG YOK"
                skor = "1-0 / 2-0 / 0-0"
            else:
                bahis = "1,5 ÜST | KG YOK"
                skor = "2-0 / 3-0 / 4-0"
        else:
            bahis = "1,5 ÜST | KG VAR"
            skor = "2-0 / 2-1 / 3-1"
        handikap = "✅ HND1 OYNANIR"
        guven = 90

    # ✅ GENEL KURAL
    if durum == "":
        durum = "🔵 GENEL KURAL | ORANLAR UYUMLU"
        istisna.append("ℹ️ **DURUM:** Oranlar normal.")
        if kg_yorum: istisna.append(kg_yorum)
        
        if cok_yuksek_gol:
            bahis = "1,5 ALT | KG YOK"
            skor = "0-0 / 1-0 / 0-1"
        else:
            bahis = "1,5 ÜST"
            skor = "1-0 / 1-1 / 2-0"
        handikap = "⚠️ RİSKLİ"
        guven = round(75 * guven_katsayi)

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