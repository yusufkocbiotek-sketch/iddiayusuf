import json

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

total = len(matches)

# ========== -571 ANALİZİ ==========
m571 = matches[total - 571]
o571 = m571.get('oranlar', {})
print('='*70)
print('IDX: -571 | Gardabaer vs Dalverik | Gercek: 0-0')
print()
print('G11 kuralı tetikledi → KG Var + 2.5 Üst önerdi → YANLIŞ (0-0)')
print()
print('G11 koşulları nelerdi?')
print('  KG Var:', o571.get('Karşılıklı Gol_Var'))      # 1.24 → ultra düşük
print('  KG Yok:', o571.get('Karşılıklı Gol_Yok'))      # 2.57
print('  MS2:', o571.get('Maç Sonucu_2'))                # 1.56 → güçlü dep
print('  MS1:', o571.get('Maç Sonucu_1'))                # 3.46
print()
print('Gözden kaçan sinyaller:')
for k, v in sorted(o571.items()):
    print('  ' + k + ' = ' + str(v))

print()
print('--- ANALIZ ---')
print('KG Var = 1.24 → Ultra düşük = Tuzak mı?')
print('Dep güçlü (1.56), ama IY Dep 0.5 Üst var mı?')
iy_dep = o571.get('Deplasman İlk Yarı Altı/Üstü 0.5_Üst', 99)
iy_ev = o571.get('Ev Sahibi İlk Yarı Altı/Üstü 0.5_Üst', 99)
print('  IY Dep 0.5 Ust:', iy_dep)
print('  IY Ev  0.5 Ust:', iy_ev)
dep35_alt = o571.get('Deplasman Alt/Üst 3.5_Alt', 99)
print('  Dep 3.5 Alt (dep 4+ gol atmaz):', dep35_alt)
print()

# Ultra düşük KG Var (1.22-1.24) + Güçlü dep + 0-0 bitmesi pattern
print('=== BENZER PATTERN TARAMA ===')
print('KG Var <= 1.25 + MS2 <= 1.60 + Skor 0-0')
found = []
for m in matches:
    o = m.get('oranlar', {})
    kg_var = o.get('Karşılıklı Gol_Var', 99)
    ms2 = o.get('Maç Sonucu_2', 99)
    sev = m.get('skor_ev', -1)
    sdep = m.get('skor_dep', -1)
    if kg_var <= 1.26 and ms2 <= 1.62 and sev >= 0:
        found.append({'kg_var': kg_var, 'ms2': ms2, 'skor': str(sev)+'-'+str(sdep),
                      'ev': m.get('ev_sahibi','?'), 'dep': m.get('deplasman','?'),
                      'idx': m.get('index','?')})

sifir_sifir = [x for x in found if x['skor']=='0-0']
gol_oldu = [x for x in found if x['skor']!='0-0']
print('Toplam:', len(found))
print('0-0 biten:', len(sifir_sifir), '%.1f%%' % (100*len(sifir_sifir)/len(found) if found else 0))
print('Gol olan:', len(gol_oldu), '%.1f%%' % (100*len(gol_oldu)/len(found) if found else 0))
print()
print('0-0 bitenler:')
for x in sifir_sifir[:10]:
    print('  #'+str(x['idx'])+' '+x['ev']+' vs '+x['dep']+' | KGVar='+str(x['kg_var'])+' MS2='+str(x['ms2']))

print()
print('='*70)
print('IDX: -574 | Lyn 1896 FK II vs Lillehammer | Gercek: IY 0-0 → MS 3-5')
print()
m574 = matches[total - 574]
o574 = m574.get('oranlar', {})
print('SİSTEM NE ÖNERDİ:')
print('  1515 kuralı → MS2 + KG Yok (Dep fark atar, 0-3/0-4)')
print('  AMAN: Dep = Lillehammer (MS2=1.06), Ev = Lyn II (MS1=10.15)')
print()
print('GERCEK: 3-5 → Ev 3 gol, Dep 5 gol → KG VAR + 8 gol!')
print()
print('HAYIR YANLIŞ DEĞİL Mİ?')
print('1515 dedi: Ev gol ATAMAZ, dep fark ATAR (0-3, 0-4)')
print('3-5 oldu → Ev 3 gol ATTı! 1515 YANLIŞ!')
print()
print('Oranlar tekrar:')
print('  MS2=', o574.get('Maç Sonucu_2'), '(1.06 = ultra)')
print('  KG Var=', o574.get('Karşılıklı Gol_Var'), '(1.38 = piyasa KG Var bekliyor)')
print('  KG Yok=', o574.get('Karşılıklı Gol_Yok'), '(2.13 = KG Var bekleniyor)')
print('  IY KG Var=', o574.get('İlk Yarı Karşılıklı Gol_Var'))
print('  IY KG Yok=', o574.get('İlk Yarı Karşılıklı Gol_Yok'))
print('  IY 1.5 Ust=', o574.get('İlk Yarı Alt/Üst 1.5_Üst'))
print('  Dep 3.5 Alt=', o574.get('Deplasman Alt/Üst 3.5_Alt'), '← Dep 4+ gol atar mı?')
print('  4.5 Alt=', o574.get('Alt/Üst 4.5_Alt'), '4.5 Ust=', o574.get('Alt/Üst 4.5_Üst'))
print()
print('SONUC: KG Var=1.38 (düşük) + IY 1.5 Üst=1.43 (gol yağacak)')
print('       Dep 3.5 Üst=1.91 (dep 4+ gol atar!)')
print("       IY KG Yok=1.19 AMA IY 1.5 Ust=1.43 (IY'de de gol var)")
print()
print('1515 KURALI HATASI: KG Var=1.38 < 1.50 iken KG Yok yerine KG Var oynamalıydı!')
print('1515 koşulu: KG Var <= 1.50 → ama bu maçta KG Var=1.38 GERCEK KG VAR DEMEKTİ!')
print()
print('KURAL REVIZYONU GEREKLİ:')
print('1515: KG Var <= 1.50 ve MS2 <= 1.50 → Sahte ev golü tuzağı')
print('AMA: IY 1.5 Üst <= 1.50 VE Dep 3.5 Üst <= 2.0 ise → KG VAR GERCEK!')
print('= Dep hem kazanır HEM GOL YAĞAR = KG Var + 3.5 Üst')
