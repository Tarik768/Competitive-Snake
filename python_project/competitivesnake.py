import pygame
import time
import random
import UI  # UI.py dosyasını import ettik!

pygame.init()

# --- EKRAN AYARLARI ---
infoObject = pygame.display.Info()
DIS_WIDTH = infoObject.current_w
DIS_HEIGHT = infoObject.current_h

# Bağımsız çalıştırma kontrolü
if __name__ == "__main__":
    dis = pygame.display.set_mode((DIS_WIDTH, DIS_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption('Competitive Snake: Shields Update')
else:
    dis = pygame.display.get_surface()

# --- OYUN AYARLARI ---
START_SPEED = 10
GAME_DURATION = 10
SPEED_INCREASE_INTERVAL = 5
SHIELD_DURATION = 5000

clock = pygame.time.Clock()

def create_random_item(snake1, snake2, other_items): # Yem veya Kalkan için koordinat üretir
    block = UI.SNAKE_BLOCK
    max_attempts = 100  # En fazla 100 kere yer arasın
    attempts = 0
    
    while attempts < max_attempts:
        rand_x = random.randrange(0, DIS_WIDTH - block)
        rand_y = random.randrange(50, DIS_HEIGHT - block)
        
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
    
    return None # Yer bulamazsa None döndür

def handle_cut_robust(victim_list, hit_point_x, hit_point_y, food_list):
    """Hassas çarpışma kontrolü ve kesme işlemi"""
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
    # --- UI BAŞLATMA ---
    UI.init_ui(screen, DIS_WIDTH, DIS_HEIGHT)
    
    try:
        shield_sfx = pygame.mixer.Sound("sounds/shield.wav")
        end_sfx = pygame.mixer.Sound("sounds/endsound.wav")
        hit_sfx = pygame.mixer.Sound("sounds/hit.wav")
        eat_sfx = pygame.mixer.Sound("sounds/eat.wav") # <--- YENİ: YEM SESİ
        
        # --- SES SEVİYESİ AYARLARI ---
        shield_sfx.set_volume(1.0)
        end_sfx.set_volume(1.0)
        hit_sfx.set_volume(1.0)
        eat_sfx.set_volume(0.5)
        
    except:
        shield_sfx = None
        end_sfx = None
        hit_sfx = None
        eat_sfx = None # <--- YENİ
        print("Ses dosyaları eksik.")

    game_over = False
    start_ticks = pygame.time.get_ticks()
    
    block = UI.SNAKE_BLOCK 

    # --- BAŞLANGIÇ KONUMLARI ---
    start_x1 = round((DIS_WIDTH / 4 * 3) / block) * block
    start_y1 = round((DIS_HEIGHT / 2) / block) * block
    
    start_x2 = round((DIS_WIDTH / 4) / block) * block
    start_y2 = round((DIS_HEIGHT / 2) / block) * block

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

    # --- KALKAN DEĞİŞKENLERİ ---
    p1_has_shield = False
    p1_shield_end_time = 0
    p2_has_shield = False
    p2_shield_end_time = 0

    foods = []
    shields = [] 
    paused = False
    pause_start_time = 0

    for _ in range(2):
        new_food = create_random_item(snake1_list, snake2_list, shields + foods)
        if new_food:
            foods.append(new_food)

    while not game_over:
        current_time = pygame.time.get_ticks()
        
        # Süreyi hesaplarken pause süresini hesaba katmak için:
        # Eğer pause durumundaysak zamanı dondurmuş gibi davranıyoruz.
        # Ancak basitlik için burayı ellemiyoruz, sadece 'continue' ekleyeceğiz.
        
        if not paused:
            seconds_passed = (current_time - start_ticks) / 1000
            remaining_time = GAME_DURATION - seconds_passed
            current_speed = START_SPEED + (int(seconds_passed) // SPEED_INCREASE_INTERVAL)

            # --- OYUN SONU KONTROLÜ ---
            if remaining_time <= 0:
                if end_sfx: end_sfx.play()
                if length_of_snake1 > length_of_snake2:
                    result = UI.winner_screen("YESIL YILAN", UI.GREEN, length_of_snake1, length_of_snake2, gameLoop)
                elif length_of_snake2 > length_of_snake1:
                    result = UI.winner_screen("KIRMIZI YILAN", UI.RED, length_of_snake1, length_of_snake2, gameLoop)
                else:
                    result = UI.winner_screen("BERABERE!", UI.WHITE, length_of_snake1, length_of_snake2, gameLoop)
                
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
                    if event.key == pygame.K_p: # DURAKLAT
                        paused = True
                        pause_start_time = pygame.time.get_ticks()
                    
                    # Kontroller
                    if event.key == pygame.K_LEFT and p1_dir != "RIGHT": p1_next_dir = "LEFT"
                    elif event.key == pygame.K_RIGHT and p1_dir != "LEFT": p1_next_dir = "RIGHT"
                    elif event.key == pygame.K_UP and p1_dir != "DOWN": p1_next_dir = "UP"
                    elif event.key == pygame.K_DOWN and p1_dir != "UP": p1_next_dir = "DOWN"
                    
                    if event.key == pygame.K_a and p2_dir != "RIGHT": p2_next_dir = "LEFT"
                    elif event.key == pygame.K_d and p2_dir != "LEFT": p2_next_dir = "RIGHT"
                    elif event.key == pygame.K_w and p2_dir != "DOWN": p2_next_dir = "UP"
                    elif event.key == pygame.K_s and p2_dir != "UP": p2_next_dir = "DOWN"

                else: # PAUSE DURUMUNDA TUŞLAR
                    if event.key == pygame.K_c: # DEVAM ET
                        paused = False
                        pause_duration = pygame.time.get_ticks() - pause_start_time
                        start_ticks += pause_duration
                    
                    elif event.key == pygame.K_r: # YENİDEN BAŞLAT
                        gameLoop(screen)
                        return
        
        if paused:
            UI.draw_pause_screen()
            pygame.display.update()
            clock.tick(15) # İşlemciyi yormamak için FPS düşür
            continue # Döngünün başına dön, HAREKET KODLARINI ÇALIŞTIRMA
        
        # --- HAREKET ---
        # P1 (Yeşil)
        if p1_next_dir == "LEFT": x1_change = -block; y1_change = 0; p1_dir = "LEFT"
        elif p1_next_dir == "RIGHT": x1_change = block; y1_change = 0; p1_dir = "RIGHT"
        elif p1_next_dir == "UP": y1_change = -block; x1_change = 0; p1_dir = "UP"
        elif p1_next_dir == "DOWN": y1_change = block; x1_change = 0; p1_dir = "DOWN"
        
        # P2 (Kırmızı)
        if p2_next_dir == "LEFT": x2_change = -block; y2_change = 0; p2_dir = "LEFT"
        elif p2_next_dir == "RIGHT": x2_change = block; y2_change = 0; p2_dir = "RIGHT"
        elif p2_next_dir == "UP": y2_change = -block; x2_change = 0; p2_dir = "UP"
        elif p2_next_dir == "DOWN": y2_change = block; x2_change = 0; p2_dir = "DOWN"

        x1 += x1_change; y1 += y1_change
        x2 += x2_change; y2 += y2_change

        # Duvarın İçinden Geçme
        if x1 >= DIS_WIDTH: x1 = 0
        elif x1 < 0: x1 = (DIS_WIDTH // block) * block - block
        if y1 >= DIS_HEIGHT: y1 = 50 
        elif y1 < 50: y1 = (DIS_HEIGHT // block) * block - block

        if x2 >= DIS_WIDTH: x2 = 0
        elif x2 < 0: x2 = (DIS_WIDTH // block) * block - block
        if y2 >= DIS_HEIGHT: y2 = 50
        elif y2 < 50: y2 = (DIS_HEIGHT // block) * block - block

        # UI Modülü Üzerinden Çizim İşlemleri
        screen.fill(UI.BG_COLOR)
        UI.draw_grid()

        # Kalkan Spawn
        if len(shields) == 0 and random.randint(0, 200) == 0:
            new_shield = create_random_item(snake1_list, snake2_list, foods)
            if new_shield:
                shields.append(new_shield)

        # Eşyaları Çiz
        for food in foods:
            UI.draw_apple(food[0], food[1])
        
        for shield in shields:
            UI.draw_shield_item(shield[0], shield[1])

        # Vücut Güncelleme
        snake1_head = [x1, y1]
        snake1_list.append(snake1_head)
        if len(snake1_list) > length_of_snake1: del snake1_list[0]

        snake2_head = [x2, y2]
        snake2_list.append(snake2_head)
        if len(snake2_list) > length_of_snake2: del snake2_list[0]

        # Kalkan Süresi
        if p1_has_shield and current_time > p1_shield_end_time:
            p1_has_shield = False
        if p2_has_shield and current_time > p2_shield_end_time:
            p2_has_shield = False

        len1_before = length_of_snake1
        len2_before = length_of_snake2

        # Çarpışma
        if not p2_has_shield:
            snake2_list, length_of_snake2 = handle_cut_robust(snake2_list, x1, y1, foods)
        if not p1_has_shield:
            snake1_list, length_of_snake1 = handle_cut_robust(snake1_list, x2, y2, foods)
        
        snake1_list, length_of_snake1 = handle_cut_robust(snake1_list, x1, y1, foods)
        snake2_list, length_of_snake2 = handle_cut_robust(snake2_list, x2, y2, foods)

        if (len1_before != length_of_snake1 or len2_before != length_of_snake2) and hit_sfx:
            hit_sfx.play()

        # Çizimler
        UI.draw_snake_with_eyes(snake1_list, UI.GREEN, p1_dir, p1_has_shield)
        UI.draw_snake_with_eyes(snake2_list, UI.RED, p2_dir, p2_has_shield)

        UI.show_hud(length_of_snake1, length_of_snake2, remaining_time, current_speed, p1_has_shield, p2_has_shield)
        
        # Yem Yeme
        for food in foods[:]:
            if abs(x1 - food[0]) < 15 and abs(y1 - food[1]) < 15:
                if eat_sfx: eat_sfx.play()
                length_of_snake1 += 1
                foods.remove(food)
                new_item = create_random_item(snake1_list, snake2_list, shields + foods)
                if new_item: foods.append(new_item)

            elif abs(x2 - food[0]) < 15 and abs(y2 - food[1]) < 15:
                if eat_sfx: eat_sfx.play()
                length_of_snake2 += 1
                foods.remove(food)
                new_item = create_random_item(snake1_list, snake2_list, shields + foods)
                if new_item: foods.append(new_item)

        # Kalkan Alma
        for shield in shields[:]:
            if abs(x1 - shield[0]) < 15 and abs(y1 - shield[1]) < 15:
                if shield_sfx: shield_sfx.play()
                p1_has_shield = True
                p1_shield_end_time = current_time + SHIELD_DURATION
                shields.remove(shield)
            elif abs(x2 - shield[0]) < 15 and abs(y2 - shield[1]) < 15:
                if shield_sfx: shield_sfx.play()
                p2_has_shield = True
                p2_shield_end_time = current_time + SHIELD_DURATION
                shields.remove(shield)

        if len(foods) < 2:
            new_item = create_random_item(snake1_list, snake2_list, shields + foods)
            if new_item:
                foods.append(new_item)

        if remaining_time <= 11: # Son 10 saniye uyarı
            UI.draw_huge_countdown(remaining_time)

        pygame.display.update()
        clock.tick(current_speed)

    pygame.quit()
    quit()
