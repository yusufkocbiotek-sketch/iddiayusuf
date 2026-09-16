import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from story_analyzer import generate_story

with open('single_match.json', encoding='utf-8') as f:
    match_data = json.load(f)

res = generate_story(match_data, verbose=True)
print(res)
