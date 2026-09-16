import json
import codecs
from story_analyzer import generate_story
import rule_engine

with codecs.open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', 'utf8') as f:
    matches = json.load(f)['matches']

match = matches[-430]
story = generate_story(match)
print(story)
