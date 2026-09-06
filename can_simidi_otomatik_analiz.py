

class RuleT46_Super_Alt(BaseRule):
    code = "T46_SUPER_ALT"
    name = "Süper Düşük Alt Patlaması (1.15 Altı Tuzağı)"
    category = "KATLIAM"

    @classmethod
    def evaluate(cls, odds):
        try:
            alt_25 = get_odd(odds, ['Alt/Üst 2.5_Alt', 'Altı/Üstü 2.5_Alt'])
            ms0 = get_odd(odds, ['Maç Sonucu_0'])
            
            if alt_25 != 99.0 and ms0 != 99.0:
                if alt_25 <= 1.15 and ms0 <= 2.65:
                    msg = (
                        "SÜPER DÜŞÜK ALT PATLAMASI (T46): İddaa 2.5 Alt oranını "
                        f"{alt_25} seviyesine, MS0'ı ise {ms0} gibi komik bir rakama indirerek "
                        "tüm dünyaya 'Bu maç 0-0 kilitlenecek' diye bağırıyor. Bu kadar bariz bir "
                        "kilitlenme her zaman devasa bir Üst patlaması tuzağıdır! İddaa kimseye "
                        "bedava 1.15 Alt yedirmez. Maç inanılmaz bir şekilde 2-2, 1-2 gibi "
                        "gollü skorlara, 2.5 ÜST'e gider. Kesinlikle ÜST aranmalıdır!"
                    )
                    return True, msg
        except Exception:
            pass
        return False, ""

class RuleT47_Sahte_Duello_V2(BaseRule):
    code = "T47_SAHTE_DUELLO"
    name = "Geliştirilmiş Sahte Düello Tuzağı (0-0 Kilidi)"
    category = "TUZAK_SKOR"

    @classmethod
    def evaluate(cls, odds):
        try:
            ms1 = get_odd(odds, ['Maç Sonucu_1'])
            ms0 = get_odd(odds, ['Maç Sonucu_0'])
            kg_var = get_odd(odds, ['Karşılıklı Gol_Var'])
            ust = get_odd(odds, ['Alt/Üst 2.5_Üst'])
            
            if ms1 != 99.0 and ms0 != 99.0 and kg_var != 99.0 and ust != 99.0:
                if 2.20 <= ms1 <= 2.65 and ms0 <= 3.20 and kg_var <= 1.45 and ust <= 1.55:
                    msg = (
                        "GELİŞTİRİLMİŞ SAHTE DÜELLO (T47): KG Var (" + str(kg_var) + ") ve Üst (" + str(ust) + ") "
                        "oranları inanılmaz düşük tutularak kitleler gollü bir maça (2-1, 1-2 vb.) yönlendiriliyor. "
                        "Ancak beraberlik (MS0) oranı 3.20'nin altında! Gerçekten gollü geçecek bir maçta "
                        "MS0 oranının daha yüksek olması gerekirdi. Bu uyumsuzluk, maçın 0-0 kilitleneceğinin veya "
                        "çok kısır bir 1-0 biteceğinin matematiksel ispatıdır. "
                        "Karar: 2.5 Alt ve KG Yok."
                    )
                    return True, msg
        except Exception:
            pass
        return False, ""



class RuleT48_Balanced_Shootout(BaseRule):
    code = "T48_BALANCED_SHOOTOUT"
    name = "Dengeli Gollü Beraberlik (Banja Luka İstisnası)"
    category = "DOMİNANT"

    @classmethod
    def evaluate(cls, odds):
        try:
            ms1 = get_odd(odds, ['Maç Sonucu_1'])
            ms2 = get_odd(odds, ['Maç Sonucu_2'])
            ms0 = get_odd(odds, ['Maç Sonucu_0'])
            kg_var = get_odd(odds, ['Karşılıklı Gol_Var'])
            
            if ms1 != 99.0 and ms2 != 99.0 and ms0 != 99.0 and kg_var != 99.0:
                # Denk güçler (2.20 - 2.80) ve MS0 aşırı düşük (2.95 altı)
                if 2.20 <= ms1 <= 2.80 and 2.20 <= ms2 <= 2.80 and ms0 <= 2.95:
                    msg = (
                        "DENGELİ DÜELLO (T48 - BANJA LUKA İSTİSNASI): İki takım da tamamen denk (2.20-2.80 bandı) "
                        f"ve MS0 oranı {ms0} gibi çok düşük bir seviyede. Makine bunu genelde '0-0 Kısır Kilit' sanıp "
                        "Alt tuzağına düşer. Ancak takımların tamamen dengeli olması, bu maçın kısır değil, "
                        "tam tersine 1-1 veya 2-2 gibi gollü bir beraberliğe (Düelloya) gideceğini gösterir. "
                        "Kesinlikle 2.5 Alt dayatması YAPILMAMALIDIR! Karar: Karşılıklı Gol Var ve MS0."
                    )
                    return True, msg
        except Exception:
            pass
        return False, ""

class RuleT49_Major_League_Over(BaseRule):
    code = "T49_MAJOR_LEAGUE_OVER"
    name = "Majör Lig Gerçek Düello (Newcastle İstisnası)"
    category = "DOMİNANT"

    @classmethod
    def evaluate(cls, odds):
        try:
            lig = str(odds.get("lig", "")).upper()
            kg_var = get_odd(odds, ['Karşılıklı Gol_Var'])
            
            # Majör liglerde (Özellikle İngiltere) KG Var düşükse, 1521 gibi kurallar "Tuzak" sanıp KG Yok verir.
            if any(x in lig for x in ["İNG", "ING", "PREMIER"]):
                if kg_var <= 1.45:
                    msg = (
                        "İNGİLTERE GERÇEK DÜELLO (T49 - NEWCASTLE İSTİSNASI): Premier Lig gibi dev liglerde "
                        f"KG Var oranı ({kg_var}) bu kadar düşükse, bu çoğunlukla bir tuzak (Sahte Düello / 1521) DEĞİL, "
                        "maçın gerçekten gollü geçeceğinin (2-2, 1-2, 2-1) net işaretidir. Makinenin "
                        "'KG Var tuzağı var, maç 0-1 biter' paranoyası bu liglerde iptal edilmelidir. "
                        "Çekirdek algoritma haklıdır: Karar KG Var ve 2.5 ÜST!"
                    )
                    return True, msg
        except Exception:
            pass
        return False, ""

