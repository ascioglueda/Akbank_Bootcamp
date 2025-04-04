from collections import defaultdict, deque
import heapq
from typing import Dict, List, Set, Tuple, Optional
import networkx as nx
import matplotlib.pyplot as plt

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
        if idx not in self.istasyonlar:
            istasyon = Istasyon(idx, ad, hat)
            self.istasyonlar[idx] = istasyon
            self.hatlar[hat].append(istasyon)

    def baglanti_ekle(self, istasyon1_id: str, istasyon2_id: str, sure: int) -> None:
        istasyon1 = self.istasyonlar[istasyon1_id]
        istasyon2 = self.istasyonlar[istasyon2_id]
        istasyon1.komsu_ekle(istasyon2, sure)
        istasyon2.komsu_ekle(istasyon1, sure)
    
    def en_az_aktarma_bul(self, baslangic_id: str, hedef_id: str) -> Optional[List[Istasyon]]:
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None
        
        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]
        
        kuyruk = deque([(baslangic, [baslangic])])
        ziyaret_edildi = {baslangic}
        
        while kuyruk:
            mevcut_istasyon, yol = kuyruk.popleft()
            
            if mevcut_istasyon == hedef:
                return yol
            
            for komsu_istasyon, _ in mevcut_istasyon.komsular:
                if komsu_istasyon not in ziyaret_edildi:
                    ziyaret_edildi.add(komsu_istasyon)
                    yeni_yol = yol + [komsu_istasyon]
                    kuyruk.append((komsu_istasyon, yeni_yol))
        
        return None

    def en_hizli_rota_bul(self, baslangic_id: str, hedef_id: str) -> Optional[Tuple[List[Istasyon], int]]:
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None
        
        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]
        
        pq = [(0, id(baslangic), baslangic, [baslangic])]
        heapq.heapify(pq)
        
        ziyaret_edildi = set()
        maliyetler = {baslangic: 0}
        
        while pq:
            toplam_sure, _, mevcut_istasyon, yol = heapq.heappop(pq)
            
            if mevcut_istasyon == hedef:
                return yol, toplam_sure
            
            if mevcut_istasyon in ziyaret_edildi:
                continue
            
            ziyaret_edildi.add(mevcut_istasyon)
            
            for komsu_istasyon, sure in mevcut_istasyon.komsular:
                yeni_maliyet = maliyetler[mevcut_istasyon] + sure
                
                if komsu_istasyon not in maliyetler or yeni_maliyet < maliyetler[komsu_istasyon]:
                    maliyetler[komsu_istasyon] = yeni_maliyet
                    yeni_yol = yol + [komsu_istasyon]
                    heapq.heappush(pq, (yeni_maliyet, id(komsu_istasyon), komsu_istasyon, yeni_yol))
        
        return None

    def metro_agi_gorsellestir(self, vurgulanacak_rota: Optional[List[Istasyon]] = None):
        """Metro ağını görselleştirir ve isteğe bağlı bir rotayı vurgular."""
        G = nx.Graph()
        
        # İstasyonları ve bağlantıları ekle
        for istasyon_id, istasyon in self.istasyonlar.items():
            G.add_node(istasyon.ad, hat=istasyon.hat)
            for komsu, sure in istasyon.komsular:
                G.add_edge(istasyon.ad, komsu.ad, weight=sure, hat=istasyon.hat)
        
        # Pozisyonları belirle
        pos = nx.spring_layout(G, k=1.0, iterations=100)  # Daha geniş bir düzen için k artırıldı
        
        # Renkleri hatlara göre ayarla
        renkler = {
            "Kirmizi Hat": "red",
            "Mavi Hat": "blue",
            "Turuncu Hat": "orange"
        }
        
        # Her hat için düğümleri çiz
        for hat, istasyonlar in self.hatlar.items():
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=[i.ad for i in istasyonlar],
                node_color=renkler[hat],
                node_size=700,
                label=hat,
                alpha=0.8
            )
        
        # Kenarları hatlara göre renklendir
        edge_colors = []
        for u, v, data in G.edges(data=True):
            hat = data.get('hat', None)
            if hat in renkler:
                edge_colors.append(renkler[hat])
            else:
                edge_colors.append("gray")  # Aktarma bağlantıları için gri
        
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2)
        
        # Vurgulanacak rotayı çiz (eğer varsa)
        if vurgulanacak_rota:
            rota_kenarlari = [(vurgulanacak_rota[i].ad, vurgulanacak_rota[i+1].ad) for i in range(len(vurgulanacak_rota)-1)]
            nx.draw_networkx_edges(G, pos, edgelist=rota_kenarlari, edge_color="green", width=4, style="dashed")
        
        # İstasyon isimlerini ekle
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")
        
        # Kenar ağırlıklarını (süreleri) ekle
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        # Grafik ayarları
        plt.title("Metro Ağı Haritası", fontsize=14, pad=20)
        plt.legend(scatterpoints=1, loc="best", fontsize=10)
        plt.axis("off")
        plt.tight_layout()
        plt.show()

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
        # Bu rotayı görselleştirmede vurgulayalım
        vurgulanacak_rota = rota
    
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
    
    # Metro ağını görselleştir (AŞTİ'den OSB'ye en hızlı rotayı vurgula)
    metro.metro_agi_gorsellestir(vurgulanacak_rota=vurgulanacak_rota)