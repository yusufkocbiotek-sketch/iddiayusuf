import sys
import rule_engine

def get_league_type(match):
    lig = match.get('lig', '').lower()
    ev = match.get('ev_sahibi', '').lower()
    dep = match.get('deplasman', '').lower()
    
    if 'japonya' in lig or 'kore' in lig or 'çin' in lig or 'asya' in lig or 'avustralya' in lig:
        return 'ASYA'
    if 'arjantin' in lig or 'brezilya' in lig or 'şili' in lig or 'kolombiya' in lig:
        return 'GÜNEY_AMERİKA'
    if 'ingiltere' in lig or 'almanya' in lig or 'italya' in lig or 'ispanya' in lig:
        return 'AVRUPA_MAJÖR'
    return 'STANDART'

def generate_story(match, verbose=False):
    odds = match.get('oranlar', {}).copy()
    lig_tipi = get_league_type(match)
    odds['__LIG_TIPI__'] = lig_tipi
    
    # Check for missing critical data
    ms1 = rule_engine.get_odd(odds, ["Maç Sonucu_1"])
    ust25 = rule_engine.get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
    ust35 = rule_engine.get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
    ust15 = rule_engine.get_odd(odds, ["Alt/Üst 1.5_Üst", "Altı/Üstü 1.5_Üst"])
    ms2 = rule_engine.get_odd(odds, ["Maç Sonucu_2", "2", "Maç Sonucu_Deplasman"])
    ms0 = rule_engine.get_odd(odds, ["Maç Sonucu_0", "0", "Beraberlik", "Maç Sonucu_X", "X"])

    if (ms1 == 99.0 and ms2 == 99.0 and ms0 == 99.0) or (ust25 == 99.0 and ust35 == 99.0 and ust15 == 99.0):
        return "⚠️ [SİSTEM UYARISI] Bu maçın temel oran verileri (MS veya HİÇBİR Alt/Üst baremi) eksik açıldığı için maç YETERSİZ VERİ sebebiyle analiz dışı bırakılmıştır."

    ev = match.get('ev_sahibi', 'Ev Sahibi')
    dep = match.get('deplasman', 'Deplasman')
    lig = match.get('lig', 'Bilinmeyen Lig')
    saat = match.get('saat', 'Bilinmiyor')
    
    rules = rule_engine.get_all_rules()
    sys.modules['rule_engine'].CURRENT_MATCH = match
    
    triggered_rules = []
    for RuleClass in rules:
        is_triggered, insight = RuleClass.evaluate(odds)
        if is_triggered:
            triggered_rules.append({
                'code': RuleClass.code,
                'category': RuleClass.category,
                'name': RuleClass.name,
                'description': RuleClass.description,
                'insight': insight
            })
            
    # Hiyerarşik Sıralama (Faz 0-5)
    def rule_sort_key(r):
        code = r['code']
        name = r['name'].lower()
        
        # 1467B özel emri: 1530'dan önce bakılması için -1 yapıldı
        if code == '1467B': return -1
        
        # 0-0 Kilitleri ve Paradokslar en yüksek önceliklidir (Faz 0)
        if 'paradoks' in name or 'matematiksel' in name or code in ['1530', '1530B', 'Y11', '1558']: return 0 
        
        # Lig veya profil kuralları dominant olmamalı (En düşük öncelik)
        if code.startswith('LIG') or code in ['2001', '2002', '999']: return 99 
        
        if code.startswith('1'): return 2 # Faz 2 (Anomaliler)
        if code.startswith('G'): return 3 # Faz 3 (Gol)
        if code.startswith('T'): return 4 # Faz 4 (Taraf)
        if code.startswith('Y'): return 5 # Faz 5 (Yarı)
        return 50

    triggered_rules.sort(key=rule_sort_key)
            
    ms1 = rule_engine.get_odd(odds, ["Maç Sonucu_1"])
    ms0 = rule_engine.get_odd(odds, ["Maç Sonucu_0"])
    ms2 = rule_engine.get_odd(odds, ["Maç Sonucu_2"])
    
    cs1x = rule_engine.get_odd(odds, ["Çifte Şans_1 ve 0", "Çifte Şans_1X"])
    cs12 = rule_engine.get_odd(odds, ["Çifte Şans_1 ve 2", "Çifte Şans_12"])
    csx2 = rule_engine.get_odd(odds, ["Çifte Şans_0 ve 2", "Çifte Şans_X2", "Çifte Şans_2 ve 0"])
    
    iy1 = rule_engine.get_odd(odds, ["1. Yarı Sonucu_1", "İlk Yarı Sonucu_1"])
    iy0 = rule_engine.get_odd(odds, ["1. Yarı Sonucu_0", "İlk Yarı Sonucu_0"])
    iy2 = rule_engine.get_odd(odds, ["1. Yarı Sonucu_2", "İlk Yarı Sonucu_2"])
    
    alt25 = rule_engine.get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
    ust25 = rule_engine.get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
    kg_var = rule_engine.get_odd(odds, ["Karşılıklı Gol_Var"])
    kg_yok = rule_engine.get_odd(odds, ["Karşılıklı Gol_Yok"])
    tek = rule_engine.get_odd(odds, ["Tek / Çift_Tek", "Tek/Çift_Tek"])
    cift = rule_engine.get_odd(odds, ["Tek / Çift_Çift", "Tek/Çift_Çift"])

    output = []
    output.append(f"# 📊 MAÇ ANALİZ ŞABLONU – {ev.upper()} – {dep.upper()}")
    output.append(f"**Maç:** {ev} – {dep} | **Lig:** {lig} ({lig_tipi}) | **Başlama Saati:** {saat}")
    output.append(f"")
    output.append(f"### 🎲 Detaylı Oran Tablosu")
    output.append(f"- **Taraf:** Ev **{ms1}** | Beraberlik **{ms0}** | Konuk **{ms2}**")
    output.append(f"- **Çifte Şans:** 1X **{cs1x}** | 12 **{cs12}** | X2 **{csx2}**")
    output.append(f"- **İlk Yarı MS:** Ev **{iy1}** | Beraberlik **{iy0}** | Konuk **{iy2}**")
    output.append(f"- **Gol (2.5):** Alt **{alt25}** | Üst **{ust25}**")
    output.append(f"- **Karşılıklı Gol:** KG Var **{kg_var}** | KG Yok **{kg_yok}**")
    output.append(f"- **Tek/Çift:** Tek **{tek}** | Çift **{cift}**")
    output.append(f"---")
    
    iy_ev = match.get("skor_1y_ev")
    iy_dep = match.get("skor_1y_dep")
    ms_ev = match.get("skor_ev")
    ms_dep = match.get("skor_dep")
    
    if iy_ev is not None and ms_ev is not None:
        ilk_yari_skoru = f"{iy_ev}-{iy_dep}"
        mac_skoru = f"{ms_ev}-{ms_dep}"
        output.append(f"\n> 🏆 **GERÇEKLEŞEN SKOR:** İlk Yarı **{ilk_yari_skoru}** | Maç Sonucu **{mac_skoru}**\n")
    
    if not triggered_rules:
        kural_kodlari = "TUZAK YOK (STANDART PİYASA)"
    else:
        kural_kodlari = " → ".join([r['code'] for r in triggered_rules])
    
    output.append(f"**Kural Sırası:** **{kural_kodlari}**")
    
    # Genel Profil
    profil = []
    if ms1 != 99.0 and ms2 != 99.0 and ms1 < ms2 and ms1 <= 1.50: profil.append("AĞIR EV FAVORİSİ")
    elif ms1 != 99.0 and ms2 != 99.0 and ms1 < ms2: profil.append("EV HAFİF FAVORİSİ")
    elif ms1 != 99.0 and ms2 != 99.0 and ms2 < ms1 and ms2 <= 1.50: profil.append("AĞIR KONUK FAVORİSİ")
    elif ms1 != 99.0 and ms2 != 99.0 and ms2 < ms1: profil.append("KONUK HAFİF FAVORİSİ")
    else: profil.append("TAM DENGE")
    
    if kg_var and kg_yok and kg_var < kg_yok: profil.append("KARŞILIKLI GOL VAR")
    else: profil.append("KG YOK AĞIRLIKLI")
    
    if ust25 and alt25 and ust25 < alt25: profil.append("GOLLÜ GEÇMEYE ADAY")
    else: profil.append("KISIR GEÇMEYE ADAY")
    
    if any(r['code'] in ['T32', 'T35', 'T9', '1470', '1478', '1479', '1480', '1481', '1482', '1483', '1484', '1485', 'G6'] for r in triggered_rules):
        profil_metni = "🚨 **AĞIR TUZAK TESPİT EDİLDİ - KLASİK PROFİL GEÇERSİZ**"
    else:
        profil_metni = " ✅ **" + " – ".join(profil) + "**"
        
    output.append(f"**Genel Profil:** {profil_metni}")
    
    output.append("\n---")
    output.append("\n## 🔹 ADIM 0 – LİG & ÖZEL DURUM")
    
    if lig_tipi == 'ASYA':
        output.append(f"**⛩️ ASYA LİGİ DİNAMİKLERİ:** Bu bölgede oran manipülasyonu (gollü maçı kısır, kısır maçı gollü gösterme) çok sıktır. Asya Tuzağı ihtimaline karşı tetikte olunmalı.")
    elif lig_tipi == 'GÜNEY_AMERİKA':
        output.append(f"**🌎 GÜNEY AMERİKA DİNAMİKLERİ:** Sert ve kısır geçen maçlar yaygındır. Düşük alt oranları genelde gerçeği yansıtır.")
    else:
        output.append(f"**🌍 {lig} DİNAMİKLERİ:**")
        
    if abs(ms1 - ms2) <= 0.50:
        output.append("- Ana oranlar birbirine çok yakın. Beraberlik riski veya sürpriz olasılığı oldukça yüksek.")
    elif ms1 <= 1.50 or ms2 <= 1.50:
        output.append("- Favori takımın oranı çok düşük. Maçın gidişatını favorinin erken gol bulup bulamayacağı belirleyecek.")
    else:
        output.append("- Oranlar favoriyi işaret etse de risk barındırıyor.")
        
    output.append("\n---")
    output.append("\n## 🔹 KURAL BASAMAK BASAMAK DEĞERLENDİRMESİ")
    output.append("| Kural | Adı | Kategori | Çıkarım / Hikaye |")
    output.append("|---|---|---|---|")
    if not triggered_rules:
        output.append("| **NORMAL** | Tuzak Tespiti Yok | BİLGİ | ✅ **AKTİF** - Bu maçta herhangi bir piyasa manipülasyonu veya ters tuzak (paradoks) tespit edilmedi. İddaa oranları gerçeği yansıtıyor. Favoriye güvenilebilir. |")
    else:
        for r in triggered_rules:
            kural_mesaji = r['insight']
            if r['code'] == "1530":
                ms0_val = rule_engine.get_odd(match.get('oranlar', {}), ["Maç Sonucu_0", "Maç Sonucu_Beraberlik"])
                if ms0_val <= 2.85 and ms0_val != 99.0:
                    kural_mesaji = "İLK YARI ŞİFRESİ (ÇİFTE TUZAK - 0-0 KİLİDİ): Piyasa 2.5 Alt (1.60 altı) gösterirken İlk Yarı 0.5 Üstü 1.30 altına çekerek 'İlk yarı kesin gol olacak' tuzağı kuruyor. FAKAT Beraberlik oranı (MS 0) 2.85 ve altındaysa bu, maçın 0-0'a kilitleneceğinin kesin kanıtıdır. İddaa sırf MS 0 oynanmasın diye İY Gol yemi atıyor. Kesinlikle 2.5 Alt ve MS 0 (0-0) oynanmalıdır!"
            output.append(f"| **{r['code']}** | {r['name']} | {r['category']} | ✅ **AKTİF** - {kural_mesaji} |")
        
    output.append("\n---")
    output.append("\n## 🧠 PİYASA PSİKOLOJİSİ & YÖN TAHMİNİ")
    output.append("### 🎯 En Olası Skorlar (Hiyerarşik)")
    gol_beklentisi = "ORTA"
    ust35 = rule_engine.get_odd(odds, ["Alt/Üst 3.5_Üst", "Alt/Üst 3,5_Üst"])
    
    if any(r['code'] in ['G1', 'G8', 'G11', 'G12', 'T32', 'T33', 'T34', 'T36', '1465', '1466', '1483'] for r in triggered_rules) or ust25 < 1.60 or ust35 < 1.90:
        gol_beklentisi = "YÜKSEK"
    elif any(r['code'] in ['G2', 'G4', 'G5', 'G5-B', 'Y4', 'G10'] for r in triggered_rules) or alt25 < 1.60:
        gol_beklentisi = "DÜŞÜK"
        
    if any(r['code'] in ['G10', '1470'] for r in triggered_rules):
        gol_beklentisi = "DÜŞÜK"
        
    
    has_g1 = any(r['code'] == 'G1' for r in triggered_rules)
    has_g11 = any(r['code'] == 'G11' for r in triggered_rules)
    has_1467B = any(r['code'] == '1467B' for r in triggered_rules)
    
    has_1485 = any(r['code'] == '1485' for r in triggered_rules)
    has_t70 = any(r['code'] == 'T70' for r in triggered_rules)
    
    if has_1467B:
        skorlar = "2-2 > 3-3 > 1-1"
        kacin = "0-0 / 1-0 / 0-1 gibi kısır skorlar"
    elif has_1485:
        skorlar = "1-0 > 0-0 > 1-1"
        kacin = "2-1 / 2-2 / 3-1 gibi gollü skorlar"
    elif has_t70:
        skorlar = "0-1 > 1-1 > 0-0 > 1-2"
        kacin = "2-0 / 3-0 gibi farklı ev sahibi skorları"
    elif has_g1:
        skorlar = "3-0 > 4-0 > 0-3 > 3-1"
        kacin = "0-0 / 1-1 / 1-0 gibi kısır veya beraberlik skorları"
    elif has_g11:
        skorlar = "2-2 > 2-1 > 1-2 > 3-2"
        kacin = "0-0 / 1-0 / 0-1 gibi kısır skorlar"
    elif gol_beklentisi == "YÜKSEK" and kg_var < kg_yok:
        skorlar = "2-1 > 1-2 > 2-2 > 3-1"
        kacin = "0-0 / 1-0 / 0-1 gibi kısır skorlar"
    elif gol_beklentisi == "YÜKSEK" and kg_yok < kg_var:
        skorlar = "3-0 > 0-3 > 4-0 > 2-0"
        kacin = "1-1 / 2-2 gibi karşılıklı gollü skorlar"
    elif gol_beklentisi == "DÜŞÜK" and kg_yok < kg_var:
        skorlar = "1-0 > 0-1 > 0-0 > 2-0"
        kacin = "2-2 / 3-1 / 1-3 gibi bol gollü skorlar"
    elif gol_beklentisi == "DÜŞÜK" and any(kural['code'] == "1530" for kural in triggered_rules):
        ms0 = rule_engine.get_odd(match.get('oranlar', {}), ["Maç Sonucu_0", "Maç Sonucu_Beraberlik"])
        if ms0 <= 2.85 and ms0 != 99.0:
            skorlar = "0-0 (Kilit Maç)"
            kacin = "Tüm gollü skorlar"
        else:
            skorlar = "1-1 > 2-1 > 1-2"
            kacin = "3-0 / 0-3 gibi farklı skorlar"
    else:
        skorlar = "1-1 > 2-1 > 1-2 > 2-0"
        kacin = "Çok farklı skorlar (Örn: 4-0)"
        
    output.append(f"**En Yüksek Olasılık:** **{skorlar}**")
    output.append(f"**Kaçınılması Gereken:** {kacin}")
    
    output.append("\n### 📌 Yön Değerlendirmesi")
    if any(r['code'] == 'T68' for r in triggered_rules):
        output.append("- **Yön Tuzağı:** Beraberlik tuzağı kurulmuş, biri kesin kazanır.")
    
    has_anomaly = any(r['code'].startswith('1') or r['code'].startswith('2') for r in triggered_rules)
    if has_anomaly or any(r['code'] in ['T32', 'T35', 'T9', 'G6', 'G10', 'T70'] for r in triggered_rules):
        output.append("- **⚠️ YÖN UYARISI:** Klasik MS bahisleri yanıltıcıdır! Makine gizli bir tuzak veya paradoks tespit etti.")
        output.append("- **Alternatif Yön:** Sistemin Ana Tahmin kısmındaki DOMİNANT öneriye sadık kalın.")
    else:
        if ms1 != 99.0 and ms2 != 99.0 and ms1 < ms2:
            output.append("- **Ev Galibiyeti:** Maçın en mantıklı senaryosu (Tuzak yoksa).")
            output.append(f"- **Beraberlik:** ({ms0}) Dikkat edilmesi gereken bir sigorta.")
        else:
            output.append("- **Konuk Galibiyeti:** Avantaj deplasmanda (Tuzak yoksa).")
            output.append(f"- **Beraberlik:** ({ms0}) Denge ihtimali her zaman var.")
        
    output.append("\n---")
    output.append("\n## ✅ SON ÖZET")
    output.append("Bu maçta **sistemin süzdüğü en kesin sinyaller:**")
    counter = 1
    
    if gol_beklentisi == "YÜKSEK":
        output.append(f"{counter}. ✅ **Yüksek Gol Beklentisi:** Kurallar maçın açılacağını ve en az 3 gol çıkacağını gösteriyor.")
        counter += 1
    elif gol_beklentisi == "DÜŞÜK":
        output.append(f"{counter}. ⚠️ **Kısır Maç Beklentisi:** Kurallar maçın kilitleneceğini ve az gollü (max 2 gol) geçeceğini işaret ediyor.")
        counter += 1
        
    if kg_var and kg_yok and kg_var < kg_yok and gol_beklentisi == "YÜKSEK":
        output.append(f"{counter}. ✅ **Karşılıklı Gol Var:** İki takımın da skora katkı yapması güçlü bir ihtimal.")
        counter += 1
    elif kg_var and kg_yok and kg_yok < 99.0 and kg_yok < kg_var:
        output.append(f"{counter}. ⚠️ **Tek Taraflı Skor Riski:** Takımlardan birinin (veya ikisinin) skora katkı verememe ihtimali yüksek (KG Yok).")
        counter += 1
        
    output.append(f"\n### ⏱️ ZAMANLAMA VE YARI ANALİZİ")
    zamanlama_notlari = 0
    iy_ust = rule_engine.get_odd(odds, ["1. Yarı Alt/Üst 0.5_Üst", "1. Yarı Altı/Üstü 0.5_Üst"])
    iy_kg_var = rule_engine.get_odd(odds, ["1. Yarı Karşılıklı Gol_Var"])
    
    if any(r['code'] in ['T32', 'T35', 'T9', '1470', '1478', '1479', '1480', '1481', '1482', '1483', '1484', '1485', 'G6'] for r in triggered_rules):
        output.append("- 🚨 **TUZAK ZAMANLAMASI:** Normal yarı bahisleri (İlk Yarı KG, Üst vb.) bu maçta tamamen tuzaktır. Ana tahminin dışına çıkılmamalıdır.")
        zamanlama_notlari += 1
    else:
        ilk_yari_kg_var = rule_engine.get_odd(odds, ["1. Yarı Karşılıklı Gol_Var"])
        if ilk_yari_kg_var and ilk_yari_kg_var < 99.0 and ilk_yari_kg_var < 4.00:
            output.append(f"- ⚔️ **İlk Yarı Düellosu (KG):** İlk yarıdan her iki takımın da gol bulma olasılığı normalden çok daha yüksek fiyatlanmış. Erken karşılıklı goller gelebilir.")
            zamanlama_notlari += 1
            
        ilk_yari_05_ust = rule_engine.get_odd(odds, ["1. Yarı Alt/Üst 0.5_Üst"])
        if ilk_yari_05_ust and ilk_yari_05_ust < 99.0 and ilk_yari_05_ust < 1.30:
            output.append(f"- ⚡ **Hareketli İlk Yarı:** Maçın ilk yarısından kesin gol sesi çıkması bekleniyor. İlk 45 dakika sert geçecek.")
            zamanlama_notlari += 1
            
        ikinci_yari_kg_var = rule_engine.get_odd(odds, ["2. Yarı Karşılıklı Gol_Var"])
        if ikinci_yari_kg_var and ikinci_yari_kg_var < 99.0 and ikinci_yari_kg_var < 3.00:
            output.append(f"- 🔥 **İkinci Yarı Şovu (KG):** İkinci yarıda her iki takımın da gol atma (2. Yarı KG Var) ihtimali çok güçlü. Son dakikalar kaos vadediyor.")
            zamanlama_notlari += 1
            
        iki_yari_kg_evet = rule_engine.get_odd(odds, ["1. Yarı ve 2. Yarıda Karşılıklı Gol Olur_Evet / Evet"])
        if iki_yari_kg_evet and iki_yari_kg_evet < 99.0 and iki_yari_kg_evet < 12.00:
            output.append(f"- 🌋 **TARİHİ DÜELLO (HER İKİ YARIDA KG VAR):** İki yarıda da karşılıklı gol olma oranı ({iki_yari_kg_evet}) şüpheli derecede düşük! Bu maçın efsanevi bir gol düellosuna (örn: 2-2, 3-2, 3-3) dönüşme ihtimali masada.")
            zamanlama_notlari += 1

    if zamanlama_notlari == 0:
        iy_ms1 = rule_engine.get_odd(match.get('oranlar', {}), ["1. Yarı Sonucu_1"])
        iy_ms0 = rule_engine.get_odd(match.get('oranlar', {}), ["1. Yarı Sonucu_0"])
        iy_ms2 = rule_engine.get_odd(match.get('oranlar', {}), ["1. Yarı Sonucu_2"])
        iy_kgyok = rule_engine.get_odd(match.get('oranlar', {}), ["1. Yarı Karşılıklı Gol_Yok", "İlk Yarı Karşılıklı Gol_Yok"])
        iy_15_ust = rule_engine.get_odd(match.get('oranlar', {}), ["1. Yarı Alt/Üst 1.5_Üst", "İlk Yarı Alt/Üst 1.5_Üst", "İlk Yarı Altı/Üstü 1.5_Üst"])
        
        timing_insights = []
        
        if iy_15_ust != 99.0 and iy_15_ust <= 2.20:
            timing_insights.append(f"⚡ **Hareketli İlk Yarı:** Maçın başından itibaren skor tabelasının değişmesi (İlk Yarı 0.5 Üst) veya hızlı bir düello (İlk Yarı 1.5 Üst) ihtimali oldukça güçlü fiyatlanmış (Oran: {iy_15_ust}).")
            
        if iy_kgyok != 99.0 and iy_kgyok <= 1.15:
            timing_insights.append(f"🛡️ **İlk Yarı Tek Taraflı:** İlk yarıda en az bir takımın (muhtemelen zayıf takımın) skor üretemeyeceği (İY KG Yok) oranlarla garanti altına alınmış (Oran: {iy_kgyok}).")
            
        if iy_ms0 != 99.0 and iy_ms0 <= 2.05:
            timing_insights.append(f"⚖️ **İlk Yarı Dengesi:** İlk yarının beraberlikle (0-0 veya 1-1) sonuçlanma ihtimali çok yüksek.")
            
        if iy_ms1 != 99.0 and iy_ms1 <= 1.95:
            timing_insights.append(f"🔥 **Erken Ev Sahibi Baskısı:** Ev sahibi takımın maça hızlı başlayıp ilk yarıyı önde kapatması bekleniyor (İlk Yarı MS1).")
        elif iy_ms2 != 99.0 and iy_ms2 <= 2.80:
            timing_insights.append(f"✈️ **Deplasman Baskını:** Deplasman takımının ilk yarıda şok bir üstünlük kurma potansiyeli var (İlk Yarı MS2).")

        if timing_insights:
            for insight in timing_insights:
                output.append(f"- {insight}")
        else:
            output.append(f"- 📉 **Standart Akış:** Zamanlama (yarı) bahisleri için ekstra bir anomali veya belirgin bir sinyal tespit edilemedi.")

    is_massive_duel = ('İlk Yarı Düellosu (KG)' in ''.join(output) and 'İkinci Yarı Şovu (KG)' in ''.join(output)) or 'TARİHİ DÜELLO' in ''.join(output) or any(r['code'] == 'G11' for r in triggered_rules)
    output.append(f"\n### 💎 KOMBİNE & TAHMİN ÖNERİLERİ")
    
    # Prediction Dictionary
    predictions = {
        '1534': ("Maç Sonucu 1 veya 1X", "Maç Sonucu 1 + 2.5 Gol Altı (Sürpriz Skor: 1-0 / 2-0)"),
        '1533': ("Ağır Favori Çöküşü (Gizli Ev Sahibi Şovu)", "1X Çifte Şans ve Ev Sahibi Golü (Sürpriz Skor: 3-1 / 3-2)"),
        '1532': ("Kısır Favori Sendromu", "2.5 Gol Altı veya Maç Sonucu 0 (Sürpriz Skor: 1-1 / 0-0)"),
        '1531': ("Gizli Favori Sendromu (Deplasman Vurgunu)", "Deplasman 0.5 Üst veya Maç Sonucu 2 (Sürpriz Skor: 1-2 / 1-3)"),
        '1530': ("İlk Yarı Şifresi (Kısır Maç, Hızlı Gol)", "İlk Yarı 0.5 Üst (Sürpriz Skor: İlk Yarı 1-0 veya 1-1)"),
        '1523': ("Şeytani İlk Yarı Şöleni (Ters Manyel)", "İlk Yarı 1.5 Üst ve İlk Yarı KG Var (Sürpriz Skor: İlk Yarı 3-1)"),
        '1522': ("Sahte Kısır 12 (Şov Patlaması Tuzağı)", "2.5 Gol Üst veya Karşılıklı Gol Var (Sürpriz Skor: 3-2 / 4-2)"),
        '1521': ("Hayalet Barem (Sahte Düello Tuzağı)", "Karşılıklı Gol Yok (Sürpriz Skor: 0-3 / 3-0)"),
        '1518': ("Gizli Düello (Alt/KG Yok İllüzyonu)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 3-1 / 1-2)"),
        '1517': ("Matematiksel KG Var Paradoksu", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 2-1)"),
        'T70': ("Süper Kısır Çift Tuzağı (0-0 / 1-1)", "Beraberlik (0) + 2.5 Alt (Sürpriz Skor: 0-0 / 1-1)"),
        'G13': ("Her İki Yarıda Da Karşılıklı Gol (İYKG)", "1. Yarı KG Var & 2. Yarı KG Var (Sürpriz Skor: 2-2 / 3-3)"),
        '1516': ("Sahte Deplasman Golü Tuzağı (Ev Sahibi Katliamı)", "MS 1 + Karşılıklı Gol Yok (Sürpriz Skor: 3-0 / 4-0 / 6-0)"),
        '1515': ("Sahte Ev Sahibi Golü Tuzağı (Deplasman Katliamı)", "MS 2 + Karşılıklı Gol Yok (Sürpriz Skor: 0-3 / 0-4)"),
        '1480': ("Tek Skor Darboğazı Tuzağı (Ev Sahibi Sürprizi)", "1X Çifte Şans + 2.5 Gol Altı (Sürpriz Skor: 1-0 / 2-0)"),
        '1484': ("Aşırı Şişirilmiş Favori Alt Tuzağı", "MS 1 + 2.5 Gol Altı (Sürpriz Skor: 1-0 / 2-0)"),
        '1485': ("Ölü Alt Tuzağı (Gizli Düello)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 1-2 / 2-2)"),
        '1491': ("Dengeli Maçlarda Gerçek Düello", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 2-2)"),
        '1493': ("Çıplak Kral Tuzağı (02 Çifte Şans)", "X2 Çifte Şans + Karşılıklı Gol Yok (Sürpriz Skor: 0-1)"),
        '1472': ("Görünür Kısır Maç, Gizli Deplasman Şovu (0.5 Üst Çelişkisi)", "Maç Sonucu 2 ve 2.5 Üst (Sürpriz: 0-3 / 0-4)"),
        '1497': ("Ölümcül Sessizlik Tuzağı (0-0 Yemi)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 0-0)"),
        '1498': ("Sahte Banko Gol Tuzağı (Kısır Maç)", "2.5 Gol Altı + Karşılıklı Gol Yok (Sürpriz Skor: 1-0 / 0-1)"),
        '1511': ("Beraberliksiz Gol Düellosu İllüzyonu", "12 Çifte Şans + 2.5 Gol Üstü (Sürpriz Skor: 3-2 / 2-1)"),
        '1476': ("Uyuyan Dev (İkinci Yarı Düello Patlaması)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 1-2 / 2-1)"),
        '1465': ("Uluslararası Ev Favorisi Tuzağı", "X2 Çifte Şans + 2.5 Gol Altı (Sürpriz Skor: 0-1)"),
        '1464': ("Hafif Ev Üstünlüğü (Gollü, 3-1)", "MS 1 + 2.5 Gol Üst (Sürpriz Skor: 3-1)"),
        '1466': ("Yakınsak Sürpriz Oran (Favori Çöküşü 1-2)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2)"),
        '1474': ("Enflasyon Tuzağı (Favori ve Beraberlik Eşitliği)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 0-0 / 1-1)"),
        '1463': ("Tamamen Dengeli Beraberlik (0-0)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 0-0)"),
        '1475': ("Yalancı İmparator Tuzağı (1.0X Favori Çöküşü)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-1 / 1-2)"),
        '1473': ("Çapraz Sürpriz Düellosu (2-2 Tuzağı)", "Maç Sonucu 0 + 2.5 Gol Üst (Sürpriz Skor: 2-2)"),
        '1558': ("Matematiksel Paradoks (Sahte Favori Çöküşü 1-2/1-3)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2 / 1-3)"),
        '1467': ("Dengeli Kısır Çelişki (0-0)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 0-0)"),
    '1467B': ("Gollü Beraberlik Tuzağı (2-2 / 3-3)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 2-2 veya 3-3)"),
    '1485': ("Sahte Düello Tuzağı (1-0 Kilitlenmesi)", "Maç Sonucu 1 veya 0 + 2.5 Gol Altı (Sürpriz Skor: 1-0 veya 0-0)"),
    'T70': ("Sahte Ağır Favori (Düşük Beraberlik Tuzağı)", "Çifte Şans X2 veya Maç Sonucu 0 (Sürpriz Skor: 0-1 veya 1-1)"),
        '1462': ("Belirgin Ev Üstünlüğü (İlk Yarı Kapalı, 1-0)", "MS 1 + 2.5 Gol Altı (Sürpriz Skor: 1-0)"),

        '2001': ("2.5 Gol Altı (Milli Maç Kısırlığı)", "2.5 Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0 / 1-1 / 1-0)"),
        '2002': ("Maç Sonucu 1/2 (Milli Maç Fark Patlaması)", "Favori Kazanır + 3.5 Gol Üst (Sürpriz Skor: 4-0 / 5-0)"),
        '1514': ("Kısır Maç (Buzul Sessizliği Tuzağı)", "2.5 Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0 / 1-0)"),
        '1481': ("Sürpriz Deplasman Galibiyeti (MS 2) veya 02 Çifte Şans", "02 Çifte Şans + 2.5 Gol Üst (Sürpriz Skor: 1-3 / 2-2)"),
        '1482': ("Karşılıklı Gol Yok (Ağır Favori Sahte KG Var Tuzağı)", "KG Yok + Maç Sonucu 2 (Sürpriz Skor: 0-2 / 0-3)"),
        '1469': ("Aşırı Düşük Beraberlik (Kısır Favori)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 1-1 / 0-0)"),
        '1483': ("Gol Düellosu (Alt/Üst Paradoksu - Kısır Maç Yalanı)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)"),
        '1486': ("Kilitli Kısır Maç (Sıfır Risk)", "2.5 Gol Altı veya KG Yok (Sürpriz: Toplam Gol 0-1)"),
        '1487': ("Gol Düellosu (İlk Yarı Uyku Tuzağı Patlaması)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)"),
        '1488': ("Maç Sonucu 1 (Fark Patlaması)", "MS 1 + 3.5 Gol Üstü (veya Handikaplı MS 1)"),
        '1489': ("Kısır Maç (Favori Yem Tuzağı)", "Karşılıklı Gol Yok + 2.5 Gol Altı"),
        '1490': ("Sürpriz Deplasman Puanı (Favori Çöküşü)", "X2 Çifte Şans + Karşılıklı Gol Var (veya Üst)"),
        '1492': ("Maç Sonucu 1 (KG Yok)", "MS 1 + Karşılıklı Gol Yok"),
        '1494': ("Gol Düellosu (Ev Sahibi Sürprizi)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 1X Çifte Şans)"),
        '1496': ("Maç Sonucu 1 veya 2 (Beraberlik İmkansız, Tek Taraflı Şov)", "Karşılıklı Gol Yok + 2.5 Gol Üst (Sürpriz Skor: 0-3 / 3-0)"),
        '1499': ("Deplasman Çifte Şans (Favori Kilitlenir)", "X2 Çifte Şans + Ev Sahibi 1.5 Alt (Sürpriz Skor: 0-2 / 1-1)"),
        '1501': ("Maç Sonucu 0 (Kilitlenmiş Kısır Maç)", "2.5 Gol Altı + Karşılıklı Gol Yok (Sürpriz Skor: 0-0)"),
        '1502': ("Handikaplı MS 1 (Tek Taraflı Ev Şovu)", "MS 1 + 2.5 Gol Üst (Sürpriz Skor: 3-0)"),
        '1504': ("Sürpriz Deplasman Galibiyeti (Favori Katliamı)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-3)"),
        '1506': ("Maç Sonucu 1 (Tek Taraflı Şov)", "MS 1 + Karşılıklı Gol Yok (Sürpriz Skor: 4-0)"),
        '1510': ("3.5 Gol Üst (Gol Şovu Tuzağı)", "MS 1 + 3.5 Gol Üst (Sürpriz Skor: 3-1 / 4-1)"),
        '1509': ("Deplasman Çifte Şans (02) veya Beraberlik", "02 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2 / 1-3)"),
        '1508': ("Deplasman Gol Paradoksu (Deplasman Kesin Atar)", "Deplasman 0.5 Üst Banko / KG Var"),
        '1507': ("Deplasman Çifte Şans (Sahte Favori)", "X2 Çifte Şans + 2.5 Gol Altı (Sürpriz Skor: 0-0)"),
        '1505': ("Maç Sonucu 2 (Sahte Beraberlik)", "MS 2 + 2.5 Gol Altı (Sürpriz Skor: 0-2)"),
        '1503': ("Sürpriz Deplasman Galibiyeti (Sahte Düello)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2)"),
        '1500': ("X2 Çifte Şans (Sahte Ev Sahibi)", "02 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-1 / 1-2)"),
        '1512A': ("Gol Düellosu (Gizli Barem - Şov Patlaması)", "3.5 Gol Üst + Karşılıklı Gol Var"),
        '1512B': ("Gizli Barem (Alt Tuzağı)", "2.5 Gol Altı (Sürpriz Skor: 1-0 / 2-0)"),
        '1513': ("Handikaplı Deplasman Yemi (Zayıf Ev Sahibi)", "MS 1 (veya 1X) + 2.5 Alt"),
        '1479': ("Favori Gol Kısırlığı Tuzağı (X2/MS2)", "Deplasman Puan Alır (02 ÇŞ) veya MS2"),
        '1478': ("Deplasman Baskını (Ev Sahibi Tıkanması)", "02 Çifte Şans + Karşılıklı Gol Yok (veya 2.5 Alt)"),
        '1477': ("Sahte Fark İllüzyonu (Matematiksel Paradoks)", "Karşılıklı Gol Var (Sürpriz Skor: 2-1 / 1-1 / 1-2)"),
        '1470': ("Kısır Maç", "2.5 Alt + KG Yok"),
        'T68': ("Görünür Favori Tuzağı", "Favorinin Karşısındaki Taraf Kaybetmez + 2.5 Alt"),
        '1495': ("Karşılıklı Gol Var", "KG Var + 2.5 Gol Üst (Sürpriz Skor: 1-2)"),
        'T27': ("Az Gollü Temiz Favori", "MS 1 + 2.5 Gol Altı (Sürpriz Skor: 1-0 / 2-0)"),
        'T28': ("Az Gollü Temiz Favori (Deplasman)", "MS 2 + 2.5 Gol Altı (Sürpriz Skor: 0-1 / 0-2)"),
        'T32': ("Ev Sahibi Sürpriz Galibiyeti (MS 1)", "MS 1 + 2.5 Gol Üst (Sürpriz Skor: 2-1 / 3-1)"),
        'T33': ("Deplasman Sürprizi (02 Çifte Şans)", "MS 2 (veya 02) + Karşılıklı Gol Var"),
        'T34': ("Sürpriz Beraberlik (Süper Beraberlik Kuralı)", "Maç Sonucu 0 + Karşılıklı Gol Var (Sürpriz Skor: 2-2)"),
        'T35': ("Sahte Çifte Şans 12 İllüzyonu", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 0-0 / 1-1)"),
        'T36': ("Maç Sonucu 0 (Sahte Denge - Derin Denge)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 1-1)"),
        '1519': ("Kısır Maç (3.5 Alt Şovmen Tuzağı)", "3.5 Gol Altı + Sürpriz Beraberlik (Sürpriz Skor: 0-0 / 1-0)"),
        '1520': ("Kısır Maç (Sahte Şölen Tuzağı)", "2.5 Gol Altı + Kısır Maç (Sürpriz Skor: 0-0 / 1-1)"),
        'T38': ("Beraberlik", "Maç Sonucu 0 + Karşılıklı Gol Var"),
        'T39': ("Maç Sonucu 2", "MS 2 + Karşılıklı Gol Yok"),
        'G10': ("Maç Sonucu 0 veya 2.5 Gol Altı (Yalancı Üst Tuzağı)", "2.5 Gol Altı + Karşılıklı Gol Yok (Sürpriz Skor: 0-0)"),
        'G2': ("Karşılıklı Gol Yok (Sahte KG Var Tuzağı)", "KG Yok + 2.5 Gol Altı (Sürpriz Skor: 2-0 veya 0-2)"),
        'G1': ("Kesin 2 Gol Sinyali (Piyasa Yanılgısı)", "1.5 Gol Üst veya 2.5 Gol Üst (Şov İhtimali: 3-0 veya 0-3)"),
        'G4': ("2.5 Gol Altı (Aşırı Şişirilmiş Üst Tuzağı)", "2.5 Gol Altı + İlk Yarı 1.5 Alt"),
        'G5': ("Kısır Maç Beklentisi (2.5 Alt)", "2.5 Gol Altı (Sürpriz Skor: 1-0 / 0-1 / 0-0)"),
        'G5-B': ("Kısır Maç Beklentisi (2.5 Alt)", "2.5 Gol Altı (Sürpriz Skor: 1-0 / 0-1 / 0-0)"),
        'G6': ("Gol Düellosu veya Tek Taraflı Şov (Beraberlik Tuzağı)", "Çifte Şans 12 + 2.5 Gol Üst (Sürpriz Skor: 3-1 / 1-3)"),
        'G7': ("Karşılıklı Gol Var", "KG Var + MS 1 veya 2"),
        'G8': ("Gol Patlaması (Süper Üst Senaryosu)", "3.5 Gol Üst + Karşılıklı Gol Var (Sürpriz Skor: 2-2 / 3-2)"),
        'G11': ("Gol Düellosu (Alt/Üst Uyuşmazlığı)", "Karşılıklı Gol Var + 2.5 Gol Üst"),
        'G12': ("Deplasman Sürprizi + Gollü Maç", "X2 Çifte Şans + 2.5 Gol Üst"),
        'Y11': ("İlk Yarı Kilitlenmesi (Psikolojik 12 Tuzağı)", "İlk Yarı 0 VEYA İlk Yarı 1.5 Alt (Sürpriz Skor: 0-0 / 1-1)"),
        '1530': ("0-0 Tuzağı VEYA İlk Yarı Kesin Gol", "Tuzak varsa: 2.5 Alt / Yoksa: İlk Yarı 0.5 Üst"),
        '1530B': ("1530 Çifte Tuzağı (Ölümcül Kısır 0-0)", "2.5 Gol Altı veya İlk Yarı 0 / Maç Sonucu 0"),
        '1558': ("Aşırı Şişirilmiş Üst Tuzağı (Kısır Maç)", "2.5 Gol Altı (Sürpriz Skor: 0-0 / 1-0)")
    }
    
    # 1. DOMİNANT KURALI BUL
    dominant_tahmin = None
    for r in triggered_rules: # triggered_rules is already sorted by Phase 1 -> 5
        # Lig veya profil kuralları dominant olmamalı
        if r['code'].startswith('LIG') or r['code'] in ['2001', '2002', '999']:
            continue
            
        if r['code'] in predictions:
            ana_tahmin, kombine_tahmin = predictions[r['code']]
            dominant_tahmin = (r['code'], ana_tahmin, kombine_tahmin)
            break
        else:
            # Kural predictions listesinde yoksa adını kullan
            dominant_tahmin = (r['code'], r['name'], "Kural detayına bakınız (Kombine için açıklamayı okuyun)")
            break
            
    if dominant_tahmin:
        code, ana, kombine = dominant_tahmin
        output.append(f"- 👑 **DOMİNANT KURAL ({code}):** Makine, tespit edilen anomaliler arasındaki en yüksek hiyerarşiye sahip kuralı baz almıştır.")
        output.append(f"- **Ana Tahmin:** {ana}")
        output.append(f"- **Kombine Öneri:** {kombine}")
    elif any(r['code'] == '1482' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 veya 1X Çifte Şans (Sahte Düello)")
        output.append(f"- **Kombine Öneri:** 1X Çifte Şans + 2.5 Gol Altı (veya KG Yok)")
    elif any(r['code'] == '1483' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (Net 1-0 Beklentisi)")
        output.append(f"- **Kombine Öneri:** MS 1 + 2.5 Gol Altı")
    elif any(r['code'] == '1484' for r in triggered_rules):
        output.append(f"- **Ana Tahmin:** 2.5 Gol Altı veya 3.5 Gol Altı (Şişirilmiş Favori)")
        output.append(f"- **Kombine Öneri:** MS 1 + 3.5 Gol Altı (Sürpriz: MS 1 + 2.5 Alt)")
    elif is_massive_duel:
        output.append(f"- **Ana Tahmin:** Mükemmel Gol Düellosu (Karşılıklı Gol Var)")
        output.append(f"- **Kombine Öneri:** KG Var + 2.5 Gol Üst (Riskli: 3.5 Üst)")
    elif ms1 != 99.0 and ms2 != 99.0 and ms1 < ms2:
        if gol_beklentisi == "YÜKSEK":
            output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (veya 1X) + 1.5 Gol Üstü")
            output.append(f"- **Kombine Öneri:** MS 1 + 2.5 Gol Üst (Sürpriz: 2-1)")
        else:
            output.append(f"- **Ana Tahmin:** 1X Çifte Şans + 3.5 Gol Altı")
            output.append(f"- **Kombine Öneri:** Maç Sonucu 1 + 2.5 Gol Altı (Sürpriz: 1-0)")
    elif ms1 != 99.0 and ms2 != 99.0 and ms2 < ms1:
        if gol_beklentisi == "YÜKSEK":
            output.append(f"- **Ana Tahmin:** Maç Sonucu 2 (veya 02) + 1.5 Gol Üstü")
            output.append(f"- **Kombine Öneri:** MS 2 + 2.5 Gol Üst (Sürpriz: 1-2)")
        else:
            output.append(f"- **Ana Tahmin:** 02 Çifte Şans + 3.5 Gol Altı")
            output.append(f"- **Kombine Öneri:** Maç Sonucu 2 + 2.5 Gol Altı (Sürpriz: 0-1)")
    else:
        output.append(f"- **Ana Tahmin:** Taraf bahsi çok riskli, gol bahisleri (KG Var/Yok veya Alt/Üst) tercih edilmeli.")
        if gol_beklentisi == "YÜKSEK":
            output.append(f"- **Kombine Öneri:** Karşılıklı Gol Var veya 2.5 Gol Üst (Sürpriz: 2-2)")
        else:
            output.append(f"- **Kombine Öneri:** Karşılıklı Gol Yok veya 2.5 Gol Alt (Sürpriz: 1.5 Alt)")

    return "\\n".join(output)
