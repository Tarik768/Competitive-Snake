import pygame
import sys
import os
import competitivesnake

pygame.init()
pygame.mixer.init() # Ses motorunu başlat

try:
    click_sfx = pygame.mixer.Sound("sounds/click.wav")
except:
    click_sfx = None
    print("Click sesi bulunamadı.")


infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Snake Menü')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_BUTTON = (0, 200, 0)
GREEN_HOVER = (0, 255, 0)
TEXT_COLOR = (240, 240, 240)

font = pygame.font.SysFont("bahnschrift", 50)
fontbig = pygame.font.SysFont("arial", 80, bold=True)

background_image_path = "arkaplan.jpg" 
bg_image = None

if os.path.exists(background_image_path):
    try:
        loaded_img = pygame.image.load(background_image_path)
        bg_image = pygame.transform.scale(loaded_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        print("Resim yüklenemedi, varsayılan renk kullanılacak.")

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def draw_key_icon(surface, text, x, y, width=60, height=60, color=(50, 50, 70)): # Ekrana klavye tuşu görünümlü kutucuk çizer
    key_rect = pygame.Rect(x, y, width, height)
    # Tuşun gövdesi
    pygame.draw.rect(surface, color, key_rect, border_radius=10)
    # Tuşun kenarlığı
    pygame.draw.rect(surface, (150, 150, 150), key_rect, 2, border_radius=10)
    # Harf
    draw_text(text, font, WHITE, surface, x + width // 2, y + height // 2)

def main_menu():
    while True:
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((20, 20, 40))

        mx, my = pygame.mouse.get_pos()
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        button_width = 350
        button_height = 70
        center_x = SCREEN_WIDTH // 2
        
        btn1_rect = pygame.Rect(center_x - button_width // 2, SCREEN_HEIGHT // 2 - 60, button_width, button_height)
        
        btn2_rect = pygame.Rect(center_x - button_width // 2, SCREEN_HEIGHT // 2 + 40, button_width, button_height)

        
        if btn1_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, GREEN_HOVER, btn1_rect, border_radius=15)
            if click:
                if click_sfx: click_sfx.play()
                try:
                    competitivesnake.gameLoop(screen)
                    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                except Exception as e:
                    print(f"Oyun hatası: {e}")
        else:
            pygame.draw.rect(screen, GREEN_BUTTON, btn1_rect, border_radius=15)
        
        if btn2_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, (0, 150, 200), btn2_rect, border_radius=15) # Buna Mavi ton verdik
            if click:
                if click_sfx: click_sfx.play() 
                controls_menu()
        else:
            pygame.draw.rect(screen, (0, 100, 150), btn2_rect, border_radius=15)

        draw_text('OYUNA BAŞLA', font, WHITE, screen, btn1_rect.centerx, btn1_rect.centery)
        draw_text('KONTROLLER', font, WHITE, screen, btn2_rect.centerx, btn2_rect.centery)
        
        draw_text('COMPETITIVE SNAKE', fontbig, (255, 215, 0), screen, center_x, SCREEN_HEIGHT // 2 - 180)
        
        draw_text('Çıkmak için [ESC]', pygame.font.SysFont("bahnschrift", 20), WHITE, screen, center_x, SCREEN_HEIGHT - 50)

        pygame.display.update()

def controls_menu():
    while True:
        if bg_image:
            screen.blit(bg_image, (0, 0))
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(220)
            s.fill((0,0,0))
            screen.blit(s, (0,0))
        else:
            screen.fill((20, 20, 40))

        mx, my = pygame.mouse.get_pos()
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        draw_text('KONTROLLER', fontbig, (255, 215, 0), screen, center_x, 80)

        line_start = (center_x, center_y - 140)
        line_end = (center_x, center_y + 80)
        pygame.draw.line(screen, (100, 100, 120), line_start, line_end, 2)

        p1_center_x = center_x + 280  
        p2_center_x = center_x - 280

        draw_text("YEŞİL YILAN", font, (50, 255, 80), screen, p1_center_x, center_y - 120)
        
        draw_key_icon(screen, "^", p1_center_x - 30, center_y - 60) # UP
        draw_key_icon(screen, "<", p1_center_x - 100, center_y + 10) # LEFT
        draw_key_icon(screen, "v", p1_center_x - 30, center_y + 10) # DOWN
        draw_key_icon(screen, ">", p1_center_x + 40, center_y + 10) # RIGHT

        draw_text("KIRMIZI YILAN", font, (255, 50, 50), screen, p2_center_x, center_y - 120)
        
        draw_key_icon(screen, "W", p2_center_x - 30, center_y - 60)
        draw_key_icon(screen, "A", p2_center_x - 100, center_y + 10)
        draw_key_icon(screen, "S", p2_center_x - 30, center_y + 10)
        draw_key_icon(screen, "D", p2_center_x + 40, center_y + 10)

        info_y = center_y + 150
        draw_text("GENEL", font, WHITE, screen, center_x, info_y)
        draw_text("[ P ] - Oyunu Duraklat", pygame.font.SysFont("bahnschrift", 25), WHITE, screen, center_x, info_y + 40)
        draw_text("[ ESC ] - Çıkış / Geri", pygame.font.SysFont("bahnschrift", 25), WHITE, screen, center_x, info_y + 70)

        btn_width = 200
        btn_height = 60
        back_btn_rect = pygame.Rect(center_x - btn_width // 2, SCREEN_HEIGHT - 100, btn_width, btn_height)

        if back_btn_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, GREEN_HOVER, back_btn_rect, border_radius=15)
            if click:
                if click_sfx: click_sfx.play()
                return
        else:
            pygame.draw.rect(screen, GREEN_BUTTON, back_btn_rect, border_radius=15)
        
        draw_text("GERİ", font, WHITE, screen, back_btn_rect.centerx, back_btn_rect.centery)

        # Event Loop
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        
        pygame.display.update()

if __name__ == "__main__":
    main_menu()
