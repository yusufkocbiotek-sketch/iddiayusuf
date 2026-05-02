from pathlib import Path
import re

path = Path("skor_json_eslestir.py")
text = path.read_text(encoding="utf-8")

yeni_fonksiyon = r'''def temizle_takim_adi(ad):
    if not ad:
        return ""

    ad = ad.lower().strip()

    tr_map = {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u"
    }

    for k, v in tr_map.items():
        ad = ad.replace(k, v)

    silinecekler = [
        " fc", "fc ",
        " fk", "fk ",
        " sk", "sk ",
        " sc", "sc ",
        " ac", "ac ",
        " as", "as ",
        " cf", "cf ",
        " cd", "cd ",
        " afc", "afc ",
        " utd",
        " united",
        " city",
        " town",
        " club",
        " deportivo",
        " atletico",
        " athletic",
        " real ",
        "spor",
        " 1908",
        " 1911",
        " 1912",
        " 1919",
        " 1929",
        " 2000"
    ]

    for s in silinecekler:
        ad = ad.replace(s, " ")

    ad = re.sub(r"[^a-z0-9]", "", ad)

    manuel = {
        "indmendoza": "independienterivadavia",
        "independientemendoza": "independienterivadavia",
        "deplagua": "deportivolaguaira",
        "deportivolagua": "deportivolaguaira",
        "catigre": "atleticotigre",
        "tigre": "atleticotigre",
        "penaroluru": "penarol",
        "capenarol": "penarol",
        "americadecali": "americadecali",
        "velezsarsfield": "velezsarsfield",
        "gimnasiaytirodesalta": "gimnasiaytirodesalta",
        "ofkbaniklehotapodvtacnikom": "baniklehotapodvtacnikom",
        "baniklehotapodvtacnikom": "baniklehotapodvtacnikom",
        "shanghaishenhua": "shanghaishenhua",
        "chengdurongcheng": "chengdurongcheng",
        "vanersborgsfk": "vanersborgs",
        "vanersborgsif": "vanersborgs",
        "kuchingfa": "kuching",
        "terengganu": "terengganu",
        "fcsudtirol": "sudtirol",
        "sudtirol": "sudtirol",
        "sscbari": "bari",
        "bari": "bari",
        "lask": "lasklinz",
        "paideflora": "paidelinnamee",
        "tartujktam": "tammekatartu",
        "throtturv": "throttur",
        "haukarhafnarfjordur": "haukar",
        "acpisa": "pisa",
        "pisa": "pisa",
        "lecce": "lecce",
        "girona": "girona",
        "mallorca": "mallorca",
        "leeds": "leeds",
        "leedsunited": "leeds",
        "burnley": "burnley",
        "gaziantepfk": "gaziantep",
        "gaziantep": "gaziantep",
        "besiktas": "besiktas",
        "rizes": "rizespor",
        "rizespor": "rizespor",
        "caykurrizespor": "rizespor",
        "konyaspor": "konyaspor"
    }

    if ad in manuel:
        ad = manuel[ad]

    return ad
'''

pattern = r"def temizle_takim_adi\(ad\):.*?\ndef benzerlik\(a, b\):"

if not re.search(pattern, text, flags=re.S):
    raise SystemExit("Fonksiyon bloğu bulunamadı. Dosya yapısı beklediğim gibi değil.")

text = re.sub(
    pattern,
    yeni_fonksiyon + "\n\ndef benzerlik(a, b):",
    text,
    flags=re.S
)

path.write_text(text, encoding="utf-8")
print("✅ skor_json_eslestir.py düzeltildi.")