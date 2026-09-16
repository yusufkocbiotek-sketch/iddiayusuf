import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    content = f.read()

# 1. Add Scores
score_injection = r"""    output.append(f"- **Tek/Çift:** Tek **{tek}** | Çift **{cift}**")
    output.append(f"---")
    
    ilk_yari_skoru = match.get("ilk_yari_skoru", "?-?")
    mac_skoru = match.get("mac_sonucu", "?-?")
    if ilk_yari_skoru != "?-?" or mac_skoru != "?-?":
        output.append(f"\n> 🏆 **GERÇEKLEŞEN SKOR:** İlk Yarı **{ilk_yari_skoru}** | Maç Sonucu **{mac_skoru}**\n")
"""
content = re.sub(r'    output\.append\(f"- \*\*Tek/Çift:\*\* Tek \*\*{tek}\*\* \| Çift \*\*{cift}\*\*"\)\s*output\.append\(f"---"\)', score_injection, content)

# 2. Dynamic Yön Uyarısı
yon_old = r"""    if any\(r\['code'\] in \['T32', 'T35', 'T9', '1470', '1478', '1479', '1480', '1481', '1482', '1483', '1484', '1485', 'G6'\] for r in triggered_rules\):
        output\.append\("- \*\*⚠️ YÖN UYARISI:\*\* Klasik MS bahisleri yanıltıcıdır! Makine gizli bir tuzak veya paradoks tespit etti\."\)
        output\.append\("- \*\*Alternatif Yön:\*\* Sistemin Ana Tahmin kısmındaki önerisine sadık kalın\."\)"""

yon_new = r"""    has_anomaly = any(r['code'].startswith('1') or r['code'].startswith('2') for r in triggered_rules)
    if has_anomaly or any(r['code'] in ['T32', 'T35', 'T9', 'G6', 'G10'] for r in triggered_rules):
        output.append("- **⚠️ YÖN UYARISI:** Klasik MS bahisleri yanıltıcıdır! Makine gizli bir tuzak veya paradoks tespit etti.")
        output.append("- **Alternatif Yön:** Sistemin Ana Tahmin kısmındaki DOMİNANT öneriye sadık kalın.")"""

content = re.sub(yon_old, yon_new, content)

# 3. Dominant Prediction Replace
old_pred_start = r'    output\.append\(f"\\n### 💎 KOMBİNE & TAHMİN ÖNERİLERİ"\)'
parts = content.split('    output.append(f"\\n### 💎 KOMBİNE & TAHMİN ÖNERİLERİ")')

