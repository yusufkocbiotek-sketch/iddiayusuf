import json
import story_analyzer

def evaluate_batch():
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    failures = []
    
    for i in range(-195, -300, -1):
        try:
            match = data['matches'][i]
            story = story_analyzer.generate_story(match, verbose=False)
            
            ev_skor = match.get('skor_ev')
            dep_skor = match.get('skor_dep')
            if ev_skor is None or dep_skor is None:
                continue
                
            ev_skor = int(ev_skor)
            dep_skor = int(dep_skor)
            
            # Simple check if prediction makes sense
            # We just want to extract predictions to see what the machine thought
            predictions = [line for line in story.split('\n') if 'Ana Tahmin:' in line or 'Kombine Öneri:' in line]
            pred_text = " ".join(predictions).lower()
            
            actual_ms = 1 if ev_skor > dep_skor else (2 if dep_skor > ev_skor else 0)
            actual_kg = "var" if ev_skor > 0 and dep_skor > 0 else "yok"
            actual_25 = "üst" if (ev_skor + dep_skor) > 2 else "alt"
            
            # A very rudimentary success check
            success = False
            if actual_ms == 1 and ('ms 1' in pred_text or 'ev sahibi' in pred_text or '1x' in pred_text):
                success = True
            elif actual_ms == 2 and ('ms 2' in pred_text or 'deplasman' in pred_text or '02' in pred_text or 'x2' in pred_text):
                success = True
            elif actual_ms == 0 and ('ms 0' in pred_text or 'beraberlik' in pred_text or '1x' in pred_text or '02' in pred_text or 'x2' in pred_text):
                success = True
                
            if 'kg var' in pred_text and actual_kg == 'yok':
                success = False
            if 'kg yok' in pred_text and actual_kg == 'var':
                success = False
                
            if not success:
                failures.append({
                    "index": i,
                    "match": f"{match.get('ev_sahibi')} - {match.get('deplasman')}",
                    "score": f"{ev_skor}-{dep_skor}",
                    "pred": pred_text
                })
        except Exception as e:
            pass

    print(f"Total failures: {len(failures)}")
    for f in failures[:10]: # Print first 10 failures to analyze
        print(f"Index: {f['index']} | {f['match']} | Score: {f['score']}")
        print(f"Pred: {f['pred']}")
        print("-" * 30)

if __name__ == "__main__":
    evaluate_batch()
