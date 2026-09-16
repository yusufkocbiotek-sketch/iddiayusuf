import codecs

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()

import re

story = re.sub(
    r"        else:\n    elif any\(r\['code'\] == '1486'",
    r"        else:\n            output.append(f'- 📉 **Standart Akış:** Zamanlama (yarı) bahisleri için ekstra bir anomali veya belirgin bir sinyal tespit edilemedi.')\n\n    # DEVASA DÜELLO TESPİTİ\n    is_massive_duel = ('İlk Yarı Düellosu (KG)' in ''.join(output) and 'İkinci Yarı Şovu (KG)' in ''.join(output)) or 'TARİHİ DÜELLO' in ''.join(output) or any(r['code'] == 'G11' for r in triggered_rules)\n\n    output.append(f'\\n### 💎 KOMBİNE & TAHMİN ÖNERİLERİ')\n    if any(r['code'] == '2001' for r in triggered_rules):\n        output.append(f'- **Ana Tahmin:** 2.5 Gol Altı (Milli Maç Kısırlığı)')\n        output.append(f'- **Kombine Öneri:** 2.5 Alt + Karşılıklı Gol Yok (Sürpriz Skor: 0-0 / 1-1 / 1-0)')\n    elif any(r['code'] == '2002' for r in triggered_rules):\n        output.append(f'- **Ana Tahmin:** Maç Sonucu 1/2 (Milli Maç Fark Patlaması)')\n        output.append(f'- **Kombine Öneri:** Favori Kazanır + 3.5 Gol Üst (Sürpriz Skor: 4-0 / 5-0)')\n    elif any(r['code'] == '1481' for r in triggered_rules):\n        output.append(f'- **Ana Tahmin:** Sürpriz Deplasman Galibiyeti (MS 2) veya 02 Çifte Şans')\n        output.append(f'- **Kombine Öneri:** 02 Çifte Şans + 2.5 Gol Üst (Sürpriz Skor: 1-3 / 2-2)')\n    elif any(r['code'] == '1469' and 'ASYA TUZAĞI' in r['insight'] for r in triggered_rules):\n        output.append(f'- **Ana Tahmin:** Gol Düellosu (Asya Tuzağı)')\n        output.append(f'- **Kombine Öneri:** Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz: 3.5 Üst)')\n    elif any(r['code'] == '1486'",
    story
)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf-8') as f:
    f.write(story)
