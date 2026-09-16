import json
import sys
import codecs
from story_analyzer import generate_story
from rule_engine import get_all_rules

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    matches = data['matches']

# Get rules to ensure they are loaded
rules = get_all_rules()

output = []
output.append("# 🕵️ BLIND ANALİZ (KÖR-TEST): -728 ile -737 Arası (10 Maç)")
output.append("")
output.append("**Metodoloji:** Sistem maçları incelerken skorları tamamen gizledik. Önce sadece kural motorumuzun oranlardan çıkardığı tahminleri ve tespit ettiği anomalileri göreceğiz. Hemen altında ise maçın GERÇEKTE nasıl bittiğini açığa çıkarıp, kurallarımızın başarısını ölçeceğiz.")
output.append("")

for i in range(728, 738):
    m = matches[-i]
    skor_1y_ev = m.get("skor_1y_ev", "?")
    skor_1y_dep = m.get("skor_1y_dep", "?")
    skor_ev = m.get("skor_ev", "?")
    skor_dep = m.get("skor_dep", "?")
    
    # Skorsuz kopyayı oluştur
    temp_m = m.copy()
    if 'skor_1y_ev' in temp_m: del temp_m['skor_1y_ev']
    if 'skor_1y_dep' in temp_m: del temp_m['skor_1y_dep']
    if 'skor_ev' in temp_m: del temp_m['skor_ev']
    if 'skor_dep' in temp_m: del temp_m['skor_dep']
    
    output.append(f"## 🎯 Index -{i} ({m.get('ev_sahibi', 'Ev')} - {m.get('deplasman', 'Dep')})")
    
    # Hikayeyi oluştur (skor olmadan)
    story = generate_story(temp_m)
    lines = story.split('\n')
    filtered_lines = [l for l in lines if 'GERÇEKLEŞEN SKOR' not in l]
    
    output.append("### 🧠 Sistemin Kör Tahmini (Skorlar Gizliyken)")
    output.append('\n'.join(filtered_lines))
    output.append("")
    output.append("### 🔍 GERÇEK SONUÇ & HESAPLAŞMA")
    output.append(f"> **Gerçekleşen Skor:** İlk Yarı **{skor_1y_ev}-{skor_1y_dep}** | Maç Sonucu **{skor_ev}-{skor_dep}**")
    output.append("")
    output.append("*(Yapay Zeka Notu: Bu kısma analizi yaptıktan sonra yorumumu ekleyeceğim)*")
    output.append("---")
    output.append("")

out_path = r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\KOR_Analiz_728_737.md'

with codecs.open(out_path, 'w', 'utf-8') as f:
    f.write('\n'.join(output))

print("Blind analysis generated successfully!")
