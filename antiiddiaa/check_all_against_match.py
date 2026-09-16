import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\Users\YUSUF\.gemini\antigravity\scratch')
from rule_engine import get_all_rules

odds = {
    'Maç Sonucu_1': 3.84,
    'Maç Sonucu_0': 3.25,
    'Maç Sonucu_2': 1.63,
    'Alt/Üst 2.5_Alt': 1.77,
    'Alt/Üst 2.5_Üst': 1.62,
    'Alt/Üst 3.5_Alt': 1.24,
    'Alt/Üst 3.5_Üst': 2.67,
    'Karşılıklı Gol_Var': 1.57,
    'Karşılıklı Gol_Yok': 1.83,
    'Ev Sahibi Alt/Üst 0.5_Üst': 1.33,
    'Deplasman Alt/Üst 0.5_Üst': 1.06,
    'Ev Sahibi Alt/Üst 1.5_Alt': 1.19,
    'Ev Sahibi Alt/Üst 1.5_Üst': 2.9,
    'Deplasman Alt/Üst 1.5_Alt': 1.75,
    'Deplasman Alt/Üst 1.5_Üst': 1.64,
    'Çifte Şans_12': 1.16,
    'Çifte Şans_1X': 1.71,
    'Çifte Şans_X2': 1.1,
    'Maç Sonucu ve Alt/Üst 3.5_1 ve Üst': 14.15,
    'Maç Sonucu ve Alt/Üst 3.5_2 ve Üst': 4.42,
}

rules = get_all_rules()
print(f"Total rules: {len(rules)}")
triggered = 0
for r in rules:
    try:
        ok, msg = r.evaluate(odds)
    except Exception as e:
        print(f"[{r.code}] ERROR: {e}")
        continue
    if ok:
        triggered += 1
        print(f"TRIGGERED [{r.code}] {r.name}: {msg}")

print(f"\nTriggered count: {triggered}")