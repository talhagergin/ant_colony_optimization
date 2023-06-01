import random

class AntColonyOptimization:
    def __init__(self, num_ants, num_iterations, evaporation_rate, alpha, beta, Q):
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        self.Q = Q

    def optimize_routing(self, wireless_network):
        # Kablosuz ağdaki düğümlerin sayısını al
        num_nodes = len(wireless_network.nodes)
        # Feromon matrisini başlat
        self.initialize_pheromone_matrix(num_nodes)
        # En iyi yol ve maliyeti için başlangıç değerleri ata
        best_path = None
        best_path_cost = float('inf')
        
        # Belirtilen iterasyon sayısı kadar döngüyü çalıştır
        for _ in range(self.num_iterations):
            
            # Her karınca için yol oluştur ve feromon matrisini güncelle
            for ant in range(self.num_ants):
                path = self.construct_path(wireless_network)
                path_cost = self.calculate_path_cost(wireless_network, path)
                
                # Eğer bulunan yolun maliyeti, şu ana kadar en iyi yol maliyetinden daha düşükse güncelle
                if path_cost < best_path_cost:
                    best_path = path
                    best_path_cost = path_cost

                # Feromon matrisini güncelle
                self.update_pheromone_matrix(path, path_cost)

        # En iyi yolu döndür
        return best_path

    def initialize_pheromone_matrix(self, num_nodes):
        # Ağdaki her düğümü arasındaki bağlantıların feromon seviyelerini içeren kare matris
        #her düğüm arasındaki feromon seviyesini aynı değere eşitledik ve bu sayede dengeli bir matris oluşturuldu
        self.pheromone_matrix = [[1 / num_nodes] * num_nodes for _ in range(num_nodes)]

    def construct_path(self, wireless_network):
        
        # Başlangıç düğümünü rastgele seç
        start_node = random.choice(list(wireless_network.nodes))
        
        # Yol listesini başlangıç düğümüyle başlat
        path = [start_node]
        visited_nodes = set([start_node])


        # Tüm düğümler ziyaret edilene kadar döngüyü sürdür
        while len(visited_nodes) < len(wireless_network.nodes):
            
            # Bir sonraki düğümü seç
            next_node = self.select_next_node(wireless_network, path[-1], visited_nodes)
            
            # Yolu güncelle ve ziyaret edilen düğümlere ekle
            path.append(next_node)
            visited_nodes.add(next_node)


        # Oluşturulan yol listesini döndür
        return path

    def select_next_node(self, wireless_network, current_node, visited_nodes):
        
        # Geçerli düğümün düğüm numarasını al (düğüm ismini düğüm numarasına çevirme)
        current_node_num = wireless_network.node_to_num[current_node] 
        
        # Geçerli düğüme ait feromon değerlerini al
        pheromone_values = self.pheromone_matrix[current_node_num-1]
        
        # Olasılıkları tutacak bir liste oluştur
        probabilities = []

        # Kablosuz ağdaki her bir düğüm için
        for node in wireless_network.nodes:
            
            # Eğer düğüm daha önce ziyaret edilmediyse
            if node not in visited_nodes:
                
                # Düğümün düğüm numarasını al (düğüm ismini düğüm numarasına çevirme)
                node_num = wireless_network.node_to_num[node]  
                
                # Geçerli düğüm ile seçilen düğüm arasındaki uzaklığı al
                distance = wireless_network.get_distance(current_node, node)
                
                # Feromon ve uzaklık değerlerini kullanarak olasılığı hesapla
                pheromone = pheromone_values[node_num-1]
                probability = pheromone ** self.alpha * (1 / distance) ** self.beta
                
                # Düğüm ve olasılığı probabilities listesine ekle
                probabilities.append((node, probability))
         # Toplam olasılığı hesapla
        total_probability = sum(prob for _, prob in probabilities)
        
        # Olasılıkları toplam olasılığa bölerek normalize et
        probabilities = [(node, prob / total_probability) for node, prob in probabilities]
        
        #Olasılıkları azalan sırada sırala
        probabilities.sort(key=lambda x: x[1], reverse=True)
        
        # Rulet tekerleği seçimi kullanarak bir düğüm seç
        selected_node = self.roulette_wheel_selection(probabilities)
        
        # Seçilen düğümü döndür
        return selected_node

    def roulette_wheel_selection(self, probabilities):
        cumulative_prob = 0
        random_num = random.random() #rulet tekerleğindeki konumu temsil eder

        # Rulet tekerleği seçimi
        for node, prob in probabilities:
            cumulative_prob += prob
            
            # Rastgele sayı, kümülatif olasılığın üzerine çıkarsa ilgili düğümü seç
            if random_num <= cumulative_prob:
                return node

    def calculate_path_cost(self, wireless_network, path):
        path_cost = 0


        # Düğümler arasındaki toplam mesafeyi hesapla
        for i in range(len(path) - 1):
            node1 = path[i]
            node2 = path[i + 1]
            distance = wireless_network.get_distance(node1, node2)
            path_cost += distance
            
        # Yol maliyetini döndür
        return path_cost

    def update_pheromone_matrix(self, path, path_cost):
        pheromone_deposit = self.Q / path_cost


        # Yol üzerindeki düğümler arasındaki feromon izlerini güncelle
        for i in range(len(path) - 1):
            node1 = path[i]
            node2 = path[i + 1]
            node1_num = wireless_network.node_to_num[node1]  # Düğüm ismini düğüm numarasına çevirme
            node2_num = wireless_network.node_to_num[node2]  # Düğüm ismini düğüm numarasına çevirme
            
            # Feromon izlerini güncelle
            self.pheromone_matrix[node1_num-1][node2_num-1] += pheromone_deposit
            self.pheromone_matrix[node2_num-1][node1_num-1] += pheromone_deposit


