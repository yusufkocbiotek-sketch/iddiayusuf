import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', encoding='utf-8') as f:
    data = json.load(f)

def get_odd(odds, keys):
    for k in keys:
        if k in odds and odds[k] != "-":
            try:
                return float(odds[k])
            except:
                pass
    return 99.0

new_threshold_hits = []
new_threshold_misses = []
old_threshold_hits = []
old_threshold_misses = []

for i, m in enumerate(data['matches'][:958]):
    odds = m.get('oranlar', {})
    if not odds: continue
    
    alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
    iy_05_ust = get_odd(odds, ["İlk Yarı Alt/Üst 0.5_Üst", "1. Yarı Altı/Üstü 0.5_Üst", "İlk Yarı Altı/Üstü 0.5_Üst"])
    ms1 = get_odd(odds, ["Maç Sonucu_1"])
    ms2 = get_odd(odds, ["Maç Sonucu_2"])
    
    if alt25 <= 1.60 and iy_05_ust <= 1.30 and iy_05_ust != 99.0 and ms1 != 99.0 and ms2 != 99.0:
        
        # Did a first half goal happen? Or did 2.5 Üst happen?
        # Success for 1530 means there WAS a goal (iy > 0 or ms > 2)
        skor_1y_ev = m.get('skor_1y_ev')
        skor_1y_dep = m.get('skor_1y_dep')
        iy_goals = 0
        if skor_1y_ev not in [None, '', '-'] and skor_1y_dep not in [None, '', '-']:
            iy_goals = int(skor_1y_ev) + int(skor_1y_dep)
            
        success = (iy_goals > 0)
        
        # Test old threshold
        if ms1 >= 2.10 and ms2 >= 2.10:
            if success:
                old_threshold_hits.append(i)
            else:
                old_threshold_misses.append(i)
                
        # Test new threshold
        if ms1 >= 1.60 and ms2 >= 1.60:
            if success:
                new_threshold_hits.append(i)
            else:
                new_threshold_misses.append(i)

print(f"Old Threshold (>=2.10): Hits={len(old_threshold_hits)}, Misses={len(old_threshold_misses)}")
print(f"New Threshold (>=1.60): Hits={len(new_threshold_hits)}, Misses={len(new_threshold_misses)}")

# What are the matches that triggered ONLY in the new threshold?
new_only_hits = set(new_threshold_hits) - set(old_threshold_hits)
new_only_misses = set(new_threshold_misses) - set(old_threshold_misses)

print(f"Matches caught by relaxing to 1.60 that were HITS (İY>0): {len(new_only_hits)}")
print(f"Matches caught by relaxing to 1.60 that were MISSES (İY=0): {len(new_only_misses)}")

