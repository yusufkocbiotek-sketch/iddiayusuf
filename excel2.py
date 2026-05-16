import json
import pandas as pd

# JSON dosyasını oku
with open('public/data/mac.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

matches = data.get('matches', [])
liste = []

# Her maçı tek tek işle
for mac in matches:
    # Temel bilgiler
    satir = {
        'Tarih': mac.get('tarih', ''),
        'Saat': mac.get('saat', ''),
        'Lig': mac.get('lig', ''),
        'Ev Sahibi': mac.get('ev_sahibi', ''),
        'Deplasman': mac.get('deplasman', ''),
        'Durum': mac.get('durum', ''),
        'Mac Kodu': mac.get('mac_kodu', ''),
        'Kaynak': mac.get('kaynak', '')
    }

    # Skorları al ve G (Maç Skoru) ile F (İlk Yarı Skoru) sütunlarını oluştur
    se = mac.get('skor_ev', 0)
    sd = mac.get('skor_dep', 0)
    s1e = mac.get('skor_1y_ev', 0)
    s1d = mac.get('skor_1y_dep', 0)
    
    satir['F'] = f"{s1e}-{s1d}"  # İlk Yarı Sonucu
    satir['G'] = f"{se}-{sd}"    # Maç Sonucu

    # Oranlar verisini al
    oranlar = mac.get('oranlar', {})

    # ---------------- TÜM ORANLARI SÜTUNLARA ÇEVİRİYORUZ ----------------
    # Maç Sonucu
    satir['J_MS1'] = oranlar.get('Maç Sonucu_1', '')
    satir['K_MS0'] = oranlar.get('Maç Sonucu_0', '')
    satir['M_MS2'] = oranlar.get('Maç Sonucu_2', '')

    # Handikaplı Maç Sonucu
    satir['H01_1'] = oranlar.get('Handikaplı Maç Sonucu 0:1_1', '')
    satir['H01_0'] = oranlar.get('Handikaplı Maç Sonucu 0:1_0', '')
    satir['H01_2'] = oranlar.get('Handikaplı Maç Sonucu 0:1_2', '')

    # Maç Sonucu ve Alt/Üst 1.5
    satir['MS15_ALT1'] = oranlar.get('Maç Sonucu ve Alt/Üst 1.5_1 ve Alt', '')
    satir['MS15_ALT0'] = oranlar.get('Maç Sonucu ve Alt/Üst 1.5_0 ve Alt', '')
    satir['MS15_ALT2'] = oranlar.get('Maç Sonucu ve Alt/Üst 1.5_2 ve Alt', '')
    satir['MS15_UST1'] = oranlar.get('Maç Sonucu ve Alt/Üst 1.5_1 ve Üst', '')
    satir['MS15_UST0'] = oranlar.get('Maç Sonucu ve Alt/Üst 1.5_0 ve Üst', '')
    satir['MS15_UST2'] = oranlar.get('Maç Sonucu ve Alt/Üst 1.5_2 ve Üst', '')

    # Çifte Şans
    satir['CS_10'] = oranlar.get('Çifte Şans_1 ve 0', '')
    satir['CS_12'] = oranlar.get('Çifte Şans_1 ve 2', '')
    satir['CS_02'] = oranlar.get('Çifte Şans_0 ve 2', '')

    # İlk Yarı Sonucu
    satir['IY_1'] = oranlar.get('İlk Yarı Sonucu_1', '')
    satir['IY_0'] = oranlar.get('İlk Yarı Sonucu_0', '')
    satir['IY_2'] = oranlar.get('İlk Yarı Sonucu_2', '')

    # İkinci Yarı Sonucu
    satir['IY2_1'] = oranlar.get('İkinci Yarı Sonucu_1', '')
    satir['IY2_0'] = oranlar.get('İkinci Yarı Sonucu_0', '')
    satir['IY2_2'] = oranlar.get('İkinci Yarı Sonucu_2', '')

    # İlk Yarı Sonucu ve KG
    satir['IYKG_VAR1'] = oranlar.get('İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_1 ve Var', '')
    satir['IYKG_YOK1'] = oranlar.get('İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_1 ve Yok', '')
    satir['IYKG_VAR0'] = oranlar.get('İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_0 ve Var', '')
    satir['IYKG_YOK0'] = oranlar.get('İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_0 ve Yok', '')
    satir['IYKG_VAR2'] = oranlar.get('İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_2 ve Var', '')
    satir['IYKG_YOK2'] = oranlar.get('İlk Yarı Sonucu ve İlk Yarı Karşılıklı Gol_2 ve Yok', '')

    # İlk Yarı Sonucu ve Alt/Üst 1.5
    satir['IY15_ALT1'] = oranlar.get('İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Alt', '')
    satir['IY15_ALT0'] = oranlar.get('İlk Yarı Sonucu ve Altı/Üstü 1.5_0 ve Alt', '')
    satir['IY15_ALT2'] = oranlar.get('İlk Yarı Sonucu ve Altı/Üstü 1.5_2 ve Alt', '')
    satir['IY15_UST1'] = oranlar.get('İlk Yarı Sonucu ve Altı/Üstü 1.5_1 ve Üst', '')
    satir['IY15_UST0'] = oranlar.get('İlk Yarı Sonucu ve Altı/Üstü 1.5_0 ve Üst', '')
    satir['IY15_UST2'] = oranlar.get('İlk Yarı Sonucu ve Altı/Üstü 1.5_2 ve Üst', '')

    # İlk Yarı Diğer
    satir['IY_KG_VAR'] = oranlar.get('İlk Yarı Karşılıklı Gol_Var', '')
    satir['IY_CS_10'] = oranlar.get('İlk Yarı Çifte Şans_1 ve 0', '')
    satir['IY_CS_12'] = oranlar.get('İlk Yarı Çifte Şans_1 ve 2', '')
    satir['IY_CS_02'] = oranlar.get('İlk Yarı Çifte Şans_0 ve 2', '')
    satir['IY_TEK'] = oranlar.get('İlk Yarı Tek/Çift_Tek', '')
    satir['IY_CIFT'] = oranlar.get('İlk Yarı Tek/Çift_Çift', '')

    # Alt/Üst ve KG Kombinasyon
    satir['AU25KG_ALTVAR'] = oranlar.get('Altı/Üstü 2.5 ve Karşılıklı Gol_Alt ve Var', '')
    satir['AU25KG_USTVAR'] = oranlar.get('Altı/Üstü 2.5 ve Karşılıklı Gol_Üst ve Var', '')
    satir['AU25KG_ALTYOK'] = oranlar.get('Altı/Üstü 2.5 ve Karşılıklı Gol_Alt ve Yok', '')
    satir['AU25KG_USTYOK'] = oranlar.get('Altı/Üstü 2.5 ve Karşılıklı Gol_Üst ve Yok', '')

    # Maç Sonucu ve KG Kombinasyon
    satir['MSKG_1VAR'] = oranlar.get('Maç Sonucu ve Karşılıklı Gol_1 ve Var', '')
    satir['MSKG_1YOK'] = oranlar.get('Maç Sonucu ve Karşılıklı Gol_1 ve Yok', '')
    satir['MSKG_0VAR'] = oranlar.get('Maç Sonucu ve Karşılıklı Gol_0 ve Var', '')
    satir['MSKG_0YOK'] = oranlar.get('Maç Sonucu ve Karşılıklı Gol_0 ve Yok', '')
    satir['MSKG_2VAR'] = oranlar.get('Maç Sonucu ve Karşılıklı Gol_2 ve Var', '')
    satir['MSKG_2YOK'] = oranlar.get('Maç Sonucu ve Karşılıklı Gol_2 ve Yok', '')

    # Genel Alt/Üst
    satir['AU15_ALT'] = oranlar.get('Alt/Üst 1.5_Alt', '')
    satir['AU15_UST'] = oranlar.get('Alt/Üst 1.5_Üst', '')
    satir['H_AU25_ALT'] = oranlar.get('Alt/Üst 2.5_Alt', '')
    satir['I_AU25_UST'] = oranlar.get('Alt/Üst 2.5_Üst', '')
    satir['AU35_ALT'] = oranlar.get('Alt/Üst 3.5_Alt', '')
    satir['AU35_UST'] = oranlar.get('Alt/Üst 3.5_Üst', '')

    # Ev Sahibi / Deplasman Alt/Üst
    satir['EVAU15_ALT'] = oranlar.get('Ev Sahibi Alt/Üst 1.5_Alt', '')
    satir['EVAU15_UST'] = oranlar.get('Ev Sahibi Alt/Üst 1.5_Üst', '')
    satir['DEPAU05_ALT'] = oranlar.get('Deplasman Alt/Üst 0.5_Alt', '')
    satir['DEPAU05_UST'] = oranlar.get('Deplasman Alt/Üst 0.5_Üst', '')

    # Diğer Özel Oranlar
    satir['IKIYARI15_EVET'] = oranlar.get('Her İki Yarıda da Alt 1.5_Evet', '')
    satir['IKIYARI15_HAYIR'] = oranlar.get('Her İki Yarıda da Alt 1.5_Hayır', '')
    satir['IKIYARIUST15_EVET'] = oranlar.get('Her İki Yarıda da Üst 1.5_Evet', '')
    satir['IYAU05_ALT'] = oranlar.get('İlk Yarı Alt/Üst 0.5_Alt', '')
    satir['IYAU05_UST'] = oranlar.get('İlk Yarı Alt/Üst 0.5_Üst', '')

    # Ev/Dep İlk Yarı Alt/Üst
    satir['EVIY05_ALT'] = oranlar.get('Ev Sahibi İlk Yarı Altı/Üstü 0.5_Alt', '')
    satir['EVIY05_UST'] = oranlar.get('Ev Sahibi İlk Yarı Altı/Üstü 0.5_Üst', '')
    satir['DEPIY05_ALT'] = oranlar.get('Deplasman İlk Yarı Altı/Üstü 0.5_Alt', '')
    satir['DEPIY05_UST'] = oranlar.get('Deplasman İlk Yarı Altı/Üstü 0.5_Üst', '')

    # Karşılıklı Gol
    satir['O_KG_VAR'] = oranlar.get('Karşılıklı Gol_Var', '')
    satir['P_KG_YOK'] = oranlar.get('Karşılıklı Gol_Yok', '')

    # Toplam Gol
    satir['TG_01'] = oranlar.get('Toplam Gol_0-1 gol', '')
    satir['TG_23'] = oranlar.get('Toplam Gol_2-3 gol', '')
    satir['TG_45'] = oranlar.get('Toplam Gol_4-5 gol', '')
    satir['TG_6PLUS'] = oranlar.get('Toplam Gol_6+ gol', '')

    # Yarı Gol Durumları
    satir['HANGIYARI_1'] = oranlar.get('Hangi Yarıda Daha Fazla Gol Olur_1.', '')
    satir['HANGIYARI_ESIT'] = oranlar.get('Hangi Yarıda Daha Fazla Gol Olur_Eşit', '')
    satir['HANGIYARI_2'] = oranlar.get('Hangi Yarıda Daha Fazla Gol Olur_2.', '')

    # Ev/Dep Yarı Gol Durumları
    satir['EVHANGI_1'] = oranlar.get('Ev Sahibi Hangi Yarıda Daha Fazla Gol Atar_1.', '')
    satir['EVHANGI_ESIT'] = oranlar.get('Ev Sahibi Hangi Yarıda Daha Fazla Gol Atar_Eşit', '')
    satir['EVHANGI_2'] = oranlar.get('Ev Sahibi Hangi Yarıda Daha Fazla Gol Atar_2.', '')
    satir['DEPHANGI_1'] = oranlar.get('Deplasman Hangi Yarıda Daha Fazla Gol Atar_1.', '')
    satir['DEPHANGI_ESIT'] = oranlar.get('Deplasman Hangi Yarıda Daha Fazla Gol Atar_Eşit', '')
    satir['DEPHANGI_2'] = oranlar.get('Deplasman Hangi Yarıda Daha Fazla Gol Atar_2.', '')

    # Tek / Çift
    satir['TC_TEK'] = oranlar.get('Tek / Çift_Tek', '')
    satir['TC_CIFT'] = oranlar.get('Tek / Çift_Çift', '')

    # İkinci Yarı Diğer
    satir['IY2_KG_VAR'] = oranlar.get('İkinci Yarı Karşılıklı Gol_Var', '')
    satir['IY2_KG_YOK'] = oranlar.get('İkinci Yarı Karşılıklı Gol_Yok', '')

    # Her İki Yarı Gol Durumu
    satir['EVHERIKI_EVET'] = oranlar.get('Ev Sahibi Her İki Yarıda da Gol Atar_Evet', '')
    satir['EVHERIKI_HAYIR'] = oranlar.get('Ev Sahibi Her İki Yarıda da Gol Atar_Hayır', '')
    satir['DEPHERIKI_EVET'] = oranlar.get('Deplasman Her İki Yarıda da Gol Atar_Evet', '')

    # Çoklu KG Durumları
    satir['IKIYARIKG_HH'] = oranlar.get('İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur_Hayır / Hayır', '')
    satir['IKIYARIKG_EH'] = oranlar.get('İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur_Evet / Hayır', '')
    satir['IKIYARIKG_EE'] = oranlar.get('İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur_Evet / Evet', '')
    satir['IKIYARIKG_HE'] = oranlar.get('İlk Yarı ve İkinci Yarıda Karşılıklı Gol Olur_Hayır / Evet', '')

    liste.append(satir)

# DataFrame oluştur
df = pd.DataFrame(liste)

# Excel sınırı kontrolü (çok fazla sütun olursa sıkıntı olmasın)
if df.shape[1] > 16000:
    df = df.transpose().reset_index()

# Excel'e Kaydet
df.to_excel('tum_veriler_ve_tum_oranlar.xlsx', index=False)

print(f"✅ TAMAMEN BAŞARILI! Toplam {len(df)} maç ve tüm oranlar Excel'e aktarıldı.")
print("📌 Dosya adı: tum_veriler_ve_tum_oranlar.xlsx")