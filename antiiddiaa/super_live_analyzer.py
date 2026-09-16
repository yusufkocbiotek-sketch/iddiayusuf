import json
import os

def check_combo_match(match, combo_template_str):
    o = match.get('oranlar', {})
    # Çok basit bir parser
    ms1 = o.get('Maç Sonucu_1', 99)
    ms2 = o.get('Maç Sonucu_2', 99)
    kgyok = o.get('Karşılıklı Gol_Yok', 99)
    kgvar = o.get('Karşılıklı Gol_Var', 0)
    alt = o.get('Alt/Üst 2.5_Alt', 99)
    ust = o.get('Alt/Üst 2.5_Üst', 0)
    iy0 = o.get('1. Yarı Sonucu_0', 99)
    iy1 = o.get('1. Yarı Sonucu_1', 99)
    iy2 = o.get('1. Yarı Sonucu_2', 99)
    
    conds_met = True
    if "MS1 Çok Ağır Fav (1.10-1.30)" in combo_template_str and not (1.10 <= ms1 <= 1.30): conds_met = False
    if "MS1 Ağır Fav (1.30-1.50)" in combo_template_str and not (1.30 <= ms1 <= 1.50): conds_met = False
    if "MS1 Fav (1.50-1.80)" in combo_template_str and not (1.50 <= ms1 <= 1.80): conds_met = False
    
    if "MS2 Çok Ağır Fav (1.10-1.30)" in combo_template_str and not (1.10 <= ms2 <= 1.30): conds_met = False
    if "MS2 Ağır Fav (1.30-1.50)" in combo_template_str and not (1.30 <= ms2 <= 1.50): conds_met = False
    if "MS2 Fav (1.50-1.80)" in combo_template_str and not (1.50 <= ms2 <= 1.80): conds_met = False
    
    if "KG VAR Favori" in combo_template_str and not (kgvar < kgyok): conds_met = False
    if "KG YOK Favori" in combo_template_str and not (kgyok < kgvar): conds_met = False
    
    if "ÜST Favori" in combo_template_str and not (ust < alt): conds_met = False
    if "ALT Favori" in combo_template_str and not (alt < ust): conds_met = False
    
    if "İY 0 Tuzağı" in combo_template_str and not (iy0 < 2.10): conds_met = False
    if "İY 1 Kesin" in combo_template_str and not (iy1 < iy0 and iy1 < iy2): conds_met = False
    if "İY 2 Kesin" in combo_template_str and not (iy2 < iy0 and iy2 < iy1): conds_met = False
    
    return conds_met

