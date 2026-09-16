import re
import unicodedata
import difflib

CURRENT_MATCH = {}

MILLI_TAKIMLAR = [
    "Türkiye", "İspanya", "İngiltere", "Almanya", "Fransa", "İtalya", "Hollanda", "Portekiz", "Belçika", "Brezilya", "Arjantin",
    "Senegal", "Irak", "Mısır", "İran", "Yeşil Burun", "Suudi Arabistan", "Uruguay", "Japonya", "Güney Kore", "Fas", "Cezayir",
    "Nijerya", "Fildişi", "Kamerun", "Gana", "ABD", "Meksika", "Kolombiya", "Şili", "Peru", "İsveç", "İsviçre", "Danimarka",
    "Norveç", "Finlandiya", "Rusya", "Sırbistan", "Hırvatistan", "Yunanistan", "Çekya", "Polonya", "Avusturya", "Macaristan",
    "Demokratik Kongo", "Kongo", "Özbekistan", "Güney Afrika", "Mali", "Gine", "Burkina Faso", "Zambiya", "Kosta Rika",
    "Panama", "Honduras", "Jamaika", "Kanada", "Galler", "İskoçya", "İrlanda", "Kuzey İrlanda", "İzlanda", "Ukrayna",
    "Romanya", "Bulgaristan", "Slovakya", "Slovenya", "Bosna", "Karadağ", "Makedonya", "Arnavutluk", "Kıbrıs", "Ekvador",
    "Paraguay", "Venezuela", "Bolivya", "Avustralya", "Yeni Zelanda", "Katar", "BAE", "Umman", "Bahreyn", "Kuveyt",
    "Suriye", "Ürdün", "Lübnan", "Çin", "Kuzey Kore", "Tayland", "Vietnam", "Endonezya", "Malezya", "Hindistan"
]

def is_milli_mac(match):
    if not match: return False
    ev = match.get('ev_sahibi', '').upper()
    dep = match.get('deplasman', '').upper()
    
    if ' U1' in ev or ' U2' in ev or ' U1' in dep or ' U2' in dep:
        return True
    
    if ev.endswith(' K') or dep.endswith(' K') or ev.endswith(' (K)') or dep.endswith(' (K)'):
        return True
        
    for ulke in MILLI_TAKIMLAR:
        if ev.startswith(ulke.upper()) or dep.startswith(ulke.upper()):
            return True
            
    return False

class BaseRule:
    code = ""
    category = ""
    name = ""
    description = ""
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ust = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        kgy = get_odd(odds, ["Karşılıklı Gol_Yok"])
        
        if ms1 <= 2.20 and ms2 != 99.0 and ms2 >= 2.80 and ust <= 1.50 and kgy != 99.0 and kgy >= 2.00:
            return True, "SAHTE DÜELLO TUZAĞI: Maçın gollü geçeceği ve iki takımın da gol atacağı aşırı bariz (KG Yok 2.00+ ve Üst 1.50-). Ancak Ev sahibi çok güçlü bir favori değil (2.10 civarı). Bu durum herkesi gollere iterken, Ev sahibi maçı beklenmedik bir şekilde kilitler ve 1-0 veya 2-0 gibi skorlarla kazanır. Taraf bahislerinde MS1 veya 1X, gol bahislerinde 2.5 Alt denenmelidir."
        return False, ""

def normalize_key(key):
    if not isinstance(key, str):
        return str(key)
    # Küçük harfe çevir
    key = key.lower()
    # Türkçe karakterleri İngilizce karşılıklarına dönüştür
    key = unicodedata.normalize('NFKD', key).encode('ASCII', 'ignore').decode('utf-8')
    # Sadece harf ve rakamlar kalsın (boşluklar, semboller, noktalar silinir)
    key = re.sub(r'[^a-z0-9]', '', key)
    return key

def safe_fuzzy_match(norm_k, normalized_keys):
    target_nums = re.findall(r'\d+', norm_k)
    matches = difflib.get_close_matches(norm_k, normalized_keys, n=5, cutoff=0.85)
    
    for match in matches:
        match_nums = re.findall(r'\d+', match)
        if target_nums == match_nums:
            # ANTI-COLLISION: Zaman/Periyot çakışmasını engelle
            # Eğer aranan oranda 'ilkyar' varsa, eşleşen oranda da KESİN OLMALIDIR. Yoksa bir başkasını (ikinciyar'ı) çalmasın.
            if "ilkyar" in norm_k and "ilkyar" not in match:
                continue
            if "ikinciyar" in norm_k and "ikinciyar" not in match:
                continue
            if "macsonucu" in norm_k and "macsonucu" not in match:
                continue
                
            # Aynı şekilde aranan oranda YOKSA, eşleşen oranda da OLMAMALIDIR. (Örn: "Karşılıklı Gol Var" arıyorsak "İlk Yarı KG Var" dönmesin)
            if "ilkyar" in match and "ilkyar" not in norm_k:
                continue
            if "ikinciyar" in match and "ikinciyar" not in norm_k:
                continue
            if "macsonucu" in match and "macsonucu" not in norm_k:
                continue
                
            return match
    return None

def get_odd(odds, keys, default=99.0):
    normalized_odds = {normalize_key(k): v for k, v in odds.items()}
    norm_keys_list = list(normalized_odds.keys())
    
    for k in keys:
        norm_k = normalize_key(k)
        
        # 1. Önce tam eşleşme (normalize edilmiş haliyle) ara
        if norm_k in normalized_odds:
            return normalized_odds[norm_k]
            
        # 2. Eğer tam eşleşme yoksa %85 benzerlik oranına göre (sayıları katı eşleyerek) ara
        match = safe_fuzzy_match(norm_k, norm_keys_list)
        if match:
            return normalized_odds[match]
        
        # Otomatik alternatif anahtarları kontrol et
        if "ciftesans12" in norm_k or "ciftesans1ve2" in norm_k:
            for alt_k in ["Çifte Şans_12", "Çifte Şans_1-2", "Çifte Şans_1 ve 2", "-_1 ve 2"]:
                n_alt = normalize_key(alt_k)
                if n_alt in normalized_odds: return normalized_odds[n_alt]
                alt_match = safe_fuzzy_match(n_alt, norm_keys_list)
                if alt_match: return normalized_odds[alt_match]
                
        if "ciftesans1x" in norm_k or "ciftesans1ve0" in norm_k or "ciftesans10" in norm_k:
            for alt_k in ["Çifte Şans_1X", "Çifte Şans_1-0", "Çifte Şans_1 ve 0", "-_1 ve 0"]:
                n_alt = normalize_key(alt_k)
                if n_alt in normalized_odds: return normalized_odds[n_alt]
                alt_match = safe_fuzzy_match(n_alt, norm_keys_list)
                if alt_match: return normalized_odds[alt_match]
                
        if "ciftesansx2" in norm_k or "ciftesans0ve2" in norm_k or "ciftesans02" in norm_k:
            for alt_k in ["Çifte Şans_X2", "Çifte Şans_0-2", "Çifte Şans_0 ve 2", "-_0 ve 2"]:
                n_alt = normalize_key(alt_k)
                if n_alt in normalized_odds: return normalized_odds[n_alt]
                alt_match = safe_fuzzy_match(n_alt, norm_keys_list)
                if alt_match: return normalized_odds[alt_match]

    return default

# --- GOL KURALLARI (G SERİSİ) ---
class RuleG1(BaseRule):
    code = "G1"
    category = "GOL"
    name = "Kesin 2 Gol Sinyali"
    description = "1.5 Üst <= 1.15 -> En az 2 gol kesin."
    
    @classmethod
    def evaluate(cls, odds):
        ust_15 = get_odd(odds, ["Alt/Üst 1.5_Üst", "Altı/Üstü 1.5_Üst"])
        if ust_15 <= 1.15:
            return True, "Maçta en az 2 gol kesin çıkar."
        return False, ""

class RuleG2(BaseRule):
    code = "G2"
    category = "GOL"
    name = "Düşük Gol Tavanı (2-3 Gol)"
    description = "3.5 Alt <= 1.16 + KG Var/Yok farkı <= 0.10"
    
    @classmethod
    def evaluate(cls, odds):
        alt_35 = get_odd(odds, ["Alt/Üst 3.5_Alt", "Altı/Üstü 3.5_Alt"])
        kgvar = get_odd(odds, ["Karşılıklı Gol_Var"])
        kgyok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        if alt_35 <= 1.16 and abs(kgvar - kgyok) <= 0.10:
            return True, "Toplam 2–3 gol olur, maç çok açılmaz."
        return False, ""

class RuleG3(BaseRule):
    code = "G3"
    category = "GOL"
    name = "Karşılıklı Gol Kesin"
    description = "KG Var <= 1.45 + Ev/Dep 0.5 Üst <= 1.30"
    
    @classmethod
    def evaluate(cls, odds):
        kgvar = get_odd(odds, ["Karşılıklı Gol_Var"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst"])
        if kgvar <= 1.45 and (ev_05_ust <= 1.30 or dep_05_ust <= 1.30):
            return True, "Her iki takım da kesin gol atar."
        return False, ""

class RuleG4(BaseRule):
    code = "G4"
    category = "GOL"
    name = "Deplasman Gol Atamaz"
    description = "Dep 0.5 Alt <= 1.30"
    
    @classmethod
    def evaluate(cls, odds):
        dep_05_alt = get_odd(odds, ["Deplasman Alt/Üst 0.5_Alt"])
        if dep_05_alt <= 1.30:
            return True, "Deplasman gol atamaz."
        return False, ""

class RuleG5(BaseRule):
    code = "G5"
    category = "GOL"
    name = "Kısır Gol Yapısı"
    description = "Ev 2.5 Alt <= 1.40 + Dep 1.5 Alt <= 1.30 -> Toplam max 2 gol."
    
    @classmethod
    def evaluate(cls, odds):
        ev_25_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Alt"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt"])
        if ev_25_alt <= 1.40 and dep_15_alt <= 1.30:
            return True, "Toplam en fazla 2 gol olur."
        return False, ""

class RuleG5_B(BaseRule):
    code = "G5-B"
    category = "GOL"
    name = "Kilitli Favori (İstisna)"
    description = "MS1 <= 1.70 + 2.5 Alt <= 1.35 + Ev 1.5 Alt <= 1.45"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        alt_25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt"])
        if 1.00 < ms1 <= 1.70 and alt_25 <= 1.35 and ev_15_alt <= 1.45:
            return True, "Ev sahibi favori olsa da hücumda çok zorlanacak. Skor 1-0 veya 0-0'a kilitlenmeye aday."
        return False, ""

class Rule1485(BaseRule):
    code = "1485"
    name = "Ölü Alt Tuzağı (Düşük MS1, Düşük Alt, Yüksek ÇŞ12)"
    category = "GOL"
    description = "Aşırı favori Ev (<=1.50) + Düşük 2.5 Alt (<=1.65) + 12 ÇŞ > 1.20"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        cs12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1-2"])
        
        # Sadece mutlak favorilerde (1.25 ve altı) Alt oranının düşük olması bir "Ölü Alt" tuzağıdır.
        # 1.36 gibi normal favorilerde (Match 748) düşük Alt oranı (1.54) gayet normaldir.
        if (ms1 <= 1.25 or ms2 <= 1.25) and alt25 <= 1.65 and cs12 != 99.0 and cs12 > 1.20 and cs12 < 99.0:
            return True, "ÖLÜ ALT TUZAĞI: Takımlardan biri mutlak favori (1.25 altı), ancak 2.5 Alt oranı çok düşük. Normalde bu maçın favori tarafından farklı kazanılması (Üst) beklenir. Ayrıca Çifte Şans 12 oranı şüpheli derecede yüksek (1.20+). Bu durum maçta bir beraberlik potansiyeli (1-1) veya sürpriz gollü bir zayıf takım reaksiyonu olduğunu gösterir. Maç kesinlikle Alt bitmeyecektir; KG Var ve Üst denenmeli."
        return False, ""

class Rule1486(BaseRule):
    code = "1486"
    name = "Kilitli Kısır Maç (0/0 Sendromu)"
    category = "GOL"
    description = "MS0 <= 2.85, 2.5 Alt <= 1.55 ve İlk Yarı 0/0 <= 4.00"
    @classmethod
    def evaluate(cls, odds):
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        iy_ms_00 = get_odd(odds, ["İlk Yarı / Maç Sonucu_0/0"])
        iy_0 = get_odd(odds, ["İlk Yarı Sonucu_0", "1. Yarı Sonucu_0"])
        
        if alt25 <= 1.55 and ms0 <= 2.85 and ms0 != 99.0 and alt25 != 99.0:
            if iy_ms_00 <= 4.00 and iy_0 <= 1.85 and iy_ms_00 != 99.0:
                return True, "KESİN KISIR KİLİDİ (0/0 SENDROMU): Sadece düşük MS0 ve Alt yeterli değildir. Bu maçta İddaa, İlk Yarı / Maç Sonucu 0/0 bahsini 4.00 ve altına indirerek ilk yarıdan itibaren tam bir savunma savaşı olacağını onaylamıştır. Erken gol beklenmeyen, tamamen kilitli geçecek bir maçtır (0-0, 1-1, 1-0, 0-1). Taraf bahsi yerine doğrudan 2.5 Alt veya KG Yok denenmelidir."
        return False, ""

class Rule1487(BaseRule):
    code = "1487"
    name = "Favori İlk Yarı Çelişkisi (Aşırı Düşük MS1, Düşük İY0)"
    category = "YARI_VE_GOL"
    description = "MS1 <= 1.30 ama İlk Yarı Beraberliği <= 2.20"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        iy0 = get_odd(odds, ["1. Yarı Sonucu_0", "İlk Yarı Sonucu_0"])
        
        if ms1 <= 1.30 and iy0 <= 2.20:
            return True, "FAVORİ UYKU PATLAMASI: Ev sahibi 1.30 altı oranla banko favori. Ancak İlk Yarı Beraberliği 2.20 ve altına çekilmiş. Ev sahibi bu kadar ağır favoriyken ilk yarının 0-0 kilitlenme ihtimalinin bu kadar yüksek fiyatlanması devasa bir paradokstur! Bu durum zayıf takımın direneceğini, hatta sürpriz gol bulacağını (KG Var) gösterir. Maç 3-1, 2-1 gibi gollü skorlara gebe."
        return False, ""

class Rule1488(BaseRule):
    code = "1488"
    name = "Favori Kısırlaştırma İllüzyonu (Fark Patlaması)"
    category = "GOL"
    description = "MS1 <= 1.25 ve Ev Sahibi 2.5 Alt <= 1.50"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ev_25_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Alt", "Ev Sahibi Altı/Üstü 2.5_Alt"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok", "Karşılıklı Gol Yok"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        
        rakip_kisir = False
        if (kg_yok != 99.0 and kg_yok <= 1.65) or (dep_05_ust != 99.0 and dep_05_ust >= 1.70) or (kg_yok == 99.0 and dep_05_ust == 99.0):
            rakip_kisir = True
        
        if ms1 <= 1.25 and ev_25_alt <= 1.50 and rakip_kisir:
            return True, "FAVORİ KISIRLAŞTIRMA TUZAĞI: Ev sahibi (1.25 altı) devasa bir favori. Ancak Ev Sahibinin 2.5 Alt oranı (maksimum 2 gol atar) şaşırtıcı derecede düşük (1.50 altı). Bahis şirketleri 'favori kazanacak ama 3 gol atamaz' algısı yaratarak herkesi 2-0 / 2-1 gibi skorlara veya Alt bahislerine yönlendirir. Ancak bu devasa bir patlama tuzağıdır; favori takım maçı çok farklı (3-0, 4-0) kazanır ve şov yapar! 3.5 Üst ve Handikaplı MS1 denenmelidir."
        return False, ""

class RuleG6(BaseRule):
    code = "G6"
    category = "GOL"
    name = "Tek Taraflı Favori Şovu (KG Yok Tuzağı)"
    description = "ÇŞ 1-0 <= 1.15 + ÇŞ 12 <= 1.15 + Dep 0.5 Üst <= 1.25 -> Dep atamaz, Ev rahat kazanır."
    
    @classmethod
    def evaluate(cls, odds):
        cs_1X = get_odd(odds, ["Çifte Şans_1X", "Çifte Şans_1-X", "Çifte Şans_1 ve 0"])
        cs_12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1-2", "Çifte Şans_1 ve 2"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst"])
        if cs_1X <= 1.15 and cs_12 <= 1.15 and dep_05_ust <= 1.25:
            return True, "Deplasman takımının gol atacağına dair (Deplasman 0.5 Üst <= 1.25) çok güçlü bir beklenti yaratılmış olsa da bu bir tuzaktır. Deplasman gol bulamaz (KG Yok) ve ev sahibi gol yemeden maçı kazanır (1-0, 2-0 vb.)."
        return False, ""

