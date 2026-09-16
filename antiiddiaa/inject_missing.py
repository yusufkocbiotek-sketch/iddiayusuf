import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf8') as f:
    analyzer = f.read()

new_rules = """
        '1480': ("Tek Skor Darboğazı Tuzağı (Ev Sahibi Sürprizi)", "1X Çifte Şans + 2.5 Gol Altı (Sürpriz Skor: 1-0 / 2-0)"),
        '1484': ("Aşırı Şişirilmiş Favori Alt Tuzağı", "MS 1 + 2.5 Gol Altı (Sürpriz Skor: 1-0 / 2-0)"),
        '1485': ("Ölü Alt Tuzağı (Beraberlik Garantisi)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 0-0)"),
        '1491': ("Dengeli Maçlarda Gerçek Düello", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 2-2)"),
        '1493': ("Çıplak Kral Tuzağı (02 Çifte Şans)", "X2 Çifte Şans + Karşılıklı Gol Yok (Sürpriz Skor: 0-1)"),
        '1497': ("Ölümcül Sessizlik Tuzağı (0-0 Yemi)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 0-0)"),
        '1498': ("Sahte Banko Gol Tuzağı (Kısır Maç)", "2.5 Gol Altı + Karşılıklı Gol Yok (Sürpriz Skor: 1-0 / 0-1)"),
        '1511': ("Beraberliksiz Gol Düellosu İllüzyonu", "Maç Sonucu 0 + Karşılıklı Gol Var (Sürpriz Skor: 2-2)"),
        '1476': ("Uyuyan Dev (İkinci Yarı Düello Patlaması)", "Karşılıklı Gol Var + 2.5 Gol Üst (Sürpriz Skor: 1-2 / 2-1)"),
        '1465': ("Uluslararası Ev Favorisi Tuzağı", "X2 Çifte Şans + 2.5 Gol Altı (Sürpriz Skor: 0-1)"),
        '1464': ("Hafif Ev Üstünlüğü (Gollü, 3-1)", "MS 1 + 2.5 Gol Üst (Sürpriz Skor: 3-1)"),
        '1466': ("Yakınsak Sürpriz Oran (Favori Çöküşü 1-2)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2)"),
        '1474': ("Enflasyon Tuzağı (Favori ve Beraberlik Eşitliği)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 0-0 / 1-1)"),
        '1463': ("Tamamen Dengeli Beraberlik (0-0)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 0-0)"),
        '1475': ("Yalancı İmparator Tuzağı (1.0X Favori Çöküşü)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-1 / 1-2)"),
        '1473': ("Çapraz Sürpriz Düellosu (2-2 Tuzağı)", "Maç Sonucu 0 + 2.5 Gol Üst (Sürpriz Skor: 2-2)"),
        '1468': ("Matematiksel Paradoks (Sahte Favori Çöküşü 1-2/1-3)", "X2 Çifte Şans + Karşılıklı Gol Var (Sürpriz Skor: 1-2 / 1-3)"),
        '1467': ("Dengeli Kısır Çelişki (0-0)", "Maç Sonucu 0 + 2.5 Gol Altı (Sürpriz Skor: 0-0)"),
        '1462': ("Belirgin Ev Üstünlüğü (İlk Yarı Kapalı, 1-0)", "MS 1 + 2.5 Gol Altı (Sürpriz Skor: 1-0)"),
"""

# Insert right after predictions = {
new_analyzer = re.sub(r'predictions = \{', 'predictions = {' + new_rules, analyzer)

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'w', 'utf8') as f:
    f.write(new_analyzer)

print("Injected!")