def run_super_analyzer():
    LIVE_PATH = r'C:\Users\YUSUF\.gemini\antigravity\scratch\live_match.json'
    LIG_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\lig_kurallari.json'
    COMBO_PATH = r'C:\Users\YUSUF\.gemini\antigravity\scratch\combo_kurallari.json'
    
    with open(LIVE_PATH, 'r', encoding='utf-8') as f:
        live = json.load(f)
        
    lig_rules = []
    if os.path.exists(LIG_PATH):
        with open(LIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            lig_rules = data.get('kurallar', []) if isinstance(data, dict) else data
            
    combo_rules = []
    if os.path.exists(COMBO_PATH):
        with open(COMBO_PATH, 'r', encoding='utf-8') as f:
            combo_rules = json.load(f)

def analyze_match(live_match, lig_rules, combo_rules, verbose=True):
    lig = live_match.get('lig', 'Bilinmeyen Lig')
    o_live = live_match.get('oranlar', {})
    
    ms1 = o_live.get('Maç Sonucu_1', 99)
    ms2 = o_live.get('Maç Sonucu_2', 99)
    kgyok = o_live.get('Karşılıklı Gol_Yok', 99)
    kgvar = o_live.get('Karşılıklı Gol_Var', 0)
    h1 = o_live.get('Handikaplı Maç Sonucu 0:1_1', 99)
    iy1 = o_live.get('1. Yarı Sonucu_1', 99)
    
    output = []
    def log(msg):
        if verbose: print(msg)
        output.append(msg)
        
    log("================================================================")
    log("🧠 ANTIGRAVITY SÜPER CANLI ANALİZÖR")
    log(f"Maç: {lig} | MS1: {ms1} | MS2: {ms2} | KG Yok: {kgyok} | KG Var: {kgvar}")
    log("================================================================\n")
    
    tetiklenenler = []
    beklenen_skorlar = []
    ana_hedef = ""
    
    # --- KATMAN 1: LİG DNA'SI ---
    log("🔍 KATMAN 1: Lig DNA Taraması...")
    # Lig kuralları kontrolü (Basitleştirilmiş eşleşme simülasyonu)
    l_kural = None
    if isinstance(lig_rules, dict):
        for k_adi, k_detay in lig_rules.items():
            if k_detay.get('lig') == lig:
                if k_detay.get('filtre', {}).get('hedef') == 'MS2' and ms2 < 1.40:
                    l_kural = k_adi
    elif isinstance(lig_rules, list):
        for idx, k_detay in enumerate(lig_rules):
            if k_detay.get('lig') == lig:
                l_kural = k_detay.get('isim', f"LİG-KURAL-{idx+1}")
    if l_kural:
        log(f"   [!] Lig Kuralı {l_kural} Tetiklendi.")
        tetiklenenler.append(l_kural)
    else:
        log("   [-] Maça uyan sabit bir Lig Kuralı bulunamadı.")
        
    # --- KATMAN 2: COMBO (MULTI-FACTOR) KURALLARI ---
    log("\n🔍 KATMAN 2: Çoklu Faktör (Combo) Taraması...")
    c_kural = None
    for r in combo_rules:
        if check_combo_match(live_match, r['filtre_kombinasyonu']):
            c_kural = r
            break # Sadece en güçlü (ilk) olanı al
            
    if c_kural:
        log(f"   [!] Combo Kural {c_kural['kural_kodu']} Tetiklendi (Şablon: {c_kural['filtre_kombinasyonu']}) -> Hedef: {c_kural['hedef']} (Başarı: %{c_kural['basari_orani']})")
        tetiklenenler.append(c_kural['kural_kodu'])
        ana_hedef = c_kural['hedef']
    else:
        log("   [-] Maça uyan Combo kalıbı bulunamadı.")
        
    # --- KATMAN 3: DENGESİZLİK VE KIRILMA NOKTASI MATRİSİ ---
    log("\n🔍 KATMAN 3: Oran Uyumu (Harmony) ve Dengesizlik Taraması...")
    matrix_msg = ""
    
    # ŞMP maçındaki deplasman 1.31 favori. MS1 veya MS2 için ağır favori durumunda kırılma testi.
    fav_oran = min(ms1, ms2)
    fav_yon = "MS 1" if ms1 < ms2 else "MS 2"
    
    if fav_oran <= 1.40:
        # SAHTE KG TUZAĞI KONTROLÜ (SUPER TRAP DETECTOR)
        sahte_kg_tuzagi = False
        if fav_yon == "MS 1" and ms1 <= 1.30 and h1 < 1.85 and iy1 < 1.70 and kgvar < 1.50:
            sahte_kg_tuzagi = True
            
        if sahte_kg_tuzagi:
            matrix_msg = f"SAHTE KG TUZAĞI (SUPER TRAP DETECTOR AKTİF!). Bahis şirketi KG Var oranını ({kgvar}) bilerek düşük tutarak herkesi sürpriz gole yönlendiriyor. Ancak Handikap 1 ({h1}) ve İY 1 ({iy1}) oranları o kadar güçlü ki, rakip yarı sahayı bile geçemeyecek. Bu devasa bir tuzaktır."
            beklenen_skorlar = ["3-0", "4-0", "5-0", "6-0"]
            tetiklenenler.append("SAHTE KG TUZAĞI")
            
        elif kgyok < 1.40:
            matrix_msg = f"DENGESİZLİK-YOK (Uyum Bölgesi). Bahisçi {fav_yon} takımına çok güveniyor ve sürpriz beklemiyor."
            beklenen_skorlar = ["0-2", "0-1"] if fav_yon == "MS 2" else ["2-0", "1-0"]
            tetiklenenler.append("UYUM BÖLGESİ (Temiz Sayfa)")
        elif 1.40 <= kgyok < 1.60:
            matrix_msg = f"GEÇİŞ BÖLGESİ. Sürpriz ihtimali yavaşça artıyor."
            beklenen_skorlar = ["1-2", "0-1"] if fav_yon == "MS 2" else ["2-1", "1-0"]
            tetiklenenler.append("GEÇİŞ BÖLGESİ")
        elif 1.60 <= kgyok < 1.80:
            matrix_msg = f"TUZAK/KIRILMA NOKTASI. {fav_yon} ağır favori ({fav_oran}) olmasına rağmen KG Yok ({kgyok}) şişirilmiş. Bahis şirketi sürpriz bekliyor!"
            beklenen_skorlar = ["1-2"] if fav_yon == "MS 2" else ["2-1"]
            tetiklenenler.append("TUZAK (Kırılma Noktası)")
        else:
            matrix_msg = f"TERS KORELASYON BÖLGESİ. Oran uyumu tamamen kopmuş. {fav_yon} kazanma ihtimali çöküşte."
            beklenen_skorlar = ["1-1", "2-2"]
            tetiklenenler.append("TERS KORELASYON")
        
        log(f"   [!] {matrix_msg}")
    else:
        log("   [-] Ağır favori olmadığı için matris analizi pas geçildi.")
        
    log("\n================================================================")
    log("🤖 NİHAİ SENTEZ RAPORU")
    if tetiklenenler:
        triggers = ", ".join(tetiklenenler)
        skor_str = " veya ".join(beklenen_skorlar) if beklenen_skorlar else "Bilinmiyor"
        
        log(f'   "Tetiklenen Kurallar: {triggers}.')
        if "SAHTE KG TUZAĞI" in triggers:
            log(f'   DİKKAT: Şirket sahte bir KG Var sinyaliyle (KG Var: {kgvar}) kullanıcıları avlamaya çalışıyor.')
            log(f'   Handikap ve İlk Yarı gücü bu sahte sinyali yok etti. Rakibin gol bulması imkansız.')
            log(f'   {fav_yon} takımı tarihi bir fark atacaktır. Beklenen Skor: {skor_str}."')
        elif "TUZAK" in triggers or "TERS KORELASYON" in triggers:
            log(f'   DİKKAT: İkincil oranlarda (KG Yok: {kgyok}) belirgin bir dengesizlik ve ters korelasyon tespit edildi.')
            log(f'   Klasik {fav_yon} favorisi görünse de, bu uyumsuzluk nedeniyle rakibin gol atacağı netleşmiştir.')
            log(f'   Temiz bir favori galibiyeti beklenmiyor, maç kilitlenebilir. Beklenen Skor: {skor_str}."')
        else:
            log(f'   Lig yapısı ve oran uyumu tamamen favoriyi destekliyor. Beklenen Skor: {skor_str}."')
    else:
        log("   Bu oran yapısı güvenilir bir şablona oturmuyor. Pas geçilmesi önerilir.")
    log("================================================================")
    return "\n".join(output)

if __name__ == "__main__":
    run_super_analyzer()

if __name__ == "__main__":
    run_super_analyzer()
