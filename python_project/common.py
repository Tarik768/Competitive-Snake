import threading
import time
import random

# --- ORTAK SABİTLER ---
LOGICAL_WIDTH = 1920
LOGICAL_HEIGHT = 1080
SNAKE_BLOCK = 25
GAME_DURATION = 20
START_SPEED = 10
SPEED_INCREASE_INTERVAL = 15
SHIELD_DURATION = 5.0

class Game:
    def __init__(self, room_id):
        self.id = room_id
        # Thread kilidini oluştur (Veri çakışmasını önler)
        self.lock = threading.RLock()
        
        self.ready = False
        self.start_ticks = time.time()
        
        # --- BAŞLANGIÇ KONUMLARI ---
        # YEŞİL YILAN (Sol Taraf)
        start_x1 = 400 
        start_y1 = 500
        self.snake1 = []
        self.len1 = 5 
        for i in range(self.len1):
            self.snake1.append([start_x1 + (i * SNAKE_BLOCK), start_y1])
            
        # KIRMIZI YILAN (Sağ Taraf)
        start_x2 = 1500 
        start_y2 = 500
        self.snake2 = []
        self.len2 = 5 
        for i in range(self.len2):
            self.snake2.append([start_x2 - (i * SNAKE_BLOCK), start_y2])

        self.foods = []
        self.shields = []
        
        # Skorlar başlangıçta yılanın boyuna eşit
        self.score = [self.len1, self.len2]
        
        self.p1_dir = "RIGHT" 
        self.p2_dir = "LEFT"
        
        # Hamle Kilitleri (Anti-Ghosting)
        self.p1_can_turn = True
        self.p2_can_turn = True
        
        self.p1_has_shield = False
        self.p1_shield_end_time = 0
        self.p2_has_shield = False
        self.p2_shield_end_time = 0

        self.p1_rematch = False
        self.p2_rematch = False
        
        self.remaining_time = GAME_DURATION
        self.current_speed = START_SPEED
        self.winner = None
        
        self.last_move_time = time.time()
        
        # Başlangıçta 2 yem oluştur
        for _ in range(2):
            self._spawn_new_item("food")

    # --- PICKLE İÇİN ÖZEL METOTLAR (HATA ÇÖZÜMÜ) ---
    def __getstate__(self):
        """Paketleme yapılırken 'lock' nesnesini çıkarır."""
        state = self.__dict__.copy()
        if 'lock' in state:
            del state['lock']
        return state

    def __setstate__(self, state):
        """Paket açılırken 'lock' nesnesini yeniden oluşturur."""
        self.__dict__.update(state)
        self.lock = threading.RLock()

    # --- OYUN MANTIĞI METOTLARI ---
    
    def _spawn_new_item(self, item_type):
        max_attempts = 100
        attempts = 0
        while attempts < max_attempts:
            rand_x = random.randrange(50, LOGICAL_WIDTH - 50)
            rand_y = random.randrange(100, LOGICAL_HEIGHT - 50)
            
            fx = round(rand_x / SNAKE_BLOCK) * SNAKE_BLOCK
            fy = round(rand_y / SNAKE_BLOCK) * SNAKE_BLOCK
            
            if ([fx, fy] not in self.snake1 and 
                [fx, fy] not in self.snake2 and 
                [fx, fy] not in self.foods and
                [fx, fy] not in self.shields):
                
                if item_type == "food":
                    self.foods.append([fx, fy])
                elif item_type == "shield":
                    self.shields.append([fx, fy])
                return
            attempts += 1

    def _handle_cut_robust(self, victim_list, hit_point_x, hit_point_y):
        cut_index = -1
        # Kendi vücuduna veya rakibe çarpma kontrolü
        for i, part in enumerate(victim_list[:-1]):
            if abs(part[0] - hit_point_x) < 10 and abs(part[1] - hit_point_y) < 10:
                cut_index = i
                break
        
        if cut_index != -1:
            dropped_parts = victim_list[:cut_index+1]
            self.foods.extend(dropped_parts)
            new_body = victim_list[cut_index+1:]
            return new_body, True
        
        return victim_list, False

    def update_game_state(self):
        # Kilit burada devreye giriyor: Hesaplama yaparken kimse araya girmesin.
        with self.lock:
            if not self.ready or self.winner is not None:
                return

            current_time = time.time()
            elapsed = current_time - self.start_ticks
            self.remaining_time = GAME_DURATION - elapsed
            self.current_speed = START_SPEED + (int(elapsed) // SPEED_INCREASE_INTERVAL)

            # Oyun süresi bitti mi?
            if self.remaining_time <= 0:
                if self.len1 > self.len2: self.winner = 0
                elif self.len2 > self.len1: self.winner = 1
                else: self.winner = 2 # Berabere
                return

            # Hız kontrolü (FPS sınırı gibi)
            if current_time - self.last_move_time < (1.0 / self.current_speed):
                return
            
            self.last_move_time = current_time

            # Kalkan süreleri
            if self.p1_has_shield and current_time > self.p1_shield_end_time: self.p1_has_shield = False
            if self.p2_has_shield and current_time > self.p2_shield_end_time: self.p2_has_shield = False

            # --- HAREKET ---
            head1 = list(self.snake1[-1])
            self._apply_direction(head1, self.p1_dir)
            
            head2 = list(self.snake2[-1])
            self._apply_direction(head2, self.p2_dir)

            self._handle_walls(head1)
            self._handle_walls(head2)

            self.snake1.append(head1)
            self.snake2.append(head2)

            # Yeni kareye geçildiği için dönüş kilitlerini aç
            self.p1_can_turn = True
            self.p2_can_turn = True

            # --- ÇARPIŞMALAR VE KESMELER ---
            # 1. Kırmızı (P2) kalkanı yoksa kesilebilir mi?
            if not self.p2_has_shield:
                new_snake2, cut = self._handle_cut_robust(self.snake2, head1[0], head1[1])
                if cut:
                    self.snake2 = new_snake2
                    self.len2 = len(new_snake2)

            # 2. Yeşil (P1) kalkanı yoksa kesilebilir mi?
            if not self.p1_has_shield:
                new_snake1, cut = self._handle_cut_robust(self.snake1, head2[0], head2[1])
                if cut:
                    self.snake1 = new_snake1
                    self.len1 = len(new_snake1)

            # 3. Kendi kendini yeme kontrolü
            new_snake1, cut = self._handle_cut_robust(self.snake1, head1[0], head1[1])
            if cut:
                self.snake1 = new_snake1
                self.len1 = len(new_snake1)
                
            new_snake2, cut = self._handle_cut_robust(self.snake2, head2[0], head2[1])
            if cut:
                self.snake2 = new_snake2
                self.len2 = len(new_snake2)

            # --- YEMEK ---
            # Yeşil Yedi mi?
            for food in self.foods[:]:
                if abs(head1[0] - food[0]) < 15 and abs(head1[1] - food[1]) < 15:
                    self.len1 += 1
                    self.foods.remove(food)
                    self._spawn_new_item("food")
                    break
            
            # Kırmızı Yedi mi?
            for food in self.foods[:]:
                if abs(head2[0] - food[0]) < 15 and abs(head2[1] - food[1]) < 15:
                    self.len2 += 1
                    self.foods.remove(food)
                    self._spawn_new_item("food")
                    break
            
            # Kalkan Alma
            for shield in self.shields[:]:
                if abs(head1[0] - shield[0]) < 15 and abs(head1[1] - shield[1]) < 15:
                    self.p1_has_shield = True
                    self.p1_shield_end_time = current_time + SHIELD_DURATION
                    self.shields.remove(shield)
                elif abs(head2[0] - shield[0]) < 15 and abs(head2[1] - shield[1]) < 15:
                    self.p2_has_shield = True
                    self.p2_shield_end_time = current_time + SHIELD_DURATION
                    self.shields.remove(shield)

            # Kuyruk Silme (Uzunluk kontrolü)
            while len(self.snake1) > self.len1: self.snake1.pop(0)
            while len(self.snake2) > self.len2: self.snake2.pop(0)

            # Rastgele Kalkan Çıkması
            if len(self.shields) == 0 and random.randint(0, 300) == 0:
                self._spawn_new_item("shield")
                
            # Yem Eksilirse Ekle
            while len(self.foods) < 2:
                self._spawn_new_item("food")

            # --- SKOR GÜNCELLEME ---
            # Skoru direkt boya eşitleyerek yerel oyunla aynı mantığı kuruyoruz.
            self.score[0] = self.len1
            self.score[1] = self.len2

    def _apply_direction(self, head, direction):
        if direction == "UP": head[1] -= SNAKE_BLOCK
        elif direction == "DOWN": head[1] += SNAKE_BLOCK
        elif direction == "LEFT": head[0] -= SNAKE_BLOCK
        elif direction == "RIGHT": head[0] += SNAKE_BLOCK

    def _handle_walls(self, head):
        if head[0] >= LOGICAL_WIDTH: head[0] = 0
        elif head[0] < 0: head[0] = LOGICAL_WIDTH - SNAKE_BLOCK
        if head[1] >= LOGICAL_HEIGHT: head[1] = 50 
        elif head[1] < 50: head[1] = LOGICAL_HEIGHT - SNAKE_BLOCK

    # --- YENİ FONKSİYON: OYUNU SIFIRLA ---
    def reset_game(self):
        """Her iki oyuncu kabul ettiğinde oyunu başa sarar"""
        with self.lock:
            self.p1_rematch = False
            self.p2_rematch = False
            self.winner = None
            self.start_ticks = time.time()
            self.remaining_time = GAME_DURATION
            self.current_speed = START_SPEED
            
            # --- DÜZELTME BURADA ---
            # Koordinatları 25'in katı yapıyoruz (Init fonksiyonundaki ile aynı)
            # Eski hatalı değerler: start_x1 = 420; start_y1 = 510
            start_x1 = 400; start_y1 = 500
            
            self.snake1 = []
            self.len1 = 5
            for i in range(self.len1):
                self.snake1.append([start_x1 + (i * SNAKE_BLOCK), start_y1])

            # Eski hatalı değerler: start_x2 = 1500; start_y2 = 510
            start_x2 = 1500; start_y2 = 500
            
            self.snake2 = []
            self.len2 = 5
            for i in range(self.len2):
                self.snake2.append([start_x2 - (i * SNAKE_BLOCK), start_y2])
            # -----------------------

            self.score = [self.len1, self.len2]
            self.p1_dir = "RIGHT" # P1 Yönünü de resetleyelim
            self.p2_dir = "LEFT"  # P2 Yönünü de resetleyelim
            
            self.foods = []
            self.shields = []
            for _ in range(2):
                self._spawn_new_item("food")