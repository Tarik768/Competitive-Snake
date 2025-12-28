import pygame
import time
import random
import UI

from common import *

pygame.init() # Pygame başlatıldığında mixer da başlar

clock = pygame.time.Clock()

def create_random_item(snake1, snake2, other_items):
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

# --- GÜNCELLEME: volume parametresi eklendi (Varsayılan 0.5) ---
def gameLoop(screen, volume=0.5):
    # --- SESLERİ YÜKLEME ---
    try:
        eat_sfx = pygame.mixer.Sound("sounds/eat.wav")
        hit_sfx = pygame.mixer.Sound("sounds/hit.wav")
        shield_sfx = pygame.mixer.Sound("sounds/shield.wav")
        end_sfx = pygame.mixer.Sound("sounds/endsound.wav")
        
        # Ses seviyelerini menüden gelen değere göre ayarla
        eat_sfx.set_volume(volume)
        hit_sfx.set_volume(volume)
        shield_sfx.set_volume(volume)
        end_sfx.set_volume(volume)
    except Exception as e:
        print(f"Ses dosyaları yüklenemedi: {e}")
        eat_sfx = hit_sfx = shield_sfx = end_sfx = None

    # Gerçek ekran boyutlarını al
    real_w, real_h = screen.get_size()
    
    virtual_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    UI.init_ui(virtual_surface, LOGICAL_WIDTH, LOGICAL_HEIGHT)
    
    game_over = False
    start_ticks = pygame.time.get_ticks()
    block = UI.SNAKE_BLOCK 

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
                # --- SES: Oyun Bitiş ---
                if end_sfx: end_sfx.play()

                winner = "BERABERE!"
                color = UI.WHITE
                if length_of_snake1 > length_of_snake2:
                    winner = "YEŞİL KAZANDI"
                    color = UI.GREEN
                elif length_of_snake2 > length_of_snake1:
                    winner = "KIRMIZI KAZANDI"
                    color = UI.RED
                
                result = UI.winner_screen(winner, color, length_of_snake1, length_of_snake2, gameLoop)
                if result == "MENU": return
                if result == "RESTART": 
                    # Restart atarken güncel ses seviyesini gönderiyoruz
                    gameLoop(screen, volume)
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
                        gameLoop(screen, volume) # Restart için volume ekledik
                        return

        if paused:
            UI.draw_pause_screen()
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

        if x1 >= LOGICAL_WIDTH: x1 = 0
        elif x1 < 0: x1 = (LOGICAL_WIDTH // block) * block - block
        if y1 >= LOGICAL_HEIGHT: y1 = 50 
        elif y1 < 50: y1 = (LOGICAL_HEIGHT // block) * block - block

        if x2 >= LOGICAL_WIDTH: x2 = 0
        elif x2 < 0: x2 = (LOGICAL_WIDTH // block) * block - block
        if y2 >= LOGICAL_HEIGHT: y2 = 50
        elif y2 < 50: y2 = (LOGICAL_HEIGHT // block) * block - block

        virtual_surface.fill(UI.BG_COLOR)
        UI.draw_grid() 

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

        # --- KESME MANTIĞI VE SES ---
        hit_occurred = False
        
        # P2 kesildi mi kontrol
        prev_len2 = len(snake2_list)
        if not p2_has_shield:
            snake2_list, length_of_snake2 = handle_cut_robust(snake2_list, x1, y1, foods)
            if len(snake2_list) < prev_len2: hit_occurred = True

        # P1 kesildi mi kontrol
        prev_len1 = len(snake1_list)
        if not p1_has_shield:
            snake1_list, length_of_snake1 = handle_cut_robust(snake1_list, x2, y2, foods)
            if len(snake1_list) < prev_len1: hit_occurred = True
        
        # Kafa kafaya çarpışma veya ekstra kontroller için tekrar çağrım
        prev_len1_check2 = len(snake1_list)
        prev_len2_check2 = len(snake2_list)
        snake1_list, length_of_snake1 = handle_cut_robust(snake1_list, x1, y1, foods) # Kendi kendine
        snake2_list, length_of_snake2 = handle_cut_robust(snake2_list, x2, y2, foods) # Kendi kendine
        
        if len(snake1_list) < prev_len1_check2 or len(snake2_list) < prev_len2_check2:
            hit_occurred = True

        if hit_occurred and hit_sfx:
            hit_sfx.play()

        UI.draw_snake_with_eyes(snake1_list, UI.GREEN, p1_dir, p1_has_shield)
        UI.draw_snake_with_eyes(snake2_list, UI.RED, p2_dir, p2_has_shield)
        UI.show_hud(length_of_snake1, length_of_snake2, remaining_time, current_speed, p1_has_shield, p2_has_shield)
        
        # --- YEME MANTIĞI VE SES ---
        ate_food = False
        for food in foods[:]:
            if abs(x1 - food[0]) < 15 and abs(y1 - food[1]) < 15:
                length_of_snake1 += 1
                foods.remove(food)
                ate_food = True
                new_item = create_random_item(snake1_list, snake2_list, shields + foods)
                if new_item: foods.append(new_item)
        for food in foods[:]:
            if abs(x2 - food[0]) < 15 and abs(y2 - food[1]) < 15:
                length_of_snake2 += 1
                foods.remove(food)
                ate_food = True
                new_item = create_random_item(snake1_list, snake2_list, shields + foods)
                if new_item: foods.append(new_item)
        
        if ate_food and eat_sfx:
            eat_sfx.play()

        # --- KALKAN MANTIĞI VE SES ---
        got_shield = False
        for shield in shields[:]:
            if abs(x1 - shield[0]) < 15 and abs(y1 - shield[1]) < 15:
                p1_has_shield = True
                p1_shield_end_time = current_time + (SHIELD_DURATION * 1000) 
                shields.remove(shield)
                got_shield = True
            elif abs(x2 - shield[0]) < 15 and abs(y2 - shield[1]) < 15:
                p2_has_shield = True
                p2_shield_end_time = current_time + (SHIELD_DURATION * 1000)
                shields.remove(shield)
                got_shield = True
        
        if got_shield and shield_sfx:
            shield_sfx.play()

        if len(foods) < 2:
            new_item = create_random_item(snake1_list, snake2_list, shields + foods)
            if new_item: foods.append(new_item)

        if remaining_time <= 11:
            UI.draw_huge_countdown(remaining_time)

        scaled_surface = pygame.transform.smoothscale(virtual_surface, (real_w, real_h))
        screen.blit(scaled_surface, (0, 0))

        pygame.display.update()
        clock.tick(current_speed)

    return
# --- ONLINE OYUN KISMI GÜNCELLENDİ ---

def online_game_loop(screen, network, volume=0.5):
    # --- SESLERİ YÜKLEME ---
    eat_sfx = hit_sfx = shield_sfx = end_sfx = None
    try:
        eat_sfx = pygame.mixer.Sound("eat.wav")
        hit_sfx = pygame.mixer.Sound("hit.wav")
        shield_sfx = pygame.mixer.Sound("shield.wav")
        end_sfx = pygame.mixer.Sound("endsound.wav")
        
        eat_sfx.set_volume(volume)
        hit_sfx.set_volume(volume)
        shield_sfx.set_volume(volume)
        end_sfx.set_volume(volume)
    except Exception as e:
        print(f"Online ses hatası: {e}")

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

    # --- DURUM TAKİBİ İÇİN DEĞİŞKENLER (SES İÇİN) ---
    prev_game_state = None

    while running:
        # --- 1. GİRİŞ KONTROLÜ ---
        key_pressed = None
        game_winner_exists = False # Döngü başında varsayılan

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                
                # 'game' nesnesi henüz tanımlanmamış olabilir, try-except ile kontrol veya 
                # prev_game_state üzerinden mantık kurabiliriz ama network.send sonrası kontrol daha güvenli.
                pass 

        # --- 2. NETWORK ---
        # Önceki turdan winner bilgisini alabiliyorsak tuş kontrolünü ona göre yapalım
        # Ancak en garantisi aşağıda game nesnesini aldıktan sonra tuş mantığını işletmektir.
        # Basitlik adına burada "get" veya yön tuşunu gönderiyoruz.
        
        # NOT: Tuş yakalamayı pygame event loop içinde yapmak daha sağlıklıdır,
        # ancak burada oyunun mevcut yapısını bozmadan devam ediyoruz.
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: key_pressed = "LEFT"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: key_pressed = "RIGHT"
        elif keys[pygame.K_UP] or keys[pygame.K_w]: key_pressed = "UP"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]: key_pressed = "DOWN"
        
        # Rematch ve Oyun Sonu kontrolleri aşağıda game nesnesi gelince netleşecek.
        if prev_game_state and prev_game_state.winner is not None:
             if keys[pygame.K_r]:
                sent_rematch_request = True
                key_pressed = "REMATCH"

        data_to_send = key_pressed if key_pressed is not None else "get"
        
        try:
            game = network.send(data_to_send)
        except Exception as e:
            print(f"Bağlantı Hatası: {e}")
            break

        if game is None: break

        # --- SES MANTIĞI (STATE COMPARISON) ---
        if prev_game_state is not None:
            # 1. YEME SESİ (Skor arttıysa)
            if (game.score[0] > prev_game_state.score[0]) or (game.score[1] > prev_game_state.score[1]):
                if eat_sfx: eat_sfx.play()

            # 2. KALKAN SESİ (Kalkan yokken var olduysa)
            p1_got_shield = game.p1_has_shield and not prev_game_state.p1_has_shield
            p2_got_shield = game.p2_has_shield and not prev_game_state.p2_has_shield
            if p1_got_shield or p2_got_shield:
                if shield_sfx: shield_sfx.play()

            # 3. ÇARPIŞMA/KESİLME SESİ (Boyut azaldıysa ve oyun yeni başlamadıysa)
            # Oyun resetlendiğinde de boyut azalır, bunu engellemek için winner kontrolü yapıyoruz.
            if game.winner is None and prev_game_state.winner is None:
                len1_dropped = len(game.snake1) < len(prev_game_state.snake1)
                len2_dropped = len(game.snake2) < len(prev_game_state.snake2)
                
                if len1_dropped or len2_dropped:
                    if hit_sfx: hit_sfx.play()

            # 4. OYUN BİTİŞ SESİ
            if game.winner is not None and prev_game_state.winner is None:
                if end_sfx: end_sfx.play()

        # Durumu güncelle
        prev_game_state = game 

        if not game.ready:
            # Bekleme Ekranı Çizimi (Aynen Kalıyor)
            virtual_surface.fill(UI.BG_COLOR)
            UI.draw_grid()
            overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            virtual_surface.blit(overlay, (0, 0))
            
            center_x, center_y = LOGICAL_WIDTH // 2, LOGICAL_HEIGHT // 2
            UI.draw_text(f"ODA NO: {network.game_id}", UI.font_big, UI.GOLD, virtual_surface, center_x, center_y - 50)
            UI.draw_text("RAKİP BEKLENİYOR...", UI.font_ui, UI.WHITE, virtual_surface, center_x, center_y + 50)
            UI.draw_text("Arkadaşına Oda Numarasını söyle!", UI.font_icon, (150, 150, 150), virtual_surface, center_x, center_y + 100)

            scaled_surface = pygame.transform.smoothscale(virtual_surface, screen.get_size())
            screen.blit(scaled_surface, (0, 0))
            pygame.display.update()
            continue

        if game.winner is None and sent_rematch_request:
            sent_rematch_request = False 

        # --- 3. ÇİZİM ---
        virtual_surface.fill(UI.BG_COLOR)
        UI.draw_grid()

        for food in game.foods: UI.draw_apple(food[0], food[1])
        for shield in game.shields: UI.draw_shield_item(shield[0], shield[1])

        UI.draw_snake_with_eyes(game.snake1, UI.GREEN, game.p1_dir, game.p1_has_shield)
        UI.draw_snake_with_eyes(game.snake2, UI.RED, game.p2_dir, game.p2_has_shield)
        UI.show_hud(game.score[0], game.score[1], game.remaining_time, game.current_speed, game.p1_has_shield, game.p2_has_shield, current_player_id=network.p)

        # --- 4. OYUN SONU EKRANI ---
        if game.winner is not None:
            overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            virtual_surface.blit(overlay, (0, 0))

            if game.winner == 0: txt = "YEŞİL KAZANDI"; color = UI.GREEN
            elif game.winner == 1: txt = "KIRMIZI KAZANDI"; color = UI.RED
            else: txt = "BERABERE"; color = UI.WHITE
            
            UI.draw_text(txt, UI.font_big, color, virtual_surface, LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 150)
            
            p1_txt = f"YEŞİL: {game.score[0]}"
            if network.p == 0: p1_txt += " (SEN)"
            UI.draw_text(p1_txt, UI.font_ui, UI.GREEN, virtual_surface, LOGICAL_WIDTH//2 - 200, LOGICAL_HEIGHT//2 - 50)

            p2_txt = f"KIRMIZI: {game.score[1]}"
            if network.p == 1: p2_txt += " (SEN)"
            UI.draw_text(p2_txt, UI.font_ui, UI.RED, virtual_surface, LOGICAL_WIDTH//2 + 200, LOGICAL_HEIGHT//2 - 50)
            
            pygame.draw.line(virtual_surface, (100, 100, 100), (LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 70), (LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 30), 2)
            
            p1_status = "HAZIR" if game.p1_rematch else "BEKLİYOR..."
            p1_color = UI.GREEN if game.p1_rematch else (100, 100, 100)
            UI.draw_text(f"DURUM: {p1_status}", UI.font_ui, p1_color, virtual_surface, LOGICAL_WIDTH//2 - 200, LOGICAL_HEIGHT//2 + 50)
            
            p2_status = "HAZIR" if game.p2_rematch else "BEKLİYOR..."
            p2_color = UI.RED if game.p2_rematch else (100, 100, 100)
            UI.draw_text(f"DURUM: {p2_status}", UI.font_ui, p2_color, virtual_surface, LOGICAL_WIDTH//2 + 200, LOGICAL_HEIGHT//2 + 50)

            UI.draw_text("Tekrar oynamak için [R] - Çıkış [ESC]", UI.font_ui, UI.WHITE, virtual_surface, LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 + 150)

        # --- 5. EKRANA BASMA ---
        scaled_surface = pygame.transform.smoothscale(virtual_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.update()

        clock.tick(60)