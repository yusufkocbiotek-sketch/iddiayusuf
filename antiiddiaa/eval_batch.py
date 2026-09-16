import sys
import json
import importlib

sys.path.append(r"C:\Users\YUSUF\.gemini\antigravity\scratch")
import rule_engine
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

rules = rule_engine.get_all_rules()

print("EVALUATING MATCHES -274 TO -293...\n")
for i in range(-274, -294, -1):
    m = data['matches'][i]
    odds = m.get('oranlar', {})
    ev = m.get('ev_sahibi', '')
    dep = m.get('deplasman', '')
    skor_ev = m.get('skor_ev')
    skor_dep = m.get('skor_dep')
    
    if skor_ev is None or skor_dep is None:
        continue
        
    skor_ev = int(skor_ev)
    skor_dep = int(skor_dep)
    toplam_gol = skor_ev + skor_dep
    kg = (skor_ev > 0 and skor_dep > 0)
    
    triggered = []
    for R in rules:
        try:
            is_active, _ = R.evaluate(odds)
            if is_active:
                triggered.append(R.code)
        except Exception:
            pass
            
    print(f"--- MATCH {i} : {ev} vs {dep} ---")
    print(f"SKOR: {skor_ev}-{skor_dep}")
    print(f"Triggered: {triggered}")
    
    # Check if there is an anomaly or weird score without a 14xx rule
    has_anomaly_rule = any(t.startswith('14') for t in triggered)
    
    if not has_anomaly_rule:
        # Check if score is an upset or weird
        ms1 = odds.get('Maç Sonucu_1')
        ms2 = odds.get('Maç Sonucu_2')
        kg_var = odds.get('Karşılıklı Gol_Var')
        
        # Determine basic outcome
        won_ms1 = skor_ev > skor_dep
        won_ms2 = skor_dep > skor_ev
        
        if ms1 and ms2:
            if ms1 <= 1.40 and won_ms2:
                print(">> 🚨 UNCAUGHT UPSET: MS1 <= 1.40 but Deplasman won!")
            elif ms2 <= 1.40 and won_ms1:
                print(">> 🚨 UNCAUGHT UPSET: MS2 <= 1.40 but Ev won!")
            elif (ms1 <= 1.50 or ms2 <= 1.50) and toplam_gol == 0:
                print(">> 🚨 UNCAUGHT TRAP: Heavy favorite but 0-0!")
            elif kg_var and kg_var <= 1.40 and not kg:
                print(">> 🚨 UNCAUGHT TRAP: KG Var <= 1.40 but KG Yok happened!")
                
    # Always print odds to let the LLM analyze
    keys = ['Maç Sonucu_1', 'Maç Sonucu_0', 'Maç Sonucu_2', 'Alt/Üst 2.5_Alt', 'Alt/Üst 2.5_Üst', 'Karşılıklı Gol_Var', 'Karşılıklı Gol_Yok']
    for k in keys:
        print(f"  {k}: {odds.get(k, 'N/A')}")
    print("")

