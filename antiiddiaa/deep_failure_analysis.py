import json
import story_analyzer

def analyze_failures():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    failures_upsets = [] # MS1 favori ama 0 veya 2 bitti
    failures_goals_under = [] # Üst beklendi ama 0-1 gol bitti
    failures_goals_over = [] # Alt beklendi ama 3+ gol bitti
    
    for i in range(-150, -76):
        try:
            match = data['matches'][i]
            story = story_analyzer.generate_story(match, verbose=False)
            
            skor_ev = int(match.get('skor_ev', -1))
            skor_dep = int(match.get('skor_dep', -1))
            if skor_ev == -1: continue
            
            actual_ms = "1" if skor_ev > skor_dep else ("2" if skor_dep > skor_ev else "0")
            total_goals = skor_ev + skor_dep
            
            predictions = [line for line in story.split('\n') if "Ana Tahmin:" in line or "Kombine" in line]
            pred_str = " | ".join(predictions).lower()
            
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
                    
            if not success and len(predictions) > 0:
                odds = match.get('oranlar', {})
                ms1 = odds.get("Maç Sonucu_1", 99.0)
                ms2 = odds.get("Maç Sonucu_2", 99.0)
                
                # Check upset
                if ms1 <= 2.00 and actual_ms in ["0", "2"]:
                    failures_upsets.append((i, match))
                elif ms2 <= 2.00 and actual_ms in ["0", "1"]:
                    failures_upsets.append((i, match))
                    
                # Check goals
                if total_goals <= 1 and ("üst" in pred_str or "var" in pred_str):
                    failures_goals_under.append((i, match))
                elif total_goals >= 4 and ("alt" in pred_str or "yok" in pred_str):
                    failures_goals_over.append((i, match))
                    
        except Exception as e:
            pass
            
    print(f"Upsets missed: {len(failures_upsets)}")
    print(f"Goal Unders missed: {len(failures_goals_under)}")
    print(f"Goal Overs missed: {len(failures_goals_over)}")
    
    # Print 2 from each to find patterns
    def print_matches(mlist, name):
        print(f"\n--- {name} ---")
        for i, m in mlist[:3]:
            print(f"Index: {i} | {m.get('ev_sahibi')} vs {m.get('deplasman')} | Skor: {m.get('skor_ev')}-{m.get('skor_dep')}")
            odds = m.get('oranlar', {})
            key_odds = {
                "MS1": odds.get("Maç Sonucu_1"), "MS0": odds.get("Maç Sonucu_0"), "MS2": odds.get("Maç Sonucu_2"),
                "KG_Var": odds.get("Karşılıklı Gol_Var"), "Ust25": odds.get("Alt/Üst 2.5_Üst"),
                "Ev15Alt": odds.get("Ev Sahibi Alt/Üst 1.5_Alt"), "Dep15Alt": odds.get("Deplasman Alt/Üst 1.5_Alt"),
                "Ev05Ust": odds.get("Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst"), "Dep05Ust": odds.get("Deplasman 1. Yarı Altı/Üstü 0.5_Üst")
            }
            print(f"Odds: {key_odds}")
            
    print_matches(failures_upsets, "MISSED UPSETS")
    print_matches(failures_goals_under, "MISSED 0-0 or 1-0 (Predicted Goals)")
    print_matches(failures_goals_over, "MISSED 4+ GOALS (Predicted Under)")

if __name__ == '__main__':
    analyze_failures()
