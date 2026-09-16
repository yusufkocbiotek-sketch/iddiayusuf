import sys
sys.path.append(r"C:\Users\YUSUF\.gemini\antigravity\scratch")
import json
from story_analyzer import generate_story

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

idx = -367
m = data['matches'][idx]
story = generate_story(m, verbose=True)
print(story)