class WirelessNetwork:
    def __init__(self):
        self.nodes = set() #her elemanın bir kere yer aldığı bir küme yapısı oluşturur
        self.connections = {}
        self.node_to_num = {}  # Düğüm ismi ile düğüm numarası arasındaki eşleştirme sözlüğü

    def add_node(self, node):
        self.nodes.add(node)
        node_num = len(self.nodes)  # Düğüm numarası
        self.node_to_num[node] = node_num

    def add_connection(self, node1, node2, distance):
        if node1 not in self.connections:
            self.connections[node1] = {}
        if node2 not in self.connections:
            self.connections[node2] = {}
        #iletim çift yönlü olduğu için ve her iki düğümde birbirine ulaşabilir.
        self.connections[node1][node2] = distance
        self.connections[node2][node1] = distance

    def get_distance(self, node1, node2):
        return self.connections[node1][node2]


# Örnek bir kablosuz ağın düğümleri ve bağlantıları
wireless_network = WirelessNetwork()

# Düğümleri ekleme
wireless_network.add_node('A')
wireless_network.add_node('B')
wireless_network.add_node('C')
wireless_network.add_node('D')

# Bağlantıları ekleme
wireless_network.add_connection('A', 'B', 3)
wireless_network.add_connection('A', 'C', 4)
wireless_network.add_connection('A', 'D', 3)
wireless_network.add_connection('B', 'C', 2)
wireless_network.add_connection('B', 'D', 1)
wireless_network.add_connection('C', 'D', 3)

# Algoritma parametreleri
num_ants = 10
num_iterations = 15 #arama işleminin kaç iterasyon(adım) gerçekleşeceğini belirleyen parametredir
evaporation_rate = 0.5 #düğümler arasındaki feromon miktarlarının önem derecesini belirleyen parametredir
alpha = 1 #düğümler arasındaki mesafenin önem derecesini belirleyen parametredir
beta = 2 #her iterasyon sonunda düğümler arasındaki feromonların hangi oranda buharlaşacağını belirleyen parametredir
Q = 1 #en iyi çözümün sonraki iterasyonlara aktarılması olasılığını belirleyen parametredir

# AntColonyOptimization sınıfını kullanarak algoritmayı başlatma
aco = AntColonyOptimization(num_ants, num_iterations, evaporation_rate, alpha, beta, Q)
optimized_path = aco.optimize_routing(wireless_network)

print("Optimized Path:", optimized_path)
