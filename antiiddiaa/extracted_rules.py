import os
import re

# Dosya yolları
input_file_path = r"C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py"
output_file_path = r"C:\Users\YUSUF\.gemini\antigravity\scratch\extracted_rules.py"

# Aranacak desenler (regex)
# 'if ' ile başlayan veya code/name/category/description ataması içeren satırlar
patterns = [
    r"^\s*code\s*=",
    r"^\s*name\s*=",
    r"^\s*category\s*=",
    r"^\s*description\s*=",
    r"^\s*if\s"
]
combined_pattern = re.compile("|".join(patterns))

extracted_lines = []
class_count = 0
in_class = False

try:
    with open(input_file_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            # Yeni bir sınıf başladığını tespit et (0 girintili class satırı)
            if line.startswith("class "):
                class_count += 1
                in_class = True
                continue

            # Sınıfın bittiğini tespit et (girinti 0'a düştüğünde ve boş satır/yorum değilse)
            if in_class:
                if line.strip() and not line.startswith(" ") and not line.startswith("\t") and not line.startswith("#"):
                    in_class = False

            # Sadece 1. sınıf bittikten sonra ve 2. sınıf başlamadan önceki bölgeyi oku
            if class_count == 1 and not in_class:
                if combined_pattern.match(line):
                    extracted_lines.append(line)

    # Elde edilen satırları yeni dosyaya yaz
    if extracted_lines:
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            outfile.writelines(extracted_lines)
        print(f"İşlem tamamlandı! {len(extracted_lines)} satır şuraya kopyalandı:\n{output_file_path}")
    else:
        print("Belirtilen kriterlere uygun satır bulunamadı veya sınıf yapısı eşleşmedi.")

except FileNotFoundError:
    print(f"Hata: '{input_file_path}' dosyası bulunamadı. Lütfen yolu kontrol edin.")
except Exception as e:
    print(f"Bir hata oluştu: {e}")