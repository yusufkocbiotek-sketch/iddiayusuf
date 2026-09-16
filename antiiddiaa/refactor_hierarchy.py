import codecs
import re

with codecs.open('rule_engine.py', 'r', 'utf-8') as f:
    content = f.read()

# find all Rule classes
classes = list(set(re.findall(r'class (Rule[A-Za-z0-9_]+)\(BaseRule\):', content)))

# separate them into phases
lig_rules = [c for c in classes if c.startswith('RuleLIG')]
anomaly_rules = sorted([c for c in classes if c.startswith('Rule14') or c == 'Rule999'], reverse=True)
taraf_rules = sorted([c for c in classes if c.startswith('RuleT')])
gol_rules = sorted([c for c in classes if c.startswith('RuleG')])
yari_rules = sorted([c for c in classes if c.startswith('RuleY')])

# the remaining ones
used = set(lig_rules + anomaly_rules + taraf_rules + gol_rules + yari_rules)
other_rules = [c for c in classes if c not in used]

new_get_all = f'''
def get_all_rules():
    # KURAL HİYERARŞİSİ (ÖNCELİK SIRALAMASI)
    # 1. FAZ: Lig ve Bölge (Makro Dinamikler - Tüm analizi şekillendirir)
    lig_rules = [{', '.join(lig_rules)}]
    
    # 2. FAZ: Devasa Anomaliler ve Tuzaklar (14xx serisi - Oran uyuşmazlıkları ve yemler)
    anomaly_rules = [{', '.join(anomaly_rules)}]
    
    # 3. FAZ: Taraf ve Maç Sonucu Temel Yönlendirmeleri (T Serisi)
    taraf_rules = [{', '.join(taraf_rules)}]
    
    # 4. FAZ: Gol Oranları (KG ve Alt/Üst - G Serisi)
    gol_rules = [{', '.join(gol_rules)}]
    
    # 5. FAZ: Yarı ve Zamanlama (Y Serisi)
    yari_rules = [{', '.join(yari_rules)}]
    
    # Digerleri
    other_rules = [{', '.join(other_rules)}]
    
    return lig_rules + anomaly_rules + taraf_rules + gol_rules + yari_rules + other_rules
'''

# replace the existing get_all_rules completely
content = re.sub(r'def get_all_rules\(\):.*', new_get_all.strip(), content, flags=re.DOTALL)

with codecs.open('rule_engine.py', 'w', 'utf-8') as f:
    f.write(content)

