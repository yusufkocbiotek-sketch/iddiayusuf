import json
import os

JSON_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\gecmis_maclar.json'
REPORT_PATH = r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Toplu_Analiz_Raporu.md'

# Kural tanımları
def rule_T70(o):
    ms1 = o.get('Maç Sonucu_1', 99)
    alt = o.get('Alt/Üst 2.5_Alt', 99)
    kgyok = o.get('Karşılıklı Gol_Yok', 99)
    iy0 = o.get('1. Yarı Sonucu_0', 99)
    return (1.30 <= ms1 <= 1.45) and (alt <= 1.60) and (kgyok <= 1.55) and (iy0 > 2.15)

def check_T70(m):
    return m.get('skor_ev', 0) > m.get('skor_dep', 0) and m.get('skor_ev', 0) + m.get('skor_dep', 0) < 3

def rule_T68(o):
    ms1 = o.get('Maç Sonucu_1', 99)
    kgvar = o.get('Karşılıklı Gol_Var', 99)
    ust = o.get('Alt/Üst 2.5_Üst', 99)
    return (1.60 <= ms1 <= 1.64) and (kgvar <= 1.45 or ust <= 1.50) and (kgvar > 1.35) and (ust > 1.35)

def check_T68(m):
    return m.get('skor_1y_ev', 1) == 0 and m.get('skor_1y_dep', 1) == 0

def rule_G80(o):
    ms1 = o.get('Maç Sonucu_1', 99)
    kgyok = o.get('Karşılıklı Gol_Yok', 99)
    ust = o.get('Alt/Üst 2.5_Üst', 99)
    return (1.05 <= ms1 <= 1.15) and (kgyok <= 1.40) and (ust <= 1.60)

def check_G80(m):
    return m.get('skor_ev', 0) > m.get('skor_dep', 1) and m.get('skor_dep', 1) == 0

def rule_T50(o):
    ms0 = o.get('Maç Sonucu_0', 99)
    alt = o.get('Alt/Üst 2.5_Alt', 99)
    kgyok = o.get('Karşılıklı Gol_Yok', 99)
    iy0 = o.get('1. Yarı Sonucu_0', 99)
    return (ms0 < 2.70) and (alt <= 1.40) and (kgyok <= 1.55) and (iy0 <= 1.80)

def check_T50(m):
    ev = m.get('skor_ev', 0)
    dep = m.get('skor_dep', 0)
    return m.get('skor_1y_ev', 1) == 0 and m.get('skor_1y_dep', 1) == 0 and (ev + dep > 0) and (ev == 0 or dep == 0)

def rule_G20(o):
    kgvar = o.get('Karşılıklı Gol_Var', 99)
    kgyok = o.get('Karşılıklı Gol_Yok', 0)
    alt = o.get('Alt/Üst 2.5_Alt', 99)
    ms1 = o.get('Maç Sonucu_1', 99)
    ms0 = o.get('Maç Sonucu_0', 0)
    return (abs(kgvar - kgyok) <= 0.05) and (alt <= 1.60) and (1.80 <= ms1 <= 1.95) and (ms0 > 3.00)

def check_G20(m):
    return m.get('skor_ev', 0) > m.get('skor_dep', 0) and m.get('skor_ev', 0) + m.get('skor_dep', 0) <= 2

def rule_G11(o):
    ms1 = o.get('Maç Sonucu_1', 99)
    iy0 = o.get('1. Yarı Sonucu_0', 99)
    iyalt = o.get('1. Yarı Alt/Üst 1.5_Alt', 99)
    return (ms1 < 1.25) and (2.30 <= iy0 <= 2.45) and (iyalt <= 1.35)

def check_G11(m):
    return m.get('skor_1y_ev', 1) == 0 and m.get('skor_1y_dep', 1) == 0 and m.get('skor_ev', 0) > m.get('skor_dep', 0)

def rule_T85(o):
    alt = o.get('Alt/Üst 2.5_Alt', 99)
    kgyok = o.get('Karşılıklı Gol_Yok', 99)
    dep_alt = o.get('Deplasman Alt/Üst 0.5_Alt', 0)
    return (alt <= 1.65) and (kgyok <= 1.75) and (dep_alt > 2.00)

def check_T85(m):
    return m.get('skor_dep', 0) > 0

rules = {
    'T70': (rule_T70, check_T70),
    'T68': (rule_T68, check_T68),
    'G80': (rule_G80, check_G80),
    'T50': (rule_T50, check_T50),
    'G20': (rule_G20, check_G20),
    'G11': (rule_G11, check_G11),
    'T85': (rule_T85, check_T85),
}

