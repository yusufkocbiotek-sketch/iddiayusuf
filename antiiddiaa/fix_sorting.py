import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    content = f.read()

# I will just write the entire function correctly. No regex risking.
import re
new_func_body = """
    output.append(f"- **Taraf:** Ev **{ms1}** | Beraberlik **{ms0}** | Konuk **{ms2}**")
    output.append(f"- **Çifte Şans:** 1X **{cs1x}** | 12 **{cs12}** | X2 **{csx2}**")
    output.append(f"- **İlk Yarı MS:** Ev **{iy1}** | Beraberlik **{iy0}** | Konuk **{iy2}**")
    output.append(f"- **Gol (2.5):** Alt **{alt25}** | Üst **{ust25}**")
    output.append(f"- **Karşılıklı Gol:** KG Var **{kg_var}** | KG Yok **{kg_yok}**")
    output.append(f"- **Tek/Çift:** Tek **{tek}** | Çift **{cift}**")
    output.append(f"---")
    
    # 5-PHASE RULE SORTING
    def rule_sort_key(r):
        code = r['code']
        if code.startswith('LIG') or code in ['2001', '2002']: return 1 # Faz 1: Makro Dinamikler
        if code.startswith('1'): return 2 # Faz 2: Devasa Anomaliler ve Çelişkiler (14xx, 15xx)
        if code.startswith('T'): return 3 # Faz 3: Taraf Kilitleri
        if code.startswith('G'): return 4 # Faz 4: Gol Kilitleri
        if code.startswith('Y'): return 5 # Faz 5: Yarı Kilitleri
        return 99

    triggered_rules.sort(key=rule_sort_key)
    
    if not triggered_rules:
        kural_kodlari = "TUZAK YOK (STANDART PİYASA)"
    else:
        kural_kodlari = " → ".join([r['code'] for r in triggered_rules])
    
    output.append(f"**Kural Sırası:** **{kural_kodlari}**")
    
    # Genel Profil
    profil = []
    if ms1 < ms2 and ms1 <= 1.50: profil.append("AĞIR EV FAVORİSİ")
    elif ms1 < ms2: profil.append("EV HAFİF FAVORİSİ")
    elif ms2 < ms1 and ms2 <= 1.50: profil.append("AĞIR KONUK FAVORİSİ")
"""

content = re.sub(r'    output\.append\(f"- \*\*Taraf:\*\* Ev \*\*{ms1}\*\* \| Beraberlik \*\*{ms0}\*\* \| Konuk \*\*{ms2}\*\*"\).*?elif ms2 < ms1 and ms2 <= 1\.50: profil\.append\("AĞIR KONUK FAVORİSİ"\)', new_func_body, content, flags=re.DOTALL)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf-8') as f:
    f.write(content)

print("Fixed!")
