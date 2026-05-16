import json
import pandas as pd

# JSON dosyasını oku
with open('public/data/mac.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Maç listesini al
matches = data.get('matches', [])

# Pandas DataFrame'e çevir (Tablo haline getir)
df = pd.DataFrame(matches)

# 'oranlar' sütunu iç içe geçmiş (nested) olabilir, onu düzleştirme gerekebilir.
# Basitlik adına sadece ana sütunları alalım:
cols_to_keep = ['tarih', 'saat', 'lig', 'ev_sahibi', 'deplasman', 'durum', 'skor_ev', 'skor_dep', 'skor_1y_ev', 'skor_1y_dep']
# Sadece mevcut olan sütunları seç
existing_cols = [col for col in cols_to_keep if col in df.columns]
df = df[existing_cols]

# Excel olarak kaydet
output_file = 'mac_raporu.xlsx'
df.to_excel(output_file, index=False)

print(f"✅ Başarılı! {len(df)} maç '{output_file}' dosyasına kaydedildi.")