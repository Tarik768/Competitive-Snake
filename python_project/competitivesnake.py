import pygame
import time
import random

# Modül olarak çalıştırıldığında init gerekebilir, ama menu.py zaten init yapıyor.
# Yine de bağımsız çalışabilmesi için buraya ekliyoruz.
pygame.init()

# --- EKRAN AYARLARI ---
infoObject = pygame.display.Info()
DIS_WIDTH = infoObject.current_w
DIS_HEIGHT = infoObject.current_h

# Eğer bu dosya direkt çalıştırılırsa ekranı oluştur, import edilirse bekle
if __name__ == "__main__":
    dis = pygame.display.set_mode((DIS_WIDTH, DIS_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption('Competitive Snake: Shields Update')
else:
    # Menu üzerinden çağrıldığında ekran zaten var, onu alıyoruz
    dis = pygame.display.get_surface()

# --- RENKLER ---
BG_COLOR = (10, 10, 20)
GRID_COLOR = (30, 30, 50)
WHITE = (240, 240, 240)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 80)
GOLD = (255, 215, 0)
APPLE_COLOR = (255, 40, 40)
LEAF_COLOR = (50, 200, 50)

# --- KALKAN RENKLERİ ---
SHIELD_COLOR = (0, 191, 255)   # Deep Sky Blue
SHIELD_GLOW = (0, 255, 255)    # Cyan (Parlayan kenar)

# --- AYARLAR ---
SNAKE_BLOCK = 25
START_SPEED = 10
GAME_DURATION = 120
SPEED_INCREASE_INTERVAL = 5
SHIELD_DURATION = 5000  # ms cinsinden (5 saniye)

clock = pygame.time.Clock()

# Fontlar
font_ui = pygame.font.SysFont("bahnschrift", 25)
font_big = pygame.font.SysFont("bahnschrift", 80)
font_icon = pygame.font.SysFont("consolas", 20, bold=True) # Kalkan üzerindeki "S" için

def draw_grid():
    for x in range(0, DIS_WIDTH, SNAKE_BLOCK):
        pygame.draw.line(dis, GRID_COLOR, (x, 0), (x, DIS_HEIGHT))
    for y in range(0, DIS_HEIGHT, SNAKE_BLOCK):
        pygame.draw.line(dis, GRID_COLOR, (0, y), (DIS_WIDTH, y))

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
    """Yerde duran kalkan itemini çizer"""
    center_x = x + SNAKE_BLOCK // 2
    center_y = y + SNAKE_BLOCK // 2
    radius = SNAKE_BLOCK // 2 - 2

    # Dış Çember (Parlak)
    pygame.draw.circle(dis, SHIELD_GLOW, (center_x, center_y), radius, 2)
    # İç Dolgu (Yarı saydam efekt veremiyoruz ama koyu mavi yapalım)
    pygame.draw.circle(dis, (0, 100, 150), (center_x, center_y), radius - 4)
    
    # Ortasına "S" harfi veya kalkan sembolü
    text = font_icon.render("S", True, WHITE)
    text_rect = text.get_rect(center=(center_x, center_y))
    dis.blit(text, text_rect)

def draw_snake_with_eyes(snake_list, color, direction, has_shield=False):
    for index, x in enumerate(snake_list):
        # Eğer kalkan varsa dışına parlak çerçeve çiz
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

def show_hud(p1_score, p2_score, remaining_time, current_speed, p1_shield, p2_shield):
    # Üst bar arka plan
    pygame.draw.rect(dis, (20, 20, 30), [0, 0, DIS_WIDTH, 50])
    pygame.draw.line(dis, WHITE, (0, 50), (DIS_WIDTH, 50), 2)

    # P1 Skor
    p1_info = f"YESIL: {p1_score}" + (" [KALKAN]" if p1_shield else "")
    p1_color = SHIELD_GLOW if p1_shield else GREEN
    p1_text = font_ui.render(p1_info, True, p1_color)
    dis.blit(p1_text, (50, 15))

    # P2 Skor
    p2_info = (" [KALKAN] " if p2_shield else "") + f"KIRMIZI: {p2_score}"
    p2_color = SHIELD_GLOW if p2_shield else RED
    p2_text = font_ui.render(p2_info, True, p2_color)
    dis.blit(p2_text, (DIS_WIDTH - 300, 15))

    # Zaman
    color_time = WHITE
    if remaining_time <= 10: color_time = RED
    mins, secs = divmod(int(remaining_time), 60)
    timer_str = '{:02d}:{:02d}'.format(mins, secs)

    center_info = f"SURE: {timer_str}  |  HIZ: {int(current_speed)}"
    time_text = font_ui.render(center_info, True, color_time)
    text_rect = time_text.get_rect(center=(DIS_WIDTH/2, 25))
    dis.blit(time_text, text_rect)

def create_random_item(snake1, snake2, other_items):
    """Yem veya Kalkan için koordinat üretir"""
    while True:
        rand_x = random.randrange(0, DIS_WIDTH - SNAKE_BLOCK)
        rand_y = random.randrange(50, DIS_HEIGHT - SNAKE_BLOCK)
        
        fx = round(rand_x / SNAKE_BLOCK) * SNAKE_BLOCK
        fy = round(rand_y / SNAKE_BLOCK) * SNAKE_BLOCK
        
        # Çakışma kontrolü
        snake1_coords = [[p[0], p[1]] for p in snake1]
        snake2_coords = [[p[0], p[1]] for p in snake2]
        other_item_coords = [[p[0], p[1]] for p in other_items]
        
        if ([fx, fy] not in snake1_coords and 
            [fx, fy] not in snake2_coords and 
            [fx, fy] not in other_item_coords):
            return [fx, fy]

def winner_screen(winner_name, winner_color, score):
    # Oyun bittiğinde döngüden çıkmak için logic. 
    # Menu sisteminde return kullanmak daha güvenlidir.
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

        info = font_ui.render("Tekrar Oynamak için [C] - Menü/Çıkış için [ESC]", True, WHITE)
        info_rect = info.get_rect(center=(DIS_WIDTH/2, DIS_HEIGHT - 100))
        dis.blit(info, info_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit() # Tüm programı kapat
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU" # Menüye dönmek için sinyal
                if event.key == pygame.K_c:
                    waiting = False
                    gameLoop() # Kendini tekrar çağırır (Recursive dikkat, ama basit oyunda sorun olmaz)
                    return "RESTART"
                
def draw_pause_screen():
    # Yarı saydam bir efekt veremesek de, ortaya şık bir kutu koyalım
    box_width, box_height = 600, 200
    box_x = (DIS_WIDTH - box_width) // 2
    box_y = (DIS_HEIGHT - box_height) // 2

    # Kutu Arka Planı (Koyu Lacivert)
    pygame.draw.rect(dis, (10, 10, 40), (box_x, box_y, box_width, box_height))
    # Kutu Çerçevesi (Beyaz)
    pygame.draw.rect(dis, WHITE, (box_x, box_y, box_width, box_height), 3)

    # "OYUN DURDURULDU" Yazısı
    title = font_big.render("DURAKLATILDI", True, RED)
    title_rect = title.get_rect(center=(DIS_WIDTH // 2, DIS_HEIGHT // 2 - 20))
    dis.blit(title, title_rect)

    # Devam etme bilgisi
    info = font_ui.render("Devam etmek için [P] - Çıkış için [ESC]", True, WHITE)
    info_rect = info.get_rect(center=(DIS_WIDTH // 2, DIS_HEIGHT // 2 + 50))
    dis.blit(info, info_rect)

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
    global dis
    dis = screen
    game_over = False
    start_ticks = pygame.time.get_ticks()

    # --- BAŞLANGIÇ KONUMLARI ---
    start_x1 = round((DIS_WIDTH / 4 * 3) / SNAKE_BLOCK) * SNAKE_BLOCK
    start_y1 = round((DIS_HEIGHT / 2) / SNAKE_BLOCK) * SNAKE_BLOCK
    
    start_x2 = round((DIS_WIDTH / 4) / SNAKE_BLOCK) * SNAKE_BLOCK
    start_y2 = round((DIS_HEIGHT / 2) / SNAKE_BLOCK) * SNAKE_BLOCK

    x1, y1 = int(start_x1), int(start_y1)
    x1_change, y1_change = 0, 0
    p1_dir = "LEFT"
    p1_next_dir = "LEFT" # Input Buffering için
    snake1_list = []
    length_of_snake1 = 5
    
    x2, y2 = int(start_x2), int(start_y2)
    x2_change, y2_change = 0, 0
    p2_dir = "RIGHT"
    p2_next_dir = "RIGHT" # Input Buffering için
    snake2_list = []
    length_of_snake2 = 5

    # --- KALKAN DEĞİŞKENLERİ ---
    p1_has_shield = False
    p1_shield_end_time = 0
    
    p2_has_shield = False
    p2_shield_end_time = 0

    foods = []
    shields = [] # Yerdeki kalkanlar listesi
    # Pause için değişkenler
    paused = False
    pause_start_time = 0

    # Başlangıç Yemleri
    for _ in range(2):
        foods.append(create_random_item(snake1_list, snake2_list, shields))

    while not game_over:
        current_time = pygame.time.get_ticks()
        seconds_passed = (current_time - start_ticks) / 1000
        remaining_time = GAME_DURATION - seconds_passed
        current_speed = START_SPEED + (int(seconds_passed) // SPEED_INCREASE_INTERVAL)

        # --- OYUN SONU KONTROLÜ ---
        if remaining_time <= 0:
            if length_of_snake1 > length_of_snake2:
                result = winner_screen("YESIL YILAN", GREEN, length_of_snake1)
            elif length_of_snake2 > length_of_snake1:
                result = winner_screen("KIRMIZI YILAN", RED, length_of_snake2)
            else:
                result = winner_screen("BERABERE!", WHITE, length_of_snake1)
            
            if result == "MENU": return # Menüye dön
            if result == "RESTART": return # Yeniden başladığı için bu fonksiyondan çık

        # --- EVENT HANDLING (GELİŞTİRİLMİŞ) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                return # Direkt çıkış
            if event.type == pygame.KEYDOWN:
                # Pause yakalama
                if event.key == pygame.K_p:
                    paused = not paused # True ise False, False ise True yap
                    
                    if paused:
                        # Duraklatma anındaki zamanı kaydet
                        pause_start_time = pygame.time.get_ticks()
                    else:
                        # Oyuna geri dönüldü:
                        # Geçen o boş süreyi başlangıç zamanına ekle ki süre azalmasın
                        pause_duration = pygame.time.get_ticks() - pause_start_time
                        start_ticks += pause_duration
                
                if event.key == pygame.K_ESCAPE:
                    game_over = True
                    return # Menüye dön
                
                # P1 Input Buffering
                if event.key == pygame.K_LEFT and p1_dir != "RIGHT": p1_next_dir = "LEFT"
                elif event.key == pygame.K_RIGHT and p1_dir != "LEFT": p1_next_dir = "RIGHT"
                elif event.key == pygame.K_UP and p1_dir != "DOWN": p1_next_dir = "UP"
                elif event.key == pygame.K_DOWN and p1_dir != "UP": p1_next_dir = "DOWN"
                
                # P2 Input Buffering
                if event.key == pygame.K_a and p2_dir != "RIGHT": p2_next_dir = "LEFT"
                elif event.key == pygame.K_d and p2_dir != "LEFT": p2_next_dir = "RIGHT"
                elif event.key == pygame.K_w and p2_dir != "DOWN": p2_next_dir = "UP"
                elif event.key == pygame.K_s and p2_dir != "UP": p2_next_dir = "DOWN"
        # Pause kontrolü
        if paused:
            draw_pause_screen() # Ekrana kutuyu çiz
            pygame.display.update() # Ekranı güncelle
            clock.tick(15) # İşlemciyi yormamak için döngüyü yavaşlat
            continue
        current_time = pygame.time.get_ticks()
        # --- HAREKET UYGULAMA (BUFFERED) ---
        # P1
        if p1_next_dir == "LEFT": x1_change = -SNAKE_BLOCK; y1_change = 0; p1_dir = "LEFT"
        elif p1_next_dir == "RIGHT": x1_change = SNAKE_BLOCK; y1_change = 0; p1_dir = "RIGHT"
        elif p1_next_dir == "UP": y1_change = -SNAKE_BLOCK; x1_change = 0; p1_dir = "UP"
        elif p1_next_dir == "DOWN": y1_change = SNAKE_BLOCK; x1_change = 0; p1_dir = "DOWN"
        
        # P2
        if p2_next_dir == "LEFT": x2_change = -SNAKE_BLOCK; y2_change = 0; p2_dir = "LEFT"
        elif p2_next_dir == "RIGHT": x2_change = SNAKE_BLOCK; y2_change = 0; p2_dir = "RIGHT"
        elif p2_next_dir == "UP": y2_change = -SNAKE_BLOCK; x2_change = 0; p2_dir = "UP"
        elif p2_next_dir == "DOWN": y2_change = SNAKE_BLOCK; x2_change = 0; p2_dir = "DOWN"

        x1 += x1_change; y1 += y1_change
        x2 += x2_change; y2 += y2_change

        # --- DUVAR WRAP ---
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

        # --- KALKAN SPAWN MANTIĞI ---
        # Ekranda kalkan yoksa ve şans (%0.5 frame başına) tutarsa kalkan üret
        if len(shields) == 0 and random.randint(0, 200) == 0:
            shields.append(create_random_item(snake1_list, snake2_list, foods))

        # --- EŞYALARI ÇİZ ---
        for food in foods:
            draw_apple(food[0], food[1])
        
        for shield in shields:
            draw_shield_item(shield[0], shield[1])

        # --- VÜCUT GÜNCELLEME ---
        snake1_head = [x1, y1]
        snake1_list.append(snake1_head)
        if len(snake1_list) > length_of_snake1: del snake1_list[0]

        snake2_head = [x2, y2]
        snake2_list.append(snake2_head)
        if len(snake2_list) > length_of_snake2: del snake2_list[0]

        # --- KALKAN SÜRESİ KONTROLÜ ---
        if p1_has_shield and current_time > p1_shield_end_time:
            p1_has_shield = False
        if p2_has_shield and current_time > p2_shield_end_time:
            p2_has_shield = False

        # --- ÇARPIŞMA VE KESME (MODİFİYE) ---
        # Kurbanın kalkanı varsa kesme işlemi yapılmaz!
        if not p2_has_shield:
            snake2_list, length_of_snake2 = handle_cut_robust(snake2_list, x1, y1, foods)
        if not p1_has_shield:
            snake1_list, length_of_snake1 = handle_cut_robust(snake1_list, x2, y2, foods)
        
        # Kendi kuyruğunu kesme durumunda kalkan korumaz (İsteğe bağlı, şimdilik korumasın dedik)
        snake1_list, length_of_snake1 = handle_cut_robust(snake1_list, x1, y1, foods)
        snake2_list, length_of_snake2 = handle_cut_robust(snake2_list, x2, y2, foods)

        # --- YILANLARI ÇİZ ---
        draw_snake_with_eyes(snake1_list, GREEN, p1_dir, p1_has_shield)
        draw_snake_with_eyes(snake2_list, RED, p2_dir, p2_has_shield)

        show_hud(length_of_snake1, length_of_snake2, remaining_time, current_speed, p1_has_shield, p2_has_shield)
        
        # --- YEM YEME KONTROLLERİ ---
        for food in foods[:]:
            if abs(x1 - food[0]) < 15 and abs(y1 - food[1]) < 15:
                length_of_snake1 += 1
                foods.remove(food)
                foods.append(create_random_item(snake1_list, snake2_list, shields))
            elif abs(x2 - food[0]) < 15 and abs(y2 - food[1]) < 15:
                length_of_snake2 += 1
                foods.remove(food)
                foods.append(create_random_item(snake1_list, snake2_list, shields))

        # --- KALKAN ALMA KONTROLLERİ ---
        for shield in shields[:]:
            # P1 Kalkanı alırsa
            if abs(x1 - shield[0]) < 15 and abs(y1 - shield[1]) < 15:
                p1_has_shield = True
                p1_shield_end_time = current_time + SHIELD_DURATION
                shields.remove(shield)
            # P2 Kalkanı alırsa
            elif abs(x2 - shield[0]) < 15 and abs(y2 - shield[1]) < 15:
                p2_has_shield = True
                p2_shield_end_time = current_time + SHIELD_DURATION
                shields.remove(shield)

        if len(foods) < 2:
             foods.append(create_random_item(snake1_list, snake2_list, shields))

        pygame.display.update()
        clock.tick(current_speed)

    pygame.quit()
    quit()

# # Bağımsız çalıştırma desteği
# if __name__ == "__main__":
#     gameLoop()