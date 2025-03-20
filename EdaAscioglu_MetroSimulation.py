from collections import defaultdict, deque
import heapq
from typing import Dict, List, Set, Tuple, Optional

class Istasyon:
    def __init__(self, idx: str, ad: str, hat: str):
        self.idx = idx
        self.ad = ad
        self.hat = hat
        self.komsular: List[Tuple['Istasyon', int]] = []  
    def komsu_ekle(self, istasyon: 'Istasyon', sure: int):
        self.komsular.append((istasyon, sure))

class MetroAgi:
    def __init__(self):
        self.istasyonlar: Dict[str, Istasyon] = {}
        self.hatlar: Dict[str, List[Istasyon]] = defaultdict(list)

    def istasyon_ekle(self, idx: str, ad: str, hat: str) -> None:
        if idx not in self.istasyonlar:  # Fixed 'id' to 'idx'
            istasyon = Istasyon(idx, ad, hat)
            self.istasyonlar[idx] = istasyon
            self.hatlar[hat].append(istasyon)

    def baglanti_ekle(self, istasyon1_id: str, istasyon2_id: str, sure: int) -> None:
        istasyon1 = self.istasyonlar[istasyon1_id]
        istasyon2 = self.istasyonlar[istasyon2_id]
        istasyon1.komsu_ekle(istasyon2, sure)
        istasyon2.komsu_ekle(istasyon1, sure)
    
    def en_az_aktarma_bul(self, baslangic_id: str, hedef_id: str) -> Optional[List[Istasyon]]:
        # Baslangic ve hedef istasyonlarin varligini kontrol et
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None
        
        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]
        
        # Kuyruk: (mevcut istasyon, yol) tuple'lari tutar
        kuyruk = deque([(baslangic, [baslangic])])
        ziyaret_edildi = {baslangic}  # Ziyaret edilen istasyonlari takip et
        
        while kuyruk:
            mevcut_istasyon, yol = kuyruk.popleft()
            
            # Hedefe ulasildiysa rotayi dondur
            if mevcut_istasyon == hedef:
                return yol
            
            # Komsu istasyonlari keşfet
            for komsu_istasyon, _ in mevcut_istasyon.komsular:
                if komsu_istasyon not in ziyaret_edildi:
                    ziyaret_edildi.add(komsu_istasyon)
                    yeni_yol = yol + [komsu_istasyon]
                    kuyruk.append((komsu_istasyon, yeni_yol))
        
        return None  # Rota bulunamadi

    def en_hizli_rota_bul(self, baslangic_id: str, hedef_id: str) -> Optional[Tuple[List[Istasyon], int]]:
        # Baslangic ve hedef istasyonlarin varligini kontrol et
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None
        
        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]
        
        # Öncelik kuyruğu: (toplam_süre, baslangic_id, istasyon, yol)
        pq = [(0, id(baslangic), baslangic, [baslangic])]
        heapq.heapify(pq)
        
        ziyaret_edildi = set()  # Ziyaret edilen istasyonlari takip et
        maliyetler = {baslangic: 0}  # Her istasyona ulasma maliyeti
        
        while pq:
            toplam_sure, _, mevcut_istasyon, yol = heapq.heappop(pq)
            
            # Hedefe ulasildiysa rotayi ve sureyi dondur
            if mevcut_istasyon == hedef:
                return yol, toplam_sure
            
            # Daha once ziyaret edildiyse gec
            if mevcut_istasyon in ziyaret_edildi:
                continue
            
            ziyaret_edildi.add(mevcut_istasyon)
            
            # Komsu istasyonlari keşfet
            for komsu_istasyon, sure in mevcut_istasyon.komsular:
                yeni_maliyet = maliyetler[mevcut_istasyon] + sure
                
                if komsu_istasyon not in maliyetler or yeni_maliyet < maliyetler[komsu_istasyon]:
                    maliyetler[komsu_istasyon] = yeni_maliyet
                    yeni_yol = yol + [komsu_istasyon]
                    # A* için basit bir yaklaşım: heuristik olmadan sadece toplam süreyi kullan
                    heapq.heappush(pq, (yeni_maliyet, id(komsu_istasyon), komsu_istasyon, yeni_yol))
        
        return None  # Rota bulunamadi