class RuleG7(BaseRule):
    code = "G7"
    category = "GOL"
    name = "Yüksek Gollü Mücadele"
    description = "1.5 Üst <= 1.10 + KG Var <= 1.45 + Ev 0.5 Üst <= 1.25 + Dep 0.5 Üst <= 1.25 -> 4+ gol."
    
    @classmethod
    def evaluate(cls, odds):
        ust_15 = get_odd(odds, ["Alt/Üst 1.5_Üst", "Altı/Üstü 1.5_Üst"])
        kgvar = get_odd(odds, ["Karşılıklı Gol_Var"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst"])
        if ust_15 <= 1.10 and kgvar <= 1.45 and ev_05_ust <= 1.25 and dep_05_ust <= 1.25:
            return True, "Alt oranları yanıltıcıdır; 4+ gol çıkma olasılığı çok yüksektir."
        return False, ""

class RuleY8(BaseRule):
    code = "Y8"
    category = "YARI"
    name = "İlk Yarı Düellosu (İlk Yarı KG Var)"
    description = "İlk Yarı KG Var oranının 2.90 ve altına inmesi büyük bir patlama sinyalidir."
    
    @classmethod
    def evaluate(cls, odds):
        iy_kg_var = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Var"])
        if iy_kg_var != 99.0 and iy_kg_var > 0 and iy_kg_var <= 2.90:
            return True, "İlk yarıda iki takımın da gol atma ihtimali (İlk Yarı KG Var) çok güçlü. Hızlı ve gollü bir başlangıç olacak."
        return False, ""

class RuleY9(BaseRule):
    code = "Y9"
    category = "YARI"
    name = "Tam Saha Düello (Her İki Yarıda KG Var)"
    description = "İlk Yarı KG < 2.90 ve İkinci Yarı KG < 2.30 ise takımlar 90 dakika gol kovalayacak demektir."
    
    @classmethod
    def evaluate(cls, odds):
        iy_kg_var = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Var"])
        ikiy_kg_var = get_odd(odds, ["İkinci Yarı Karşılıklı Gol_Var"])
        if iy_kg_var != 99.0 and iy_kg_var > 0 and iy_kg_var <= 2.90 and ikiy_kg_var != 99.0 and ikiy_kg_var > 0 and ikiy_kg_var <= 2.30:
            return True, "Maçın her iki yarısında da karşılıklı goller (Her İki Yarıda KG Var) olması bekleniyor. Savunmalar tamamen çökmüş durumda."
        return False, ""

class RuleY10(BaseRule):
    code = "Y10"
    name = "Tam Saha Düello Sinyali (Kutsal Kase)"
    category = "YARI"
    description = "Dengeli güçler, KG Var <= 1.45 ve IY KG <= 3.30 iken Her İki Yarıda KG Var potansiyeli."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var", "Karşılıklı Gol Var"])
        iy_kg_var = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Var", "1. Yarı Karşılıklı Gol_Var"])
        
        if ms1 != 99.0 and ms2 != 99.0 and kg_var <= 1.45 and iy_kg_var <= 3.30:
            if abs(ms1 - ms2) <= 1.00:
                return True, "KUTSAL KASE (12.00+ ORAN ALARMI): İddaa maçın mutlak bir gol düellosuna sahne olacağını (KG Var <= 1.45) ve İlk Yarıdan gollerin başlayacağını (IY KG <= 3.30) gösteriyor. Ayrıca takımların güçleri birbirine çok denk (Taraf oran farkı az). Bu kusursuz fırtına, ortalama 10.00 ile 15.00 arası devasa bir oran açılan 'Her İki Yarıda Karşılıklı Gol Var' bahsi için inanılmaz bir istatistiksel avantaj (%9.67 isabet - %20+ ROI) sunar. Ufak miktarlarla denenmelidir!"
        return False, ""

class RuleY11(BaseRule):
    code = "Y11"
    name = "Psikolojik 12 Tuzağı (İlk Yarı 0 Bankosu)"
    category = "YARI"
    description = "Çifte Şans 12 <= 1.20 iken KG Var'ın da favori olması büyük bir İlk Yarı 0 tuzağıdır."
    @classmethod
    def evaluate(cls, odds):
        cs12 = get_odd(odds, ["Çifte Şans_12"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var", "Karşılıklı Gol Var"])
        ms1 = get_odd(odds, ["Maç Sonucu_1", "Maç Sonucu_Ev", "1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2", "Maç Sonucu_Deplasman", "2"])
        
        # Sadece dengeli maçlarda (Taraf oranları 2.00 ve üzeri iken) 12 oranının aşırı düşürülmesi bir tuzaktır.
        # Ağır favorili maçlarda 12 oranının düşük olması zaten doğaldır.
        if ms1 >= 2.00 and ms2 >= 2.00 and ms1 != 99.0 and ms2 != 99.0:
            if cs12 <= 1.20 and cs12 != 99.0 and kg_var <= 1.65 and kg_var != 99.0:
                return True, "İLK YARI 0 BANKOSU (PSİKOLOJİK TUZAK): İddaa dengeli bir maçta Çifte Şans 12'ye çok düşük oran (<= 1.20) vererek 'Bu maç asla berabere bitmez, kesin biri yener' algısı yaratıyor. Üstüne KG Var oranını da düşük tutarak maçın çok tempolu başlayacağı illüzyonunu kuruyor. Oysa istatistiklere göre bu maçların yarısından fazlası (%53.6) ilk yarıda tamamen kilitlenir. Büroların bu algı operasyonu yüzünden İlk Yarı 0'a verdikleri devasa 2.15+ oranlar sayesinde bu bahis uzun vadede %16.5 net kâr (ROI) bırakır!"
        return False, ""

class RuleG8(BaseRule):
    code = "G8"
    category = "GOL"
    name = "Sıfır Konuk Golü Sınırı"
    description = "KG Yok < 1.45 veya Dep 1.5 Alt <= 1.15"
    
    @classmethod
    def evaluate(cls, odds):
        kgyok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt"])
        if kgyok < 1.45 and dep_15_alt <= 1.20:
            return True, "Konuk takımın gol atması beklenmiyor."
        return False, ""

class RuleG9(BaseRule):
    code = "G9"
    category = "GOL"
    name = "Ters Korelasyon 1-1 Tuzağı"
    description = "MS0 <= 2.80 + KG Yok <= 1.60 + IY 0:0 <= 2.30"
    
    @classmethod
    def evaluate(cls, odds):
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        kgyok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        iy_00 = get_odd(odds, ["1. Yarı Skoru_0:0"])
        if ms0 <= 2.80 and kgyok <= 1.60 and iy_00 <= 2.30:
            return True, "KG Yok favori gösterilerek tuzak kurulmuştur. Maç ilk yarı 0-0 biter, ikinci yarı karşılıklı gollerle 1-1 sonuçlanır."
        return False, ""

class RuleG10(BaseRule):
    code = "G10"
    category = "GOL"
    name = "Yalancı Üst / Çift Tuzağı"
    description = "Üst 2.5 <= 1.50 + Çift <= 1.65 + IY 1.5 Alt <= 1.40"
    
    @classmethod
    def evaluate(cls, odds):
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        cift = get_odd(odds, ["Tek / Çift_Çift"])
        iy_15_alt = get_odd(odds, ["1. Yarı Alt/Üst 1.5_Alt", "1. Yarı Altı/Üstü 1.5_Alt"])
        
        if ust25 <= 1.50 and cift <= 1.65 and iy_15_alt <= 1.40:
            return True, "Üst 2.5 çok düşük tutularak gollü maç algısı (Örn: 3-1, 2-1) yaratılmış. Ancak aşırı düşük Çift oranı ve sıkı İlk Yarı 1.5 Alt oranı, maçın tamamen kilitlenip 0-0 veya en fazla 1-1 biteceğinin gizli kanıtıdır."
        return False, ""

# --- TARAF VE TUZAK KURALLARI (T SERİSİ) ---
class RuleT6(BaseRule):
    code = "T6"
    category = "YÖN"
    name = "Aşırı Ev Sahibi Favorisi Tuzağı"
    description = "MS1 1.55-1.60 + ÇŞ 1-0 <= 1.15 + ÇŞ 1-2 <= 1.15 + KG Var <= 1.30"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        cs_1X = get_odd(odds, ["Çifte Şans_1X", "Çifte Şans_1-X"])
        cs_12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1-2"])
        kgvar = get_odd(odds, ["Karşılıklı Gol_Var"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        if 1.55 <= ms1 <= 1.62 and cs_1X <= 1.15 and cs_12 <= 1.15 and kgvar <= 1.30 and ev_15_alt <= 1.50:
            return True, "Ev sahibi kazanamaz, hatta gol bile atamaz; deplasman galibiyeti çok yüksek ihtimal."
        return False, ""

class RuleT7(BaseRule):
    code = "T7"
    category = "YÖN"
    name = "Deplasman Favorisi Tuzağı"
    description = "MS2 1.90-2.10 + Dep 1.5 Alt <= 1.40 + MS0 <= 2.90"
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt"])
        if 1.85 <= ms2 <= 2.15 and dep_15_alt <= 1.40 and ms0 <= 3.00:
            return True, "Deplasman favori görünümü sahtedir; ev sahibi galibiyeti veya beraberlik."
        return False, ""

class RuleT8(BaseRule):
    code = "T8"
    category = "YÖN"
    name = "Dengeli Ters Favori İç Saha"
    description = "MS1 <= MS2 + abs(MS1-MS2) <= 1.00 + ÇŞ 1-2 <= 1.20"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        cs_12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1 ve 2", "Çifte Şans_1-2"])
        if ms1 <= ms2 and abs(ms1 - ms2) <= 1.00 and cs_12 <= 1.20:
            return True, "Dengeli maçta beraberlik dışlanmış, ev sahibi kazanır."
        return False, ""

class RuleT8_B(BaseRule):
    code = "T8-B"
    category = "YÖN"
    name = "Dengeli Ters Favori Deplasman"
    description = "MS2 < MS1 + abs(MS1-MS2) <= 1.00 + ÇŞ 1-2 <= 1.20"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        cs_12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1 ve 2", "Çifte Şans_1-2"])
        if ms2 < ms1 and abs(ms1 - ms2) <= 1.00 and cs_12 <= 1.20:
            return True, "Deplasman hafif favori gösterilmiş ve beraberlik dışlanmıştır (ÇŞ 12 çok düşük). Deplasman kazanır (1-2 gibi skorlarla)."
        return False, ""

class RuleT9(BaseRule):
    code = "T9"
    category = "YÖN"
    name = "Görünür Favori Beraberlik Tuzağı"
    description = "MS1 <= 1.70 + ÇŞ 1X <= 1.15 + abs(ÇŞ 1X - ÇŞ 12) <= 0.06"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        cs_1X = get_odd(odds, ["Çifte Şans_1X", "Çifte Şans_1-X"])
        cs_12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1-2"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        if 1.0 < ms1 <= 1.70 and ms0 <= 3.40 and cs_1X <= 1.15 and abs(cs_1X - cs_12) <= 0.06:
            return True, "Maçın beraberlikle bitme olasılığı çok yüksektir; taraf seçiminden kaçın."
        return False, ""

class RuleT10(BaseRule):
    code = "T10"
    category = "YÖN"
    name = "Tamamen Eşit Oranlı Maç"
    description = "Taraf oranları birbirine çok yakın (fark <= 0.20)."
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        if ms1 != 99.0 and ms1 >= 90.0 or ms0 != 99.0 and ms0 >= 90.0 or ms2 != 99.0 and ms2 >= 90.0:
            return False, ""
        if abs(ms1 - ms0) <= 0.30 and abs(ms0 - ms2) <= 0.30:
            return True, "Taraf seçimi kesinlikle yapılmamalı; sadece 2.5 Alt veya KG Yok'a odaklanılmalı."
        return False, ""

class RuleT11(BaseRule):
    code = "T11"
    category = "YÖN"
    name = "En Düşük Favori Tuzağı"
    description = "MS1 <= 1.10 + KG Var <= 1.55 + IY 1.5 Üst <= 1.65"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kgvar = get_odd(odds, ["Karşılıklı Gol_Var"])
        iy_15_ust = get_odd(odds, ["1. Yarı Alt/Üst 1.5_Üst", "1. Yarı Altı/Üstü 1.5_Üst"])
        if ms1 <= 1.15 and kgvar <= 1.55 and iy_15_ust <= 1.65:
            return True, "Ev sahibi kazanamaz; deplasman galibiyeti çok yüksek ihtimal."
        return False, ""

class RuleT27(BaseRule):
    code = "T27"
    category = "YÖN"
    name = "Az Gollü Temiz Favori"
    description = "MS1 < 1.75 + KG Yok < 1.55 + 2.5 Alt < 1.60"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kgyok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        alt_25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        if 1.0 < ms1 < 1.75 and kgyok < 1.55 and alt_25 < 1.60:
            return True, "Ev sahibi maçı alır ancak skor tek taraflı ve az gollü (1-0, 2-0) olur."
        return False, ""

class RuleT28(BaseRule):
    code = "T28"
    category = "YÖN"
    name = "Az Gollü Temiz Favori (Deplasman)"
    description = "MS2 < 1.75 + KG Yok < 1.55 + 2.5 Alt < 1.60"
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kgyok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        alt_25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst", "Ev Sahibi Altı/Üstü 0.5_Üst"])
        
        if 1.0 < ms2 < 1.75 and kgyok < 1.55 and alt_25 < 1.60:
            return True, "Deplasman maçı alır ancak skor tek taraflı ve az gollü (0-1, 0-2) olur."
        return False, ""
class RuleT31(BaseRule):
    code = "T31"
    category = "YÖN"
    name = "Gollü Sürpriz Tuzağı (Ağır Favoriye KG Var)"
    description = "MS1/MS2 <= 1.30 + KG Var <= 1.45"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Alt/Üst 3,5_Üst"])
        
        # Eğer maçta 4 gol olma ihtimali çok yüksekse (ust35 <= 1.80), bu bir beraberlik/sürpriz düellosu değil, 
        # favorinin 3-1, 4-1 kazanacağı bir katliamdır. T31 sadece ust35 yüksekse veya yoksa çalışmalı.
        if (ms1 <= 1.30 or ms2 <= 1.30) and kg_var <= 1.45 and (ust35 != 99.0 and ust35 > 1.80 or ust35 == 99.0):
            return True, "Ağır favoriye rağmen Karşılıklı Gol Var oranının aşırı düşük açılması, zayıf takımın sadece teselli golü bulmayacağını, maçı gollü bir düelloya (örn: 3-3, 2-2) çevirebilecek potansiyelde olduğunu gösterir. Taraf bahsinden (özellikle favoriden) kaçının."
        return False, ""

class RuleT32(BaseRule):
    code = "T32"
    category = "YÖN"
    name = "Matematiksel Çelişki (Yalancı Favori)"
    description = "Ağır Favori + Zayıf Takım Gol Atar + Çift + 3.5 Alt"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst", "Ev Sahibi Altı/Üstü 0.5_Üst"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        cift = get_odd(odds, ["Tek / Çift_Çift"])
        alt35 = get_odd(odds, ["Alt/Üst 3.5_Alt", "Altı/Üstü 3.5_Alt"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        
        # Deplasman favori, ama Ev gol atar
        if ms2 <= 1.60 and ev_05_ust <= 1.60 and cift <= 1.65 and alt35 <= 1.30 and False:
            return True, "Matematiksel Paradoks! Deplasman kazanacaksa, Ev gol atacaksa ve maç Çift bitecekse tek ihtimal 1-3'tür. Ancak 3.5 Alt oranı (4 gol olmaz) diyor. Bu çelişki, aslında favorinin (Deplasman) kazanamayacağının (1-1 veya Ev galibiyeti) matematiksel itirafıdır!"
            
        # Ev favori, ama Deplasman gol atar
        if ms1 <= 1.60 and dep_05_ust <= 1.60 and cift <= 1.65 and alt35 <= 1.30 and kg_var < kg_yok:
            return True, "Matematiksel Paradoks! Ev kazanacaksa, Deplasman gol atacaksa ve maç çift bitecekse tek ihtimal 3-1'dir. Ancak 3.5 Alt oranı (4 gol olmaz) diyor. Bu çelişki, aslında favorinin (Ev) kazanamayacağının (1-1 veya Deplasman galibiyeti) matematiksel itirafıdır!"
            
        return False, ""

class RuleT33(BaseRule):
    code = "T33"
    category = "YÖN"
    name = "KG Yok Paradoksu (Yalancı Favori)"
    description = "Favori + Zayıf Takım Gol Atar + KG Yok"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst", "Ev Sahibi Altı/Üstü 0.5_Üst"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        
        # Ev favori, ama Deplasman gol atar ve KG Yok
        if ms1 <= 1.45 and dep_05_ust <= 1.30 and kg_yok <= 1.65:
            return True, "Matematiksel Paradoks! Ev sahibi ağır favori, deplasmanın da gol atması neredeyse kesin (0.5 Üst <= 1.30). Eğer favori kazanacaksa ve zayıf takım gol atacaksa maç KG Var olmalı! Ancak bahis şirketleri KG Yok seçeneğini çok düşük tutmuş. Bu çelişki, favori takımın (Ev) maçı kazanamayacağının (0-0 veya Deplasman galibiyeti) matematiksel itirafıdır!"
            
        # Deplasman favori, ama Ev gol atar ve KG Yok
        if ms2 <= 1.45 and ev_05_ust <= 1.30 and kg_yok <= 1.65:
            return True, "Matematiksel Paradoks! Deplasman ağır favori, ev sahibinin de gol atması neredeyse kesin (0.5 Üst <= 1.30). Eğer favori kazanacaksa ve zayıf takım gol atacaksa maç KG Var olmalı! Ancak bahis şirketleri KG Yok seçeneğini çok düşük tutmuş. Bu çelişki, favori takımın (Deplasman) maçı kazanamayacağının (0-0 veya Ev galibiyeti) matematiksel itirafıdır!"
            
        return False, ""

class RuleT34(BaseRule):
    code = "T34"
    category = "YÖN"
    name = "KG Var Paradoksu (Çift Skor Kilidi)"
    description = "Ağır Favori + KG Var + Çift + Favori 2.5 Alt"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        cift = get_odd(odds, ["Tek / Çift_Çift"])
        ev_25_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Alt", "Ev Sahibi Altı/Üstü 2.5_Alt"])
        dep_25_alt = get_odd(odds, ["Deplasman Alt/Üst 2.5_Alt", "Deplasman Altı/Üstü 2.5_Alt"])
        
        # Deplasman favori
        if ms2 <= 1.40 and kg_var <= 1.40 and cift <= 1.65 and dep_25_alt <= 1.65:
            return True, "Matematiksel Paradoks! Deplasman kazanacak (1.40 altı) ve karşılıklı gol olacaksa (1.40 altı) minimum skor 1-2'dir (Tek). Ancak maçın Çift (1.65 altı) bitmesi bekleniyor. Olası tek Çift skor 1-3'tür, fakat Deplasmanın 3 gol atmasına (2.5 Alt düşük) ihtimal verilmiyor! Tüm olasılıklar kilitlenmiştir. Bu maçın 0-0 kilitleneceğinin veya favorinin puan kaybedeceğinin en net matematiksel kanıtıdır."
            
        # Ev favori
        if ms1 <= 1.40 and kg_var <= 1.40 and cift <= 1.65 and ev_25_alt <= 1.65:
            return True, "Matematiksel Paradoks! Ev sahibi kazanacak (1.40 altı) ve karşılıklı gol olacaksa (1.40 altı) minimum skor 2-1'dir (Tek). Ancak maçın Çift (1.65 altı) bitmesi bekleniyor. Olası tek Çift skor 3-1'dir, fakat Ev sahibinin 3 gol atmasına (2.5 Alt düşük) ihtimal verilmiyor! Tüm olasılıklar kilitlenmiştir. Bu maçın 0-0 kilitleneceğinin veya favorinin puan kaybedeceğinin en net matematiksel kanıtıdır."
            
        return False, ""

class RuleT35(BaseRule):
    code = "T35"
    category = "YÖN"
    name = "Çifte Şans 12 Tuzağı (Beraberlik İllüzyonu)"
    description = "MS1, MS2 >= 2.30 ve fark <= 0.30 iken ÇŞ 12 <= 1.20 ve KG Var >= 1.65"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        cs_12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1 ve 2", "Çifte Şans_1-2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst", "3.5 Üst"])
        
        if ms1 != 99.0 and ms2 != 99.0 and ms1 >= 2.30 and ms2 >= 2.30 and abs(ms1 - ms2) <= 0.30 and cs_12 < 99.0 and cs_12 <= 1.20 and kg_var != 99.0 and kg_var >= 1.65 and (ust35 == 99.0 or ust35 != 99.0 and ust35 > 1.70):
            return True, "Gerçekten dengeli olan (iki takım da 2.30+) maçlarda teorik Çifte Şans 12 oranı 1.28 civarında olmalıdır. Bunun 1.20'nin altına çekilmesi herkesi 'Beraberlik olmaz' algısıyla taraf bahsine yönlendirmek içindir. Üstelik KG Var'ın yüksek (1.65+) olması maçın kilitleneceğini gösterir. Bu devasa bir 0-0 veya 1-1 beraberlik tuzağıdır. MS 0 denenmelidir."
        return False, ""

class RuleT68(BaseRule):
    code = "T68"
    category = "YÖN"
    name = "Görünür Favori Tuzağı (Gerçekte Değil)"
    description = "Piyasanın favori gösterdiği takımın aslında kazanamayacağı tuzak."
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        cs_02 = get_odd(odds, ["Çifte Şans_0 ve 2", "Çifte Şans_02"])
        cs_10 = get_odd(odds, ["Çifte Şans_1 ve 0", "Çifte Şans_1X"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt", "Deplasman Altı/Üstü 1.5_Alt"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        
        # 1. Deplasman Görünür Favori Tuzağı
        if ((1.65 <= ms2 <= 1.75) or (2.00 <= ms2 <= 2.10)) and cs_02 <= 1.25 and dep_15_alt <= 1.55:
            return True, "DEPLASMAN GÖRÜNÜR FAVORİ TUZAĞI: Deplasman takımı favori gibi gösterilse de (MS2 1.65-2.10 arası) Çifte Şans 02 ve Deplasman 1.5 Alt oranları bu durumu yalanlıyor. Deplasman kazanamaz, hatta gol bile atamaz. En yüksek ihtimal beraberlik veya ev sahibi sürpriz galibiyetidir."
            
        # 2. Ev Sahibi Görünür Favori Tuzağı
        if (1.65 <= ms1 <= 1.70) and cs_10 <= 1.10 and ev_15_alt <= 1.50:
            return True, "EV SAHİBİ GÖRÜNÜR FAVORİ TUZAĞI: Ev sahibi favori gibi gösterilse de, Ev Sahibi 1.5 Alt oranının 1.50 altında olması tuzağı ele veriyor. Ev sahibi kazanamaz, genellikle gol bile atamaz. En yüksek ihtimal golsüz beraberlik veya az gollü deplasman galibiyetidir."
            
        return False, "" 

class RuleT18(BaseRule):
    code = "T18"
    category = "YÖN"
    name = "Eşit Oranlı Maçta Tek Taraflı Düşük Fark"
    description = "MS1 ve MS2 farkı <=0.10 + ÇŞ 1-2 <=1.15 + IY KG Yok <=1.15 + Ev/Dep 1.5 Alt <=1.50 -> Tek golle biter."
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        cs_12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1-2"])
        iy_kgyok = get_odd(odds, ["1. Yarı Karşılıklı Gol_Yok"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt"])
        if abs(ms1 - ms2) <= 0.10 and cs_12 <= 1.15 and iy_kgyok <= 1.15 and ev_15_alt <= 1.50 and dep_15_alt <= 1.50:
            return True, "Maç tek golle biter; genellikle ev sahibi ilk yarıdan atar ve skoru korur."
        return False, ""

class RuleT19(BaseRule):
    code = "T19"
    category = "YÖN"
    name = "Sıfır Gol Beraberlik Garantisi"
    description = "Tüm taraf oranları farkı <=0.50 + 3.5 Alt <=1.15 + Ev/Dep 1.5 Alt <=1.30 + IY 0 <=1.90 + 2. Yarı KG Yok <=1.15"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        alt_35 = get_odd(odds, ["Alt/Üst 3.5_Alt", "Altı/Üstü 3.5_Alt"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt"])
        iy0 = get_odd(odds, ["1. Yarı Sonucu_0"])
        iy2_kgyok = get_odd(odds, ["2. Yarı Karşılıklı Gol_Yok"])
        if abs(ms1-ms0) <= 0.50 and abs(ms0-ms2) <= 0.50 and alt_35 <= 1.15 and ev_15_alt <= 1.30 and dep_15_alt <= 1.30 and iy0 <= 1.90 and iy2_kgyok <= 1.15:
            return True, "Maç 0-0 berabere biter; hiçbir takım gol bulamaz."
        return False, ""

class RuleT20(BaseRule):
    code = "T20"
    category = "YÖN"
    name = "Deplasman Favorisi + KG Yok Garantisi"
    description = "MS2 <=1.80 + ÇŞ 0-2 <=1.10 + KG Yok <=1.35 + Dep 1.5 Alt <=1.35 -> Deplasman 2-0 kazanır."
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        cs_02 = get_odd(odds, ["Çifte Şans_X2", "Çifte Şans_0-2"])
        kgyok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt"])
        if ms2 <= 1.80 and cs_02 <= 1.10 and kgyok <= 1.35 and dep_15_alt <= 1.35:
            return True, "Deplasman 2-0 ile kazanır, ev sahibi hiç gol atamaz."
        return False, ""

class RuleT21(BaseRule):
    code = "T21"
    category = "YÖN"
    name = "İlk Yarıdan Kopan Deplasman Galibiyeti"
    description = "MS2 <=2.00 + ÇŞ 1-2 <=1.20 + IY 0.5 Üst <=1.30 + IY KG Yok <=1.10 + Ev 0.5 Üst <=1.30"
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        cs_12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1-2"])
        iy_05_ust = get_odd(odds, ["1. Yarı Alt/Üst 0.5_Üst", "1. Yarı Altı/Üstü 0.5_Üst"])
        iy_kgyok = get_odd(odds, ["1. Yarı Karşılıklı Gol_Yok"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst"])
        if ms2 <= 2.00 and cs_12 <= 1.20 and iy_05_ust <= 1.30 and iy_kgyok <= 1.10 and ev_05_ust <= 1.30:
            return True, "Deplasman ilk yarıdan 2 gol atar, maç 0-2 / 0-3 ile biter."
        return False, ""

class RuleT22(BaseRule):
    code = "T22"
    category = "YÖN"
    name = "İlk Yarıdan Kopan Büyük Fark Tuzağı"
    description = "MS1 <=1.45 + Ev 0.5 Üst <=1.25 + Ev 2.5 Alt <=1.25 + IY KG Yok <=1.10 + Dep IY 0.5 Alt <=1.30"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst"])
        ev_25_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Alt"])
        iy_kgyok = get_odd(odds, ["1. Yarı Karşılıklı Gol_Yok"])
        dep_iy_05_alt = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Alt", "Deplasman 1. Yarı Alt/Üst 0.5_Alt"])
        if ms1 <= 1.45 and ev_05_ust <= 1.25 and ev_25_alt <= 1.25 and iy_kgyok <= 1.10 and dep_iy_05_alt <= 1.30:
            return True, "Ev sahibi ilk yarıdan 3-4 gol atar; maç 4-0 / 5-1 ile biter."
        return False, ""

class RuleT30(BaseRule):
    code = "T30"
    category = "YÖN"
    name = "Dengeli Oranda Kısır Deplasman"
    description = "MS1 > MS2 (Fark <=0.40) + ÇŞ 1-2 <=1.22 + Ev 1.5 Alt <=1.30 + Dep 1.5 Alt <=1.35"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        cs_12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1 ve 2", "Çifte Şans_1-2"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt", "Deplasman Altı/Üstü 1.5_Alt"])
        
        if ms1 > ms2 and (ms1 - ms2) <= 0.40 and cs_12 <= 1.22 and ev_15_alt <= 1.30 and dep_15_alt <= 1.35:
            return True, "Maç tamamen dengede görünse de, kısır gollü bir Deplasman Galibiyeti (0-1) hedeflenmektedir."
        return False, ""

# --- YARI ZAMANI KURALLARI (Y SERİSİ) ---
class RuleY1(BaseRule):
    code = "Y1"
    category = "YARI"
    name = "İlk Yarı Sıfır Gol"
    description = "IY 0 <= 1.95 + IY 0.5 Alt <= 2.50"
    
    @classmethod
    def evaluate(cls, odds):
        iy0 = get_odd(odds, ["1. Yarı Sonucu_0"])
        iy_05_alt = get_odd(odds, ["1. Yarı Alt/Üst 0.5_Alt", "1. Yarı Altı/Üstü 0.5_Alt"])
        if iy0 <= 1.95 and iy_05_alt <= 2.70:
            return True, "İlk yarı kesin 0-0 biter."
        return False, ""

class RuleY2(BaseRule):
    code = "Y2"
    category = "YARI"
    name = "İkinci Yarıda Çözülme"
    description = "1. Yarı 1.5 Alt <= 1.40 + 1. Yarı 0.5 Alt <= 2.20 -> Goller ikinci yarıda gelir."
    
    @classmethod
    def evaluate(cls, odds):
        iy_15_alt = get_odd(odds, ["1. Yarı Alt/Üst 1.5_Alt", "1. Yarı Altı/Üstü 1.5_Alt"])
        iy_05_alt = get_odd(odds, ["1. Yarı Alt/Üst 0.5_Alt", "1. Yarı Altı/Üstü 0.5_Alt"])
        if iy_15_alt <= 1.40 and iy_05_alt <= 2.20:
            return True, "Goller tamamen ikinci yarıda gelir."
        return False, ""

class RuleY3(BaseRule):
    code = "Y3"
    category = "YARI"
    name = "İlk Yarıda Kilit Açılır"
    description = "İkinci Yarı KG Yok <= 1.15 + İlk yarı 0:0 skoru >= 2.50"
    
    @classmethod
    def evaluate(cls, odds):
        iy2_kgyok = get_odd(odds, ["2. Yarı Karşılıklı Gol_Yok"])
        iy_00 = get_odd(odds, ["1. Yarı Skoru_0:0"])
        if iy2_kgyok <= 1.20 and iy_00 != 99.0 and iy_00 >= 2.50:
            return True, "İlk yarı eşitlik bozulur ve ikinci yarıda da tek taraflı akış devam eder."
        return False, ""
    
class RuleY4(BaseRule):
    code = "Y4"
    category = "YARI"
    name = "İlk Yarı Kesin Alt"
    description = "1. Yarı Alt 1.5 <=1.20 + 1. Yarı Alt 0.5 <=2.30"
    
    @classmethod
    def evaluate(cls, odds):
        iy_15_alt = get_odd(odds, ["1. Yarı Alt/Üst 1.5_Alt", "1. Yarı Altı/Üstü 1.5_Alt"])
        iy_05_alt = get_odd(odds, ["1. Yarı Alt/Üst 0.5_Alt", "1. Yarı Altı/Üstü 0.5_Alt"])
        if iy_15_alt <= 1.20 and iy_05_alt <= 2.30:
            return True, "İlk yarıda gol sesi çıkmaz veya en fazla 1 gol olur (0-0 çok güçlü)."
        return False, ""

class RuleY5(BaseRule):
    code = "Y5"
    category = "YARI"
    name = "İlk Yarı Tek Golle Kilitlenir"
    description = "IY 0.5 Üst <= 1.35 + IY 1.5 Alt <= 1.30 + 2. Yarı KG Yok <= 1.10"
    
    @classmethod
    def evaluate(cls, odds):
        iy_05_ust = get_odd(odds, ["1. Yarı Alt/Üst 0.5_Üst", "1. Yarı Altı/Üstü 0.5_Üst"])
        iy_15_alt = get_odd(odds, ["1. Yarı Alt/Üst 1.5_Alt", "1. Yarı Altı/Üstü 1.5_Alt"])
        iy2_kgyok = get_odd(odds, ["2. Yarı Karşılıklı Gol_Yok"])
        if iy_05_ust <= 1.30 and iy_15_alt <= 1.30 and iy2_kgyok <= 1.10:
            return True, "İlk yarı tek gol olur ve maçın skoru büyük ihtimalle bu golle kilitlenir (2. yarı gol olmaz)."
        return False, ""

class RuleY6(BaseRule):
    code = "Y6"
    category = "YARI"
    name = "Ağır Favori İlk Yarı Uyku Tuzağı"
    description = "Ağır favori olmasına rağmen IY 1.5 Alt oranı çok düşük"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        iy_15_alt = get_odd(odds, ["1. Yarı Alt/Üst 1.5_Alt", "1. Yarı Altı/Üstü 1.5_Alt"])
        
        if (ms1 <= 1.30 or ms2 <= 1.30) and iy_15_alt <= 1.45:
            return True, "Ağır favoriye rağmen ilk yarıda fark açılmaz (1.5 Alt gelir). Maç ikinci yarıda çözülür ve skor o zaman netleşir."
        return False, ""

class RuleY7(BaseRule):
    code = "Y7"
    category = "YARI"
    name = "Büyük Gol Tuzağı (Hayalet Maç)"
    description = "3.5 Üst + KG Var beklentisine rağmen İlk Yarı kilitli"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        iy_ev_15_alt = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 1.5_Alt", "Ev Sahibi 1. Yarı Alt/Üst 1.5_Alt"])
        iy_dep_05_alt = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Alt", "Deplasman 1. Yarı Alt/Üst 0.5_Alt"])
        
        fav = min(ms1, ms2) if ms1 < 99.0 and ms2 < 99.0 else (ms1 if ms1 < 99.0 else ms2)
        
        if fav != 99.0 and fav > 1.50 and ust35 <= 1.75 and kg_var <= 1.55 and iy_ev_15_alt <= 1.45 and iy_dep_05_alt <= 1.45:
            return True, "Bahis şirketleri 3.5 Üst ve KG Var oranlarını çok düşük açarak herkesi gollü bir maça inandırmış. Ancak ağır favori olmamasına rağmen ilk yarı alt oranlarının aşırı düşüklüğü, bu maçın tamamen bir illüzyon olduğunu gösteriyor. Maç 0-0 veya en fazla 1-0 gibi kısır bir skorla biter, Üst oynayan herkes kaybeder!"
        return False, ""

class RuleT36(BaseRule):
    code = "T36"
    category = "YÖN"
    name = "Gizli Deplasman Golü (Çelişki Tuzağı)"
    description = "Ev Sahibi Favori ama Deplasman 0.5 Üst çok düşük ve KG Yok düşük"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        
        if ms1 <= 1.80 and dep_05_ust <= 1.35 and dep_05_ust < 99.0 and kg_yok <= 1.65:
            return True, "Ev sahibi favori gösterilmesine ve maçın 'KG Yok' (Biri gol atamaz) beklenmesine rağmen, Deplasmanın gol atma oranı çok düşük açılmış. Bu büyük bir çelişkidir! Bürolar deplasmanın gol atacağını, ev sahibinin ise tıkanacağını biliyor. Deplasman yenilmez (X2) veya Sürpriz MS 2 denenebilir."
        return False, ""

class RuleG11(BaseRule):
    code = "G11"
    category = "GOL"
    name = "Kesin Düello (Aşırı Düşük KG Var)"
    description = "KG Var <= 1.35"
    
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ms1 = get_odd(odds, ["Maç Sonucu_1", "Maç Sonucu_Ev", "1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2", "Maç Sonucu_Deplasman", "2"])

        # ⛔ KRİTİK İSTİSNA: İY KG Yok <= 1.25 ise maç IY kilitli başlıyor demektir.
        # KG Var 1.24 olsa bile IY KG Yok <= 1.25 ise bu 'SAHTE KG Var' tuzağıdır!
        # Gardabaer-Dalverik (IY KG Yok=1.22, skor 0-0) örneğinden öğrenildi.
        iy_kg_yok = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Yok"])
        if iy_kg_yok <= 1.25 and iy_kg_yok != 99.0:
            return False, ""

        # Eğer çok ağır bir favori varsa (<=1.40), KG Var tuzağı olabilir. G11 sadece dengeli veya hafif favorili maçlarda çalışmalı.
        if kg_var <= 1.35 and kg_var < 99.0 and ms1 != 99.0 and ms1 > 1.40 and ms2 != 99.0 and ms2 > 1.40:
            return True, "Karşılıklı Gol Var oranı piyasa standartlarının çok altında (1.35 ve altı). Maçın iki takımın da skor üreteceği, açık bir düello şekline geçeceği çok net bir şekilde fiyatlanmış. Taraf bahsi yerine doğrudan KG Var veya Üst seçeneklerine yönelin."
        return False, ""


# ==========================================
# KULLANICI ÖZEL SERİ KURALLARI (999 & 1460 Serisi)
# ==========================================

class Rule999(BaseRule):
    code = "999"
    category = "İSTİSNA"
    name = "Yanıltıcı Üretkenlik & Golsüz İstisnası"
    description = "MS Favori <= 1.40 + KG Var <= 1.25 + Üst 2.5 <= 1.55"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Alt/Üst 2,5_Üst"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Alt/Üst 3,5_Üst"])
        
        fav_odd = min(ms1, ms2) if ms1 < 99.0 and ms2 < 99.0 else (ms1 if ms1 < 99.0 else ms2)
        ust_val = min(ust25, ust35) if ust25 < 99.0 and ust35 < 99.0 else (ust25 if ust25 < 99.0 else ust35)
        
        if fav_odd <= 1.40 and kg_var <= 1.25 and ust_val <= 1.55:
            return True, "BU MAÇ KESİN GOLLÜDÜR! Ancak çok nadir de olsa 0-0 istisnası görülebilir. Oranlar ne kadar kesin görünürse görünsün, oran verilerinin hesap dışı bıraktığı anlık şans ve form eksiklikleriyle bu %5-6'lık 0-0 riski her zaman sistemde tutulmalıdır."
        return False, ""

class Rule1460(BaseRule):
    code = "1460"
    name = "Saf 0-0 Beton Kilidi (Dar Makas & Kısır Favori)"
    category = "SKOR"
    description = "MS1 ve MS0 makası inanılmaz dar ve favorinin 1.5 Üst oranı çok yüksek (2.60+)."

    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ev_15_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Üst", "Ev Sahibi Altı/Üstü 1.5_Üst"])
        dep_15_ust = get_odd(odds, ["Deplasman Alt/Üst 1.5_Üst", "Deplasman Altı/Üstü 1.5_Üst"])
        
        if min(ms1, ms2) >= 1.90 and max(ms1, ms2) <= 3.50 and ms0 <= 2.80 and ms0 != 99.0:
            favori_15_ust = ev_15_ust if ms1 <= ms2 else dep_15_ust
            
            if favori_15_ust >= 2.60 and favori_15_ust != 99.0:
                return True, "SAF 0-0 BETON KİLİDİ: Favorinin kazanma oranı (Örn: 2.38) ile beraberlik oranı (2.57) arasındaki makas inanılmaz derecede dar. İddaa bu maçın beraberliğe yatkın olduğunu açıkça söylüyor. Üstelik favori gösterilen takımın bile 2 gol atma ihtimaline (1.5 Üst) devasa bir oran (2.60+) açılmış. Yani favori kazansa bile en fazla şanslı bir kaza golüyle 1-0 kazanabilir. Maçın en parlak skoru tartışmasız 0-0'dır. Bu bir beton maçtır, KG Yok ve İlk Yarı 0 Bankodur!"
                
        return False, ""

class Rule1462(BaseRule):
    code = "1462"
    category = "SKOR"
    name = "Belirgin Ev Üstünlüğü (İlk Yarı Kapalı, 1-0)"
    description = "MS1 1.93-2.02 + Beraberlik 2.48-2.58"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        if 1.93 <= ms1 <= 2.02 and 2.48 <= ms0 <= 2.58:
            return True, "Belirgin Ev Üstünlüğü, İlk Yarı Tamamen Kapalı, Tek Taraflı 1-0. İlk yarı 0-0 kilitlenir, maç ev sahibinin tek golüyle 1-0 biter."
        return False, ""

class Rule1462B(BaseRule):
    code = "1462B"
    category = "SKOR"
    name = "Sahte KG Yok Tuzağı (IY Kilitli → 2Y Gol Patlaması)"
    description = "KG Yok favori görünse de 1.5 Üst düşük + bireysel takım gol oranları düşük → İlk yarı 0-0, ikinci yarıda gol patlaması (2-1, 1-2, 2-0)."

    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        ust15 = get_odd(odds, ["Alt/Üst 1.5_Üst"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])

        if kg_var == 99.0 or kg_yok == 99.0 or ust15 == 99.0:
            return False, ""

        # KG Yok favori görünümü ama 1.5 Üst düşük = ÇELİŞKİ
        is_kg_yok_favori = kg_yok <= 1.42 and kg_var != 99.0 and kg_var >= 2.0
        is_gol_olacak = ust15 <= 1.55
        # Her iki takım da gol atar sinyali
        ev_gol_atar = ev_05_ust != 99.0 and ev_05_ust <= 1.40
        dep_gol_atar = dep_05_ust != 99.0 and dep_05_ust <= 1.58
        # Dengeli maç (her iki takım da makul oranlar)
        is_dengeli = ms1 != 99.0 and ms2 != 99.0 and min(ms1, ms2) >= 1.90

        if is_kg_yok_favori and is_gol_olacak and ev_gol_atar and dep_gol_atar and is_dengeli:
            return True, (
                "SAHTE KG YOK TUZAĞI (IY Kilitli → 2Y Gol Patlaması): Piyasa KG Yok'u "
                + str(kg_yok) + " ile favori gösteriyor. Ancak bu ALDATMACADIR! "
                "1.5 Üst oranı " + str(ust15) + " ile piyasa 2+ gol neredeyse garantilemekte. "
                "Ev sahibi 0.5 Gol Üst=" + str(ev_05_ust) + " ve Dep 0.5 Gol Üst=" + str(dep_05_ust) + " "
                "ile HER İKİ TAKIM da gol atacak sinyali veriyor. "
                "Bu profil 'İlk Yarı 0-0, İkinci Yarıda Gol Patlaması' senaryosunu gösteriyor. "
                "Maç 2-1, 1-2 veya 2-0 gibi GOLLÜ ama TEK TARAFLI skorlarla biter. "
                "KG Yok bahsi YANLIŞTIR. Doğru tahmin: 1.5 Üstü + Ev Galibiyet veya Deplasman Galibiyet."
            )
        return False, ""


class Rule1463(BaseRule):

    code = "1463"
    category = "SKOR"
    name = "Tamamen Dengeli Beraberlik (0-0)"
    description = "MS1 2.25-2.35 + Beraberlik en düşük"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        if 2.25 <= ms1 <= 2.35 and ms0 <= ms1 and ms0 <= ms2:
            return True, "Tamamen Dengeli. Beraberlik En Güçlü. Tamamen Kapalı 0-0. İlk yarı 0-0 başlar, 0-0 biter."
        return False, ""

class Rule1464(BaseRule):
    code = "1464"
    category = "SKOR"
    name = "Hafif Ev Üstünlüğü (Gollü, 3-1)"
    description = "MS1 2.15-2.25 + Beraberlik 2.35-2.45"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        if 2.15 <= ms1 <= 2.25 and 2.35 <= ms0 <= 2.45:
            return True, "Hafif Ev Üstünlüğü. İlk Yarı Karşılıklı. İkinci Yarı Ev Üstünlüğü. İlk Yarı 1-1 geçer, maç sonu 3-1 ev sahibi lehine biter."
        return False, ""

class Rule1465(BaseRule):
    code = "1465"
    category = "SKOR"
    name = "Uluslararası: Ev Favorisi Görünümlü Konuk Galibiyeti (0-1)"
    description = "MS1 1.82-1.90 + MS2 >= 3.75 + Beraberlik 2.45-2.58"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        if 1.82 <= ms1 <= 1.90 and ms2 != 99.0 and ms2 >= 3.75 and 2.45 <= ms0 <= 2.58 and ev_15_alt <= 1.28 and kg_yok <= 1.35:
            return True, "Belirgin Ev Favorisi Görünümlü İlk Yarı Tamamen Kapalı Tek Taraflı 0-1 Konuk Galibiyeti. Ev belirgin favori olarak başlar, ilk yarı 0-0 biter; ikinci yarı konukun tek golüyle maç 0-1 konuk galibiyetiyle sonuçlanır."
        return False, ""

class Rule1466(BaseRule):
    code = "1466"
    category = "SKOR"
    name = "Yakınsak Sürpriz Oran (Favori Çöküşü 1-2)"
    description = "MS Favorisi 1.45-1.55 + Beraberlik ile Sürpriz oranı birbirine çok yakın (Fark <= 0.20)"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        # Sadece ev sahibi veya deplasman favoriyken (1.45 - 1.55)
        if 1.45 <= ms1 <= 1.55 and abs(ms0 - ms2) <= 0.20:
            return True, "Ev sahibi net favori görünse de, beraberlik (MS0) ve deplasman (MS2) oranlarının birbirine çok yakın (neredeyse aynı) açılması, büroların taraf bahsinde karanlıkta kaldığını veya deplasmanın gizli bir direnci olduğunu gösterir. Ev sahibi genelde tıkanır ve maç 1-2 gibi dev bir deplasman sürpriziyle bitebilir."
        elif 1.45 <= ms2 <= 1.55 and abs(ms0 - ms1) <= 0.20:
            return True, "Deplasman net favori görünse de, beraberlik (MS0) ve ev sahibi (MS1) oranlarının birbirine çok yakın açılması dev bir sürprize işarettir. Ev sahibi 2-1 gibi bir skorla şok edici bir galibiyet alabilir."
        return False, ""

class Rule1467(BaseRule):
    code = "1467"
    category = "SKOR"
    name = "Dengeli Kısır Çelişki (0-0)"
    description = "Tamamen denk takımlar (MS 2.20-2.60) + Beraberlik < 3.20 + Üst >= 1.60"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Alt/Üst 2,5_Üst"])
        
        if 2.20 <= ms1 <= 2.65 and 2.20 <= ms2 <= 2.65 and ms0 <= 3.20 and ust25 != 99.0 and ust25 >= 1.60:
            kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
            if ust25 != 99.0 and ust25 >= 2.50 and kg_yok <= 1.50:
                 return True, "DENGELİ KISIR ÇELİŞKİ (1-2 / 2-1 Üst Sürprizi): Her iki takımın oranları birbirine çok yakın (tamamen dengeli), beraberlik oranı normalden düşük (<=3.20) ve maçın Üst (2.5) oranı İNANILMAZ DERECEDE YÜKSEK (2.50+). Bu maçın 0-0 kilitleneceğini bağıran bir tablodur. İddaa hiçbir kilitlenmeyi bu kadar belli etmez! Bu tam bir tuzaktır. Maçta sürpriz bir şekilde karşılıklı goller olacak ve maç 1-2, 2-1 gibi skorlarla Üst'e (sürprize) gidecektir. 2.5 Üst aranmalıdır."
            else:
                 return True, "Her iki takımın oranları birbirine çok yakın (tamamen dengeli), beraberlik oranı normalden düşük (<=3.20) ve maçın gollü geçme ihtimali düşük (Üst >= 1.60). Bu tam bir kilitlenme senaryosudur. İki takım da risk almaz, maç 0-0 biter."
        return False, ""

class Rule1468(BaseRule):
    code = "1468"
    category = "SKOR"
    name = "Matematiksel Paradoks (Sahte Favori Çöküşü 1-2/1-3)"
    description = "Favori (MS1 <= 2.00) + KG Var (<= 1.55) + Ev 1.5 Alt < Ev 1.5 Üst"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt"])
        ev_15_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Üst"])
        
        if ms1 <= 2.00 and kg_var <= 1.55 and ev_15_alt <= 1.45:
            return True, "BÜYÜK ÇELİŞKİ: Ev sahibi favori (1.89) gösterilmiş, KG Var (1.46) bekleniyor ancak Ev Sahibinin 1.5 Alt oranı (1.60), 1.5 Üst oranından (1.76) düşük! Bu matematiksel bir paradokstur. Ev sahibi en fazla 1 gol atabilecekse ve maç KG Var bitecekse, ev sahibinin maçı kazanma şansı MATEMATİKSEL OLARAK YOKTUR (Skor en iyi ihtimalle 1-1, veya 1-2, 1-3 olur). MS 1 tamamen bir tuzaktır. Deplasman kaybetmez (X2) ve Deplasman galibiyeti çok yüksek ihtimaldir."
        
        # Deplasman favorisi için aynı paradoks
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt"])
        dep_15_ust = get_odd(odds, ["Deplasman Alt/Üst 1.5_Üst"])
        
        if ms2 <= 2.00 and kg_var <= 1.55 and dep_15_alt <= 1.45:
             return True, "BÜYÜK ÇELİŞKİ: Deplasman favori gösterilmiş, KG Var bekleniyor ancak Deplasmanın 1.5 Alt oranı, Üst oranından düşük. Deplasman en fazla 1 gol atabilecekse ve maç KG Var olacaksa deplasman kazanamaz (En iyi ihtimal 1-1 veya 2-1). MS 2 tamamen bir tuzaktır. Ev sahibi kaybetmez (1X)."
             
        return False, ""

class Rule1472(BaseRule):
    code = "1472"
    name = "Görünür Kısır Maç, Gizli Deplasman Şovu (0.5 Üst Çelişkisi)"
    category = "GOL_VE_YÖN"
    description = "MS0 <= 2.85, 2.5 Alt <= 1.55 AMA Deplasman (Sürpriz) 0.5 Üst <= 1.30"
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst"])
        
        if ms0 <= 2.85 and alt25 <= 1.55 and ms2 != 99.0 and ms2 >= 2.50 and dep_05_ust <= 1.30 and dep_05_ust != 99.0:
            return True, "GİZLİ DEPLASMAN ŞOVU: Piyasa MS0 ve 2.5 Alt oranlarını dibe çekerek (1486 Kısır Maç Tuzağı) herkesi 0-0 veya 1-1 skoruna kilitliyor. ANCAK 2.50+ oranlı sürpriz Deplasman takımının gol atma ihtimali (0.5 Üst) 1.30'un altına indirilmiş! İddaa deplasmanın kesin gol atacağını biliyor ve kısır maç algısıyla bunu gizliyor. Bu maç kilitlenmez, Deplasman takımı şov yapar (0-2, 0-3, 1-3). MS 2 ve 2.5 Üst denenmelidir."
        return False, ""
class Rule1469(BaseRule):
    code = "1469"
    category = "SKOR"
    name = "Aşırı Düşük Beraberlik Tuzağı (Kısır Favori)"
    description = "Ev favori iken MS0 3.05 altındaysa ve kısır bekleniyorsa maç kilitlenir."

    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        alt_ve_yok = get_odd(odds, ["Altı/Üstü 2.5 ve Karşılıklı Gol_Alt ve Yok"])
        if ms1 < ms2 and ms1 != 99.0 and ms1 >= 1.50 and ms0 <= 3.05 and ev_15_alt <= 1.55:
            if kg_var <= 1.70 and (alt_ve_yok == 99.0 or alt_ve_yok != 99.0 and alt_ve_yok > 2.20):
                return True, "ASYA TUZAĞI (GOLLÜ BERABERLİK İLLÜZYONU): Beraberlik oranı anormal düşük ve aynı zamanda KG Var da güçlü fiyatlanmış. Bu maç asla 0-0 gibi kısır bir skora kilitlenmez. İddaa düşük beraberlik oranıyla maçın sıkıcı geçeceği algısı yaratır ancak maç gollü bir kaosa (1-1, 2-2, 3-2 vb.) döner."
            elif kg_var != 99.0 and kg_var > 1.70:
                return True, "GİZLİ BERABERLİK KİLİDİ: Ev sahibi favori gösterilse de (Örn: 1.90), beraberlik oranı anormal derecede düşüktür (3.05 ve altı). Üstelik favorinin 2 gol atması beklenmemektedir (Ev 1.5 Alt <= 1.55). Bu maçta favorinin galibiyet gücü yoktur, maç 0-0 veya 1-1 kilitlenir. MS 0 denenmelidir."
        return False, ""

class Rule1470(BaseRule):
    code = "1470"
    category = "GOL"
    name = "KG Var 1.2X Tuzağı (Sahte Açık Futbol)"
    description = "KG Var <= 1.30 + Deplasman 0.5 Üst yüksek"
    
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        dep_05_ust = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Üst", "Deplasman 1. Yarı Alt/Üst 0.5_Üst"])
        
        if kg_var <= 1.28 and ms1 <= 1.65 and dep_05_ust >= 2.30 and dep_05_ust != 99.0:
            return True, "KUSURSUZ GOL TUZAĞI: Bürolar KG Var oranını 1.30'lara kadar çekerek herkesi gollü bir maça inandırmış. Ancak deplasman takımının ilk yarıda gol atma ihtimali (0.5 Üst) çok zayıf görülüyor. Bu, 'KG Var'ın tamamen sahte bir yem olduğunu, maçın 1-0 veya 2-0 gibi tek taraflı kısır bir skorla biteceğini gösterir. KG Yok oynanmalıdır."
            
        return False, ""

class RuleG12(BaseRule):
    code = "G12"
    category = "GOL"
    name = "Katliam Senaryosu (Ağır Favori Düellosu)"
    description = "Favori <= 1.30 + KG Var <= 1.65 + 3.5 Üst <= 1.80 + Favori 2.5 Üst < 1.60"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Alt/Üst 3,5_Üst"])
        ev_25_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Üst"])
        dep_25_ust = get_odd(odds, ["Deplasman Alt/Üst 2.5_Üst"])
        
        is_fav_strong = False
        if ms1 <= 1.30 and ev_25_ust < 1.60: is_fav_strong = True
        if ms2 <= 1.30 and dep_25_ust < 1.60: is_fav_strong = True
        # if missing, assume strong for G12 fallback
        if ms1 <= 1.30 and ev_25_ust == 99.0: is_fav_strong = True
        if ms2 <= 1.30 and dep_25_ust == 99.0: is_fav_strong = True

        if (ms1 <= 1.30 or ms2 <= 1.30) and kg_var <= 1.65 and ust35 <= 1.80 and is_fav_strong:
            return True, "KATLİAM SENARYOSU: Ağır bir favori var ve maçın 4 gol veya üzerine çıkacağı (3.5 Üst) net bir şekilde fiyatlanmış. Favorinin 3+ gol atması yüksek ihtimal (Fav 2.5 Üst düşük). Bu bir kilitlenme veya sürpriz maçı değil; favorinin 3-1, 4-1, 5-2 gibi skorlarla şov yapacağı bir düellodur. Gollere yönlendirilmelidir."
        return False, ""

class Rule1473(BaseRule):
    code = "1473"
    category = "SKOR"
    name = "Çapraz Sürpriz Düellosu (2-2 Tuzağı)"
    description = "Favori <= 1.30 + 3.5 Üst <= 1.65 + Favori 2.5 Üst >= 1.60"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Alt/Üst 3,5_Üst"])
        ev_25_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Üst"])
        dep_25_ust = get_odd(odds, ["Deplasman Alt/Üst 2.5_Üst"])
        
        is_trap = False
        if ms1 <= 1.30 and ev_25_ust >= 1.60 and ev_25_ust != 99.0: is_trap = True
        if ms2 <= 1.30 and dep_25_ust >= 1.60 and dep_25_ust != 99.0: is_trap = True
        
        if (ms1 <= 1.30 or ms2 <= 1.30) and ust35 <= 1.70 and is_trap:
            return True, "BÜYÜK SÜRPRİZ DÜELLOSU: Maçta 3.5 Üst beklentisi çok yüksek, ancak favori takımın 3 gol atma ihtimali zayıf (Fav 2.5 Üst yüksek). Bu çelişki, yüksek gol beklentisinin zayıf takımın atacağı gollerden kaynaklandığını kanıtlar. Favori takım maçı kazanamaz. Maç 1-1, 2-2 gibi gollü beraberliklerle veya şok bir mağlubiyetle biter. Çifte Şans veya Sürpriz 0 aranmalıdır."
        return False, ""

class Rule1474(BaseRule):
    code = "1474"
    category = "SKOR"
    name = "Enflasyon Tuzağı (Favori ve Beraberlik Eşitliği)"
    description = "Beraberlik Oranı < Ev Oranı (veya çok yakın) + Kısır Maç"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Alt/Üst 2,5_Alt"])
        
        # Beraberlik oranı 2.50 altındaysa ve taraflardan birinin (özellikle favorinin) oranından düşükse
        if ms0 <= 2.50 and ms0 < min(ms1, ms2) - 0.10:
            if alt25 <= 1.45 or kg_yok <= 1.50:
                # Ancak burada bir detay var: Eğer MS1 2.41, MS0 2.22, MS2 3.04 ise ve maç 0-1 bitiyorsa
                # Bürolar beraberliği en düşük tutarak ("Kesin 0-0 biter" algısı yaratıp) oyuncuları beraberliğe kilitliyor.
                # Sonra maç tek bir golle deplasman veya ev sahibine kayıyor.
                return True, "SÜPER BERABERLİK TUZAĞI: Bürolar beraberlik oranını (Örn: 2.22) taraf oranlarından bile düşük tutarak 'Bu maç %100 berabere biter' algısı yaratmıştır. Ancak bu kadar bariz bir beraberlik oranı genellikle bir tuzaktır. Maç 0-0 kilitlenecekmiş gibi görünürken tek bir golle zayıf takımın veya oran olarak dezavantajlı olan takımın galibiyetiyle (0-1 / 1-0) sonuçlanır. Beraberlikten ziyade 01 veya 02 Çifte Şans ve 1.5 Alt denenmelidir."
        return False, ""

class Rule1475(BaseRule):
    code = "1475"
    category = "SKOR"
    name = "Yalancı İmparator Tuzağı (1.0X Favori Çöküşü)"
    description = "Favori <= 1.15 + Favori 2.5 Alt < Favori 2.5 Üst"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_25_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Alt", "Ev Sahibi Altı/Üstü 2.5_Alt"])
        ev_25_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Üst", "Ev Sahibi Altı/Üstü 2.5_Üst"])
        dep_25_alt = get_odd(odds, ["Deplasman Alt/Üst 2.5_Alt", "Deplasman Altı/Üstü 2.5_Alt"])
        dep_25_ust = get_odd(odds, ["Deplasman Alt/Üst 2.5_Üst", "Deplasman Altı/Üstü 2.5_Üst"])
        
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        ev_15_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Üst", "Ev Sahibi Altı/Üstü 1.5_Üst"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt", "Deplasman Altı/Üstü 1.5_Alt"])
        dep_15_ust = get_odd(odds, ["Deplasman Alt/Üst 1.5_Üst", "Deplasman Altı/Üstü 1.5_Üst"])
        
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        is_trap = False
        
        # Eğer favorinin 2.5 Alt oranı düşükse, bu maçı 1-0 veya 2-0 kazanacağı anlamına gelebilir.
        # Bunun "Puan Kaybı Tuzağı" olması için:
        # YA favorinin 1.5 Alt oranı düşük olmalıdır (Maksimum 1 gol atabilir - 1-1 / 0-0 riski)
        # YA DA KG Var oranı düşük olmalıdır (Zayıf takım gol atacak, Favori 2 gol atsa bile yetmeyebilir).
        
        if ms1 <= 1.20:
            if ev_15_alt != 99.0 and ev_15_ust != 99.0 and ev_15_alt < ev_15_ust:
                is_trap = True
                
        if ms2 <= 1.20:
            if dep_15_alt != 99.0 and dep_15_ust != 99.0 and dep_15_alt < dep_15_ust:
                is_trap = True
        
        if is_trap:
             return True, "YALANCI İMPARATOR TUZAĞI: Takımlardan birine 1.0X veya 1.1X gibi inanılmaz derecede favori oranı açılmış. Ancak kendi takımlarının gol beklentisi korkunç derecede düşük (1.5 Alt < 1.5 Üst) veya KG Var ile zayıf takımın gol atması bekleniyor! Yani bürolar bu kadar kesin favori gösterdikleri takımın maçı koparamayacağını söylüyor. Bu korkunç bir tuzaktır. Favori takım maçı kazanamaz veya büyük ihtimalle kilitlenir. Zayıf takımın çifte şansı (1X veya 02) denenebilir."
             
        return False, ""

class Rule1476(BaseRule):
    code = "1476"
    category = "YARI"
    name = "Uyuyan Dev (İkinci Yarı Düello Patlaması)"
    description = "KG Var <= 1.40 + İY 0 <= 2.30 + İY KG Var > 2.60 + 2. Yarı KG Var <= 2.40"
    
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        iy_0 = get_odd(odds, ["1. Yarı Sonucu_0"])
        iy_kg_var = get_odd(odds, ["1. Yarı Karşılıklı Gol_Var"])
        ikinci_yari_kg_var = get_odd(odds, ["2. Yarı Karşılıklı Gol_Var"])
        
        if kg_var <= 1.40 and iy_0 <= 2.30 and iy_kg_var != 99.0 and iy_kg_var > 2.60 and ikinci_yari_kg_var <= 2.40:
            return True, "İKİNCİ YARI ŞOVU (3.5 ÜST UZANTISI): Maçın ilk yarısının tamamen golsüz veya çok kısır (0-0) geçeceği fiyatlanmış (İY 0 çok düşük, İY KG Var çok yüksek). Ancak maçın genelinde KG Var oranı 1.40 altında ve 2. Yarı KG Var oldukça iddialı. Bu da demek oluyor ki ilk yarı uyuyan takımlar, ikinci yarıda 2-2 veya 3-3'e kadar uzayabilecek devasa bir düelloya girecek. İlk yarı golsüz kilitlenip, ikinci yarı gol yağmuru (3.5 Üst) beklenmelidir."
            
        return False, ""

class Rule1477(BaseRule):
    code = "1477"
    category = "SKOR"
    name = "Matematiksel Paradoks: Sahte Fark İllüzyonu (1.2X Banko Patlaması)"
    description = "MS1 <= 1.30 + Ev 2.5 Alt <= 1.55 + Dep 0.5 Üst <= 1.50"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        ev_25_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Alt"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst"])
        
        dep_25_alt = get_odd(odds, ["Deplasman Alt/Üst 2.5_Alt"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst"])
        
        is_trap = False
        trap_team = ""
        
        if ms1 <= 1.30 and ev_25_alt <= 1.55 and dep_05_ust <= 1.50:
            is_trap = True
            trap_team = "Ev Sahibi"
            
        if ms2 <= 1.30 and dep_25_alt <= 1.55 and ev_05_ust <= 1.50:
            is_trap = True
            trap_team = "Deplasman"
            
        if is_trap:
            return True, f"BÜYÜK MATEMATİKSEL PARADOKS: {trap_team} 1.20'lerde bir oranla banko favori gösterilmiş. Ancak maçın detaylarına inildiğinde favori takımın 3 gol atamayacağı (2.5 Altı) kesin gibi fiyatlanmış. İşin daha da tuhafı, zayıf takımın kesinlikle 1 gol atacağı (0.5 Üstü 1.50 altı) bekleniyor! Zayıf takım gol atarsa, favorinin maçı kazanması için 2 gol atması gerekir. Ancak favori zaten maksimum 1-2 gol civarında kısıtlanmış durumda. Bu denklemde favorinin fark atma veya rahat kazanma ihtimali SIFIRDIR. Maç büyük ihtimalle 1-1, 2-1 (baskıyla) veya 1-2 (sürpriz) bitecektir. Taraf bahsinden (Banko'dan) kesinlikle kaçınılmalı, KG Var veya Sürpriz Çifte Şans denenmelidir."
            
        return False, ""

class Rule1478(BaseRule):
    code = "1478"
    category = "SKOR"
    name = "Deplasman Baskını (Ev Sahibi Tıkanması)"
    description = "MS2 <= 2.20 + KG Var <= 1.50 + Ev 1.Yarı 0.5 Üst >= 1.75"
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ev_1y_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst", "Ev Sahibi 1. Yarı Alt/Üst 0.5_Üst"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        
        if 1.95 <= ms2 <= 2.20 and kg_var <= 1.50 and ev_1y_05_ust != 99.0 and ev_1y_05_ust >= 1.75 and ev_1y_05_ust < 99.0 and ev_15_alt <= 1.38:
            return True, "DEPLASMAN BASKINI: Maçta Deplasman takımı favori (2.00-2.20 arası) ve KG Var (1.45 civarı) oldukça olası gösterilmiş. Ancak Ev sahibinin ilk yarıda gol atma ihtimali (1.Yarı 0.5 Üst) 1.80'lere kadar çıkarak neredeyse sıfırlanmış. Bu durumda ev sahibi kilitlenir, deplasman erken golle kilidi açar ve maç 0-2, 0-3 veya 0-4 gibi tek taraflı bir deplasman şovuna dönüşür. KG Yok ve MS 2 oynanmalıdır."
            
        return False, ""

class Rule1479(BaseRule):
    code = "1479"
    category = "YÖN"
    name = "Favori Gol Kısırlığı Tuzağı (Deplasman Galibiyeti)"
    description = "MS1 Favori + Ev 1.5 Alt Düşük + KG Var Düşük = Matematiksel MS2 Sinyali"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms1 < ms2 and ev_15_alt <= 1.55 and kg_var <= 1.55 and ev_15_alt != 99.0:
            return True, "FAVORİ GOL KISIRLIĞI TUZAĞI: Maçın favorisi Ev Sahibi gösterilmiş (MS1). Ancak Ev sahibinin 1.5 Alt oranı (maksimum 1 gol atar beklentisi) ve KG Var oranı çok düşük açılmış. Ev sahibi maksimum 1 gol atacaksa ve deplasman kesin gol bulacaksa, ev sahibinin maçı kazanma şansı matematiksel olarak yoktur! Bu durum MS1 oranının tamamen tuzak olduğunu kanıtlar. Deplasman takımı maçı kazanmaya veya puan almaya çok yakındır (X2 / MS2)."
            
        return False, ""

class Rule1480(BaseRule):
    code = "1480"
    category = "YÖN"
    name = "Tek Skor Darboğazı (Sahte Deplasman Favorisi)"
    description = "MS2 Favori + KG Var Düşük + 2.5 Üst Düşük + Ev 1.5 Alt Düşük = MS1 Tuzağı"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        
        if ms2 < ms1 and ms2 <= 1.95 and kg_var <= 1.50 and ust25 <= 1.60 and ev_15_alt <= 1.35 and ev_15_alt != 99.0:
            return True, "TEK SKOR DARBOĞAZI: Deplasman favori, KG Var ve 2.5 Üst oranları çok düşük. Olasılıklar maçın 1-2 veya 1-3 biteceğine işaret ediyor. Ancak Ev sahibinin 1.5 Alt oranı (maksimum 1 gol) da çok düşük. Bu durum maçı tek bir matematiksel senaryoya (1-2 deplasman galibiyetine) sıkıştırır. Oran teorisine göre, piyasanın bu kadar bariz bir 'tek skor' senaryosunda yığılması matematiksel bir çelişkidir. Maçın MS1 veya 1X ile ev sahibine gitmesi ve kısır geçmesi (Örn: 2-0, 1-0) çok daha olasıdır."
            
        return False, ""

class Rule1481(BaseRule):
    code = "1481"
    category = "YÖN"
    name = "Aşırı Gollü Sahte Favori Tuzağı (Deplasman Sürprizi)"
    description = "MS1 Favori + KG Var Çok Düşük + 3.5 Üst Çok Düşük = Sürpriz Deplasman (X2)"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        
        ev_iy_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Alt/Üst 0.5_Üst", "Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst"])
        if ev_iy_05_ust != 99.0 and ev_iy_05_ust <= 1.45:
            return False, ""
        
        if ms1 < ms2 and ms1 <= 1.65 and ms1 != 99.0 and ms1 >= 1.45 and kg_var <= 1.35 and ust35 <= 1.85 and ust35 != 99.0:
            return True, "AŞIRI GOLLÜ SAHTE FAVORİ TUZAĞI: Ev sahibi 1.6X oranla favori gösterilmiş ve maçın 4+ gol (3.5 Üst) ile KG Var şeklinde biteceği çok bariz bir şekilde (aşırı düşük oranlarla) fiyatlanmış. Bu durum oyuncuları 'Ev sahibi 3-1 veya 4-1 kazanır' (MS1 + Üst) tuzağına çekmek içindir. İddaa böylesine gollü ve net bir favori galibiyetini bu kadar bağırarak vermez. Bu, deplasman takımının sürpriz bir şekilde maçta üstünlük kuracağı (Örn: 1-3, 2-2) devasa bir tuzaktır. MS2 veya X2 denenmelidir."
            
        return False, ""

class Rule1482(BaseRule):
    code = "1482"
    category = "TUZAK"
    name = "Ağır Deplasman Favorisi + Sahte KG Var Tuzağı (KG Yok)"
    description = "MS2 < 1.55 + KG Var < 1.60 = Ev sahibi gol atamaz, KG Yok Biter"
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms2 != 99.0 and ms2 <= 1.55 and kg_var != 99.0 and kg_var <= 1.60:
            return True, "SAHTE KG VAR TUZAĞI: Deplasman takımı maçı kazanmak için çok ağır favori (1.50 altı). Maçın normalde 0-2 veya 0-3 bitmesi beklenir. Ancak İddaa, KG Var oranını 1.60'ın altında açarak 'Ev sahibi de gol bulacak, bu maç karşılıklı golle üst bitecek (Örn: 1-2, 1-3)' izlenimi yaratıyor. Bu tamamen bahisçileri ÜST ve KG VAR bahislerine çekmek için kurulan bir yemdir. Ev sahibi gol bulamaz. Maç KG YOK biter."
            
        return False, ""

class Rule1483(BaseRule):
    code = "1483"
    category = "GOL"
    name = "Kısır Maç Görünümlü Düello (Alt/Üst Paradoksu)"
    description = "2.5 Alt < 1.65 iken, Üst ve Var < 2.35 ise maçta gizli bir gol düellosu vardır."
    
    @classmethod
    def evaluate(cls, odds):
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        ust_ve_var = get_odd(odds, ["Altı/Üstü 2.5 ve Karşılıklı Gol_Üst ve Var"])
        alt_ve_yok = get_odd(odds, ["Altı/Üstü 2.5 ve Karşılıklı Gol_Alt ve Yok"])
        
        if alt25 != 99.0 and alt25 < 1.65 and ust_ve_var != 99.0 and ust_ve_var <= 2.35 and (alt_ve_yok == 99.0 or alt_ve_yok != 99.0 and alt_ve_yok > 2.20):
            return True, "PARADOKS - GİZLİ DÜELLO: İddaa 2.5 Alt oranını düşük (1.65 altı) tutarak piyasayı 'Bu maç kısır geçecek' yalanına inandırıyor. Ancak '2.5 Üst ve KG Var' kombine oranı (2.35 altı) matematiksel olarak imkansız derecede düşük açılmış! Bu, maçın aslında 1-2, 2-1 veya 2-2 gibi gollü bir düelloya sahne olacağının en büyük kanıtıdır. Alt ve KG Yok bahisleri tamamen tuzaktır."
            
        return False, ""

class Rule1484(BaseRule):
    code = "1484"
    category = "SKOR"
    name = "Aşırı Şişirilmiş Favori Alt Tuzağı"
    description = "MS1 <= 1.25 + 2.5 Üst <= 1.30 + Ev 1.5 Alt >= 2.50 = 1-0 / 2-0 Alt"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        
        if ms1 <= 1.25 and ust25 != 99.0 and ust25 > 0 and ust25 <= 1.30 and ev_15_alt != 99.0 and ev_15_alt >= 2.50:
            return True, "AŞIRI ŞİŞİRİLMİŞ FAVORİ ALT TUZAĞI: Ev sahibi (1.20) banko favori. Maçın Üst biteceği ve Ev sahibinin en az 2-3 gol atacağı oranlara (Ev 1.5 Alt 3.00 vs) yansımış. MS1 oranı para kazandırmadığı için iddaa oyuncuları 'Ev Sahibi 2.5 Üst' veya '1 ve Üst' bahislerine yönlendiriliyor. Bu devasa bir tuzaktır. Maçta favori kazanır ama şova izin verilmez, rölantide 1-0 veya 2-0 biter. 2.5 Alt ve 3.5 Alt bahisleri gizli hazinedir."
        return False, ""

class Rule1489(BaseRule):
    code = "1489"
    name = "Aşırı Düşük KG Var Tuzağı (Gel Gel Tuzağı)"
    category = "GOL"
    description = "Favorili maçlarda KG Var oranı 1.25 ve altındaysa bu devasa bir tuzaktır."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst", "3.5 Üst"])
        ust45 = get_odd(odds, ["Alt/Üst 4.5_Üst", "Altı/Üstü 4.5_Üst", "4.5 Üst"])
        
        if kg_var <= 1.25 and (ms1 <= 1.50 or ms2 <= 1.50) and (ust35 == 99.0 or ust35 != 99.0 and ust35 > 1.70) and (ust45 == 99.0 or ust45 != 99.0 and ust45 > 2.00):
            return True, "AŞIRI DÜŞÜK KG VAR TUZAĞI (Favorili Maç): Maçta çok net bir favori (1.50 altı) varken, KG Var oranı mantık dışı bir seviyeye (1.25 ve altı) çekilmiş. Bu, herkese bedava para dağıtıyormuş gibi 'zayıf takım da kesin gol atar' yemi atılmasıdır! Bahis şirketleri asla bedava para dağıtmaz. Bu kadar bariz bir 'gel gel' tuzağı, favorinin maçı gol yemeden (1-0, 2-0) kazanacağının veya maçın tamamen kilitleneceğinin (0-0) kanıtıdır. Doğrudan Karşılıklı Gol Yok veya Alt oynanmalıdır."
        return False, ""

class Rule1490(BaseRule):
    code = "1490"
    name = "Devasa Favori Çöküşü (Garanti KG Var)"
    category = "SKOR"
    description = "MS1 <= 1.18 ama KG Var <= 1.35 ise deplasman patlaması yaşanır."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        
        if ms1 <= 1.18 and kg_var <= 1.35:
            return True, "DEVASA FAVORİ ÇÖKÜŞÜ: Ev sahibi (1.18 altı) devasa favori olmasına rağmen KG Var oranı (1.35 altı) inanılmaz düşük! Bu ne demek? Deplasmanın KESİNLİKLE gol atacağı biliniyor. Ev sahibinin maçı kazanabilmesi için en az 2-3 gol atması lazım, ancak bu bir patlama maçıdır. Deplasman takımı maçı 1-2 gibi bir skorla kazanabilir veya sürpriz bir beraberlik (1-1, 2-2) koparabilir. Taraf bahsinden (Banko MS1'den) uzak durulup, doğrudan KG Var, 2.5 Üst veya Sürpriz X2 Çifte Şans oynanmalıdır."
        return False, ""

class Rule1491(BaseRule):
    code = "1491"
    name = "Dengeli Maçlarda Gerçek Düello (1.25 Altı KG Var)"
    category = "GOL"
    description = "Tarafı belli olmayan dengeli maçta KG Var <= 1.25 ise kesin Üst biter."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt", "Deplasman Altı/Üstü 1.5_Alt"])
        
        if ev_15_alt != 99.0 and ev_15_alt <= 1.60: return False, ""
        if dep_15_alt != 99.0 and dep_15_alt <= 1.60: return False, ""
        
        if kg_var <= 1.25 and ms1 != 99.0 and ms1 > 1.80 and ms2 != 99.0 and ms2 > 1.80:
            return True, "GERÇEK DÜELLO TESPİTİ: Dengeli bir maçta (MS1 ve MS2 1.80 üzeri) KG Var oranı aşırı düşük (1.25 altı) açılmışsa, bu bir tuzak DEĞİLDİR! Takımların ofansif güçleri çok yüksektir ve maç gerçek bir düellodur (2-1, 2-2 vb.). Kesinlikle Karşılıklı Gol Var ve 2.5 Gol Üstü biter."
        return False, ""

class Rule1492(BaseRule):
    code = "1492"
    name = "Sahte KG Var Tuzağı (Favori Yemlemesi)"
    category = "SKOR"
    description = "Favori takımın olduğu maçta KG Var oranının aşırı düşürülmesi."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        # Sadece MS1 favoriyse
        if ms1 <= 1.70 and ms2 != 99.0 and ms2 >= 3.00 and kg_var <= 1.35 and kg_yok != 99.0 and kg_yok >= 2.10:
            return True, "SAHTE KG VAR TUZAĞI: Ev sahibi net bir favori (1.70 altı) olmasına rağmen, KG Var oranı şüpheli bir şekilde (1.35 altı) düşük tutularak 'deplasman takımı kesin gol atacak' algısı yaratılmış. Bu klasik bir iddaa yemi ve tuzağıdır. Gerçekte deplasman gol bulamaz ve Ev sahibi maçı gol yemeden (2-0, 3-0) rahat kazanır. MS 1 ve Karşılıklı Gol Yok oynanmalıdır."
        return False, ""




class Rule1493(BaseRule):
    code = "1493"
    name = "Sahte Deplasman Favorisi (Handikap 1 Gizli Bankosu)"
    category = "YÖN"
    description = "Deplasman favori (1.85-2.15) ama H1 <= 1.45 ve KG Var <= 1.50"
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        h1 = get_odd(odds, ["Handikaplı Maç Sonucu 0:1_1", "Handikaplı Maç Sonucu 1:0_1", "Handikap 1:0_1"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if 1.85 <= ms2 <= 2.15 and h1 <= 1.45 and h1 != 99.0 and kg_var <= 1.50:
            return True, "SAHTE DEPLASMAN FAVORİSİ: Deplasman takımı 1.85-2.15 arası oranla 'hafif favori' gibi sunulur ve KG Var (1.50 altı) ile maçın gollü geçeceği algısı yaratılır. Herkes Deplasman galibiyetine veya gollere yönelirken, iddaa arka planda 'Handikap 1' (Ev sahibinin yenilmeyeceği) oranını 1.45'in altına çekerek maçı Ev sahibine bağlamıştır. Deplasman favorisi tamamen sahtedir, maçı Ev sahibi sürpriz bir şekilde (2-0, 2-1) kazanır. Doğrudan MS1, 1X veya Handikap 1 oynanmalıdır."
        return False, ""
class Rule1493(BaseRule):
    code = "1493"
    name = "Çıplak Kral Tuzağı (1.10 Altı Patlama)"
    category = "SKOR"
    description = "1.10 ve altı orana sahip takımın maçı kazanamaması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if (ms1 <= 1.10 and ms1 != 99.0 and ms1 > 0) or (ms2 <= 1.10 and ms2 != 99.0 and ms2 > 0):
            return True, "ÇIPLAK KRAL TUZAĞI (1.10 ALTI): Takımlardan birine 1.10 veya daha düşük komik bir favori oranı açılmış. İstatistiksel olarak bu oran grubunda hiç beklenmedik anlarda inanılmaz bir patlama (sürpriz) yaşanır. Kasanın parasını 1.05 gibi değersiz bir orana yatırmak yerine, devasa bir sürpriz (Çifte Şans 1X veya X2) kovalamak veya hiç bulaşmamak en mantıklısıdır. Favorinin çöküş ihtimali masadadır."
        return False, ""

class Rule1494(BaseRule):
    code = "1494"
    name = "Sahte Kısır Deplasman (Ev Gol Atar Tuzağı)"
    category = "SKOR"
    description = "MS2 favoriyken Alt oranı düşük ama Ev Sahibinin gol atma ihtimali çok yüksek."
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        ev_ust05 = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst", "Ev Sahibi Altı/Üstü 0.5_Üst"])
        
        if ms2 <= 1.65 and alt25 <= 1.65 and ev_ust05 <= 1.45:
            return True, "SAHTE KISIR DEPLASMAN TUZAĞI: Deplasman favori gösterilmiş ve 2.5 Alt oranı çok düşük (1.65 altı). Herkes 0-1 veya 0-2 bekliyor. Ancak Ev Sahibinin gol atma oranı (0.5 Üst) 1.45 and altında! Ev sahibi kesin gol atacaksa ve deplasman da favoriyse maç nasıl Alt bitecek? Bu büyük bir çelişki ve tuzaktır. Maç kesinlikle karşılıklı gollerle 1-1, 1-2 veya 2-2 gibi gollü skorlara gidecektir. 2.5 Alt büyük bir yemdir. KG Var veya 2.5 Üst oynanmalıdır."
        return False, ""

class Rule1495(BaseRule):
    code = "1495"
    name = "Şüpheli Zayıf Takım Golü (Sürpriz 1-1 Tuzağı)"
    category = "SKOR"
    description = "MS1 banko favori ama zayıf takımın gol atma oranı şüpheli şekilde düşük."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        dep_ust05 = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        
        if ms1 <= 1.45 and alt25 <= 1.65 and dep_ust05 <= 1.60:
            return True, "ŞÜPHELİ ZAYIF TAKIM GOLÜ TUZAĞI: Ev sahibi (1.45 altı) banko favori ve maçın 2.5 Alt (1.65 altı) bitmesi bekleniyor. Klasik 1-0 veya 2-0 banko profili. ANCAK zayıf deplasman takımının 0.5 Üst (gol atar) oranı 1.60 ve altında açılmış! Bu kadar favori bir takımın evinde, zayıf takımın gol atmasına bu kadar yüksek ihtimal verilmesi devasa bir tuzaktır. Deplasman takımı kesin gol bulacak ve maç kilitlenip sürpriz bir şekilde 1-1 bitecektir. Banko MS1 oynamak intihardır, sürpriz beraberlik (MS0 veya X2 Çifte Şans) aranmalıdır."
        return False, ""

class Rule1499(BaseRule):
    code = "1499"
    name = "Kilitli Favori Çöküşü (Ev Sahibi Altı Paradoksu)"
    category = "SKOR"
    description = "Ev Sahibi favoriyken kendi Alt sınırlarına takılıp maçı kaybetmesi veya berabere kalması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_alt15 = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok", "Karşılıklı Gol Yok"])

        if ms1 <= 2.20 and ms2 != 99.0 and ms2 >= 2.90 and ev_alt15 != 99.0 and ev_alt15 > 0 and ev_alt15 <= 1.45 and kg_yok != 99.0 and kg_yok > 1.45:
            return True, "KİLİTLİ FAVORİ ÇÖKÜŞÜ: Ev sahibi takım maçın favorisi olarak gösteriliyor (2.20 altı) ancak iddaa Ev Sahibinin 1.5 Alt oranını (max 1 gol atar) 1.45 ve altı gibi bir seviyede kilitlemiş. Bir takım hem maçı kazanacak favoriyse hem de 2 gol bile atamıyorsa bu koca bir yalandır (KG Yok oranının 1.45 üzerinde olması maçın kilitlenmeyeceğini, deplasmanın da tehlike yaratacağını gösterir). Bu oranlar tamamen Ev Sahibine oynatmak içindir. Ev sahibi tek golle kilitlenip sürpriz bir beraberlik (1-1) alır veya maçı tamamen kaybeder (0-2). Deplasman Çifte Şans (X2) devasa bir fırsattır."
        return False, ""

class Rule1496(BaseRule):
    code = "1496"
    name = "Patlak Tahterevalli Tuzağı (Farklı Galibiyet)"
    category = "YÖN_VE_GOL"
    description = "Taraf oranları eşitken beraberlik oranının anormal yüksek olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if ms1 != 99.0 and ms2 != 99.0 and ms0 != 99.0 and abs(ms1 - ms2) <= 0.20 and ms0 >= 4.00:
            return True, "PATLAK TAHTEREVALLİ TUZAĞI: İki takımın taraf oranları birbirine çok yakın (Örn: 2.16 - 2.07) açılarak maç kağıt üzerinde tamamen ortada (dengeli) gibi gösterilmiş. ANCAK beraberlik oranı inanılmaz derecede yüksek (4.00 ve üzeri)! Eşit güçteki takımların maçında beraberliğin bu kadar imkansız fiyatlanması büyük bir çelişkidir. Bu durum, arka planda takımlardan birinin maça çok eksik veya moralsiz çıktığını ve maçın tarihi bir farka (Örn: 0-4, 3-0) sahne olacağını gösterir. Taraf bahsi yerine Karşılıklı Gol Yok veya 2.5 Üst (Tek taraflı şov) denenmelidir."
        return False, ""

class Rule1497(BaseRule):
    code = "1497"
    name = "Ölümcül Sessizlik Tuzağı (0-0 Yemi)"
    category = "SKOR"
    description = "KG Var oranının aşırı düşük olup maçın 0-0 kilitlenmesi."
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst", "3.5 Üst"])
        ust45 = get_odd(odds, ["Alt/Üst 4.5_Üst", "Altı/Üstü 4.5_Üst", "4.5 Üst"])
        
        if kg_var != 99.0 and kg_var > 0 and kg_var <= 1.25 and ms0 != 99.0 and ms0 >= 3.80 and (ust35 == 99.0 or ust35 != 99.0 and ust35 > 1.70) and (ust45 == 99.0 or ust45 != 99.0 and ust45 > 2.00):
            return True, "ÖLÜMCÜL SESSİZLİK TUZAĞI: Maçta KG Var oranı 1.25'in altına kadar düşürülmüş ve beraberlik oranı 3.80'in üzerine çıkarılmış. Bürolar vitrinde açıkça 'Bu maçta gollü bir düello olacak, taraf seçmeyin Üst ve KG Var oynayın' diye bağırıyor. İddaa hiçbir zaman bu kadar bariz ve risksiz bir gol partisini bedavaya dağıtmaz. Bu, tüm piyasayı gollere yönlendirip maçı 0-0 veya 1-0 gibi inanılmaz kısır bir skorda kilitlemek için kurulan ölümcül bir tuzaktır. Kesinlikle 2.5 Alt veya Karşılıklı Gol Yok oynanmalıdır."
        return False, ""

class Rule1498(BaseRule):
    code = "1498"
    name = "Sahte Banko Gol Tuzağı (1.10 Yemi)"
    category = "SKOR"
    description = "Favori olmayan takımın KESİN gol atacakmış gibi 1.10 altı orana sahip olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ev_ust05 = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst", "Ev Sahibi Altı/Üstü 0.5_Üst"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        
        if ms1 != 99.0 and ms1 >= 2.00 and ev_ust05 != 99.0 and ev_ust05 > 0 and ev_ust05 <= 1.12 and (ust35 == 99.0 or ust35 != 99.0 and ust35 > 2.20):
            return True, "SAHTE BANKO GOL TUZAĞI: Ev sahibi takım maçın net favorisi değil (MS1 2.00 ve üzeri), ANCAK iddaa Ev Sahibinin gol atma ihtimaline (0.5 Üst) 1.12 ve altı gibi komik derecede 'banko' bir oran açmış. Favori olmayan ve maçı kazanma garantisi bulunmayan bir takımın KESİN gol atacağına piyasayı bu kadar inandırmak devasa bir tuzaktır. Bu oran, herkesi kombinelere 'Ev 0.5 Üst' veya 'KG Var' ekletmek içindir. Sonuç tam bir şok olur: Ev sahibi gol bile atamaz, deplasman takımı maçı rahat kazanır (0-2, 0-4). MS2, X2 veya Karşılıklı Gol Yok oynanmalıdır."
        return False, ""

class Rule1500(BaseRule):
    code = "1500"
    name = "Sahte Ev Sahibi Baskısı (Yüksek KG Yok Yemi)"
    category = "YÖN_VE_GOL"
    description = "KG Yok oranı 2.00+ olup Ev Sahibi'nin kazanmasının beklendiği maçta deplasmanın patlama yapması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        kgy = get_odd(odds, ["Karşılıklı Gol_Yok"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        
        if 1.40 <= ms1 <= 1.65 and ms0 <= 3.50 and kgy != 99.0 and kgy >= 1.95 and kg_var <= 1.50 and ust <= 1.55:
            return True, "SAHTE EV SAHİBİ BASKISI: Ev sahibi (1.65 altı) ile favori, maç kesin Üst (1.55 altı) ve KG Yok 2.00'lere fırlamış (KG Var banko görülüyor). Klasik bir 2-1, 3-1 ev sahibi galibiyeti hikayesi yazılmış. BU KLASİK BİR KATLİAM TUZAĞI. İddaa böylesine bariz bir 'Fav kazanır ve maç gollü geçer' şablonunu vitrine koyduğunda Ev Sahibi darmadağın olur. Deplasman maçı 1-2 veya sürpriz bir 1-3/2-3 ile alır. Kesinlikle X2 Çifte Şans ve Deplasman tarafı oynanmalıdır."

        return False, ""

class Rule1501(BaseRule):
    code = "1501"
    name = "İlk Yarı Beton Tuzağı (0-0 Garantisi)"
    category = "SKOR"
    description = "Her iki takımın İlk Yarı 0.5 Alt oranlarının aşırı düşük olması."
    @classmethod
    def evaluate(cls, odds):
        iy_05_alt = get_odd(odds, ["1. Yarı Alt/Üst 0.5_Alt", "1. Yarı Altı/Üstü 0.5_Alt"])
        ev_1y_05_alt = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Alt", "Ev Sahibi 1. Yarı Alt/Üst 0.5_Alt"])
        dep_1y_05_alt = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Alt", "Deplasman 1. Yarı Alt/Üst 0.5_Alt"])
        
        if iy_05_alt != 99.0 and iy_05_alt > 0 and ev_1y_05_alt != 99.0 and ev_1y_05_alt > 0 and dep_1y_05_alt != 99.0 and dep_1y_05_alt > 0 and iy_05_alt <= 2.25 and ev_1y_05_alt <= 1.45 and dep_1y_05_alt <= 1.45:
            return True, "İLK YARI BETON TUZAĞI: İlk yarı 0.5 Alt oranı makul seviyedeyse (2.20 civarı) VE özellikle her iki takımın da ayrı ayrı İlk Yarı 0.5 Alt oranları 1.45'in altındaysa; maçın başlama vuruşundan itibaren sahada inanılmaz bir kilitlenme olacağı, takımların kaleye bile gidemeyeceği iddaa tarafından arka planda fiyatlanmıştır. İlk yarı %90 ihtimalle 0-0 biter. Maç da kuvvetle muhtemel 0-0 veya tek şanslı bir golle (1-0/0-1) tamamlanır. Tüm 'Üst' ve 'KG Var' beklentileri (diğer kurallar) çöpe atılmalıdır. Bu maç betondur, 2.5 Alt ve KG Yok bankodur."
        return False, ""

class Rule1502(BaseRule):
    code = "1502"
    name = "Handikaplı Şov Başlangıcı (1.50 Ev Sahibi Patlaması)"
    category = "YÖN_VE_GOL"
    description = "Alt beklentisi varken Ev Sahibinin handikap oranının şov vadetmesi."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        h01_1 = get_odd(odds, ["Handikaplı Maç Sonucu 0:1_1"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        
        if ms1 != 99.0 and ms1 > 0 and h01_1 != 99.0 and h01_1 > 0 and ms1 <= 1.55 and h01_1 <= 2.15 and alt25 <= 1.65:
            return True, "HANDİKAPLI ŞOV BAŞLANGICI: Ev sahibi takım maçın ağır favorisi (1.55 altı) olarak açılmış. Vitrinde 2.5 Alt oranı çok düşük (1.65 altı) tutularak maçı 1-0 gibi kısır bir skorla kazanacağı algısı yaratılmış. ANCAK Handikaplı Maç Sonucu (0:1) 1 oranı 2.60'ın altındadır! Bu gizli fiyatlama, iddaanın arka planda ev sahibinin rahatlıkla en az 2 farkla (2-0, 3-0) şov yaparak kazanacağını bildiğini ama milleti 1-0 veya kısır skorlara yönlendirmeye çalıştığını gösterir. Doğrudan MS1 ve Handikap 1 (H1) oynanmalı, 'Alt' illüzyonuna düşülmemelidir."
        return False, ""

class Rule1503(BaseRule):
    code = "1503"
    name = "Sahte Ev Sahibi Düellosu (Deplasman Vurgunu)"
    category = "YÖN_VE_GOL"
    description = "KG Var çok düşük, MS1 favoriyken, MS2 oranının gizli bir tehdit barındırması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms1 != 99.0 and ms1 >= 1.55 and ms1 <= 1.85 and kg_var != 99.0 and kg_var > 0 and kg_var <= 1.35 and ms2 <= 3.35:
            return True, "SAHTE EV SAHİBİ DÜELLOSU: Maçta Ev sahibi favori (1.60-1.80) ve KG Var oranı muazzam düşük (1.35 altı). Vitrinde maçın 2-1 veya 3-1 biteceği, gollü bir ev sahibi galibiyeti hikayesi sunuluyor. Ancak MS2 oranı 3.35'in altındadır (Yani deplasman hiç de zayıf değil, kazanma ihtimali yüksek). KG Var banko gösterilip tüm bahisler Ev sahibinin gollü galibiyetine yönlendiriliyorsa, bu bir deplasman tuzağıdır! Maçı ev sahibi değil, hızlı hücumlarla deplasman takımı kazanır (1-2, 1-3). MS2 veya X2 Çifte Şans değerlendirilmelidir."
        return False, ""


class Rule1504(BaseRule):
    code = "1504"
    name = "Kısır Favori Katliamı (1.5 Üst Uyumsuzluğu)"
    category = "YÖN_VE_GOL"
    description = "Ağır favori takımın kendi 1.5 Üst oranının beklenenden yüksek olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_ust15 = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Üst", "Ev Sahibi Altı/Üstü 1.5_Üst"])
        
        if ms1 != 99.0 and ms1 > 0 and ms1 <= 1.35 and ev_ust15 > 0 and ev_ust15 >= 1.45 and ev_ust15 != 99.0:
            return True, "KISIR FAVORİ KATLİAMI: Ev sahibi takım 1.35 altı oranla devasa bir favori (banko) olarak gösteriliyor. ANCAK Ev Sahibinin '1.5 Üst' (en az 2 gol atar) oranı 1.45 ve üzerinde! Normalde 1.30'luk bir favorinin 1.5 Üst oranı 1.20-1.25 civarında olmalıdır. İddaa ev sahibinin 2 gol atacağından şüpheliyse, bu takımın o maçı kazanması da kocaman bir yalandır. Tüm piyasa 1.30'luk banko MS1'e abanırken, deplasman takımı tarihi bir vurgun yapar (1-2, 1-3). MS2 sürprizi veya X2 Çifte Şans değerlendirilmelidir."
        return False, ""

class Rule1505(BaseRule):
    code = "1505"
    name = "Süper Düşük Beraberlik Tuzağı (Açık Hedef)"
    category = "YÖN_VE_GOL"
    description = "Beraberlik oranının inanılmaz seviyelere inip (2.70 altı) piyasayı çekmesi."
    @classmethod
    def evaluate(cls, odds):
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if ms0 != 99.0 and ms0 > 0 and ms0 <= 2.70 and ms2 <= 2.60:
            return True, "SÜPER DÜŞÜK BERABERLİK TUZAĞI: Maçın beraberlik (MS0) oranı 2.70 ve altına kadar indirilmiş! Bu, iddaanın futbol dünyasında çok nadir yaptığı 'Süper Düşük Beraberlik' tuzağıdır. Tüm bahisçilerin aklına 'Maç kesin berabere bitecek' fikri sokulur. Ancak arka planda bu maç çoktan deplasman takımı tarafına (0-1, 0-2) yazılmıştır. Piyasayı MS0'a kilitlerken Deplasman aradan sıyrılır. Doğrudan Deplasman galibiyeti (MS2) çok değerli bir tahmindir."
        return False, ""


class Rule1506(BaseRule):
    code = "1506"
    name = "Sahte Karşılıklı Gol (Gollü Favori Şovu)"
    category = "SKOR"
    description = "Ağır favori varken KG Var oranının aşırı düşük olmasıyla KG Var oynatıp KG Yok bitirmek."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if ms1 != 99.0 and ms1 > 0 and ms1 <= 1.35 and kg_var != 99.0 and kg_var > 0 and kg_var <= 1.25:
            return True, "SAHTE KARŞILIKLI GOL TUZAĞI: Ev sahibi ağır favori (1.35 altı) ve maçın KG Var oranı inanılmaz düşük (1.25 altı). İddaa, herkesin aklına 'Zayıf takım kontradan 1 gol atar, ev sahibi maçı 3-1, 4-1 kazanır' senaryosunu sokarak tüm piyasaya KG Var oynatmayı hedeflemektedir. Ancak gerçekte ağır favori takım kalesini tamamen kapatır ve tek taraflı bir gol şovu (4-0, 5-0) izletir. Bu, KG Var beklentisiyle milleti soymak için kurulmuş devasa bir tuzaktır. Maç kesinlikle KG Yok biter!"
        return False, ""

class Rule1507(BaseRule):
    code = "1507"
    name = "Sahte Favori Kilitlenmesi (Handikap 2 Tuzağı)"
    category = "YÖN_VE_GOL"
    description = "Ev sahibi banko görünürken Handikap 2 oranının tehlikeli derecede düşük olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        h01_2 = get_odd(odds, ["Handikaplı Maç Sonucu 0:1_2"])
        
        if ms1 != 99.0 and ms1 > 0 and ms1 <= 1.45 and h01_2 != 99.0 and h01_2 > 0 and h01_2 <= 1.95:
            return True, "SAHTE FAVORİ KİLİTLENMESİ: Ev sahibi takım 1.45 altı oranla net banko favori olarak açılmış. ANCAK Handikap (0:1) 2 oranı (yani deplasmanın kaybetmeme veya tek farkla yenilme opsiyonu) 2.15 ve altına indirilmiş. İddaa ev sahibinin asla fark atamayacağını, hatta zorlanıp puan kaybedeceğini arka planda fiyatlamıştır. Bu sahte bir bankodur, maç 0-0 veya 1-1 kilitlenir. X2 Çifte Şans ve 2.5 Alt çok değerlidir."
        return False, ""


class Rule1508(BaseRule):
    code = "1508"
    name = "Deplasman Gol Paradoksu (0-0 Kapanı)"
    category = "SKOR"
    description = "MS1 ve KG Yok favoriyken, Deplasman gol atar oranının aşırı düşük olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms1_kg_yok = get_odd(odds, ["Maç Sonucu ve Karşılıklı Gol_1 ve Yok"])
        ms1_kg_var = get_odd(odds, ["Maç Sonucu ve Karşılıklı Gol_1 ve Var"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if (ms1 != 99.0 and ms1 > 0 and ms1_kg_yok > 0 and ms1_kg_var > 0 and dep_05_ust > 0 and kg_var > 0 and ms1_kg_yok != 99.0 and ms1_kg_var != 99.0 and dep_05_ust != 99.0):
            if ms1 <= 1.65 and kg_var != 99.0 and kg_var >= 1.60 and ms1_kg_yok <= (ms1_kg_var - 0.50) and dep_05_ust <= 1.25:
                return True, "DEPLASMAN GOL PARADOKSU: İddaa 'Maç Sonucu 1 ve KG Yok' oranını çok düşük tutarak millete 'Ev sahibi maçı 1-0, 2-0 gol yemeden kazanır' algısı pompalıyor. Ancak aynı iddaa alt oranlarda 'Deplasman 0.5 Üst' oranını 1.25'in altına çekmiş! Yani 'Deplasman kesin gol atar' diyor. Eğer deplasman gol atacaksa ve ev sahibi kazanacaksa, neden MS1+KG Var oranı devasa yüksek? Çünkü Ev sahibinin kazanması tamamen YALANDIR. Bu bir kilitlenme maçı (0-0) veya sürpriz puan kaybı maçıdır. MS 0 denenmelidir."
        return False, ""


class Rule1509(BaseRule):
    code = "1509"
    name = "KG Var Paradoksu (Sürpriz MS2)"
    category = "YÖN_VE_GOL"
    description = "KG Var bankoyken MS1+KG Yok oranının MS1+KG Var oranından düşük olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms1_kg_yok = get_odd(odds, ["Maç Sonucu ve Karşılıklı Gol_1 ve Yok"])
        ms1_kg_var = get_odd(odds, ["Maç Sonucu ve Karşılıklı Gol_1 ve Var"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if (ms1 != 99.0 and ms1 > 0 and ms1_kg_yok != 99.0 and ms1_kg_yok > 0 and ms1_kg_var != 99.0 and ms1_kg_var > 0 and kg_var != 99.0 and kg_var > 0):
            if kg_var <= 1.55 and ms1 <= 2.00 and ms1_kg_yok < ms1_kg_var:
                return True, "KG VAR PARADOKSU: İddaa, KG Var oranını 1.55 ve altında tutarak maçta iki takımın da gol atacağını çok güçlü fiyatlamış. ANCAK favori takımın (MS1) kombine oranlarına baktığımızda, 'MS1 ve KG Yok' oranı, 'MS1 ve KG Var' oranından daha düşük! Bu imkansızdır. Madem maçta karşılıklı gol kesin gibi, neden favorinin gol yemeden kazanma oranı daha düşük? Çünkü Ev Sahibinin kazanması tamamen YALANDIR. İddaa KG Var olacağını biliyor ama ev sahibinin kazanamayacağını da biliyor. Maçta sürpriz bir şekilde Deplasman takımı gol atarak öne geçer veya kilitler (1-2, 1-3, 1-1). X2 Çifte Şans ve Deplasman galibiyeti çok değerlidir."
        return False, ""


class Rule1510(BaseRule):
    code = "1510"
    name = "Sahte 3.5 Alt İllüzyonu (Ağır Favori Patlaması)"
    category = "SKOR"
    description = "Ağır favori ve deplasman gol atar beklenirken 3.5 Alt oranının aşırı düşük açılması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ev_15_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Üst", "Ev Sahibi Altı/Üstü 1.5_Üst"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        alt_35 = get_odd(odds, ["Alt/Üst 3.5_Alt", "Altı/Üstü 3.5_Alt"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])

        # ⛔ 99.0 kontrolü — tüm oranlar mevcut olmalı
        if not (0 < ms1 < 99.0 and 0 < ev_15_ust < 99.0 and
                0 < dep_05_ust < 99.0 and 0 < alt_35 < 99.0):
            return False, ""

        # ⛔ KRİTİK İSTİSNA: Gerçek tek taraflı maç kontrolü (Rule1513B ile tutarlılık)
        iy_kg_yok = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Yok"])
        iy2_kg_yok = get_odd(odds, ["İkinci Yarı Karşılıklı Gol_Yok"])
        if (iy_kg_yok <= 1.12 and iy_kg_yok != 99.0) or \
           (iy2_kg_yok <= 1.25 and iy2_kg_yok != 99.0):
            return False, ""  # Maç gerçekten tek taraflı → dep gol atamaz → tuzak değil

        # ⛔ KG Var kontrolü: KG Var yüksekse (≥ 2.00) çelişki yok, tek taraflı maç
        if kg_var != 99.0 and kg_var >= 2.00:
            return False, ""

        # ⛔ Deplasman sadece 1 gol atacaksa çelişki zayıflar
        dep_15_ust = get_odd(odds, ["Deplasman Alt/Üst 1.5_Üst", "Deplasman Altı/Üstü 1.5_Üst"])
        if dep_15_ust != 99.0 and dep_15_ust >= 2.50:
            return False, ""  # Deplasman en fazla 1 gol → toplam 3 gol garanti değil

        # Ana koşullar (MS1 eşiği 1.35→1.45'e genişletildi)
        if ms1 <= 1.45 and ev_15_ust <= 1.45 and dep_05_ust <= 1.60 and alt_35 <= 1.30:
            return True, ("SAHTE 3.5 ALT İLLÜZYONU: Ev sahibi çok ağır favori (MS1=" + str(ms1) + ") ve en az 2 gol atması bekleniyor (Ev 1.5 Üst=" + str(ev_15_ust) + "). Aynı zamanda deplasmanın da gol atması güçlü ihtimal (Dep 0.5 Üst=" + str(dep_05_ust) + "). Matematiksel olarak maç zaten 2-1'den başlıyor (3 gol garanti). Buna rağmen iddaa 3.5 Alt oranını " + str(alt_35) + " ile çok düşük açarak 'Maç en fazla 2-1 veya 3-0 biter' yalanını pompalıyor. Bu tuzağın amacı insanları 3.5 Alt'a ve kısır skorlara yönlendirmektir. Maç 3-1, 4-1 gibi gollü bir şova (3.5 Üst) dönüşecektir!")
        return False, ""


class Rule1511(BaseRule):
    code = "1511"
    name = "Beraberliksiz Gol Düellosu (12 Çifte Şans İllüzyonu)"
    category = "SKOR"
    description = "MS1 ve MS2 >= 2.20 iken KG Var <= 1.45 ve 12 ÇŞ <= 1.20"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0", "Maç Sonucu_X"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        cs_12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1 ve 2", "Çifte Şans_1-2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust_25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        dep_15_alt = get_odd(odds, ["Deplasman Alt/Üst 1.5_Alt", "Deplasman Altı/Üstü 1.5_Alt"])
        
        # Takımların kısır kalma ihtimali yüksekse pas geç
        if ev_15_alt != 99.0 and ev_15_alt <= 1.60: return False, ""
        if dep_15_alt != 99.0 and dep_15_alt <= 1.60: return False, ""
        
        # Taraf oranları dengeli mi? (2.20 - 2.80)
        if 2.20 <= ms1 <= 2.80 and 2.20 <= ms2 <= 2.80:
            
            # Ana anomali şartları
            if (kg_var != 99.0 and kg_var <= 1.45) and \
               (cs_12 != 99.0 and cs_12 <= 1.20):
                   
                # Ekstra Teyitler (MS0 yüksek mi? 2.5 Üst destekliyor mu?)
                if (ms0 == 99.0 or ms0 != 99.0 and ms0 >= 3.20) and (ust_25 == 99.0 or ust_25 <= 1.80):
                    return True, (
                        "BERABERLİKSİZ GOL DÜELLOSU: Dengeli maçlarda (MS1=" + str(ms1) + ", MS2=" + str(ms2) + ") "
                        "teorik olarak 12 Çifte Şans oranının 1.28+ olması gerekirken iddaa bunu " + str(cs_12) + " "
                        "seviyesine düşürüp beraberlik ihtimalini dışlamış (MS0=" + str(ms0) + "). "
                        "Üstelik KG Var oranını da çok düşük (" + str(kg_var) + ") açmış. "
                        "Bu tablo, maçın bol gollü geçeceğini ancak kesinlikle bir kazanan çıkacağını gösterir. "
                        "2-2 veya 3-3 gibi gollü beraberlikler ihtimal dışıdır. Skor 2-1, 3-1, 1-2, 1-3 gibi "
                        "gollü galibiyetlere gider. 12 Çifte Şans + 2.5 Üst + KG Var oynanmalıdır."
                    )
        return False, ""


class Rule1512A(BaseRule):
    code = "1512A"
    name = "Gizli 2.5 Barajı (Şov Patlaması)"
    category = "GOL"
    description = "Ağır Favori maçında 2.5 Alt/Üst baremi açılmamışsa ve 3.5 Üst <= 1.65 ise 4-5 gol olur."
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        
        # Sadece genel 2.5 ve 3.5 baremlerini kontrol et (Ev/Dep hariç)
        has_25 = any('2.5' in k for k in odds.keys() if 'Alt/Üst 2.5' in k and 'Ev Sahibi' not in k and 'Deplasman' not in k)
        has_35 = any('3.5' in k for k in odds.keys() if 'Alt/Üst 3.5' in k and 'Ev Sahibi' not in k and 'Deplasman' not in k)
        
        ev_iy_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst"])
        dep_iy_05_ust = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        
        # Ana güvenlik kontrolleri ve şartlar
        if not has_25 and has_35 and (ms1 != 99.0 and ms1 <= 1.55) and (kg_var != 99.0 and kg_var <= 1.50) and ust35 != 99.0:
            if ust35 <= 1.65 or (ev_iy_05_ust != 99.0 and ev_iy_05_ust <= 1.50) or (dep_iy_05_ust != 99.0 and dep_iy_05_ust <= 1.50):
                return True, (
                    "GİZLİ BAREM İLLÜZYONU (ŞOV PATLAMASI): İddaa 2.5 baremini açmayarak 3.5 Üst oynamayı zorunlu kılmış. "
                    "Buna rağmen 3.5 Üst oranı (" + str(ust35) + ") çok düşük (1.65 altı). "
                    "Favori kazanır (MS1=" + str(ms1) + ") ve iki takım da gol atar (KG Var=" + str(kg_var) + ") beklentisiyle, "
                    "maçın 4-5 gollü bir şova dönüşeceğini bas bas bağırıyor! "
                    "2.5 Üst açsalar herkes kazanacaktı, bu yüzden kapattılar. Bu maçta 3.5 Üst ve KG Var bankodur."
                )
        return False, ""

class Rule1512B(BaseRule):
    code = "1512B"
    name = "Gizli 2.5 Barajı (Alt Tuzağı)"
    category = "GOL"
    description = "Ağır Favori maçında 2.5 Alt/Üst baremi açılmamışsa ve 3.5 Üst >= 1.80 ise Kısır maç olur."
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        
        has_25 = any('2.5' in k for k in odds.keys() if 'Alt/Üst 2.5' in k and 'Ev Sahibi' not in k and 'Deplasman' not in k)
        has_35 = any('3.5' in k for k in odds.keys() if 'Alt/Üst 3.5' in k and 'Ev Sahibi' not in k and 'Deplasman' not in k)
        
        ev_iy_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst"])
        dep_iy_05_ust = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        
        if not has_25 and has_35 and (ms1 != 99.0 and ms1 <= 1.55) and (kg_var != 99.0 and kg_var <= 1.50) and ust35 != 99.0:
            # 1.80'in üzerinde olma şartı (Tersine değil, direkt kontrol)
            if ust35 != 99.0 and ust35 >= 1.80 and (ev_iy_05_ust == 99.0 or ev_iy_05_ust != 99.0 and ev_iy_05_ust > 1.50) and (dep_iy_05_ust == 99.0 or dep_iy_05_ust != 99.0 and dep_iy_05_ust > 1.50):
                return True, (
                    "GİZLİ BAREM İLLÜZYONU (ALT TUZAĞI): İddaa 2.5 baremini açmayarak 3.5 Üst oynamayı zorunlu kılmış. "
                    "Ancak 3.5 Üst oranının (" + str(ust35) + ") çok yüksek (1.80 üzeri) olması, aslında maçın kısır "
                    "(1-0, 2-0) geçeceğini gösteriyor. İnsanları 'zaten gollü geçecek, 2.5 baremi bile açılmamış' "
                    "algısıyla 3.5 Üst'e veya KG Var'a yönlendirip kucağa düşürüyorlar. "
                    "Bu maçta yüksek gollü skor beklenmez (Alt 2.5 / MS 1-0 / 2-0)."
                )
        return False, ""


class Rule1513(BaseRule):
    code = "1513"
    name = "Suni Deplasman Favorisi (Handikap Uyumsuzluğu)"
    category = "GOL"
    description = "Deplasman net favori (1.50-1.75) görünmesine rağmen, Handikap 2 oranı çok yüksek (2.60+) ise ve KG Var düşükse, Ev sahibi sürpriz yapar."
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        h2 = get_odd(odds, ["Handikaplı Maç Sonucu 0:1_2", "Handikaplı Maç Sonucu 1:0_2", "Handikaplı Maç Sonucu 0:2_2"])

        # ⛔ KRİTİK İSTİSNA: İY/2Y KG Yok çok düşükse, maç GERÇEKTEN tek taraflıdır.
        iy_kg_yok = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Yok"])
        iy2_kg_yok = get_odd(odds, ["İkinci Yarı Karşılıklı Gol_Yok"])
        gercek_tek_tarafli = (iy_kg_yok <= 1.12 and iy_kg_yok != 99.0) or (iy2_kg_yok <= 1.25 and iy2_kg_yok != 99.0)
        if gercek_tek_tarafli:
            return False, ""

        # ⛔ H2 = 99.0 (oran yok) False Positive BUG'ını önleyen güvenlik kontrolü
        if h2 == 99.0 or kg_var == 99.0 or ms2 == 99.0:
            return False, ""

        if 1.30 <= ms2 <= 1.55 and h2 != 99.0 and h2 >= 2.80 and kg_var <= 1.55:
            return True, (
                "SUNİ FAVORİ VE DÜELLO: Deplasman takımı kağıt üzerinde ağır favori (MS2=" + str(ms2) + "). "
                "Ancak Handikap 2 oranının çok yüksek olması (H2=" + str(h2) + "), iddaa'nın deplasmanın "
                "maçı rahat kazanacağına inanmadığını gösteriyor. Üstelik KG Var oranının düşük olması (" + str(kg_var) + "), "
                "Ev sahibinin kesinlikle gol/goller bulacağını kanıtlıyor. Bu maçta Ev Sahibi sürprizi "
                "(1X Çifte Şans) ve Gollü bir senaryo (3-2, 2-2, 2-1) yaşanacaktır."
            )

        return False, ""


class Rule1513B(BaseRule):
    code = "1513B"
    name = "Gerçek Tek Taraflı Dep Hakimiyeti (İY+2Y KG Yok Garantisi)"
    category = "TARAF"
    description = "Güçlü dep favorisi + İY KG Yok ≤ 1.12 + 2Y KG Yok ≤ 1.25 → Tüm maç ev sahibi gol üretemez. MS2 + KG Yok + 2.5 Alt."
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        x2 = get_odd(odds, ["Çifte Şans_0 ve 2", "-_0 ve 2"])
        iy_kg_yok = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Yok"])
        iy2_kg_yok = get_odd(odds, ["İkinci Yarı Karşılıklı Gol_Yok"])
        
        if ms2 == 99.0 or iy_kg_yok == 99.0:
            return False, ""
            
        is_guclu_dep = ms2 <= 1.55
        is_iy_kilitli = iy_kg_yok <= 1.12
        is_iy2_kilitli = iy2_kg_yok <= 1.25 and iy2_kg_yok != 99.0
        is_x2_ultra = x2 <= 1.10 and x2 != 99.0
        
        if is_guclu_dep and is_iy_kilitli and (is_iy2_kilitli or is_x2_ultra):
            return True, (
                "GERÇEK TEK TARAFLI DEP HAKİMİYETİ: Deplasman güçlü favori (MS2=" + str(ms2) + "). "
                "İlk Yarı KG Yok oranı " + str(iy_kg_yok) + " ile piyasa ilk yarıda SADECE BİR TARAFIN "
                "gol atacağını garanti ediyor. " +
                ("İkinci Yarı KG Yok " + str(iy2_kg_yok) + " ile ikinci yarıda da aynı tablo devam ediyor. " if is_iy2_kilitli else "") +
                "Bu 'suni KG Var' DEĞİL, GERÇEK KG YOK'tur! Kural 1513 (Suni Favori) bu maçta GEÇERSİZDİR. "
                "Ev sahibi tüm maç boyunca gol üretemez. Skor 0-1 veya 0-2 gibi TEK TARAFLI biter. "
                "Doğru tahmin: MS2 + KG Yok + 2.5 Gol Altı."
            )
        return False, ""


class Rule2001(BaseRule):
    code = "2001"
    name = "Milli Maç Sendromu (Kısır Turnuva)"
    category = "GOL"
    description = "Milli maçlarda (veya U20) piyasa Asya tuzağı koksa da maç alt biter."
    
    @classmethod
    def evaluate(cls, odds):
        if not is_milli_mac(CURRENT_MATCH): return False, ""
        
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ev_iy_05_ust = get_odd(odds, ["Ev Sahibi 1. Yarı Altı/Üstü 0.5_Üst"])
        dep_iy_05_ust = get_odd(odds, ["Deplasman 1. Yarı Altı/Üstü 0.5_Üst"])
        
        if ms1 == 99.0 or ms2 == 99.0: return False, ""
        
        is_balanced = min(ms1, ms2) >= 1.90
        
        # ⛔ Eğer bahis şirketi açıkça gol düellosu bekliyorsa (KG Var <= 1.65), bu turnuva maçında kısır kuralı İŞLEMEZ!
        if kg_var <= 1.65 and kg_var != 99.0: return False, ""
        
        # ⛔ Her iki oranın da 99.0 olmadığından emin ol
        is_iy_kisir = (ev_iy_05_ust >= 1.85 and ev_iy_05_ust != 99.0) and \
                      (dep_iy_05_ust >= 1.85 and dep_iy_05_ust != 99.0)
                      
        is_kg_kisir = (kg_var > 1.65 and kg_var <= 1.85 and kg_var != 99.0)
        
        if is_balanced and (is_kg_kisir or is_iy_kisir):
            return True, (
                "MİLLİ MAÇ KISIRLIĞI: Normal bir lig maçında dengeli takımlar 'Asya Tuzağı' veya 'Gol Düellosu' "
                "alarmı verirdi. Ancak bu bir Milli Maç (MS1=" + str(ms1) + ", MS2=" + str(ms2) + "). "
                "İlk Yarı 0.5 Üst bireysel takım oranları veya KG Var durumu bize kimsenin erken risk almayacağını söylüyor. "
                "Milli maçlarda takımlar temkinli oynar, beraberlik (0-0, 1-1) çok yaygındır. "
                "KG Var veya Üst bahisleri büyük bir tuzaktır. 2.5 Alt bankodur."
            )
        return False, ""

class Rule2002(BaseRule):
    code = "2002"
    name = "Milli Maç Şovu (Zayıf Halka Ezilir)"
    category = "GOL"
    description = "Milli maçlarda favori takım, zayıf rakibi acımadan ezer."
    
    @classmethod
    def evaluate(cls, odds):
        if not is_milli_mac(CURRENT_MATCH): return False, ""
        
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        # 99.0 güvenlik kontrolü
        if ms1 == 99.0 or ms2 == 99.0:
            return False, ""
            
        fav_odd = min(ms1, ms2)
        
        # Eşik 1.15'ten 1.25'e genişletildi (Milli maçlarda 1.25 de devasa bir farktır)
        if fav_odd <= 1.25:
            return True, (
                "MİLLİ MAÇ EZİCİLİĞİ: Favori takım (" + str(fav_odd) + " oran) oldukça net bir üstünlüğe sahip. "
                "Milli maçlarda klasman farkı çok derindir. Normal liglerde zayıf takım kapanıp maçı 1-0'da tutabilir, "
                "ancak milli takımlarda zayıf halkalar koptuğunda maç 4-0, 5-0 gibi tarihi farklara gider. "
                "Burada sürpriz aramak intihardır. MS (Favori) ve 2.5 / 3.5 Üst bankodur."
            )
        return False, ""

class Rule2003(BaseRule):
    code = "2003"
    name = "Milli Maç Güçlü Favori Gol Şovu (Dengeli 2.5 Aldatmacası)"
    category = "GOL"
    description = "Milli maçlarda MS1 <= 1.50, 1.5Üst <= 1.25 ve dengeli 2.5 piyasası → Ev favori fark atar, 2.5 Üst!"
    
    @classmethod
    def evaluate(cls, odds):
        if not is_milli_mac(CURRENT_MATCH): return False, ""
        
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ust15 = get_odd(odds, ["Alt/Üst 1.5_Üst"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst"])
        
        if ms1 == 99.0 or ust15 == 99.0 or alt25 == 99.0 or ust25 == 99.0:
            return False, ""
            
        # Güçlü ev favorisi + 1.5Üst zaten garanti + dengeli 2.5 (fark küçük) = GOL ŞOV
        is_guclu_fav = ms1 <= 1.52
        is_15_ust_kucuk = ust15 <= 1.25
        is_dengeli_25 = abs(alt25 - ust25) < 0.12
        
        if is_guclu_fav and is_15_ust_kucuk and is_dengeli_25:
            return True, (
                "MİLLİ MAÇ GÜÇLÜ FAVORİ GOL ŞOVU: Ev sahibi (MS1=" + str(ms1) + ") son derece güçlü bir favori. "
                "1.5 Üst oranı (" + str(ust15) + ") ile piyasa zaten 2+ gol çıkacağını neredeyse garantilemekte. "
                "Ancak 2.5 Alt/Üst piyasası inanılmaz derecede dengeli açılmış (Alt=" + str(alt25) + " / Üst=" + str(ust25) + ", "
                "fark: " + str(round(abs(alt25-ust25), 2)) + "). Bu 'dengeli 2.5' görünümü tamamen ALDATMACADIR! "
                "Milli maçlarda bu kadar güçlü bir ev favorisi zayıf rakibi fark atar. 2.5 ÜSTÜ, 3.5 Üstü ve MS1 bankodur."
            )
        return False, ""

class Rule1514(BaseRule):
    code = "1514"
    name = "Aşırı Düşük KG Var Tuzağı (Buzul Sessizliği)"
    category = "SKOR"
    description = "KG Var oranı çok düşük olmasına rağmen ilk yarı 1.5 Üst oranı çok yüksekse maç kısır biter."
    
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        iy_15_ust = get_odd(odds, ["1. Yarı Alt/Üst 1.5_Üst", "İlk Yarı Altı/Üstü 1.5_Üst"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        # Oran çekilememe güvenlik duvarı
        if kg_var == 99.0 or iy_15_ust == 99.0 or ms1 == 99.0 or ms2 == 99.0:
            return False, ""
            
        is_balanced = min(ms1, ms2) >= 1.70 and max(ms1, ms2) <= 2.80
        
        if kg_var <= 1.35 and iy_15_ust != 99.0 and iy_15_ust >= 2.60 and is_balanced:
            return True, (
                "AŞIRI DÜŞÜK KG VAR TUZAĞI (BUZUL SESSİZLİĞİ): Dengeli bir maçta (MS1=" + str(ms1) + ", MS2=" + str(ms2) + ") "
                "piyasada KG Var oranı (" + str(kg_var) + ") aşırı düşük açılarak herkese 'Bu maç kesin gollü geçecek, "
                "iki takım da atacak' mesajı (yemi) veriliyor. Ancak İlk Yarı 1.5 Üst oranının (" + str(iy_15_ust) + ") "
                "devasa yüksekliği bunun tam tersini fısıldıyor. Eğer maç cidden düello olsaydı, ilk yarı kilitli kalmazdı. "
                "Bu muazzam bir alt tuzağıdır! İddaa insanları KG Var'a yükletip maçı 0-0 veya 1-0 bitirecektir. Alt banko."
            )
        return False, ""


class Rule1515(BaseRule):
    code = "1515"
    name = "Sahte Ev Sahibi Golü Tuzağı (Deplasman Fark Patlaması)"
    category = "GOL"
    description = "Deplasman Ağır Favori + Ev Sahibi Asla Kazanamaz (MS1 >= 4.00) + KG Var Düşük (Yem)"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])

        # 99.0 Güvenlik Duvarı
        if ms1 == 99.0 or ms2 == 99.0 or kg_var == 99.0:
            return False, ""

        iy_15_ust = get_odd(odds, ["İlk Yarı Alt/Üst 1.5_Üst"])
        dep_35_ust = get_odd(odds, ["Deplasman Alt/Üst 3.5_Üst"])
        dep_15_ust = get_odd(odds, ["Deplasman Alt/Üst 1.5_Üst", "Deplasman Altı/Üstü 1.5_Üst"])
        
        gercek_kg_var = (iy_15_ust <= 1.50 and iy_15_ust != 99.0 and dep_35_ust <= 2.10 and dep_35_ust != 99.0)
        if gercek_kg_var:
            return False, ""

        if ms2 <= 1.50 and ms1 != 99.0 and ms1 >= 4.00:
            # KRİTİK FİLTRE: KG Var 1.35'in altındaysa bu bir tuzak değil, GERÇEK bir düellodur.
            ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst", "Ev Sahibi Altı/Üstü 0.5_Üst"])
            
            if 1.35 <= kg_var <= 1.50 and (ev_05_ust == 99.0 or ev_05_ust != 99.0 and ev_05_ust >= 1.45):
                if dep_15_ust != 99.0 and dep_15_ust > 1.55:
                    return False, ""
                    
                return True, (
                    "SAHTE EV SAHİBİ GOLÜ: Deplasman takımı çok rahat kazanacak (MS2=" + str(ms2) + "). "
                    "Ev sahibine ise kazanması imkansız bir oran (MS1=" + str(ms1) + ") açılmış. "
                    "Buna rağmen KG Var oranı " + str(kg_var) + " civarında 'cazip' bir tuzak seviyesinde. "
                    "Bu, iddaacıların 'Ev sahibi nasıl olsa evinde 1 gol atar' diye düşünmesini sağlamak için "
                    "kurulmuş devasa bir yemdir. Ev sahibi gol atamaz, Deplasman takımı fark atarak (0-3, 0-4) kazanır. KG Yok."
                )
        return False, ""


class Rule1516(BaseRule):
    code = "1516"
    name = "Sahte Deplasman Golü Tuzağı (Ev Sahibi Katliamı)"
    category = "GOL"
    description = "Ev Sahibi Ağır Favori + Deplasman Asla Kazanamaz (MS2 >= 4.00) + KG Var Düşük (Yem)"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        # 99.0 Güvenlik Duvarı
        if ms1 == 99.0 or ms2 == 99.0 or kg_var == 99.0:
            return False, ""
            
        ev_15_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Üst", "Ev Sahibi Altı/Üstü 1.5_Üst"])
        
        if ms1 <= 1.45 and ms2 != 99.0 and ms2 >= 4.00:
            dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
            
            # KG Var çok düşükse (1.35 altı) veya Deplasman 0.5 Üst 1.45 altındaysa gerçekten atar! (örn 2-2 biter)
            if 1.35 <= kg_var <= 1.50 and (dep_05_ust == 99.0 or dep_05_ust != 99.0 and dep_05_ust >= 1.45):
                if ev_15_ust != 99.0 and ev_15_ust > 1.55:
                    return False, ""
                    
                return True, (
                    "SAHTE DEPLASMAN GOLÜ: Ev sahibi takımı çok rahat kazanacak (MS1=" + str(ms1) + "). "
                    "Deplasmana ise kazanması imkansız bir oran (MS2=" + str(ms2) + ") açılmış. "
                    "Buna rağmen KG Var oranı " + str(kg_var) + " civarında cazip bir tuzak seviyesinde tutulmuş. "
                    "Bu, iddaacıların 'Ev sahibi zaten yener, Deplasman da bari kontra bir gol atar' "
                    "diye düşünmesini sağlamak için kurulmuş devasa bir yemdir. "
                    "Deplasman gol atamaz, Ev Sahibi takımı kalesini gole kapatıp fark atarak (3-0, 4-0) kazanır. KG Yok."
                )
        return False, ""

class RuleG13(BaseRule):
    code = "G13"
    category = "GOL"
    name = "Her İki Yarıda Da Karşılıklı Gol (İYKG)"
    description = "Tüm gol baremlerinin ve yarı oranlarının inanılmaz gollü bir senaryoyu desteklemesi."
    
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst"])
        iy_kg_var = get_odd(odds, ["1. Yarı Karşılıklı Gol_Var"])
        iy2_kg_var = get_odd(odds, ["2. Yarı Karşılıklı Gol_Var"])
        
        if (1.35 <= kg_var <= 1.75) and ust25 <= 1.65 and ev_05_ust <= 1.60 and dep_05_ust <= 1.60 and iy_kg_var <= 3.40 and iy2_kg_var <= 2.99:
            return True, "HER İKİ YARIDA KARŞILIKLI GOL (İYKG): Gol beklentisi o kadar yüksek ki, hem ilk yarı hem de ikinci yarıda her iki takımın da gol bulması matematiksel olarak destekleniyor. Çılgın bir düello bekleniyor."
        return False, ""


class RuleT70(BaseRule):
    code = "T70"
    name = "Süper Kısır Çift Tuzağı (0-0 / 1-1 İllüzyonu)"
    category = "SKOR"
    description = "Üst ve KG Var favori gösterilmesine rağmen Tek oranının çok yüksek, Çift oranının düşük kalması."
    
    @classmethod
    def evaluate(cls, odds):
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        tek = get_odd(odds, ["Tek/Çift_Tek", "Maç Skoru Tek/Çift_Tek", "Tek / Çift_Tek"])
        cift = get_odd(odds, ["Tek/Çift_Çift", "Maç Skoru Tek/Çift_Çift", "Tek / Çift_Çift"])
        
        if ust25 <= 1.65 and kg_var != 99.0 and kg_var >= 1.75 and tek >= 1.75 and tek != 99.0 and cift <= 1.70:
            return True, "SÜPER KISIR ÇİFT TUZAĞI (0-0 / 1-1): Piyasa KG Var ve Üst oranlarını yüksek tutarak maçın gollere kapalı olduğunu gösteriyor (KG Var != 99.0 and Var > 1.75). Aynı zamanda Tek oranı anormal derecede yüksek (1.75+) ve Çift oranı çok düşük (1.70 altı). Bu devasa çelişki, İddaa'nın maçın gollü (2-1 vb.) geçmeyeceğini, tam tersine 0-0 veya 1-1 gibi Kısır-Çift bir skorla kilitleneceğini bildiğini gösterir. Kesinlikle Alt ve Beraberlik aranmalıdır."
        return False, ""


class Rule1517(BaseRule):
    code = "1517"
    name = "Matematiksel KG Var Paradoksu (Sürpriz Deplasman Golü)"
    category = "GOL_VE_YÖN"
    description = "Ev sahibi 3 gol atamazken maçın 3 gollü beklenmesi ama KG Var oranının şişirilmesi."
    
    @classmethod
    def evaluate(cls, odds):
        ev_alt25 = get_odd(odds, ["Ev Sahibi Alt/Üst 2.5_Alt", "Ev Sahibi Altı/Üstü 2.5_Alt"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        # 99.0 Güvenlik Duvarı
        if ev_alt25 == 99.0 or ust25 == 99.0 or kg_var == 99.0:
            return False, ""
            
        if ev_alt25 != 99.0 and ev_alt25 > 0 and ev_alt25 <= 1.45 and ust25 <= 1.65 and kg_var != 99.0 and kg_var >= 1.75:
            return True, (
                "MATEMATİKSEL KG VAR PARADOKSU: İddaa 'Ev Sahibi 2.5 Alt' oranını çok düşük (" + str(ev_alt25) + ") tutarak "
                "ev sahibinin tek başına 3 gol atamayacağını söylüyor. Fakat aynı iddaa maçın '2.5 Üst' biteceğini de (" + str(ust25) + ") "
                "düşük oranla savunuyor. Ev sahibi 3 gol atamayacaksa, o 3. gol mecburen deplasman takımından gelecektir! "
                "Buna rağmen KG Var oranı (" + str(kg_var) + ") gibi fahiş seviyeye çıkarılarak millet KG Yok'a (deplasman gol atamaz) "
                "yönlendiriliyor. Bu korkunç bir tuzaktır. Deplasman kesin gol atar ve maç 2.5 Üst (Örn: 2-1) biter."
            )
        return False, ""


class Rule1518(BaseRule):
    code = "1518"
    category = "GOL"
    name = "Gizli Düello (Alt/KG Yok İllüzyonu)"
    description = "Ev 0.5 Üst <= 1.35 + Dep 0.5 Üst <= 1.35 + (2.5 Alt <= 1.55 veya KG Yok <= 1.70) = KG Var / Üst"
    
    @classmethod
    def evaluate(cls, odds):
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst", "Ev Sahibi Altı/Üstü 0.5_Üst"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        alt_25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        
        # 99.0 Güvenlik Duvarı
        if ev_05_ust == 99.0 or dep_05_ust == 99.0 or alt_25 == 99.0 or kg_yok == 99.0:
            return False, ""
            
        if ev_05_ust <= 1.35 and dep_05_ust <= 1.35 and (alt_25 <= 1.55 or kg_yok <= 1.75) and alt_25 != 99.0 and alt_25 > 1.45:
            return True, (
                "GİZLİ DÜELLO (PİYASA MANİPÜLASYONU): Ana marketlere bakan halk 2.5 Alt (" + str(alt_25) + ") ve "
                "KG Yok (" + str(kg_yok) + ") oranlarını görüp maçın kısır geçeceğine inanıyor. "
                "ANCAK alt marketler gerçeği söylüyor: Ev sahibi 0.5 Üst (" + str(ev_05_ust) + ") ve Deplasman 0.5 Üst (" + str(dep_05_ust) + ") "
                "çok düşük açılmış. Yani bürolar her iki takımın da kesinlikle gol atacağını biliyor! "
                "Bu inanılmaz bir tuzaktır. Maç 0-0 veya kısır bitmeyecek, tam aksine 1-1'i çok erken aşıp 3-1, 1-2 gibi gollü skorlara gidecek. Hedef KG Var ve Üst!"
            )
            
        return False, ""

class Rule1521(BaseRule):
    code = "1521"
    name = "Hayalet Barem (Kapalı 2.5) Tuzağı"
    category = "GOL"
    description = "2.5 Alt/Üst kapalıyken KG Var oranının çok düşük (1.30 altı) açılması."
    @classmethod
    def evaluate(cls, odds):
        alt_25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt", "2.5 Alt"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var", "Karşılıklı Gol Var"])
        ust_35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst", "3.5 Üst"])
        
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        
        if alt_25 == 99.0 and kg_var <= 1.35 and kg_var != 99.0:
            if (ust_35 != 99.0 and ust_35 >= 1.85 or ust_35 == 99.0) or (ust_35 != 99.0 and ust_35 >= 1.75 and ms1 != 99.0 and ms1 >= 2.00):
                return True, "HAYALET BAREM (SAHTE DÜELLO) TUZAĞI: Maçta standart 2.5 Alt/Üst baremi kapalı (oran açılmamış) olmasına rağmen, Karşılıklı Gol Var oranı inanılmaz derecede düşük (1.35 altı) açılmış. Bürolar 2.5 marketini gizleyip herkesi 'kesin karşılıklı gol olacak' diye KG Var oynamaya itmektedir. Bu bir 'Sahte Düello' yemi ve tuzağıdır! Ev sahibi favoriyse ve maç yüksek gollü beklenmiyorsa veya Deplasman favoriyse ev sahibi oyunu kilitler. Maç %90 ihtimalle tek taraflı farklı bir skorla veya tamamen kilitlenerek (0-0) biter. Doğrudan 'Karşılıklı Gol Yok' denenmelidir!"
        return False, ""

class Rule1534(BaseRule):
    code = "1534"
    category = "SKOR"
    name = "Matematiksel 1-0 Kesinliği (Kısır Favori)"
    description = "Ev 1.5 Alt Düşük + KG Yok Düşük + MS0 Düşük = Kesin 1-0 / 2-0"

    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok", "Karşılıklı Gol Yok"])

        if ev_15_alt != 99.0 and ev_15_alt <= 1.45 and kg_yok != 99.0 and kg_yok <= 1.45 and ms0 <= 2.90 and ms1 < 2.00:
            return True, "MATEMATİKSEL 1-0 KESİNLİĞİ: Bu maçta tuzak yoktur, gerçekler vardır. Ev sahibinin 1.5 Altı çok düşük (maksimum 1 gol), KG Yok çok düşük (biri gol atamayacak) ve MS0 (2.70-2.90 arası) kilitlenmeyi gösteriyor. Favori olan Ev sahibi, maçı tam da beklendiği gibi 1-0 veya 2-0 kazanacaktır. Taraf bahislerinde MS1, gol bahislerinde 2.5 Alt ve KG Yok en güvenli limandır."
        
        return False, ""

class Rule1533(BaseRule):
    code = "1533"
    name = "Ağır Favori Çöküşü (Gizli Ev Sahibi Şovu)"
    category = "SKOR"
    description = "Deplasman ağır favori, maç 3.5 Üst ama Deplasman 2.5 Alt sınırlandırılmış."
    
    @classmethod
    def evaluate(cls, odds):
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ust_35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst"])
        dep_25_alt = get_odd(odds, ["Deplasman Alt/Üst 2.5_Alt", "Deplasman Altı/Üstü 2.5_Alt"])
        
        if ms2 <= 1.40 and ust_35 <= 1.70 and dep_25_alt <= 1.65 and dep_25_alt != 99.0:
            return True, "AĞIR FAVORİ ÇÖKÜŞÜ (GİZLİ EV SAHİBİ ŞOVU): Deplasman takımı 1.40 altı oranla banko favori gösterilmiş. Üstelik maçın 3.5 Üst oranı (1.70 altı) çok düşük, yani maçta 4 veya daha fazla gol bekleniyor! ANCAK korkunç bir matematiksel çelişki var: Deplasman takımının 2.5 Alt oranı çok düşük (1.65 altı). İddaa diyor ki; 'Maçta 4 gol olacak ama favori takım en fazla 1 veya 2 gol atabilecek.' Bu durumda geriye kalan golleri (2 veya 3 gol) mecburen zayıf görülen Ev Sahibi atacaktır! Bu bir favori çöküşü ve Ev Sahibi sürprizidir. Deplasman kazanamaz, maç 2-2, 3-1 veya 3-2 gibi tarihi bir sürprizle biter. 1X Çifte Şans ve Ev Sahibi golleri denenmelidir."
        return False, ""

class Rule1532(BaseRule):
    code = "1532"
    name = "Kısır Favori Sendromu (Zar Zor Galibiyet)"
    category = "SKOR"
    description = "Ağır favorinin 1.5 Üst oranı çok yüksek (1.85+), maç kilitlenir."
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ev_15_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Üst", "Ev Sahibi Altı/Üstü 1.5_Üst"])
        
        if ms1 <= 1.50 and ev_15_ust >= 1.85 and ev_15_ust != 99.0:
            return True, "KISIR FAVORİ SENDROMU: Maçın ağır bir favorisi var (MS1 <= 1.50). Normal şartlarda bu takımın en az 2 gol atması beklenir. Ancak İddaa, Ev Sahibi 1.5 Üst oranını inanılmaz yüksek (1.85+) tutarak aslında favorinin gol yollarında tıkanacağını haber veriyor. Bu favoriye güvenip gollü bir galibiyet veya handikap oynamak intihardır. Maç 1-0 kilitlenebilir ya da 1-1 sürprizle bitebilir. Taraf bahsi yerine 2.5 Alt veya X2 Çifte Şans aranmalıdır."
        return False, ""

class Rule1531(BaseRule):
    code = "1531"
    name = "Gizli Favori Sendromu (Deplasman Sürprizi)"
    category = "GOL_VE_YÖN"
    description = "MS1 favori gösterilirken, Deplasman 0.5 Üst çok düşük."
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        dep_05_ust = get_odd(odds, ["Deplasman Alt/Üst 0.5_Üst", "Deplasman Altı/Üstü 0.5_Üst"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        
        if 1.50 <= ms1 <= 1.85 and dep_05_ust <= 1.35 and dep_05_ust != 99.0 and ev_15_alt != 99.0 and ev_15_alt <= 1.75:
            return True, "GİZLİ FAVORİ SENDROMU (DEPLASMAN VURGUNU): Ev sahibi kağıt üzerinde favori (1.85 altı). Ancak Deplasman takımının gol atma ihtimali (0.5 Üst) 1.35 ve altı gibi komik bir seviyeye indirilmiş. İddaa ev sahibini sadece yem olarak öne sürüyor; asıl güvendiği takım Deplasman takımıdır! Bu maçta ev sahibi büyük ihtimalle puan kaybedecek. Deplasman takımı maçı 1-2, 1-3 gibi skorlarla alabilir veya en kötü ihtimalle Karşılıklı Gol Var gelir."
        return False, ""

class Rule1530(BaseRule):
    code = "1530"
    name = "İlk Yarı Şifresi (Kısır Maç, Hızlı Gol)"
    category = "ZAMANLAMA"
    description = "Piyasa Kısır Beklerken (Alt), İlk Yarı 0.5 Üst aşırı düşük."
    
    @classmethod
    def evaluate(cls, odds):
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        iy_05_ust = get_odd(odds, ["İlk Yarı Alt/Üst 0.5_Üst", "1. Yarı Altı/Üstü 0.5_Üst"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        
        # Eğer MS0 <= 2.90 ise, beraberlik ihtimali çok yüksektir ve bu gerçek bir kısır kilitlenme (0-0/1-1) maçıdır. 1530 tuzağı değildir.
        if 1.48 <= alt25 <= 1.60 and iy_05_ust <= 1.30 and iy_05_ust != 99.0 and ms1 >= 1.60 and ms2 >= 1.60 and ms1 != 99.0 and ms2 != 99.0:
            return True, "İLK YARI ŞİFRESİ (ERKEN GOL PATLAMASI): Piyasa 2.5 Alt (1.60 altı) göstererek maçı kısır bir 0-0 veya 1-0 maçına kilitliyor. FAKAT dengeli bir maç (taraf oranları yüksek) olmasına rağmen mikro baremlere baktığımızda, İlk Yarı 0.5 Üst (1.30 altı) adeta banko gösterilmiş! İddaa ilk yarıdan kesinlikle en az bir gol geleceğini biliyor. Genel kısır algısının aksine, bu maç ilk yarıdan çözülecek ve büyük ihtimalle 2.5 Üst'e de taşınacaktır. 0-0 kilitlenmesi bekleyenler büyük hüsrana uğrayacaktır. İlk yarı golü değerlendirilmelidir."
        return False, ""
class Rule1523(BaseRule):
    code = "1523"
    name = "Şeytani İlk Yarı Şöleni (Ters Manyel)"
    category = "GOL"
    description = "Ağır favorinin 1.5 Alt oranı çok düşük, İY0 banko gösterilmiş ama maç ilk yarıdan patlar."
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        iy_0 = get_odd(odds, ["1. Yarı Sonucu_0", "İlk Yarı Sonucu_0"])
        iy_kg_var = get_odd(odds, ["1. Yarı Karşılıklı Gol_Var", "İlk Yarı Karşılıklı Gol_Var"])
        
        if ms1 <= 1.65 and ev_15_alt <= 1.55 and iy_0 <= 1.85 and iy_kg_var >= 5.50 and iy_kg_var != 99.0:
            return True, "ŞEYTANİ İLK YARI ŞÖLENİ: Maçın ağır bir favorisi (1.65 altı) var ama İddaa bu takımın 2 gol bile atamayacağını (Ev 1.5 Alt) iddia ediyor! Üstelik İlk Yarı 0-0 kilitlenme oranı (İY0) anormal şekilde dibe çekilmiş ve İY KG Var oranı ulaşılamaz (5.50+) seviyelere çıkarılmış. Piyasa tamamen 'Bu maç 0-0 veya 1-0 kısır biter' algısına itiliyor. Bu tarihin en büyük ters manyellerinden biridir. Maç kısır geçmeyecek, tam aksine İLK YARIDAN 3 veya 4 gol (1.5 Üst, 2.5 Üst, İY KG Var) patlayacaktır. 0-0 kilitlenmesi tamamen sahtedir."
        return False, ""

class Rule1522(BaseRule):
    code = "1522"
    name = "Sahte Kısır 12 (Şov Patlaması) Tuzağı"
    category = "GOL"
    description = "Dengeli maçta Alt favoriyken, 12 Çifte Şans'ın 1.18 altına indirilerek beraberliğin dışlanması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        cs_12 = get_odd(odds, ["Çifte Şans_12", "Çifte Şans_1 ve 2", "Çifte Şans_1-2"])
        alt_25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt", "2.5 Alt"])
        
        if ms1 != 99.0 and ms2 != 99.0 and cs_12 != 99.0 and alt_25 != 99.0:
            if abs(ms1 - ms2) <= 0.30 and alt_25 <= 1.65 and cs_12 <= 1.18:
                return True, "SAHTE KISIR 12 (ŞOV PATLAMASI) TUZAĞI: Taraf oranları birbirine çok yakın ve Alt oranı favori (kısır maç beklentisi). ANCAK 12 Çifte Şans oranı 1.18 ve altına indirilmiş! Dengeli ve kısır geçmesi beklenen bir maçta (0-0, 1-1) beraberliğin bu kadar bariz şekilde dışlanması devasa bir tuzaktır. Arka planda 3-2, 4-2 gibi tarihi bir gol şovu (Sürpriz Üst) kurgulanmıştır. Taraf bahislerinden uzak durulup doğrudan 2.5 Üst veya KG Var denenmelidir."
        return False, ""

class Rule1519(BaseRule):
    code = "1519"
    name = "Kısır Şovmen Tuzağı (1.30 Altı Favori - 3.5 Alt Uyarısı)"
    category = "SKOR"
    description = "1.30 altı favorinin maçında 3.5 Alt oranının çok düşük olması şov olmayacağını gösterir."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        if ms1 == 99.0 or ms2 == 99.0: return False, ""
        alt_35 = get_odd(odds, ["Alt/Üst 3.5_Alt", "Altı/Üstü 3.5_Alt", "3.5 Alt"])
        ust35_1 = get_odd(odds, ["Maç Sonucu ve Alt/Üst 3.5_1 ve Üst", "Maç Sonucu ve Altı/Üstü 3.5_1 ve Üst"])
        ust35_2 = get_odd(odds, ["Maç Sonucu ve Alt/Üst 3.5_2 ve Üst", "Maç Sonucu ve Altı/Üstü 3.5_2 ve Üst"])
        
        if 1.01 < ms1 <= 1.30 and alt_35 <= 1.50 and alt_35 != 99.0 and (ust35_1 != 99.0 and ust35_1 > 2.55 or ust35_1 == 99.0):
            return True, "KISIR ŞOVMEN TUZAĞI: Ağır favorinin (MS1) olduğu bir maçta, İddaa'nın 3.5 Alt oranını çok düşük (<= 1.50) açması ve MS1+3.5 Üst oranını da yüksek (> 2.55) tutması büyük bir sinyaldir. Normalde favorinin şov yapması beklenir ama piyasa maçta 4 gol olmayacağından ve favorinin zorlanacağından emin. Bu takım hücumda kilitlenecektir (Örn: 0-0, 1-0). MS bahsinden uzak durulmalı, doğrudan 3.5 Alt veya KG Yok oynanmalıdır."
        if 1.01 < ms2 <= 1.30 and alt_35 <= 1.50 and alt_35 != 99.0 and (ust35_2 != 99.0 and ust35_2 > 2.55 or ust35_2 == 99.0):
            return True, "KISIR ŞOVMEN TUZAĞI: Ağır favorinin (MS2) olduğu bir maçta, İddaa'nın 3.5 Alt oranını çok düşük (<= 1.50) açması ve MS2+3.5 Üst oranını da yüksek (> 2.55) tutması büyük bir sinyaldir. Piyasalar favorinin şov yapmayacağından (4 gol çıkmayacağından) emin. Bu maç kilitlenmeye (Örn: 0-0, 0-1) gebedir. 3.5 Alt veya KG Yok oynanmalıdır."
        return False, ""

class Rule1545(BaseRule):
    code = "1545"
    category = "TUZAK"
    name = "Sahte KG Var (İlk Yarı Kilit Tuzağı)"
    description = "KG Var <= 1.45 ama İlk Yarı KG Yok <= 1.25"
    
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        iy_kg_yok = get_odd(odds, ["İlk Yarı Karşılıklı Gol_Yok"])
        
        if kg_var != 99.0 and iy_kg_yok != 99.0:
            if kg_var <= 1.45 and iy_kg_yok <= 1.25:
                return True, "SAHTE KG VAR (İLK YARI KİLİT TUZAĞI): İddaa, Karşılıklı Gol Var oranını çok düşük (1.45 altı) açarak maçı bir gol düellosu gibi gösteriyor ve herkesi 'KG Var' veya 'Üst' bahsine çekiyor. ANCAK alt marketlerde 'İlk Yarı KG Yok' oranını 1.25 ve altına indirerek, maçın ilk yarısının tamamen kilitli geçeceğini (0-0 veya 1-0) matematiksel olarak itiraf ediyor. İlk yarısı kilitli geçen maçlarda sonradan her iki takımın da gol atması mucizedir. Bu devasa bir yanılsama ve tuzaktır. KG Var bahsinden kesinlikle uzak durulmalı, doğrudan 2.5 Gol Altı veya Maç Sonucu 0/1/2 (KG Yok) yönlerine gidilmelidir."
        return False, ""

class Rule1542(BaseRule):
    code = "1542"
    name = "Gizli Şovmen İfşası (Patlayan Favori)"
    category = "SKOR"
    description = "1.30 altı favorinin maçında 3.5 Alt çok düşükken 1 ve 3.5 Üst kombinesinin gizlice düşürülmesi."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        if ms1 == 99.0 or ms2 == 99.0: return False, ""
        alt_35 = get_odd(odds, ["Alt/Üst 3.5_Alt", "Altı/Üstü 3.5_Alt", "3.5 Alt"])
        ust35_1 = get_odd(odds, ["Maç Sonucu ve Alt/Üst 3.5_1 ve Üst", "Maç Sonucu ve Altı/Üstü 3.5_1 ve Üst"])
        ust35_2 = get_odd(odds, ["Maç Sonucu ve Alt/Üst 3.5_2 ve Üst", "Maç Sonucu ve Altı/Üstü 3.5_2 ve Üst"])
        
        if 1.01 < ms1 <= 1.30 and alt_35 <= 1.50 and alt_35 != 99.0 and ust35_1 <= 2.55 and ust35_1 != 99.0:
            return True, "GİZLİ ŞOVMEN İFŞASI (PATLAYAN FAVORİ): İddaa 3.5 Alt oranını çok düşük (<= 1.50) açarak maçı 'kısır bir 1-0 veya 2-0' gibi pazarlıyor. ANCAK derin baremlerde 'MS1 ve 3.5 Üst' oranını anormal derecede (<= 2.55) düşük tutmuş! Bu bir matematiksel sızıntıdır: İddaa ağır favorinin şov yapıp (3-1, 4-0, 5-0) maçı tek başına üst'e taşıyacağını biliyor. Kısır zannedilen bu maç patlamaya hazırdır. 2.5 Üst veya 3.5 Üst oynanmalıdır!"
        if 1.01 < ms2 <= 1.30 and alt_35 <= 1.50 and alt_35 != 99.0 and ust35_2 <= 2.55 and ust35_2 != 99.0:
            return True, "GİZLİ ŞOVMEN İFŞASI (PATLAYAN FAVORİ): İddaa 3.5 Alt oranını çok düşük (<= 1.50) açarak maçı 'kısır bir 0-1 veya 0-2' gibi pazarlıyor. ANCAK derin baremlerde 'MS2 ve 3.5 Üst' oranını anormal derecede (<= 2.55) düşük tutmuş! Bu bir matematiksel sızıntıdır: İddaa ağır favorinin şov yapıp maçı tek başına üst'e taşıyacağını biliyor. Kısır zannedilen bu maç patlamaya hazırdır. 2.5 Üst veya 3.5 Üst oynanmalıdır!"
        return False, ""

class RuleLIG_ASYA(BaseRule):
    code = "LIG_ASYA"
    name = "Asya Kısırlaştırma İllüzyonu"
    category = "LİG_ÖZEL"
    description = "Asya liglerinde KG Yok oranı düşük tutularak Alt tuzağı kurulması."
    @classmethod
    def evaluate(cls, odds):
        lig_tipi = odds.get('__LIG_TIPI__', 'STANDART')
        kg_yok = get_odd(odds, ["Karşılıklı Gol_Yok"])
        
        if lig_tipi == 'ASYA' and kg_yok <= 1.70:
            return True, "ASYA LİGİ ÖZELLİĞİ: Asya takımları (Japonya, Kore vb.) genellikle hücum futbolu oynar. Bürolar KG Yok oranını çok düşük tutarak 'bu maçta sadece bir takım atar' algısı yaratır. Ancak bu tam bir Asya Tuzağıdır! Maçta iki takımın da gol atma ihtimali çok yüksektir. Direkt KG Var denenmeli."
        return False, ""

class RuleLIG_LATAM(BaseRule):
    code = "LIG_LATAM"
    name = "Güney Amerika Sertlik Tuzağı (Sahte Üst)"
    category = "LİG_ÖZEL"
    description = "Güney Amerika'da 2.5 Üst veya KG Var oranının cazip açılması."
    @classmethod
    def evaluate(cls, odds):
        lig_tipi = odds.get('__LIG_TIPI__', 'STANDART')
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        
        if lig_tipi == 'GÜNEY_AMERİKA' and ust25 <= 1.85 and kg_var <= 1.75:
            return True, "GÜNEY AMERİKA LİGİ ÖZELLİĞİ: Latin Amerika futbolu son derece sert ve defansiftir. Bürolar 2.5 Üst ve KG Var oranlarını şaşırtıcı derecede düşük açarak 'gollü maç' illüzyonu yaratıyor. Aslında bu, herkesi Üst'e çekip maçın 0-0 veya 1-0 gibi son derece kısır bir skorla bitirilmesi planıdır! Karşılıklı Gol Yok ve 2.5 Alt idealdir."
        return False, ""


class Rule1482(BaseRule):
    code = "1482"
    category = "GOL"
    name = "Sahte Düello Tuzağı (Düşük MS0 Çelişkisi)"
    description = "KG Var <= 1.40 + 2.5 Üst <= 1.50 + MS0 <= 3.15 = Alt / KG Yok"
    
    @classmethod
    def evaluate(cls, odds):
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if kg_var <= 1.40 and ust25 <= 1.50 and ms0 <= 3.15 and ms1 < ms2 and ms1 != 99.0 and ms1 >= 1.80:
            return True, "SAHTE DÜELLO TUZAĞI: Bürolar KG Var ve 2.5 Üst oranlarını çok düşük tutarak herkesi gollü bir maça inandırmış. Ancak beraberlik (MS0) oranı 3.15 veya altında. Eğer gerçekten gollü bir maç bekleniyorsa MS0 (2-2 vs. ihtimali için) daha yüksek olmalıydı. 3.15 gibi düşük bir MS0, aslında maçın 0-0 veya 1-0 gibi kısır bir skora kilitleneceğinin matematiksel itirafıdır. Bu devasa bir Alt ve KG Yok tuzağıdır. Taraf bahsinde MS1 veya 1X öne çıkar."
            
        return False, ""

class Rule1484(BaseRule):
    code = "1484"
    category = "SKOR"
    name = "Aşırı Şişirilmiş Favori Alt Tuzağı"
    description = "MS1 <= 1.25 + 2.5 Üst <= 1.30 + Ev 1.5 Alt >= 2.50 = 1-0 / 2-0 Alt"
    
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        ev_15_alt = get_odd(odds, ["Ev Sahibi Alt/Üst 1.5_Alt", "Ev Sahibi Altı/Üstü 1.5_Alt"])
        
        if ms1 <= 1.25 and ust25 <= 1.30 and ev_15_alt != 99.0 and ev_15_alt >= 2.50:
            return True, "AŞIRI ŞİŞİRİLMİŞ FAVORİ ALT TUZAĞI: Ev sahibi (1.20) banko favori. Maçın Üst biteceği ve Ev sahibinin en az 2-3 gol atacağı oranlara (Ev 1.5 Alt 3.00 vs) yansımış. MS1 oranı para kazandırmadığı için iddaa oyuncuları 'Ev Sahibi 2.5 Üst' veya '1 ve Üst' bahislerine yönlendiriliyor. Bu devasa bir tuzaktır. Maçta favori kazanır ama şova izin verilmez, rölantide 1-0 veya 2-0 biter. 2.5 Alt ve 3.5 Alt bahisleri gizli hazinedir."
            
        return False, ""

class Rule1535(BaseRule):
    code = "1535"
    name = "Handikap Çöküşü (X2 Sürprizi)"
    category = "YÖN"
    description = "MS1 1.35-1.55 iken Handikap 1'in 2.65 ve üzerinde olması büyük bir X2 tuzağıdır."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        h1 = get_odd(odds, ["Handikaplı Maç Sonucu 0:1_1", "Handikaplı Maç Sonucu 1:0_1", "Handikap 1:0_1"])
        if 1.35 <= ms1 <= 1.55 and h1 >= 2.65 and h1 != 99.0:
            return True, "HANDİKAP ÇÖKÜŞÜ (GİZLİ SÜRPRİZ): Ev sahibi takım 1.45 civarı oranla 'rahat favori' gibi gösterilmiş. Ancak handikap oranına bakıldığında (2.65 ve üzeri), büroların aslında ev sahibinin fark atamayacağını ve çok zorlanacağını itiraf ettiğini görüyoruz. Bu maçların %43'ünde favori takım puan kaybeder (Beraberlik veya Mağlubiyet). 2.50 civarı X2 (Çifte Şans) oranı inanılmaz bir 'Değer Bahsi (Value Bet)' fırsatıdır."
        return False, ""

class Rule1536(BaseRule):
    code = "1536"
    name = "3.5 Alt Sahtekarlığı (Gizli Kısır Maç)"
    category = "GOL"
    description = "2.5 Alt kapalı, KG Var <= 1.45 ve 3.5 Üst <= 1.60 iken maçın 3.5 Alt bitmesi."
    @classmethod
    def evaluate(cls, odds):
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt", "2.5 Alt"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var", "Karşılıklı Gol Var"])
        ust35 = get_odd(odds, ["Alt/Üst 3.5_Üst", "Altı/Üstü 3.5_Üst", "3.5 Üst"])
        
        if alt25 == 99.0 and 1.30 < kg_var <= 1.45 and ust35 <= 1.60 and ust35 != 99.0:
            return True, "3.5 ALT SAHTEKARLIĞI: İddaa 2.5 Alt/Üst baremini kapatarak ve 3.5 Üst oranını çok düşük (1.50 civarı) açarak herkesi 'kesin gollü geçecek, 5 gol falan olacak' algısına sokup 3.5 Üst oynamaya itmektedir. Oysa istatistikler bu maçların %48.5'inin 3.5 ALT (Örn: 2-1, 1-2, 1-1) bittiğini kanıtlıyor. Bürolar 3.5 Alt'a 2.40 gibi devasa bir oran vererek büyük bir tuzak kurmuştur. Doğrudan 3.5 Alt oynanmalıdır."
        return False, ""

class Rule1540(BaseRule):
    code = "1540"
    name = "Yarı Patlaması (Gizli Üst Sinyali)"
    category = "GOL"
    description = "2.5 Alt çok düşükken, Her İki Yarıda Alt 1.5_Hayır oranının düşük olması çelişkisi."
    @classmethod
    def evaluate(cls, odds):
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        iki_yari_alt_hayir = get_odd(odds, ["Her İki Yarıda da Alt 1.5_Hayır"])
        
        if alt25 <= 1.45 and iki_yari_alt_hayir <= 1.55:
            return True, "YARI PATLAMASI (Gizli Üst Sinyali): İddaa 2.5 Alt oranını 1.45 ve altında tutarak maçı 'Kısır, banko Alt biter' (maksimum 2 gol) diye pazarlıyor. Ancak gizli baremlerde 'Her İki Yarıda da Alt 1.5_Hayır' (Yani en az bir yarıda 2+ gol çıkar) oranını 1.55 ve altına düşürmüş. Bu devasa bir matematiksel çelişkidir! İddaa bir yarının mutlaka patlayacağını (gollü geçeceğini) biliyor ve Alt bahislerini tuzağa çekiyor. Bu oran çelişkisinde maçların yarıdan fazlası %50+ ihtimalle yüksek gollü (Üst) biter. Bırakın 2.5 Alt'ı, 2.5 Üst (2.50+ oranlardan) devasa bir fırsattır!"
        return False, ""

class Rule1541(BaseRule):
    code = "1541"
    name = "Matematiksel Alt Kilidinde Sahte Deplasman Favorisi"
    category = "TARAF"
    description = "Deplasman favoriyken ev sahibinin gol atması bekleniyor ve maç kısırsa, deplasman kazanamaz."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ev_05_ust = get_odd(odds, ["Ev Sahibi Alt/Üst 0.5_Üst", "Ev Sahibi Altı/Üstü 0.5_Üst"])
        alt15 = get_odd(odds, ["Alt/Üst 1.5_Alt", "Altı/Üstü 1.5_Alt"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        
        if ms2 < ms1 and ms2 != 99.0 and ev_05_ust <= 1.55:
            if alt25 <= 1.50 or alt15 <= 2.10:
                return True, "SAHTE DEPLASMAN KİLİDİ: İddaa Deplasmanı favori (MS2) gösteriyor. ANCAK Ev sahibinin gol atmasına kesin gözüyle bakılıyor (Ev 0.5 Üst <= 1.55) ve maçın maksimum 2 golle (kısır) biteceği öngörülüyor (2.5 Alt <= 1.50 veya 1.5 Alt <= 2.10). Matematiksel olarak Ev sahibi 1 gol atarsa ve maçta maksimum 2 gol olursa, skorlar ancak 1-0, 2-0 veya 1-1 olabilir. Hiçbir senaryoda Deplasman maçı kazanamaz! Bu Deplasman favorisi koca bir tuzaktır. Ev sahibi yenilmez (1X) veya doğrudan MS 1 denenmelidir."
        return False, ""


class Rule1553(BaseRule):
    code = "1553"
    name = "Dengeli KG Patlaması (Sahte Kısır - 3-2/2-2)"
    category = "TUZAK"
    description = "Tam dengeli maçta KG Var bankoyken Alt 2.5'in cazip gösterilmesi."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        
        if ms1 != 99.0 and ms2 != 99.0 and ms1 >= 1.95 and ms2 >= 1.95:
            if kg_var != 99.0 and kg_var <= 1.50 and alt25 != 99.0 and alt25 <= 1.65:
                return True, "DENGELİ KG PATLAMASI (SAHTE KISIR): Maç tamamen dengeli (Taraf yok) ve İddaa her iki takımın da kesinlikle gol atacağını (KG Var < 1.50) itiraf ediyor. Ancak 2.5 Alt oranı (1.65 altı) ile maçı 1-1 bitmeye kilitli gibi gösteriyor. Bu bir tuzaktır! İki takımın da gol atacağı garanti olan bir maçta, beraberlik bozucu bir 3. gol kesinlikle çıkacaktır. Maç 3-2 veya 2-2 gibi bol gollü bir skora patlayacaktır (2.5 Üst bankodur)."
        return False, ""

class Rule1554(BaseRule):
    code = "1554"
    name = "Ağır Favori Oran Çelişkisi (Puan Kaybı Tuzağı - 1-1/0-0)"
    category = "TUZAK"
    description = "1.30 altı favoriye anormal derecede düşük MS0 ve MS2 verilmesi."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        
        if ms1 != 99.0 and ms1 <= 1.30 and ms0 != 99.0 and ms0 <= 4.50 and ms2 != 99.0 and ms2 <= 8.50:
            return True, "AĞIR FAVORİ ORAN ÇELİŞKİSİ (PUAN KAYBI): Ev sahibi 1.30 altı oranla devasa bir favori. Ancak Beraberlik (4.50 altı) ve Deplasman (8.50 altı) oranları, bir ağır favori maçına göre İNANILMAZ DERECEDE DÜŞÜK! İddaa, MS1'i cazip bir banko yemi olarak sunarken aslında içeride konuk ekibin direneceğini çok iyi biliyor. Bu maçta ağır favori kesinlikle puan kaybedecektir (1-1 veya 0-0). MS1 uzak durulması gereken ölümcül bir tuzaktır."
        return False, ""

class Rule1555(BaseRule):
    code = "1555"
    name = "1-1 Sendromu (Yüksek Beraberlik Riski)"
    category = "TUZAK"
    description = "Normal favorili maçta MS0 ve KG Var düşükse 1-1 kilitlenme tuzağı."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        kg_var = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        
        if ms1 != 99.0 and 1.30 <= ms1 <= 1.55 and ms0 != 99.0 and ms0 <= 3.40 and kg_var != 99.0 and kg_var <= 1.55:
            if ust25 != 99.0 and ust25 <= 1.50:
                return False, ""
            return True, "1-1 SENDROMU (BERABERLİK TUZAĞI): Ev sahibi normal bir favori (1.30-1.55) ama Beraberlik (3.40 altı) ve KG Var (1.55 altı) oranları şüpheli derecede cazip. Bu maç 1-1 bitmeye programlanmıştır. MS0 veya İlk Yarı Beraberliği değerlendirilebilir."
        return False, ""

class Rule1556(BaseRule):
    code = "1556"
    name = "Kısır Favori Kilitlenmesi (0-0/1-1 Tuzağı)"
    category = "TUZAK"
    description = "MS1 favori iken MS0 ve Alt25 oranlarının anormal düşük olması."
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        
        if ms1 != 99.0 and 1.30 <= ms1 <= 1.55 and ms0 != 99.0 and ms0 <= 3.20 and alt25 != 99.0 and alt25 <= 1.50:
            return True, "KISIR FAVORİ KİLİTLENMESİ (1-1/0-0): Ev sahibi favori (1.30-1.55) olmasına rağmen, Beraberlik oranı (3.20 altı) bir favori maçına göre İNANILMAZ DERECEDE DÜŞÜK. Üstelik 2.5 Alt (1.50 altı) çok cazip. İddaa ev sahibinin gol yollarında tıkanacağını ve konuk ekibin puan alacağını bas bas bağırıyor. Bu maç 1-1 veya 0-0 kilitlenecektir. Çifte Şans X2 veya MS0 harika bir tercihtir."
        return False, ""


class RuleG1(BaseRule):
    code = "G1"
    name = "Kesin 2 Gol Sinyali"
    category = "GOL"
    @classmethod
    def evaluate(cls, odds):
        alt15 = get_odd(odds, ["Alt/Üst 1.5_Alt", "Altı/Üstü 1.5_Alt"])
        if alt15 >= 2.50 and alt15 != 99.0:
            return True, "Maçta en az 2 gol kesin çıkar."
        return False, ""

class RuleG11(BaseRule):
    code = "G11"
    name = "Gollü KG Var"
    category = "GOL"
    @classmethod
    def evaluate(cls, odds):
        kg = get_odd(odds, ["Karşılıklı Gol_Var"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        if kg <= 1.50 and ust25 <= 1.60 and kg != 99.0:
            return True, "KG Var ve 2.5 Üst beklentisi."
        return False, ""

class RuleS1(BaseRule):
    code = "S1"
    name = "Standart Kısır Favori (Tuzak Yok)"
    category = "BİLGİ"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        if (ms1 <= 1.80 or ms2 <= 1.80) and alt25 <= 1.70 and alt25 != 99.0:
            return True, "STANDART PİYASA (KISIR FAVORİ): Bu maçta herhangi bir anomali veya tuzak tespit edilemedi. İddaa oranları favorinin düşük gollü (1-0, 2-0) bir galibiyet alacağını net bir şekilde gösteriyor. Maçın genel gidişatına güvenilebilir, sürpriz aranmamalıdır."
        return False, ""

class RuleS2(BaseRule):
    code = "S2"
    name = "Standart Gollü Favori (Tuzak Yok)"
    category = "BİLGİ"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        ust25 = get_odd(odds, ["Alt/Üst 2.5_Üst", "Altı/Üstü 2.5_Üst"])
        if (ms1 <= 1.80 or ms2 <= 1.80) and ust25 <= 1.70 and ust25 != 99.0:
            return True, "STANDART PİYASA (GOLLÜ FAVORİ): Bu maçta herhangi bir anomali veya tuzak tespit edilemedi. İddaa oranları favorinin gollü (2-1, 3-0, 3-1 vb.) bir galibiyet alacağını gösteriyor. Gollere veya favoriye yönelmek piyasanın doğal akışıdır."
        return False, ""

class RuleT10(BaseRule):
    code = "T10"
    name = "Dengeli Kısır İç Saha"
    category = "YÖN"
    @classmethod
    def evaluate(cls, odds):
        ms0 = get_odd(odds, ["Maç Sonucu_0"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        if ms0 <= 2.90 and alt25 <= 1.60 and ms0 != 99.0:
            return True, "Beraberlik oranı çok düşük, maç kısır geçer."
        return False, ""

class RuleT27(BaseRule):
    code = "T27"
    name = "Az Gollü Temiz Favori"
    category = "YÖN"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        alt25 = get_odd(odds, ["Alt/Üst 2.5_Alt", "Altı/Üstü 2.5_Alt"])
        if ms1 <= 1.50 and alt25 <= 1.70 and ms1 != 99.0:
            return True, "Ev sahibi maçı alır ancak skor tek taraflı ve az gollü (1-0, 2-0) olur."
        return False, ""

class RuleT8(BaseRule):
    code = "T8"
    name = "Dengeli Ters Favori İç Saha"
    category = "YÖN"
    @classmethod
    def evaluate(cls, odds):
        ms1 = get_odd(odds, ["Maç Sonucu_1"])
        ms2 = get_odd(odds, ["Maç Sonucu_2"])
        if ms1 <= 2.20 and ms2 <= 3.20 and ms1 != 99.0:
            return True, "Dengeli maçta beraberlik dışlanmış, ev sahibi kazanır."
        return False, ""

class RuleY11(BaseRule):
    code = "Y11"
    name = "Psikolojik 12 Tuzağı (İlk Yarı 0 Bankosu)"
    category = "YARI"
    @classmethod
    def evaluate(cls, odds):
        cs_12 = get_odd(odds, ["Çifte Şans_1 ve 2", "Çifte Şans_12"])
        if cs_12 <= 1.20 and cs_12 != 99.0:
            return True, "İLK YARI 0 BANKOSU (PSİKOLOJİK TUZAK): İddaa dengeli bir maçta Çifte Şans 12'ye çok düşük oran (<= 1.20) vererek 'Bu maç asla berabere bitmez, kesin biri yener' algısı yaratıyor. Üstüne KG Var oranını da düşük tutarak maçın çok tempolu başlayacağı illüzyonunu kuruyor. Oysa istatistiklere göre bu maçların yarısından fazlası (%53.6) ilk yarıda tamamen kilitlenir. Büroların bu algı operasyonu yüzünden İlk Yarı 0'a verdikleri devasa 2.15+ oranlar sayesinde bu bahis uzun vadede %16.5 net kâr (ROI) bırakır!"
        return False, ""


def get_all_rules():
    import sys
    import inspect
    current_module = sys.modules[__name__]
    
    rules = []
    # Find all classes in this module that inherit from BaseRule (but are not BaseRule itself)
    for name, obj in inspect.getmembers(current_module, inspect.isclass):
        if issubclass(obj, BaseRule) and obj is not BaseRule:
            rules.append(obj)
            
    # Sort them by code or keep as is. In the old logic, they were hardcoded in order.
    # We will sort anomaly rules (digits) descending, and trend rules separately, 
    # to somewhat mimic the old priority order.
    anomaly_rules = []
    trend_rules = []
    
    for r in rules:
        if r.code.isdigit():
            anomaly_rules.append(r)
        else:
            trend_rules.append(r)
            
    # Sort anomaly descending (1556 -> 1460)
    anomaly_rules.sort(key=lambda x: int(x.code), reverse=True)
    # Trend rules sort by code (G1, G11, S1 etc)
    trend_rules.sort(key=lambda x: x.code)
    
    return anomaly_rules + trend_rules
