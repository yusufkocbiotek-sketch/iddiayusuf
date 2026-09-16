import json
import rule_engine
import story_analyzer

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    matches = data['matches']
    for m in matches:
        o = m.get('oranlar', {})
        if o.get('Maç Sonucu_1') == 2.54 and o.get('Alt/Üst 1.5_Üst') == 1.24 and o.get('Karşılıklı Gol_Var') == 1.71:
            report = story_analyzer.generate_story(m, verbose=True)
            break
