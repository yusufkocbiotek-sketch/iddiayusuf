import json
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("\n" + "="*50)
for idx in range(-381, -391, -1):
    m = data['matches'][idx]
    skor_ev = m.get('skor_ev', '?')
    skor_dep = m.get('skor_dep', '?')
    skor_iy_ev = m.get('skor_1y_ev', '?')
    skor_iy_dep = m.get('skor_1y_dep', '?')
    
    print(f"📌 İndex: {idx} | {m['ev_sahibi']} - {m['deplasman']}")
    print(f"💥 GERÇEK SKOR: {skor_ev} - {skor_dep} (İlk Yarı: {skor_iy_ev} - {skor_iy_dep})")
    
    story = generate_story(m, verbose=False)
    
    # Extract prediction parts to see how it did
    lines = story.split('\n')
    for line in lines:
        if line.startswith('### ⏱️ ZAMANLAMA') or line.startswith('- ⚡') or line.startswith('- ⚔️') or line.startswith('- 🔥') or line.startswith('- 🔒') or line.startswith('- 🛡️') or line.startswith('- ⚖️') or line.startswith('- 🏠') or line.startswith('- ✈️') or line.startswith('- 📉'):
            print(line)
        if line.startswith('### 💎 KOMBİNE') or line.startswith('- **Ana Tahmin:**') or line.startswith('- **Kombine Öneri:**'):
            print(line)
    
    print("\n---\n")
    print("## 🧠 ÖĞRENME MOTORU GERİ BİLDİRİMİ (SELF-EVALUATION)")
    print(f"**Gerçekleşen Skor:** {skor_ev} - {skor_dep}")
    
    taraf_tahmini = "Belirsiz"
    gol_tahmini = "Belirsiz"
    
    # Very basic self-eval string matching
    if skor_ev != '?' and skor_dep != '?':
        ev, dep = int(skor_ev), int(skor_dep)
        toplam = ev + dep
        kg = (ev > 0 and dep > 0)
        
        if "Maç Sonucu 1" in story:
            taraf_tahmini = "✅ BAŞARILI (Ev Sahibi Kazandı)" if ev > dep else "❌ ÇUVALLADI (Taraf Yattı)"
        elif "Maç Sonucu 2" in story or "02 Çifte Şans" in story or "X2 Çifte Şans" in story:
            taraf_tahmini = "✅ BAŞARILI (Deplasman Yenilmedi)" if dep >= ev else "❌ ÇUVALLADI (Taraf Yattı)"
        elif "Maç Sonucu 0" in story or "1X Çifte Şans" in story:
            taraf_tahmini = "✅ BAŞARILI (Beraberlik/1X Geldi)" if ev >= dep else "❌ ÇUVALLADI (Taraf Yattı)"
            
        if "2.5 Gol Üst" in story or "3.5 Gol Üst" in story or "Gol Düellosu" in story:
            gol_tahmini = "✅ BAŞARILI (Üst Geldi)" if toplam >= 3 else "❌ ÇUVALLADI (Alt Bitti)"
        elif "2.5 Gol Alt" in story or "Kısır Maç" in story:
            gol_tahmini = "✅ BAŞARILI (Alt Geldi)" if toplam < 3 else "❌ ÇUVALLADI (Üst Bitti)"
            
        if "Karşılıklı Gol Var" in story and "KG Var" in story:
            if kg: gol_tahmini += " / ✅ KG VAR"
            else: gol_tahmini += " / ❌ KG YOK"
        elif "Karşılıklı Gol Yok" in story:
            if not kg: gol_tahmini += " / ✅ KG YOK"
            else: gol_tahmini += " / ❌ KG VAR"
            
    print(f"- **Taraf/Yön Tahmini:** {taraf_tahmini}")
    print(f"- **Gol/Senaryo Tahmini:** {gol_tahmini}")
    
    if "❌" in taraf_tahmini or "❌" in gol_tahmini:
        print("> 🚨 **ÖĞRENME MOTORU ALARMI:** Sistem bu maçta tuzağa düştü veya eksik bir kural var! Bu maçın alt oranlarına (0.5 Üst, İlk Yarı Oranları vb.) inilerek acil yeni kural (istisna) yazılmalıdır.")
    else:
        print("> 🟢 **MAKİNE KUSURSUZ:** Tüm yönlendirmeler ve tuzaklar doğru okundu.")
        
    print("\n" + "="*50)