if __name__ == "__main__":
    metro = MetroAgi()
    
    # İstasyonlar ekleme
    # Kirmizi Hat
    metro.istasyon_ekle("K1", "Kizilay", "Kirmizi Hat")
    metro.istasyon_ekle("K2", "Ulus", "Kirmizi Hat")
    metro.istasyon_ekle("K3", "Demetevler", "Kirmizi Hat")
    metro.istasyon_ekle("K4", "OSB", "Kirmizi Hat")
    
    # Mavi Hat
    metro.istasyon_ekle("M1", "ASTI", "Mavi Hat")
    metro.istasyon_ekle("M2", "Kizilay", "Mavi Hat")  # Aktarma noktası
    metro.istasyon_ekle("M3", "Sihhiye", "Mavi Hat")
    metro.istasyon_ekle("M4", "Gar", "Mavi Hat")
    
    # Turuncu Hat
    metro.istasyon_ekle("T1", "Batikent", "Turuncu Hat")
    metro.istasyon_ekle("T2", "Demetevler", "Turuncu Hat")  # Aktarma noktasi
    metro.istasyon_ekle("T3", "Gar", "Turuncu Hat")  # Aktarma noktasi
    metro.istasyon_ekle("T4", "Kecioren", "Turuncu Hat")
    
    # Bağlantilar ekleme
    # Kirmizi Hat baglantilari
    metro.baglanti_ekle("K1", "K2", 4)  # Kizilay -> Ulus
    metro.baglanti_ekle("K2", "K3", 6)  # Ulus -> Demetevler
    metro.baglanti_ekle("K3", "K4", 8)  # Demetevler -> OSB
    
    # Mavi Hat baglantilari
    metro.baglanti_ekle("M1", "M2", 5)  # ASTI -> Kizilay
    metro.baglanti_ekle("M2", "M3", 3)  # Kizilay -> Sihhiye
    metro.baglanti_ekle("M3", "M4", 4)  # Sihhiye -> Gar
    
    # Turuncu Hat baglantilari
    metro.baglanti_ekle("T1", "T2", 7)  # Batikent -> Demetevler
    metro.baglanti_ekle("T2", "T3", 9)  # Demetevler -> Gar
    metro.baglanti_ekle("T3", "T4", 5)  # Gar -> Keçiören
    
    # Hat aktarma baglantilari (aynı istasyon farkli hatlar)
    metro.baglanti_ekle("K1", "M2", 2)  # Kizilay aktarma
    metro.baglanti_ekle("K3", "T2", 3)  # Demetevler aktarma
    metro.baglanti_ekle("M4", "T3", 2)  # Gar aktarma
    
    # Test senaryolari
    print("\n=== Test Senaryolari ===")
    
    # Senaryo 1: AŞTİ'den OSB'ye
    print("\n1. ASTI'den OSB'ye:")
    rota = metro.en_az_aktarma_bul("M1", "K4")
    if rota:
        print("En az aktarmali rota:", " -> ".join(i.ad for i in rota))
    
    sonuc = metro.en_hizli_rota_bul("M1", "K4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hizli rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
    
    # Senaryo 2: Batikent'ten Kecioren'e
    print("\n2. Batikent'ten Kecioren'e:")
    rota = metro.en_az_aktarma_bul("T1", "T4")
    if rota:
        print("En az aktarmali rota:", " -> ".join(i.ad for i in rota))
    
    sonuc = metro.en_hizli_rota_bul("T1", "T4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hizli rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
    
    # Senaryo 3: Kecioren'den ASTI'ye
    print("\n3. Kecioren'den ASTI'ye:")
    rota = metro.en_az_aktarma_bul("T4", "M1")
    if rota:
        print("En az aktarmali rota:", " -> ".join(i.ad for i in rota))
    
    sonuc = metro.en_hizli_rota_bul("T4", "M1")
    if sonuc:
        rota, sure = sonuc
        print(f"En hizli rota ({sure} dakika):", " -> ".join(i.ad for i in rota))