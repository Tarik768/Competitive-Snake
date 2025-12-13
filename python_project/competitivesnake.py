import pygame
import time
import random

pygame.init()

# --- EKRAN AYARLARI (TAM EKRAN) ---
infoObject = pygame.display.Info()
DIS_WIDTH = infoObject.current_w
DIS_HEIGHT = infoObject.current_h

dis = pygame.display.set_mode((DIS_WIDTH, DIS_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Competitive Snake: Turbo & Apples')

# --- RENKLER ---
BG_COLOR = (10, 10, 20)       
GRID_COLOR = (30, 30, 50)     
WHITE = (240, 240, 240)
BLACK = (0, 0, 0)
RED = (255, 50, 50)           
GREEN = (50, 255, 80)         
GOLD = (255, 215, 0)
APPLE_COLOR = (255, 40, 40)   # Parlak Kırmızı Elma
LEAF_COLOR = (50, 200, 50)    # Yeşil Sap

# --- AYARLAR ---
SNAKE_BLOCK = 25              
START_SPEED = 10              
GAME_DURATION = 120           
SPEED_INCREASE_INTERVAL = 5   # Her 5 saniyede bir hızlanacak

clock = pygame.time.Clock()

# Fontlar
font_ui = pygame.font.SysFont("bahnschrift", 25)
font_big = pygame.font.SysFont("bahnschrift", 80)

def draw_grid():
    for x in range(0, DIS_WIDTH, SNAKE_BLOCK):
        pygame.draw.line(dis, GRID_COLOR, (x, 0), (x, DIS_HEIGHT))
    for y in range(0, DIS_HEIGHT, SNAKE_BLOCK):
        pygame.draw.line(dis, GRID_COLOR, (0, y), (DIS_WIDTH, y))

def draw_apple(x, y):
    """Yemi Elma Şeklinde Çizer"""
    center_x = x + SNAKE_BLOCK // 2
    center_y = y + SNAKE_BLOCK // 2
    radius = SNAKE_BLOCK // 2 - 2

    # Elma Gövdesi
    pygame.draw.circle(dis, APPLE_COLOR, (center_x, center_y), radius)
    
    # Parlama Efekti (Hacim kazandırır)
    pygame.draw.circle(dis, (255, 150, 150), (center_x - 4, center_y - 4), 4)

    # Sap (Yaprak)
    leaf_start = (center_x, center_y - radius)
    leaf_end = (center_x + 6, center_y - radius - 6)
    pygame.draw.line(dis, LEAF_COLOR, leaf_start, leaf_end, 3)

def draw_snake_with_eyes(snake_list, color, direction):
    for index, x in enumerate(snake_list):
        pygame.draw.rect(dis, color, [x[0], x[1], SNAKE_BLOCK, SNAKE_BLOCK])
        pygame.draw.rect(dis, BG_COLOR, [x[0], x[1], SNAKE_BLOCK, SNAKE_BLOCK], 1)

    if len(snake_list) > 0:
        head_x, head_y = snake_list[-1]
        center_x = head_x + SNAKE_BLOCK // 2
        center_y = head_y + SNAKE_BLOCK // 2
        
        eye_offset = SNAKE_BLOCK // 4
        
        if direction == "LEFT":
            e1 = (center_x - eye_offset, center_y - eye_offset)
            e2 = (center_x - eye_offset, center_y + eye_offset)
        elif direction == "RIGHT":
            e1 = (center_x + eye_offset, center_y - eye_offset)
            e2 = (center_x + eye_offset, center_y + eye_offset)
        elif direction == "UP":
            e1 = (center_x - eye_offset, center_y - eye_offset)
            e2 = (center_x + eye_offset, center_y - eye_offset)
        else: # DOWN
            e1 = (center_x - eye_offset, center_y + eye_offset)
            e2 = (center_x + eye_offset, center_y + eye_offset)
            
        pygame.draw.circle(dis, WHITE, e1, 4)
        pygame.draw.circle(dis, WHITE, e2, 4)
        pygame.draw.circle(dis, BLACK, e1, 2)
        pygame.draw.circle(dis, BLACK, e2, 2)

def show_hud(p1_score, p2_score, remaining_time, current_speed):
    pygame.draw.rect(dis, (20, 20, 30), [0, 0, DIS_WIDTH, 50])
    pygame.draw.line(dis, WHITE, (0, 50), (DIS_WIDTH, 50), 2)

    p1_text = font_ui.render(f"YESIL: {p1_score}", True, GREEN)
    p2_text = font_ui.render(f"KIRMIZI: {p2_score}", True, RED)
    dis.blit(p1_text, (50, 15))
    dis.blit(p2_text, (DIS_WIDTH - 200, 15))

    color_time = WHITE
    if remaining_time <= 10: color_time = RED
    
    mins, secs = divmod(int(remaining_time), 60)
    timer_str = '{:02d}:{:02d}'.format(mins, secs)

    center_info = f"SURE: {timer_str}  |  HIZ: {int(current_speed)}"
    time_text = font_ui.render(center_info, True, color_time)
    text_rect = time_text.get_rect(center=(DIS_WIDTH/2, 25))
    dis.blit(time_text, text_rect)

def create_random_food(snake1, snake2):
    while True:
        rand_x = random.randrange(0, DIS_WIDTH - SNAKE_BLOCK)
        rand_y = random.randrange(50, DIS_HEIGHT - SNAKE_BLOCK)
        
        fx = round(rand_x / SNAKE_BLOCK) * SNAKE_BLOCK
        fy = round(rand_y / SNAKE_BLOCK) * SNAKE_BLOCK
        
        # Yem yılanların üstüne doğmasın
        snake1_coords = [[p[0], p[1]] for p in snake1]
        snake2_coords = [[p[0], p[1]] for p in snake2]
        
        if [fx, fy] not in snake1_coords and [fx, fy] not in snake2_coords:
            return [fx, fy]

def winner_screen(winner_name, winner_color, score):
    waiting = True
    while waiting:
        dis.fill(BG_COLOR)
        
        title = font_big.render("KAZANAN", True, WHITE)
        title_rect = title.get_rect(center=(DIS_WIDTH/2, DIS_HEIGHT/2 - 100))
        dis.blit(title, title_rect)
        
        name = font_big.render(winner_name, True, winner_color)
        name_rect = name.get_rect(center=(DIS_WIDTH/2, DIS_HEIGHT/2))
        
        score_txt = font_ui.render(f"Toplam Uzunluk: {score}", True, GOLD)
        score_rect = score_txt.get_rect(center=(DIS_WIDTH/2, DIS_HEIGHT/2 + 80))

        pygame.draw.rect(dis, winner_color, name_rect.inflate(40, 20), 3)

        dis.blit(name, name_rect)
        dis.blit(score_txt, score_rect)

        info = font_ui.render("Tekrar Oynamak için [C] - Çıkmak için [ESC]", True, WHITE)
        info_rect = info.get_rect(center=(DIS_WIDTH/2, DIS_HEIGHT - 100))
        dis.blit(info, info_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_c:
                    waiting = False
                    gameLoop()

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
        food_list.extend(dropped_parts) # Kopan parçaları yeme dönüştür
        new_body = victim_list[cut_index+1:]
        return new_body, len(new_body)
    
    return victim_list, len(victim_list)

def gameLoop():
    game_over = False
    start_ticks = pygame.time.get_ticks()
    
    # Başlangıç Konumları (Grid Hizalı)
    start_x1 = round((DIS_WIDTH / 4 * 3) / SNAKE_BLOCK) * SNAKE_BLOCK
    start_y1 = round((DIS_HEIGHT / 2) / SNAKE_BLOCK) * SNAKE_BLOCK
    
    start_x2 = round((DIS_WIDTH / 4) / SNAKE_BLOCK) * SNAKE_BLOCK
    start_y2 = round((DIS_HEIGHT / 2) / SNAKE_BLOCK) * SNAKE_BLOCK

    x1, y1 = int(start_x1), int(start_y1)
    x1_change, y1_change = 0, 0
    p1_dir = "LEFT"
    snake1_list = []
    length_of_snake1 = 5
    
    x2, y2 = int(start_x2), int(start_y2)
    x2_change, y2_change = 0, 0
    p2_dir = "RIGHT"
    snake2_list = []
    length_of_snake2 = 5

    foods = []
    p1_next_dir = p1_dir
    p2_next_dir = p2_dir
    # BAŞLANGIÇTA 2 YEM OLSUN
    for _ in range(2):
        foods.append(create_random_food(snake1_list, snake2_list))

    while not game_over:
        
        seconds_passed = (pygame.time.get_ticks() - start_ticks) / 1000
        remaining_time = GAME_DURATION - seconds_passed
        
        # --- HIZLANMA MANTIĞI (HER 5 SANİYEDE BİR) ---
        current_speed = START_SPEED + (int(seconds_passed) // SPEED_INCREASE_INTERVAL)

        if remaining_time <= 0:
            if length_of_snake1 > length_of_snake2:
                winner_screen("YESIL YILAN", GREEN, length_of_snake1)
            elif length_of_snake2 > length_of_snake1:
                winner_screen("KIRMIZI YILAN", RED, length_of_snake2)
            else:
                winner_screen("BERABERE!", WHITE, length_of_snake1)
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_over = True
                
                # P1 Kontrol
                if event.key == pygame.K_LEFT and p1_dir != "RIGHT":
                    p1_next_dir = "LEFT"
                elif event.key == pygame.K_RIGHT and p1_dir != "LEFT":
                    p1_next_dir = "RIGHT"
                elif event.key == pygame.K_UP and p1_dir != "DOWN":
                    p1_next_dir = "UP"
                elif event.key == pygame.K_DOWN and p1_dir != "UP":
                    p1_next_dir = "DOWN"

                # P2 Kontrol
                if event.key == pygame.K_a and p2_dir != "RIGHT":
                    p2_next_dir = "LEFT"
                elif event.key == pygame.K_d and p2_dir != "LEFT":
                    p2_next_dir = "RIGHT"
                elif event.key == pygame.K_w and p2_dir != "DOWN":
                    p2_next_dir = "UP"
                elif event.key == pygame.K_s and p2_dir != "UP":
                    p2_next_dir = "DOWN"
        
        if p1_next_dir == "LEFT":
             x1_change = -SNAKE_BLOCK; y1_change = 0; p1_dir = "LEFT"
        elif p1_next_dir == "RIGHT":
            x1_change = SNAKE_BLOCK; y1_change = 0; p1_dir = "RIGHT"
        elif p1_next_dir == "UP":
            y1_change = -SNAKE_BLOCK; x1_change = 0; p1_dir = "UP"
        elif p1_next_dir == "DOWN":
            y1_change = SNAKE_BLOCK; x1_change = 0; p1_dir = "DOWN"
        
        if p2_next_dir == "LEFT":
            x2_change = -SNAKE_BLOCK; y2_change = 0; p2_dir = "LEFT"
        elif p2_next_dir == "RIGHT":
            x2_change = SNAKE_BLOCK; y2_change = 0; p2_dir = "RIGHT"
        elif p2_next_dir == "UP":
            y2_change = -SNAKE_BLOCK; x2_change = 0; p2_dir = "UP"
        elif p2_next_dir == "DOWN":
            y2_change = SNAKE_BLOCK; x2_change = 0; p2_dir = "DOWN"
        # Hareket
        x1 += x1_change; y1 += y1_change
        x2 += x2_change; y2 += y2_change

        # Duvar Wrap
        if x1 >= DIS_WIDTH: x1 = 0
        elif x1 < 0: x1 = (DIS_WIDTH // SNAKE_BLOCK) * SNAKE_BLOCK - SNAKE_BLOCK
        if y1 >= DIS_HEIGHT: y1 = 50 
        elif y1 < 50: y1 = (DIS_HEIGHT // SNAKE_BLOCK) * SNAKE_BLOCK - SNAKE_BLOCK

        if x2 >= DIS_WIDTH: x2 = 0
        elif x2 < 0: x2 = (DIS_WIDTH // SNAKE_BLOCK) * SNAKE_BLOCK - SNAKE_BLOCK
        if y2 >= DIS_HEIGHT: y2 = 50
        elif y2 < 50: y2 = (DIS_HEIGHT // SNAKE_BLOCK) * SNAKE_BLOCK - SNAKE_BLOCK

        dis.fill(BG_COLOR)
        draw_grid()

        # YEMLERİ ÇİZ (ELMA)
        for food in foods:
            draw_apple(food[0], food[1])

        # Vücut Güncelleme
        snake1_head = [x1, y1]
        snake1_list.append(snake1_head)
        if len(snake1_list) > length_of_snake1: del snake1_list[0]

        snake2_head = [x2, y2]
        snake2_list.append(snake2_head)
        if len(snake2_list) > length_of_snake2: del snake2_list[0]

        # Çarpışmalar (foods listesini parametre olarak gönderiyoruz ki parçalar eklensin)
        snake2_list, length_of_snake2 = handle_cut_robust(snake2_list, x1, y1, foods)
        snake1_list, length_of_snake1 = handle_cut_robust(snake1_list, x2, y2, foods)
        snake1_list, length_of_snake1 = handle_cut_robust(snake1_list, x1, y1, foods)
        snake2_list, length_of_snake2 = handle_cut_robust(snake2_list, x2, y2, foods)

        draw_snake_with_eyes(snake1_list, GREEN, p1_dir)
        draw_snake_with_eyes(snake2_list, RED, p2_dir)

        show_hud(length_of_snake1, length_of_snake2, remaining_time, current_speed)
        
        # YEM YEME (P1)
        for food in foods[:]:
            if abs(x1 - food[0]) < 15 and abs(y1 - food[1]) < 15:
                length_of_snake1 += 1
                foods.remove(food)
                # YENİLENME MANTIĞI: Yenenin yerine hemen yenisi gelsin
                foods.append(create_random_food(snake1_list, snake2_list))
        
        # YEM YEME (P2)
        for food in foods[:]:
            if abs(x2 - food[0]) < 15 and abs(y2 - food[1]) < 15:
                length_of_snake2 += 1
                foods.remove(food)
                foods.append(create_random_food(snake1_list, snake2_list))

        # Eğer herhangi bir sebeple yem biterse (güvenlik için)
        if len(foods) < 2:
             foods.append(create_random_food(snake1_list, snake2_list))

        pygame.display.update()
        clock.tick(current_speed)

    pygame.quit()
    quit()
