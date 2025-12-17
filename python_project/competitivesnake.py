import pygame
import time
import random
import UI

from common import *

pygame.init()



clock = pygame.time.Clock()

def create_random_item(snake1, snake2, other_items):
    # DİKKAT: Artık LOGICAL_WIDTH kullanıyoruz
    block = UI.SNAKE_BLOCK
    max_attempts = 100
    attempts = 0
    
    while attempts < max_attempts:
        rand_x = random.randrange(50, LOGICAL_WIDTH - 50)
        rand_y = random.randrange(100, LOGICAL_HEIGHT - 50)
        
        fx = round(rand_x / block) * block
        fy = round(rand_y / block) * block
        
        snake1_coords = [[p[0], p[1]] for p in snake1]
        snake2_coords = [[p[0], p[1]] for p in snake2]
        other_item_coords = [[p[0], p[1]] for p in other_items]
        
        if ([fx, fy] not in snake1_coords and 
            [fx, fy] not in snake2_coords and 
            [fx, fy] not in other_item_coords):
            return [fx, fy]
        
        attempts += 1
    return None

def handle_cut_robust(victim_list, hit_point_x, hit_point_y, food_list):
    cut_index = -1
    for i, part in enumerate(victim_list[:-1]):
        part_x, part_y = part
        dist_x = abs(part_x - hit_point_x)
        dist_y = abs(part_y - hit_point_y)
        
        if dist_x < 10 and dist_y < 10:
            cut_index = i
            break
    
    if cut_index != -1:
        dropped_parts = victim_list[:cut_index+1]
        food_list.extend(dropped_parts)
        new_body = victim_list[cut_index+1:]
        return new_body, len(new_body)
    return victim_list, len(victim_list)

