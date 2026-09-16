import json
import story_analyzer
import sys

def check_match(match, index):
    story = story_analyzer.generate_story(match, verbose=False)
    
    skor_ev = match.get('skor_ev')
    skor_dep = match.get('skor_dep')
    
    if skor_ev is None or skor_dep is None:
        return None
        
    skor_ev = int(skor_ev)
    skor_dep = int(skor_dep)
    
    actual_ms = "0"
    if skor_ev > skor_dep:
        actual_ms = "1"
    elif skor_dep > skor_ev:
        actual_ms = "2"
        
    total_goals = skor_ev + skor_dep
    actual_kg = "Var" if (skor_ev > 0 and skor_dep > 0) else "Yok"
    
    predictions = [line for line in story.split('\n') if "Ana Tahmin:" in line or "Kombine" in line]
    pred_str = " | ".join(predictions).lower()
    
    # Very basic success logic
    success = False
    
    if actual_ms == "1" and ("ms 1" in pred_str or "ev sahibi kazanır" in pred_str or "maç sonucu 1" in pred_str):
        success = True
    elif actual_ms == "2" and ("ms 2" in pred_str or "deplasman kazanır" in pred_str or "maç sonucu 2" in pred_str or "02 çifte şans" in pred_str):
        success = True
    elif actual_ms == "0" and ("ms 0" in pred_str or "beraberlik" in pred_str or "taraf bahsi çok riskli" in pred_str):
        success = True
    elif ("02 çifte şans" in pred_str or "1x çifte şans" in pred_str) and actual_ms == "0":
        success = True
        
    if not success and "taraf bahsi çok riskli" in pred_str:
        if "gol düellosu" in pred_str and total_goals >= 3:
            success = True
            
    result = {
        'index': index,
        'home_team': match.get('ev_sahibi', 'Ev'),
        'away_team': match.get('deplasman', 'Dep'),
        'score': f"{skor_ev}-{skor_dep}",
        'actual_ms': actual_ms,
        'success': success,
        'predictions': predictions,
        'odds': match.get('oranlar', {})
    }
    return result

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
    failed_matches = []
    success_count = 0
    total_count = 0
    
    for i in range(-150, -76):
        try:
            match = data['matches'][i]
            res = check_match(match, i)
            if res:
                total_count += 1
                if res['success']:
                    success_count += 1
                else:
                    failed_matches.append(res)
        except Exception as e:
            pass

    print(f"Total Evaluated: {total_count}")
    print(f"Successes (Basic Eval): {success_count} / {total_count}")
    
    print("\n--- NOTABLE FAILURES (For Rule Generation) ---")
    # Show first 5 failures to find new traps
    for fail in failed_matches[:5]:
        print(f"Index: {fail['index']} | {fail['home_team']} vs {fail['away_team']} | SCORE: {fail['score']}")
        print(f"Predictions: {fail['predictions']}")
        
        # print key odds for this fail
        odds = fail['odds']
        key_odds = {
            "MS1": odds.get("Maç Sonucu_1"),
            "MS0": odds.get("Maç Sonucu_0"),
            "MS2": odds.get("Maç Sonucu_2"),
            "KG_Var": odds.get("Karşılıklı Gol_Var"),
            "KG_Yok": odds.get("Karşılıklı Gol_Yok"),
            "Ust25": odds.get("Alt/Üst 2.5_Üst"),
            "Ev15Alt": odds.get("Ev Sahibi Alt/Üst 1.5_Alt"),
            "Ev15Ust": odds.get("Ev Sahibi Alt/Üst 1.5_Üst"),
            "Dep15Alt": odds.get("Deplasman Alt/Üst 1.5_Alt"),
            "Dep15Ust": odds.get("Deplasman Alt/Üst 1.5_Üst")
        }
        print(f"Odds: {key_odds}")
        print("-" * 30)