# Lig Bazlı Kuralların JSON'dan Yüklenmesi
LIG_KURALLARI_PATH = r'C:\Users\YUSUF\Desktop\iddiayusuf-main\public\data\lig_kurallari.json'
if os.path.exists(LIG_KURALLARI_PATH):
    with open(LIG_KURALLARI_PATH, 'r', encoding='utf-8') as f:
        lig_kurallari = json.load(f)
        
    for kural in lig_kurallari:
        kodu = kural['kural_kodu']
        hedef = kural['hedef']
        
        # Dinamik kural koşul fonksiyonu
        def make_cond_func(k):
            def cond_func(o, match_lig):
                if match_lig != k['lig']: return False
                
                ms1 = o.get('Maç Sonucu_1', 99)
                kgyok = o.get('Karşılıklı Gol_Yok', 99)
                kgvar = o.get('Karşılıklı Gol_Var', 0)
                alt = o.get('Alt/Üst 2.5_Alt', 99)
                ust = o.get('Alt/Üst 2.5_Üst', 0)
                
                if not (k['ms1_min'] <= ms1 <= k['ms1_max']): return False
                
                if k['kg_fav'] == 'var' and kgvar >= kgyok: return False
                if k['kg_fav'] == 'yok' and kgyok >= kgvar: return False
                
                if k['au_fav'] == 'alt' and alt >= ust: return False
                if k['au_fav'] == 'ust' and ust >= alt: return False
                
                # İkincil Kilit Kontrolü
                ikincil = k.get('ikincil_kilitler', {})
                if ikincil:
                    for lock_key, lock_range in ikincil.items():
                        val = o.get(lock_key)
                        if val is None: return False
                        if not (lock_range['min'] <= val <= lock_range['max']): return False
                
                return True
            return cond_func
            
        # Dinamik kural doğrulama fonksiyonu
        def make_check_func(h):
            def check_func(m):
                ev = m.get('skor_ev', 0)
                dep = m.get('skor_dep', 0)
                if h == 'KG Var': return ev > 0 and dep > 0
                if h == 'KG Yok': return ev == 0 or dep == 0
                if h == '2.5 Alt': return (ev + dep) < 3
                if h == '2.5 Üst': return (ev + dep) >= 3
                if h == 'MS 1': return ev > dep
                return False
            return check_func
            
        rules[kodu] = (make_cond_func(kural), make_check_func(hedef))

results = {k: {'success': [], 'exceptions': []} for k in rules}

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    matches = json.load(f)['matches']

# Sadece 0 ile 23000 arasındaki maçları filtrele
target_matches = [m for m in matches if 0 <= m.get('index', 0) <= 23000]

REPORT_PATH_NEW = r'C:\Users\YUSUF\.gemini\antigravity\brain\d6708fe4-425a-4c22-8337-22d967dd2651\Toplu_Analiz_Raporu_Devasa.md'

for m in target_matches:
    o = m.get('oranlar', {})
    if not o: continue
    
    for rule_name, (cond_func, check_func) in rules.items():
        try:
            # Lig kuralları için 2 parametre gerekiyor (oranlar, lig)
            if rule_name.count('-') > 0 and rule_name.split('-')[1].isdigit():
                lig = m.get('lig', '').strip()
                if cond_func(o, lig):
                    if check_func(m):
                        results[rule_name]['success'].append(m)
                    else:
                        results[rule_name]['exceptions'].append(m)
            else:
                # Standart kurallar için 1 parametre (oranlar)
                if cond_func(o):
                    if check_func(m):
                        results[rule_name]['success'].append(m)
                    else:
                        results[rule_name]['exceptions'].append(m)
        except Exception:
            pass

# Rapor oluştur
with open(REPORT_PATH_NEW, 'w', encoding='utf-8') as f:
    f.write("# 🚀 ANTIGRAVITY DEVASA TOPLU ANALİZ RAPORU (İndeks 0 - 23000)\n\n")
    f.write("Bu rapor, tam 23.000 maçın yepyeni Çift Kilitli (Ana Oran + Alt Oran) Kural Motoru tarafından otomatik taranması sonucu oluşturulmuştur.\n\n")
    
    for rule_name, data in results.items():
        succ = len(data['success'])
        exc = len(data['exceptions'])
        total = succ + exc
        rate = (succ / total * 100) if total > 0 else 0
        
        f.write(f"## 📌 KURAL: {rule_name}\n")
        f.write(f"- **Toplam Eşleşme:** {total}\n")
        f.write(f"- **Başarı (Beklenen Skor):** {succ}\n")
        f.write(f"- **İstisna (Farklı Biten):** {exc}\n")
        f.write(f"- **Başarı Oranı:** %{rate:.2f}\n\n")
        
        if exc > 0:
            f.write("### ⚠️ İstisna Maçlar (Kök Neden Analizi İçin):\n")
            for ex_m in data['exceptions'][:5]: # İlk 5 istisnayı göster
                idx = ex_m.get('index')
                ev = ex_m.get('ev_sahibi')
                dep = ex_m.get('deplasman')
                skor = f"{ex_m.get('skor_ev')}-{ex_m.get('skor_dep')}"
                iy_skor = f"{ex_m.get('skor_1y_ev')}-{ex_m.get('skor_1y_dep')}"
                f.write(f"  - İndeks: {idx} | {ev} - {dep} | İY: {iy_skor} | MS: {skor}\n")
            if exc > 5:
                f.write(f"  - *(Ve {exc - 5} maç daha...)*\n")
        f.write("\n---\n\n")

print("Rapor başarıyla oluşturuldu!")
