import codecs

with codecs.open('story_analyzer.py', 'r', 'utf-8') as f:
    content = f.read()

func = '''
def get_league_type(match):
    lig = match.get('lig', '').lower()
    ev = match.get('ev_sahibi', '').lower()
    dep = match.get('deplasman', '').lower()
    
    if 'japonya' in lig or 'kore' in lig or 'çin' in lig or 'asya' in lig or 'avustralya' in lig:
        return 'ASYA'
    if 'arjantin' in lig or 'brezilya' in lig or 'şili' in lig or 'kolombiya' in lig:
        return 'GÜNEY_AMERİKA'
    if 'ingiltere' in lig or 'almanya' in lig or 'italya' in lig or 'ispanya' in lig:
        return 'AVRUPA_MAJÖR'
    return 'STANDART'

'''

if 'def get_league_type' not in content:
    content = content.replace('def generate_story(match, verbose=True):', func + 'def generate_story(match, verbose=True):')
    
    content = content.replace('odds = match.get("oranlar", {})', 'odds = match.get("oranlar", {})\n    lig_tipi = get_league_type(match)')
    content = content.replace('{lig_tipi}', '{lig_tipi}')  # it's fine as is in f-string

    with codecs.open('story_analyzer.py', 'w', 'utf-8') as f:
        f.write(content)
        
    print("Injected successfully!")
else:
    print("Already injected!")
