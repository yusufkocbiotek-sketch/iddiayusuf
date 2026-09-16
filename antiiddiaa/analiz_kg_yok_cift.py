import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

# ==========================================================
# Karşılaştırma:
# HATALI (-563, -566): Ev 0.5 Üst = 1.34 / 99(yok), Dep 0.5 Üst = 1.47 / 1.54
# DOGRU  (-564, -567): Ev 0.5 Üst = 1.31 / 1.27, Dep 0.5 Üst = 1.48 / 1.54
#
# Çok yakın. Asıl fark:
# -563: Tek/Çift Çift = 1.54 (ÇIFT gol bekle = 2,4,6...)
#        1.5 Üst = 1.51 → Bu maçta 1.51 daha yüksek
# -564: 1.5 Üst = 1.49 daha düşük
#
# Fark çok küçük...
#
# Asıl ayrım şu olabilir:
# Dep Handikap 0:1 = 1.29 vs 1.33 → -563 daha favori dep
# CS12 = 1.31 vs 1.28 → benzer
#
# Başka ayrım dene: "Tek" oranı vs "Çift" oranı
# -563: Tek=1.84, Çift=1.54 → Çift fav = 2 veya 0 gol
# -564: Tek=1.79, Çift=1.57 → Çift fav ama fark daha az
# -567: Tek=1.78, Çift=1.59
#
# TEK/ÇİFT ayırımı → KG Yok + Çift gol sayısı = 0 veya 2!
# Eğer Çift favori ve KG Yok = 0 gol (kısır) veya 2 gol (açık)
# Ama 2 gol = KG Var OLMADAN DA olabilir → tek taraflı (2-0)
#
# GERÇEK FARKI BUL: Tek / Çift Çift ile 1.5 Üst arasındaki ilişki
# ==========================================================

print('=== DERINLEMESINE KARŞILAŞTIRMA ===')
print()
print('Kritik metrik: TEK/ÇIFT_Çift ve 1.5 Üst ilişkisi')
print()

for idx, label in [(563, 'HATALI-563'), (566, 'HATALI-566'), (564, 'DOGRU-564'), (567, 'DOGRU-567'), (565, 'BERAB-565')]:
    m = matches[len(matches) - idx]
    o = m.get('oranlar', {})
    ust15 = o.get('Alt/Üst 1.5_Üst', 99)
    alt15 = o.get('Alt/Üst 1.5_Alt', 99)
    tek = o.get('Tek / Çift_Tek', 99)
    cift = o.get('Tek / Çift_Çift', 99)
    kg_var = o.get('Karşılıklı Gol_Var', 99)
    kg_yok = o.get('Karşılıklı Gol_Yok', 99)
    ms1 = o.get('Maç Sonucu_1', 99)
    ms0 = o.get('Maç Sonucu_0', 99)
    ms2 = o.get('Maç Sonucu_2', 99)
    # ÇİFT oranı düşükse → 0 veya 2 gol expected
    # Eğer KG Yok da favori → 0 gol bekleniyor
    # Ama 1.5 Üst < 1.55 → 2+ gol da bekleniyor
    # Bu çelişki = ANA GOSTERGE
    cift_minus_ust15 = round(cift - ust15, 3)
    skor = str(m.get('skor_ev')) + '-' + str(m.get('skor_dep'))
    print(label + ' | Skor: ' + skor)
    print('  KGYok=' + str(kg_yok) + ' KGVar=' + str(kg_var))
    print('  1.5Ust=' + str(ust15) + ' 1.5Alt=' + str(alt15))
    print('  Tek=' + str(tek) + ' Cift=' + str(cift) + ' (Cift-1.5Ust fark: ' + str(cift_minus_ust15) + ')')
    print('  MS: ' + str(ms1) + '/' + str(ms0) + '/' + str(ms2))
    print()

# İstatistik: KGVar>=2.0, KGYok<=1.42, 1.5Ust<=1.55
# Şimdi Tek/Çift Çift <= 1.55 olanlar vs > 1.55 olanlar
print('=== İSTATİSTİK: Çift <= 1.55 vs > 1.55 ===')
alt_cift = []  # Çift oranı <= 1.55 → "çift gol sayısı daha olası"
ust_cift = []  # Çift oranı > 1.55

for m in matches:
    o = m.get('oranlar', {})
    kg_var = o.get('Karşılıklı Gol_Var', 99)
    kg_yok = o.get('Karşılıklı Gol_Yok', 99)
    ust15 = o.get('Alt/Üst 1.5_Üst', 99)
    cift = o.get('Tek / Çift_Çift', 99)
    skor_ev = m.get('skor_ev', -1)
    skor_dep = m.get('skor_dep', -1)

    if kg_var >= 2.0 and kg_yok <= 1.42 and ust15 <= 1.55 and ust15 != 99 and cift != 99 and skor_ev >= 0:
        total = skor_ev + skor_dep
        rec = {'total': total, 'cift': cift, 'ust15': ust15}
        if cift <= 1.56:
            alt_cift.append(rec)
        else:
            ust_cift.append(rec)

def stats(lst, label):
    if not lst: return
    gol2p = [x for x in lst if x['total'] >= 2]
    kisir = [x for x in lst if x['total'] <= 1]
    print(label + ': ' + str(len(lst)) + ' mac')
    print('  2+ gol: ' + str(len(gol2p)) + ' (%.1f%%)' % (100*len(gol2p)/len(lst)))
    print('  0-1 gol: ' + str(len(kisir)) + ' (%.1f%%)' % (100*len(kisir)/len(lst)))

stats(alt_cift, 'Cift <= 1.56 (cift gol sayisi daha olasi)')
stats(ust_cift, 'Cift > 1.56 (tek gol sayisi daha olasi / belirsiz)')
