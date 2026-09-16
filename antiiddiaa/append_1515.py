import codecs

rule = """
| **1515** | Sahte Ev Sahibi Golü Tuzağı (Deplasman Fark Patlaması) | GOL | **SAHTE EV SAHİBİ GOLÜ:** Deplasman takımı rahat kazanacak (1.50 altı). Ev sahibine ise kazanması imkansız bir oran (4.00 ve üzeri) açılmış. Buna rağmen KG Var oranı 1.45 gibi çok düşük ve komik bir seviyede. Bu, iddaacıların 'Ev sahibi nasıl olsa evinde 1 gol atar' diye düşünmesini sağlamak için kurulmuş devasa bir yemdir. Ev sahibi gol atamaz, Deplasman takımı fark atarak (0-3, 0-4) kazanır. KG Yok. |
"""

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Kurallar_Kitabi.md', 'a', 'utf8') as f:
    f.write(rule)
