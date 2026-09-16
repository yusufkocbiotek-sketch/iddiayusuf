import json
import story_analyzer

with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

m = data['matches'][-380] # Senegal
print("Generating story for Senegal...")
story = story_analyzer.generate_story(m, verbose=False)
print(story)
