import json
try:
    with open(r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        print(f"Data is dict with {len(data)} keys.")
        matches = list(data.values())
    elif isinstance(data, list):
        print(f"Data is list with {len(data)} elements.")
        matches = data
    else:
        print("Unknown JSON structure.")
        matches = []
        
    print(f"Total Matches: {len(matches)}")
except Exception as e:
    print(f"Error: {e}")