def gameLoop(screen):
    # Gerçek ekran boyutlarını al
    real_w, real_h = screen.get_size()
    
    # SANAL TUVAL OLUŞTUR (Oyunun çizileceği yer)
    virtual_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    
    # UI Modülünü SANAL boyutlara göre başlat
    # Böylece UI elemanları da 1920x1080'e göre konumlanacak
    UI.init_ui(virtual_surface, LOGICAL_WIDTH, LOGICAL_HEIGHT)
    
    game_over = False
    start_ticks = pygame.time.get_ticks()
    block = UI.SNAKE_BLOCK 

    # --- BAŞLANGIÇ KONUMLARI (LOGICAL BOYUTLARA GÖRE) ---
    start_x1 = round((LOGICAL_WIDTH * 0.75) / block) * block
    start_y1 = round((LOGICAL_HEIGHT * 0.5) / block) * block
    
    start_x2 = round((LOGICAL_WIDTH * 0.25) / block) * block
    start_y2 = round((LOGICAL_HEIGHT * 0.5) / block) * block

    x1, y1 = int(start_x1), int(start_y1)
    x1_change, y1_change = 0, 0
    p1_dir = "LEFT"
    p1_next_dir = "LEFT"
    snake1_list = []
    length_of_snake1 = 5
    
    x2, y2 = int(start_x2), int(start_y2)
    x2_change, y2_change = 0, 0
    p2_dir = "RIGHT"
    p2_next_dir = "RIGHT"
    snake2_list = []
    length_of_snake2 = 5

    p1_has_shield = False
    p1_shield_end_time = 0
    p2_has_shield = False
    p2_shield_end_time = 0

    foods = []
    shields = [] 
    paused = False
    pause_start_time = 0
    total_pause_duration = 0

    for _ in range(2):
        new_food = create_random_item(snake1_list, snake2_list, shields + foods)
        if new_food: foods.append(new_food)

    while not game_over:
        current_time = pygame.time.get_ticks()
        
        if not paused:
            elapsed_time = (current_time - start_ticks - total_pause_duration) / 1000
            remaining_time = GAME_DURATION - elapsed_time
            current_speed = START_SPEED + (int(elapsed_time) // SPEED_INCREASE_INTERVAL)

            if remaining_time <= 0:
                winner = "BERABERE!"
                color = UI.WHITE
                if length_of_snake1 > length_of_snake2:
                    winner = "YEŞİL KAZANDI"
                    color = UI.GREEN
                elif length_of_snake2 > length_of_snake1:
                    winner = "KIRMIZI KAZANDI"
                    color = UI.RED
                
                # Winner screen'e gerçek screen'i gönderiyoruz ki oradan tekrar başlatabilsin
                result = UI.winner_screen(winner, color, length_of_snake1, length_of_snake2, gameLoop)
                if result == "MENU": return
                if result == "RESTART": 
                    gameLoop(screen)
                    return

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                return 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_over = True
                    return 
                
                if not paused:
                    if event.key == pygame.K_p:
                        paused = True
                        pause_start_time = pygame.time.get_ticks()
                    
                    if event.key == pygame.K_LEFT and p1_dir != "RIGHT": p1_next_dir = "LEFT"
                    elif event.key == pygame.K_RIGHT and p1_dir != "LEFT": p1_next_dir = "RIGHT"
                    elif event.key == pygame.K_UP and p1_dir != "DOWN": p1_next_dir = "UP"
                    elif event.key == pygame.K_DOWN and p1_dir != "UP": p1_next_dir = "DOWN"
                    
                    if event.key == pygame.K_a and p2_dir != "RIGHT": p2_next_dir = "LEFT"
                    elif event.key == pygame.K_d and p2_dir != "LEFT": p2_next_dir = "RIGHT"
                    elif event.key == pygame.K_w and p2_dir != "DOWN": p2_next_dir = "UP"
                    elif event.key == pygame.K_s and p2_dir != "UP": p2_next_dir = "DOWN"
                else:
                    if event.key == pygame.K_c:
                        paused = False
                        total_pause_duration += (pygame.time.get_ticks() - pause_start_time)
                    elif event.key == pygame.K_r:
                        gameLoop(screen)
                        return

        if paused:
            # Pause ekranını da sanal yüzeye çiz
            # UI.dis şu an virtual_surface'i işaret ediyor
            UI.draw_pause_screen()
            
            # --- ÖLÇEKLEME VE ÇİZİM (PAUSE İÇİN) ---
            scaled_surface = pygame.transform.smoothscale(virtual_surface, (real_w, real_h))
            screen.blit(scaled_surface, (0, 0))
            
            pygame.display.update()
            clock.tick(15)
            continue 

        # --- HAREKET ---
        p1_dir = p1_next_dir
        if p1_dir == "LEFT": x1_change = -block; y1_change = 0
        elif p1_dir == "RIGHT": x1_change = block; y1_change = 0
        elif p1_dir == "UP": y1_change = -block; x1_change = 0
        elif p1_dir == "DOWN": y1_change = block; x1_change = 0
        
        p2_dir = p2_next_dir
        if p2_dir == "LEFT": x2_change = -block; y2_change = 0
        elif p2_dir == "RIGHT": x2_change = block; y2_change = 0
        elif p2_dir == "UP": y2_change = -block; x2_change = 0
        elif p2_dir == "DOWN": y2_change = block; x2_change = 0

        x1 += x1_change; y1 += y1_change
        x2 += x2_change; y2 += y2_change

        # --- SINIRLARI LOGICAL_WIDTH/HEIGHT'A GÖRE KONTROL ET ---
        if x1 >= LOGICAL_WIDTH: x1 = 0
        elif x1 < 0: x1 = (LOGICAL_WIDTH // block) * block - block
        if y1 >= LOGICAL_HEIGHT: y1 = 50 
        elif y1 < 50: y1 = (LOGICAL_HEIGHT // block) * block - block

        if x2 >= LOGICAL_WIDTH: x2 = 0
        elif x2 < 0: x2 = (LOGICAL_WIDTH // block) * block - block
        if y2 >= LOGICAL_HEIGHT: y2 = 50
        elif y2 < 50: y2 = (LOGICAL_HEIGHT // block) * block - block

        # --- ÇİZİM İŞLEMLERİ (Sanal Yüzeye) ---
        virtual_surface.fill(UI.BG_COLOR)
        UI.draw_grid() # Grid artık sanal yüzeye çiziliyor

        if len(shields) == 0 and random.randint(0, 300) == 0:
            new_shield = create_random_item(snake1_list, snake2_list, foods)
            if new_shield: shields.append(new_shield)

        for food in foods: UI.draw_apple(food[0], food[1])
        for shield in shields: UI.draw_shield_item(shield[0], shield[1])

        snake1_head = [x1, y1]
        snake1_list.append(snake1_head)
        if len(snake1_list) > length_of_snake1: del snake1_list[0]

        snake2_head = [x2, y2]
        snake2_list.append(snake2_head)
        if len(snake2_list) > length_of_snake2: del snake2_list[0]

        if p1_has_shield and current_time > p1_shield_end_time: p1_has_shield = False
        if p2_has_shield and current_time > p2_shield_end_time: p2_has_shield = False

        # --- KESME MANTIĞI ---
        if not p2_has_shield:
            snake2_list, length_of_snake2 = handle_cut_robust(snake2_list, x1, y1, foods)
        if not p1_has_shield:
            snake1_list, length_of_snake1 = handle_cut_robust(snake1_list, x2, y2, foods)
        
        snake1_list, length_of_snake1 = handle_cut_robust(snake1_list, x1, y1, foods)
        snake2_list, length_of_snake2 = handle_cut_robust(snake2_list, x2, y2, foods)

        UI.draw_snake_with_eyes(snake1_list, UI.GREEN, p1_dir, p1_has_shield)
        UI.draw_snake_with_eyes(snake2_list, UI.RED, p2_dir, p2_has_shield)
        UI.show_hud(length_of_snake1, length_of_snake2, remaining_time, current_speed, p1_has_shield, p2_has_shield)
        
        for food in foods[:]:
            if abs(x1 - food[0]) < 15 and abs(y1 - food[1]) < 15:
                length_of_snake1 += 1
                foods.remove(food)
                new_item = create_random_item(snake1_list, snake2_list, shields + foods)
                if new_item: foods.append(new_item)
        for food in foods[:]:
            if abs(x2 - food[0]) < 15 and abs(y2 - food[1]) < 15:
                length_of_snake2 += 1
                foods.remove(food)
                new_item = create_random_item(snake1_list, snake2_list, shields + foods)
                if new_item: foods.append(new_item)

        for shield in shields[:]:
            if abs(x1 - shield[0]) < 15 and abs(y1 - shield[1]) < 15:
                p1_has_shield = True
                # SHIELD_DURATION saniye olduğu için 1000 ile çarpıp milisaniyeye çeviriyoruz
                p1_shield_end_time = current_time + (SHIELD_DURATION * 1000) 
                shields.remove(shield)
            elif abs(x2 - shield[0]) < 15 and abs(y2 - shield[1]) < 15:
                p2_has_shield = True
                # SHIELD_DURATION saniye olduğu için 1000 ile çarpıp milisaniyeye çeviriyoruz
                p2_shield_end_time = current_time + (SHIELD_DURATION * 1000)
                shields.remove(shield)

        if len(foods) < 2:
            new_item = create_random_item(snake1_list, snake2_list, shields + foods)
            if new_item: foods.append(new_item)

        if remaining_time <= 11:
            UI.draw_huge_countdown(remaining_time)

        # --- KRİTİK NOKTA: ÖLÇEKLEME VE EKRANA BASMA ---
        # 1. Sanal Tuvali (1920x1080), Gerçek Pencere Boyutuna (Örn: 800x600) sığdır
        # smoothscale biraz daha yavaş ama kaliteli, scale hızlı ama pixelated (piksel oyunları için scale daha iyi olabilir)
        scaled_surface = pygame.transform.smoothscale(virtual_surface, (real_w, real_h))
        
        # 2. Ölçeklenmiş resmi gerçek ekrana yapıştır
        screen.blit(scaled_surface, (0, 0))

        pygame.display.update()
        clock.tick(current_speed)

    return


# --- ONLINE OYUN İÇİN GEREKLİ SINIF VE FONKSİYONLAR ---


def online_game_loop(screen, network):
    # --- SANAL ÇÖZÜNÜRLÜK AYARLARI ---
    LOGICAL_WIDTH = 1920
    LOGICAL_HEIGHT = 1080
    virtual_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    
    UI.init_ui(virtual_surface, LOGICAL_WIDTH, LOGICAL_HEIGHT)
    
    clock = pygame.time.Clock()
    running = True
    p_id = network.p

    print(f"Oyuna Başlandı! Oyuncu ID: {p_id}")
    sent_rematch_request = False 

    while running:
        # --- 1. GİRİŞ KONTROLÜ ---
        key_pressed = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                
                # Oyun bittiyse ve R'ye basıldıysa
                if game.winner is not None and event.key == pygame.K_r:
                    sent_rematch_request = True
                    key_pressed = "REMATCH" # Sunucuya bunu yollayacağız

                # Oyun devam ediyorsa yön tuşları
                if game.winner is None:
                    if event.key in [pygame.K_LEFT, pygame.K_a]: key_pressed = "LEFT"
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]: key_pressed = "RIGHT"
                    elif event.key in [pygame.K_UP, pygame.K_w]: key_pressed = "UP"
                    elif event.key in [pygame.K_DOWN, pygame.K_s]: key_pressed = "DOWN"

        # --- 2. NETWORK ---
        # Rematch isteği gönderildiyse "REMATCH", değilse normal tuş veya "get" gönder
        data_to_send = key_pressed if key_pressed is not None else "get"
        
        try:
            game = network.send(data_to_send)
        except Exception as e:
            print(f"Bağlantı Hatası: {e}")
            break

        if game is None: break

        if not game.ready:
            # 1. Arka planı temizle (Siyah veya Lacivert)
            virtual_surface.fill(UI.BG_COLOR)
            UI.draw_grid()

            # 2. Yarı saydam siyah bir perde çek
            overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            overlay.set_alpha(200) # 255 tam opak, 0 tam şeffaf
            overlay.fill((0, 0, 0))
            virtual_surface.blit(overlay, (0, 0))

            # 3. Bilgileri Yazdır
            center_x = LOGICAL_WIDTH // 2
            center_y = LOGICAL_HEIGHT // 2

            # Oda Numarası (Büyük ve Altın Sarısı)
            UI.draw_text(f"ODA NO: {network.game_id}", UI.font_big, UI.GOLD, virtual_surface, center_x, center_y - 50)
            
            # Durum Mesajı (Yanıp sönen efekt yapılabilir ama şimdilik sabit olsun)
            UI.draw_text("RAKİP BEKLENİYOR...", UI.font_ui, UI.WHITE, virtual_surface, center_x, center_y + 50)
            
            UI.draw_text("Arkadaşına Oda Numarasını söyle!", UI.font_icon, (150, 150, 150), virtual_surface, center_x, center_y + 100)

            # 4. Ekrana Bas ve Döngüyü Atla
            scaled_surface = pygame.transform.smoothscale(virtual_surface, screen.get_size())
            screen.blit(scaled_surface, (0, 0))
            pygame.display.update()
        
            continue  # Oyun henüz başlamadı, döngüye devam et

        # Eğer oyun sunucuda sıfırlandıysa (winner None olduysa), yerel değişkeni de sıfırla
        if game.winner is None and sent_rematch_request:
            sent_rematch_request = False # Yeni oyun başladı, isteği temizle

        # --- 3. ÇİZİM ---
        virtual_surface.fill(UI.BG_COLOR)
        UI.draw_grid()

        # ... (Yem, Yılan, HUD çizimleri AYNEN KALSIN) ...
        for food in game.foods: UI.draw_apple(food[0], food[1])

        for shield in game.shields: UI.draw_shield_item(shield[0], shield[1])

        # ...
        UI.draw_snake_with_eyes(game.snake1, UI.GREEN, game.p1_dir, game.p1_has_shield)
        UI.draw_snake_with_eyes(game.snake2, UI.RED, game.p2_dir, game.p2_has_shield)
        UI.show_hud(game.score[0], game.score[1], game.remaining_time, game.current_speed, game.p1_has_shield, game.p2_has_shield, current_player_id=network.p)

        # --- 4. OYUN SONU EKRANI (OVERLAY) ---

        if game.winner is not None:
            # Yarı şeffaf siyah perde
            overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            virtual_surface.blit(overlay, (0, 0))

            # Kazanan Yazısı (Ortada)
            if game.winner == 0: txt = "YEŞİL KAZANDI"; color = UI.GREEN
            elif game.winner == 1: txt = "KIRMIZI KAZANDI"; color = UI.RED
            else: txt = "BERABERE"; color = UI.WHITE
            
            UI.draw_text(txt, UI.font_big, color, virtual_surface, LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 150)
            
            # --- SKOR TABLOSU (SOL: YEŞİL | SAĞ: KIRMIZI) ---
            
            # SOL TARAF (YEŞİL)
            p1_txt = f"YEŞİL: {game.score[0]}"
            if network.p == 0: p1_txt += " (SEN)" # Ben Yeşilsem belirt
            UI.draw_text(p1_txt, UI.font_ui, UI.GREEN, virtual_surface, LOGICAL_WIDTH//2 - 200, LOGICAL_HEIGHT//2 - 50)

            # SAĞ TARAF (KIRMIZI)
            p2_txt = f"KIRMIZI: {game.score[1]}"
            if network.p == 1: p2_txt += " (SEN)" # Ben Kırmızıysam belirt
            UI.draw_text(p2_txt, UI.font_ui, UI.RED, virtual_surface, LOGICAL_WIDTH//2 + 200, LOGICAL_HEIGHT//2 - 50)
            
            # Araya Çizgi
            pygame.draw.line(virtual_surface, (100, 100, 100), (LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 70), (LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 30), 2)
            
            # --- DURUMLAR (HAZIR / BEKLİYOR) ---

            # SOL TARAF (YEŞİL DURUMU)
            p1_status = "HAZIR" if game.p1_rematch else "BEKLİYOR..."
            p1_color = UI.GREEN if game.p1_rematch else (100, 100, 100)
            UI.draw_text(f"DURUM: {p1_status}", UI.font_ui, p1_color, virtual_surface, LOGICAL_WIDTH//2 - 200, LOGICAL_HEIGHT//2 + 50)
            
            # SAĞ TARAF (KIRMIZI DURUMU)
            p2_status = "HAZIR" if game.p2_rematch else "BEKLİYOR..."
            p2_color = UI.RED if game.p2_rematch else (100, 100, 100)
            UI.draw_text(f"DURUM: {p2_status}", UI.font_ui, p2_color, virtual_surface, LOGICAL_WIDTH//2 + 200, LOGICAL_HEIGHT//2 + 50)

            # Talimat (En Altta)
            UI.draw_text("Tekrar oynamak için [R] - Çıkış [ESC]", UI.font_ui, UI.WHITE, virtual_surface, LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 + 150)
            # ----------------------------------------

        # --- 5. EKRANA BASMA ---
        scaled_surface = pygame.transform.smoothscale(virtual_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.update()

        clock.tick(60)