new_pred = r"""    output.append(f"\n### 💎 KOMBİNE & TAHMİN ÖNERİLERİ")
    
    # Prediction Dictionary
    predictions = {
        '2001': ("2.5 Gol Altı (Milli Maç Kısırlığı)", "2.5 Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0 / 1-1 / 1-0)"),
        '2002': ("Maç Sonucu 1/2 (Milli Maç Fark Patlaması)", "Favori Kazanır + 3.5 Gol Üst (Sürpriz Skor: 4-0 / 5-0)"),
        '1514': ("Kısır Maç (Buzul Sessizliği Tuzağı)", "2.5 Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0 / 1-0)"),
        '1481': ("Sürpriz Deplasman Galibiyeti (MS 2) veya 02 Çifte Şans", "02 Çifte Şans + 2.5 Gol Üst (Sürpriz Skor: 1-3 / 2-2)"),
        '1482': ("Karşılıklı Gol Yok (Ağır Favori Sahte KG Var Tuzağı)", "KG Yok + Maç Sonucu 2 (Sürpriz Skor: 0-2 / 0-3)"),
        '1469': ("Gol Düellosu (Asya Tuzağı)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)"),
        '1483': ("Gol Düellosu (Alt/Üst Paradoksu - Kısır Maç Yalanı)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)"),
        '1486': ("Gol Düellosu (Kısır Beraberlik Tuzağı Kırıldı)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)"),
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
        '1508': ("Deplasman Çifte Şans (02) veya Beraberlik", "02 Çifte Şans + Deplasman 0.5 Gol Üstü (Sürpriz Skor: 1-1)"),
        '1507': ("Deplasman Çifte Şans (Sahte Favori)", "X2 Çifte Şans + 2.5 Gol Altı (Sürpriz Skor: 0-0)"),
        '1505': ("Maç Sonucu 2 (Sahte Beraberlik)", "MS 2 + 2.5 Gol Altı (Sürpriz Skor: 0-2)"),
        '1503': ("Sürpriz Deplasman Galibiyeti (Sahte Düello)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2)"),
        '1500': ("X2 Çifte Şans (Sahte Ev Sahibi)", "02 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-1 / 1-2)"),
        '1512': ("Ev Sahibi Puan Kaybı (X2 ÇŞ)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2 / 2-2)"),
        '1513': ("Ev Sahibi Kaybetmez (1X ÇŞ)", "1X Çifte Şans + 2.5 Gol Altı (Sürpriz Skor: 1-1 / 1-0)"),
        '1479': ("Gol Düellosu (Altın Çelişki)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)"),
        '1478': ("Sürpriz Deplasman Galibiyeti (Sahte Favori)", "02 Çifte Şans + Karşılıklı Gol Var"),
        '1477': ("Beraberlik (Sahte Fark İllüzyonu)", "MS 0 + KG Var (Sürpriz: 1-1 / 2-2)"),
        '1470': ("Kısır Maç", "2.5 Alt + KG Yok"),
        'T68': ("Beraberlik İptali (Sürpriz Taraf Kazanır)", "Çifte Şans 12 + 2.5 Gol Altı"),
        '1495': ("Karşılıklı Gol Var", "KG Var + 2.5 Gol Üst (Sürpriz Skor: 1-2)"),
        'T27': ("Sürpriz Deplasman Puanı (X2 Çifte Şans)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-1 / 1-2)"),
        'T32': ("Ev Sahibi Sürpriz Galibiyeti (MS 1)", "MS 1 + 2.5 Gol Üst (Sürpriz Skor: 2-1 / 3-1)"),
        'T33': ("Deplasman Sürprizi (02 Çifte Şans)", "MS 2 (veya 02) + Karşılıklı Gol Var"),
        'T34': ("Sürpriz Beraberlik (Süper Beraberlik Kuralı)", "Maç Sonucu 0 + Karşılıklı Gol Var (Sürpriz Skor: 2-2)"),
        'T35': ("Beraberlik Tuzağı (Favori Kazanır veya Ev Sahibi Sürprizi)", "MS 1 veya 2 + Karşılıklı Gol Yok"),
        'T36': ("Maç Sonucu 0 (Sahte Denge - Derin Denge)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 1-1)"),
        'T37': ("Ev Sahibi Çifte Şans (1X)", "1X Çifte Şans + Karşılıklı Gol Yok"),
        'T38': ("Beraberlik", "Maç Sonucu 0 + Karşılıklı Gol Var"),
        'T39': ("Maç Sonucu 2", "MS 2 + Karşılıklı Gol Yok"),
        'G10': ("Maç Sonucu 0 veya 2.5 Gol Altı (Yalancı Üst Tuzağı)", "2.5 Gol Altı + Karşılıklı Gol Yok (Sürpriz Skor: 0-0)"),
        'G2': ("Karşılıklı Gol Yok (Sahte KG Var Tuzağı)", "KG Yok + 2.5 Gol Altı (Sürpriz Skor: 2-0 veya 0-2)"),
        'G1': ("Karşılıklı Gol Var (Sahte KG Yok Tuzağı)", "KG Var + 2.5 Gol Üst (Sürpriz Skor: 2-1 veya 1-2)"),
        'G4': ("2.5 Gol Altı (Aşırı Şişirilmiş Üst Tuzağı)", "2.5 Gol Altı + İlk Yarı 1.5 Alt"),
        'G5': ("Kısır Beraberlik (Maç Sonucu 0)", "Maç Sonucu 0 + 2.5 Alt (Sürpriz Skor: 1-1 / 0-0)"),
        'G5-B': ("Kısır Beraberlik (Maç Sonucu 0)", "Maç Sonucu 0 + 2.5 Alt (Sürpriz Skor: 1-1 / 0-0)"),
        'G6': ("Gol Düellosu veya Tek Taraflı Şov (Beraberlik Tuzağı)", "Çifte Şans 12 + 2.5 Gol Üst (Sürpriz Skor: 3-1 / 1-3)"),
        'G7': ("Karşılıklı Gol Var", "KG Var + MS 1 veya 2"),
        'G8': ("Gol Patlaması (Süper Üst Senaryosu)", "3.5 Gol Üst + Karşılıklı Gol Var (Sürpriz Skor: 2-2 / 3-2)"),
        'G11': ("Gol Düellosu (Alt/Üst Uyuşmazlığı)", "Karşılıklı Gol Var + 2.5 Gol Üst"),
        'G12': ("Deplasman Sürprizi + Gollü Maç", "X2 Çifte Şans + 2.5 Gol Üst")
    }
    
    # 1. DOMİNANT KURALI BUL
    dominant_tahmin = None
    for r in triggered_rules: # triggered_rules is already sorted by Phase 1 -> 5
        if r['code'] in predictions:
            ana_tahmin, kombine_tahmin = predictions[r['code']]
            dominant_tahmin = (r['code'], ana_tahmin, kombine_tahmin)
            break
            
    if dominant_tahmin:
        code, ana, kombine = dominant_tahmin
        output.append(f"- 👑 **DOMİNANT KURAL ({code}):** Makine, tespit edilen anomaliler arasındaki en yüksek hiyerarşiye sahip kuralı baz almıştır.")
        output.append(f"- **Ana Tahmin:** {ana}")
        output.append(f"- **Kombine Öneri:** {kombine}")
    elif is_massive_duel:
        output.append(f"- **Ana Tahmin:** Mükemmel Gol Düellosu (Karşılıklı Gol Var)")
        output.append(f"- **Kombine Öneri:** KG Var + 2.5 Gol Üst (Riskli: 3.5 Üst)")
    elif ms1 < ms2:
        if gol_beklentisi == "YÜKSEK":
            output.append(f"- **Ana Tahmin:** Maç Sonucu 1 (veya 1X) + 1.5 Gol Üstü")
            output.append(f"- **Kombine Öneri:** MS 1 + 2.5 Gol Üst (Sürpriz: 2-1)")
        else:
            output.append(f"- **Ana Tahmin:** 1X Çifte Şans + 3.5 Gol Altı")
            output.append(f"- **Kombine Öneri:** Maç Sonucu 1 + 2.5 Gol Altı (Sürpriz: 1-0)")
    elif ms2 < ms1:
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
"""

new_content = parts[0] + new_pred
with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf-8') as f:
    f.write(new_content)

print("Applied!")
