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
        self.komsular: List[Tuple['Istasyon', int, bool]] = []
    
    def komsu_ekle(self, istasyon: 'Istasyon', sure: int, aktarma: bool = False):
        self.komsular.append((istasyon, sure, aktarma))

class MetroAgi:
    def __init__(self):
        self.istasyonlar: Dict[str, Istasyon] = {}
        self.hatlar: Dict[str, List[Istasyon]] = defaultdict(list)
    
    def istasyon_ekle(self, idx: str, ad: str, hat: str) -> None:
        if not idx or not ad or not hat:
            raise ValueError("İstasyon ID, ad ve hat bilgileri boş olamaz.")
        if idx in self.istasyonlar:
            raise ValueError(f"{idx} ID'sine sahip bir istasyon zaten mevcut.")
        istasyon = Istasyon(idx, ad, hat)
        self.istasyonlar[idx] = istasyon
        self.hatlar[hat].append(istasyon)
    
    def baglanti_ekle(self, istasyon1_id: str, istasyon2_id: str, sure: int, aktarma: bool = False) -> None:
        if istasyon1_id not in self.istasyonlar or istasyon2_id not in self.istasyonlar:
            raise ValueError("Geçersiz istasyon ID'si.")
        if sure <= 0:
            raise ValueError("Süre pozitif bir sayı olmalıdır.")
        istasyon1 = self.istasyonlar[istasyon1_id]
        istasyon2 = self.istasyonlar[istasyon2_id]
        istasyon1.komsu_ekle(istasyon2, sure, aktarma)
        istasyon2.komsu_ekle(istasyon1, sure, aktarma)
    
    def en_az_aktarma_bul(self, baslangic_id: str, hedef_id: str) -> Optional[List[Istasyon]]:
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None
        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]
        kuyruk = deque([(baslangic, [baslangic], baslangic.hat, 0)])  # (istasyon, yol, mevcut hat, aktarma sayısı)
        ziyaret_edildi = {(baslangic, baslangic.hat): 0}  # (istasyon, hat) -> aktarma sayısı
        while kuyruk:
            mevcut_istasyon, yol, mevcut_hat, aktarmalar = kuyruk.popleft()
            if mevcut_istasyon == hedef:
                return yol
            for komsu_istasyon, sure, aktarma in mevcut_istasyon.komsular:
                yeni_hat = komsu_istasyon.hat if aktarma else mevcut_hat
                yeni_aktarmalar = aktarmalar + (1 if aktarma else 0)
                if (komsu_istasyon, yeni_hat) not in ziyaret_edildi or yeni_aktarmalar < ziyaret_edildi[(komsu_istasyon, yeni_hat)]:
                    ziyaret_edildi[(komsu_istasyon, yeni_hat)] = yeni_aktarmalar
                    yeni_yol = yol + [komsu_istasyon]
                    kuyruk.append((komsu_istasyon, yeni_yol, yeni_hat, yeni_aktarmalar))
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
            for komsu_istasyon, sure, aktarma in mevcut_istasyon.komsular:
                ek_maliyet = 2 if aktarma else 0  # Aktarma için ek 2 dakika
                yeni_maliyet = maliyetler[mevcut_istasyon] + sure + ek_maliyet
                if komsu_istasyon not in maliyetler or yeni_maliyet < maliyetler[komsu_istasyon]:
                    maliyetler[komsu_istasyon] = yeni_maliyet
                    yeni_yol = yol + [komsu_istasyon]
                    heapq.heappush(pq, (yeni_maliyet, id(komsu_istasyon), komsu_istasyon, yeni_yol))
        return None
    
    def en_hizli_rota_bul_hat_filtreli(self, baslangic_id: str, hedef_id: str, izin_verilen_hatlar: List[str]) -> Optional[Tuple[List[Istasyon], int]]:
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
            for komsu_istasyon, sure, aktarma in mevcut_istasyon.komsular:
                if not aktarma and komsu_istasyon.hat not in izin_verilen_hatlar:
                    continue
                ek_maliyet = 2 if aktarma else 0
                yeni_maliyet = maliyetler[mevcut_istasyon] + sure + ek_maliyet
                if komsu_istasyon not in maliyetler or yeni_maliyet < maliyetler[komsu_istasyon]:
                    maliyetler[komsu_istasyon] = yeni_maliyet
                    yeni_yol = yol + [komsu_istasyon]
                    heapq.heappush(pq, (yeni_maliyet, id(komsu_istasyon), komsu_istasyon, yeni_yol))
        return None
    
    def metro_agi_gorsellestir(self, vurgulanacak_rota: Optional[List[Istasyon]] = None):
        G = nx.Graph()
        for istasyon_id, istasyon in self.istasyonlar.items():
            G.add_node(istasyon.ad, hat=istasyon.hat)
            for komsu, sure, _ in istasyon.komsular:
                G.add_edge(istasyon.ad, komsu.ad, weight=sure, hat=istasyon.hat)
        pos = nx.spring_layout(G, k=1.5, iterations=150)  # Daha iyi düzenleme için k artırıldı
        renkler = {"Kırmızı Hat": "red", "Mavi Hat": "blue", "Turuncu Hat": "orange"}
        for hat, istasyonlar in self.hatlar.items():
            nx.draw_networkx_nodes(G, pos, nodelist=[i.ad for i in istasyonlar],
                                 node_color=renkler[hat], node_size=800, label=hat, alpha=0.8)
        edge_colors = [renkler.get(data.get('hat', ''), 'gray') for u, v, data in G.edges(data=True)]
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2)
        if vurgulanacak_rota:
            rota_kenarlari = [(vurgulanacak_rota[i].ad, vurgulanacak_rota[i+1].ad) for i in range(len(vurgulanacak_rota)-1)]
            nx.draw_networkx_edges(G, pos, edgelist=rota_kenarlari, edge_color="green", width=4, style="dashed")
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        plt.title("Metro Ağı Haritası", fontsize=14, pad=20)
        plt.legend(scatterpoints=1, loc="best", fontsize=10)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig('metro_agi.png')  # Görselleştirmeyi dosyaya kaydet
        plt.close()
    
    def kullanici_arayuzu(self):
        while True:
            print("\n=== Metro Ağı Sistemi ===")
            print("1. En az aktarmalı rota bul")
            print("2. En hızlı rota bul")
            print("3. Belirli hatlarla en hızlı rota bul")
            print("4. Metro ağını görselleştir")
            print("5. Çıkış")
            secim = input("Seçiminizi yapın (1-5): ")
            if secim == "5":
                print("Çıkılıyor...")
                break
            if secim in ["1", "2", "3"]:
                print("\nMevcut istasyonlar:")
                for idx, istasyon in sorted(self.istasyonlar.items()):
                    print(f"{idx}: {istasyon.ad} ({istasyon.hat})")
                baslangic_id = input("Başlangıç istasyon ID'sini girin: ")
                hedef_id = input("Hedef istasyon ID'sini girin: ")
                if secim == "1":
                    rota = self.en_az_aktarma_bul(baslangic_id, hedef_id)
                    if rota:
                        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
                        self.metro_agi_gorsellestir(vurgulanacak_rota=rota)
                    else:
                        print("Rota bulunamadı.")
                elif secim == "2":
                    sonuc = self.en_hizli_rota_bul(baslangic_id, hedef_id)
                    if sonuc:
                        rota, sure = sonuc
                        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
                        self.metro_agi_gorsellestir(vurgulanacak_rota=rota)
                    else:
                        print("Rota bulunamadı.")
                elif secim == "3":
                    print("\nMevcut hatlar:", ", ".join(self.hatlar.keys()))
                    hatlar = input("İzin verilen hatları virgülle ayırarak girin (örn: Kırmızı Hat,Mavi Hat): ").split(",")
                    hatlar = [h.strip() for h in hatlar]
                    sonuc = self.en_hizli_rota_bul_hat_filtreli(baslangic_id, hedef_id, hatlar)
                    if sonuc:
                        rota, sure = sonuc
                        print(f"Belirli hatlarla en hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
                        self.metro_agi_gorsellestir(vurgulanacak_rota=rota)
                    else:
                        print("Rota bulunamadı.")
            elif secim == "4":
                self.metro_agi_gorsellestir()
                print("Metro ağı görselleştirildi, 'metro_agi.png' dosyasına kaydedildi.")
            else:
                print("Geçersiz seçim, lütfen tekrar deneyin.")

if __name__ == "__main__":
    metro = MetroAgi()
    
    # İstasyonlar ekleme
    # Kırmızı Hat
    metro.istasyon_ekle("K1", "Kızılay", "Kırmızı Hat")
    metro.istasyon_ekle("K2", "Ulus", "Kırmızı Hat")
    metro.istasyon_ekle("K3", "Demetevler", "Kırmızı Hat")
    metro.istasyon_ekle("K4", "OSB", "Kırmızı Hat")
    
    # Mavi Hat
    metro.istasyon_ekle("M1", "AŞTİ", "Mavi Hat")
    metro.istasyon_ekle("M2", "Kızılay", "Mavi Hat")
    metro.istasyon_ekle("M3", "Sıhhiye", "Mavi Hat")
    metro.istasyon_ekle("M4", "Gar", "Mavi Hat")
    
    # Turuncu Hat
    metro.istasyon_ekle("T1", "Batıkent", "Turuncu Hat")
    metro.istasyon_ekle("T2", "Demetevler", "Turuncu Hat")
    metro.istasyon_ekle("T3", "Gar", "Turuncu Hat")
    metro.istasyon_ekle("T4", "Keçiören", "Turuncu Hat")
    
    # Bağlantılar ekleme
    # Kırmızı Hat bağlantıları
    metro.baglanti_ekle("K1", "K2", 4)
    metro.baglanti_ekle("K2", "K3", 6)
    metro.baglanti_ekle("K3", "K4", 8)
    
    # Mavi Hat bağlantıları
    metro.baglanti_ekle("M1", "M2", 5)
    metro.baglanti_ekle("M2", "M3", 3)
    metro.baglanti_ekle("M3", "M4", 4)
    
    # Turuncu Hat bağlantıları
    metro.baglanti_ekle("T1", "T2", 7)
    metro.baglanti_ekle("T2", "T3", 9)
    metro.baglanti_ekle("T3", "T4", 5)
    
    # Aktarma bağlantıları
    metro.baglanti_ekle("K1", "M2", 3, aktarma=True)  # Kızılay aktarması
    metro.baglanti_ekle("K3", "T2", 4, aktarma=True)  # Demetevler aktarması
    metro.baglanti_ekle("M4", "T3", 2, aktarma=True)  # Gar aktarması
    
    # Kullanıcı arayüzünü başlat
    metro.kullanici_arayuzu()