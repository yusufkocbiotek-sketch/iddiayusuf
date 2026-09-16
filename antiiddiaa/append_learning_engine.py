import codecs
import re

with codecs.open('story_analyzer.py', 'r', 'utf-8') as f:
    content = f.read()

eval_logic = '''
    # --- 🧠 ÖĞRENME MOTORU GERİ BİLDİRİMİ ---
    skor_ev = match.get('skor_ev')
    skor_dep = match.get('skor_dep')
    
    if skor_ev is not None and skor_dep is not None:
        skor_ev = int(skor_ev)
        skor_dep = int(skor_dep)
        
        actual_ms = 1 if skor_ev > skor_dep else (2 if skor_dep > skor_ev else 0)
        actual_kg = "Var" if (skor_ev > 0 and skor_dep > 0) else "Yok"
        actual_ust = (skor_ev + skor_dep) >= 3
        
        output.append("")
        output.append("---")
        output.append("")
        output.append("## 🧠 ÖĞRENME MOTORU GERİ BİLDİRİMİ (SELF-EVALUATION)")
        output.append(f"**Gerçekleşen Skor:** {skor_ev} - {skor_dep}")
        
        # Check Ana Tahmin / Yön
        ana_tahmin = output[-6] if len(output) > 6 else "" # Rough grab
        kombine = output[-5] if len(output) > 5 else ""
        
        full_prediction_text = "\\n".join(output[-10:]).lower()
        
        # Taraf Tahmini Değerlendirmesi
        taraf_sonuc = "Belirsiz"
        if "ms 1" in full_prediction_text or "ev sahibi" in full_prediction_text:
            if actual_ms == 1: taraf_sonuc = "✅ BAŞARILI (Ev Sahibi Kazandı)"
            else: taraf_sonuc = "❌ ÇUVALLADI (Yanlış Taraf)"
        elif "ms 2" in full_prediction_text or "deplasman" in full_prediction_text:
            if actual_ms == 2: taraf_sonuc = "✅ BAŞARILI (Deplasman Kazandı)"
            else: taraf_sonuc = "❌ ÇUVALLADI (Yanlış Taraf)"
        elif "ms 0" in full_prediction_text or "beraberlik" in full_prediction_text:
            if actual_ms == 0: taraf_sonuc = "✅ BAŞARILI (Beraberlik Doğru)"
            else: taraf_sonuc = "❌ ÇUVALLADI (Yanlış Taraf)"
            
        if "1x" in full_prediction_text:
            if actual_ms in [1, 0]: taraf_sonuc = "✅ BAŞARILI (1X Geldi)"
            else: taraf_sonuc = "❌ ÇUVALLADI (1X Yattı)"
        elif "x2" in full_prediction_text or "02" in full_prediction_text:
            if actual_ms in [0, 2]: taraf_sonuc = "✅ BAŞARILI (X2 Geldi)"
            else: taraf_sonuc = "❌ ÇUVALLADI (X2 Yattı)"
            
        # Gol Tahmini Değerlendirmesi
        gol_sonuc = "Belirsiz"
        if "karşılıklı gol var" in full_prediction_text or "kg var" in full_prediction_text:
            if actual_kg == "Var": gol_sonuc = "✅ BAŞARILI (KG Var Geldi)"
            else: gol_sonuc = "❌ ÇUVALLADI (KG Yok Bitti)"
        elif "karşılıklı gol yok" in full_prediction_text or "kg yok" in full_prediction_text:
            if actual_kg == "Yok": gol_sonuc = "✅ BAŞARILI (KG Yok Geldi)"
            else: gol_sonuc = "❌ ÇUVALLADI (KG Var Bitti)"
            
        if "2.5 gol üst" in full_prediction_text or "2.5 üst" in full_prediction_text:
            if actual_ust: gol_sonuc = "✅ BAŞARILI (Üst Geldi)"
            elif "❌" not in gol_sonuc: gol_sonuc = "❌ ÇUVALLADI (Alt Bitti)"
        elif "2.5 alt" in full_prediction_text:
            if not actual_ust: gol_sonuc = "✅ BAŞARILI (Alt Geldi)"
            elif "❌" not in gol_sonuc: gol_sonuc = "❌ ÇUVALLADI (Üst Bitti)"
            
        output.append(f"- **Taraf/Yön Tahmini:** {taraf_sonuc}")
        output.append(f"- **Gol/Senaryo Tahmini:** {gol_sonuc}")
        
        # Eger herhangi bir çuvallama varsa kırmizi bayrak
        if "❌" in taraf_sonuc or "❌" in gol_sonuc:
            output.append("> 🚨 **ÖĞRENME MOTORU ALARMI:** Sistem bu maçta tuzağa düştü veya eksik bir kural var! Bu maçın alt oranlarına (0.5 Üst, İlk Yarı Oranları vb.) inilerek acil yeni kural (istisna) yazılmalıdır.")
        else:
            output.append("> 🟢 **MAKİNE KUSURSUZ:** Tüm yönlendirmeler ve tuzaklar doğru okundu.")

    return "\\n".join(output)
'''

content = re.sub(r'return "\\n"\.join\(output\)', eval_logic.strip(), content, flags=re.DOTALL)

with codecs.open('story_analyzer.py', 'w', 'utf-8') as f:
    f.write(content)

print("Learning Engine Feedback added to story_analyzer.py")
