import pygame

# Sabit değerler
SNAKE_BLOCK = 25
SCREEN_WIDTH = 0 
SCREEN_HEIGHT = 0

# Renkler
BG_COLOR = (10, 10, 20)
GRID_COLOR = (30, 30, 50)
WHITE = (240, 240, 240)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 80)
GOLD = (255, 215, 0)
APPLE_COLOR = (255, 40, 40)
LEAF_COLOR = (50, 200, 50)
SHIELD_COLOR = (0, 191, 255)
SHIELD_GLOW = (0, 255, 255)


dis = None
font_ui = None
font_big = None
font_icon = None

def init_ui(screen, width, height): # Ana dosyadan ekranı ve boyutları alır, fontları hazırlar.
    global dis, SCREEN_WIDTH, SCREEN_HEIGHT, font_ui, font_big, font_icon, font_countdown
    
    if not pygame.font.get_init():
        pygame.font.init()

    dis = screen
    SCREEN_WIDTH = width
    SCREEN_HEIGHT = height

    font_ui = pygame.font.SysFont("bahnschrift", 25)
    font_big = pygame.font.SysFont("bahnschrift", 80)
    font_icon = pygame.font.SysFont("consolas", 20, bold=True)
    font_countdown = pygame.font.SysFont("bahnschrift", 400, bold=True)

def draw_grid():
    for x in range(0, SCREEN_WIDTH, SNAKE_BLOCK):
        pygame.draw.line(dis, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, SNAKE_BLOCK):
        pygame.draw.line(dis, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

def draw_apple(x, y):
    center_x = x + SNAKE_BLOCK // 2
    center_y = y + SNAKE_BLOCK // 2
    radius = SNAKE_BLOCK // 2 - 2
    pygame.draw.circle(dis, APPLE_COLOR, (center_x, center_y), radius)
    pygame.draw.circle(dis, (255, 150, 150), (center_x - 4, center_y - 4), 4)
    leaf_start = (center_x, center_y - radius)
    leaf_end = (center_x + 6, center_y - radius - 6)
    pygame.draw.line(dis, LEAF_COLOR, leaf_start, leaf_end, 3)

def draw_shield_item(x, y):
    center_x = x + SNAKE_BLOCK // 2
    center_y = y + SNAKE_BLOCK // 2
    radius = SNAKE_BLOCK // 2 - 2

    pygame.draw.circle(dis, SHIELD_GLOW, (center_x, center_y), radius, 2)
    pygame.draw.circle(dis, (0, 100, 150), (center_x, center_y), radius - 4)
    
    text = font_icon.render("S", True, WHITE)
    text_rect = text.get_rect(center=(center_x, center_y))
    dis.blit(text, text_rect)

def draw_snake_with_eyes(snake_list, color, direction, has_shield=False):
    for index, x in enumerate(snake_list):
        if has_shield:
            pygame.draw.rect(dis, SHIELD_GLOW, [x[0]-2, x[1]-2, SNAKE_BLOCK+4, SNAKE_BLOCK+4], 2)
        
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

def show_hud(p1_score, p2_score, remaining_time, current_speed, p1_shield, p2_shield): # HUD
    pygame.draw.rect(dis, (20, 20, 30), [0, 0, SCREEN_WIDTH, 50])
    pygame.draw.line(dis, WHITE, (0, 50), (SCREEN_WIDTH, 50), 2)

    p2_info = f"KIRMIZI: {p2_score}" + (" [KALKAN]" if p2_shield else "")
    p2_color = SHIELD_GLOW if p2_shield else RED
    p2_text = font_ui.render(p2_info, True, p2_color)
    dis.blit(p2_text, (50, 15)) # Sol tarafa çiz

    p1_info = (" [KALKAN] " if p1_shield else "") + f"YEŞİL: {p1_score}"
    p1_color = SHIELD_GLOW if p1_shield else GREEN
    p1_text = font_ui.render(p1_info, True, p1_color)
    dis.blit(p1_text, (SCREEN_WIDTH - 350, 15))

    color_time = WHITE
    if remaining_time <= 10: color_time = RED
    mins, secs = divmod(int(remaining_time), 60)
    timer_str = '{:02d}:{:02d}'.format(mins, secs)

    center_info = f"SURE: {timer_str}  |  HIZ: {int(current_speed)}"
    time_text = font_ui.render(center_info, True, color_time)
    text_rect = time_text.get_rect(center=(SCREEN_WIDTH/2, 25))
    dis.blit(time_text, text_rect)

def draw_pause_screen(): # pause screen
    box_width, box_height = 600, 200
    box_x = (SCREEN_WIDTH - box_width) // 2
    box_y = (SCREEN_HEIGHT - box_height) // 2

    pygame.draw.rect(dis, (10, 10, 40), (box_x, box_y, box_width, box_height))
    pygame.draw.rect(dis, WHITE, (box_x, box_y, box_width, box_height), 3)

    title = font_big.render("DURAKLATILDI", True, RED)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
    dis.blit(title, title_rect)

    info = font_ui.render("Devam [C] - Yeniden Başla [R] - Çıkış [ESC]", True, WHITE)
    info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    dis.blit(info, info_rect)

def draw_huge_countdown(seconds): # Countdown
    if seconds <= 0: return
    display_str = str(int(seconds))
    text = font_countdown.render(display_str, True, (255, 0, 0))
    text.set_alpha(40) # Şeffaflık
    
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    dis.blit(text, text_rect)

def winner_screen(winner_name, winner_color, p1_score, p2_score, game_loop_callback):
    waiting = True
    while waiting:
        dis.fill(BG_COLOR)
        
        if winner_name == "BERABERE":
            header_text = "OYUN BİTTİ"
        else:
            header_text = "KAZANAN"
            
        title = font_big.render(header_text, True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 120))
        dis.blit(title, title_rect)
        
        # Kazanan İsmi
        name = font_big.render(winner_name, True, winner_color)
        name_rect = name.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20))
        pygame.draw.rect(dis, winner_color, name_rect.inflate(40, 20), 3)
        dis.blit(name, name_rect)
        
        p2_text = font_ui.render(f"KIRMIZI: {p2_score}", True, RED)
        p2_rect = p2_text.get_rect(center=(SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT/2 + 80))
        
        p1_text = font_ui.render(f"YEŞİL: {p1_score}", True, GREEN)
        p1_rect = p1_text.get_rect(center=(SCREEN_WIDTH/2 + 150, SCREEN_HEIGHT/2 + 80))

        pygame.draw.line(dis, (60, 60, 80), (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 65), (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 95), 2)

        dis.blit(p2_text, p2_rect) 
        dis.blit(p1_text, p1_rect) 

        info = font_ui.render("Tekrar oynamak için [R] - Menüye dönmek için [ESC]", True, WHITE)
        info_rect = info.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 100))
        dis.blit(info, info_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"       # Menüye dön
                if event.key == pygame.K_r:
                    waiting = False
                    return "RESTART"    # Yeniden başla
