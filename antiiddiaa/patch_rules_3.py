import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Rule 1530: relax ms1/ms2 constraint to >= 1.60
content = content.replace('ms1 >= 2.10 and ms2 >= 2.10', 'ms1 >= 1.60 and ms2 >= 1.60')

# 2. Update Rule 1552: require ms0 >= 3.20 and check either ms1 or ms2 as favorite
old_1552_eval = '''        if ms1 != 99.0 and 1.45 <= ms1 <= 1.75 and alt25 != 99.0 and alt25 <= 1.45 and kg_yok != 99.0 and kg_yok <= 1.60:
            return True, "SAHTE KISIR FAVORİ TUZAĞI (ÜST PATLAMASI): Ev sahibi favori (1.75 altı) olmasına rağmen, 2.5 Alt oranı anormal derecede düşük (1.45 altı) açılmış. Bu, maçı 'garanti 1-0 veya 2-0' gösterebilmek için kurulan devasa bir 'Sahte Alt' tuzağıdır. İddaa ev sahibinin 3 veya 4 gol atabileceğini çok iyi biliyor ancak piyasayı Alt'a yönlendiriyor. Gerçekte ev sahibi takımın hücum gücü gizlenmektedir. Bu maç 3-0 veya 4-0 gibi farklı bir ev sahibi galibiyetine ve dolayısıyla 2.5 Üst'e patlayacaktır! Alt tuzağına düşmeyin."'''

new_1552_eval = '''        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        # Check if either MS1 or MS2 is the slight favorite (1.45 - 1.75) and MS0 >= 3.20
        is_home_fav = (ms1 != 99.0 and 1.45 <= ms1 <= 1.75)
        is_away_fav = (ms2 != 99.0 and 1.45 <= ms2 <= 1.75)
        
        if (is_home_fav or is_away_fav) and ms0 != 99.0 and ms0 >= 3.20 and alt25 != 99.0 and alt25 <= 1.45 and kg_yok != 99.0 and kg_yok <= 1.60:
            return True, "SAHTE KISIR FAVORİ TUZAĞI (ÜST PATLAMASI): Favori takımın oranı 1.45-1.75 bandında olmasına rağmen, 2.5 Alt oranı anormal derecede düşük (1.45 altı) açılmış. Bu, maçı 'garanti 1-0 veya 0-1' gösterebilmek için kurulan devasa bir 'Sahte Alt' tuzağıdır. İddaa favorinin 3 veya 4 gol atabileceğini çok iyi biliyor ancak piyasayı Alt'a yönlendiriyor. (Not: Eğer MS0 düşük olsaydı bu gerçek bir kısır kilitlenme olabilirdi, ancak MS0 3.20 ve üzeri). Bu maç farklı bir galibiyete ve 2.5 Üst'e patlayacaktır! Alt tuzağına düşmeyin."'''

content = content.replace(old_1552_eval, new_1552_eval)

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied for 1530 and 1552.")
