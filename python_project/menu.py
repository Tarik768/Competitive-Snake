import pygame
import sys
import os
import competitivesnake # Oyun dosyası
from network import Network

from common import Game

pygame.init()
# --- SES BAŞLATMA (MIXER) ---
pygame.mixer.init()

# --- SABİT MANTIKSAL ÇÖZÜNÜRLÜK ---
LOGICAL_WIDTH = 1920
LOGICAL_HEIGHT = 1080
SCREEN_WIDTH = LOGICAL_WIDTH
SCREEN_HEIGHT = LOGICAL_HEIGHT

# --- AYAR DEĞİŞKENLERİ ---
IS_FULLSCREEN = False
CURRENT_RES_INDEX = 1
RESOLUTIONS = [
    (1920, 1080),
    (1366, 768),
    (1280, 720),
    (800, 600)
]
VOLUME_LEVEL = 0.5 

# --- MENÜ SESLERİNİ YÜKLE ---
click_sfx = None
try:
    if os.path.exists("sounds/click.wav"):
        click_sfx = pygame.mixer.Sound("sounds/click.wav")
        click_sfx.set_volume(VOLUME_LEVEL)
    else:
        print("click.wav bulunamadı.")
except Exception as e:
    print(f"Ses hatası: {e}")

# --- EKRAN BAŞLATMA ---
initial_res = RESOLUTIONS[CURRENT_RES_INDEX]
if IS_FULLSCREEN:
    screen = pygame.display.set_mode(initial_res, pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode(initial_res)

pygame.display.set_caption('Snake Menü')

virtual_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))

# --- RENKLER ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_BUTTON = (0, 200, 0)
GREEN_HOVER = (0, 255, 0)
PURPLE_BUTTON = (128, 0, 128)
PURPLE_HOVER = (150, 50, 150)
BLUE_BUTTON = (0, 100, 200)
ORANGE_BUTTON = (200, 100, 0)
COLOR_INACTIVE = (100, 100, 120)
COLOR_ACTIVE = (200, 200, 255)
TEXT_COLOR = (240, 240, 240)

font = pygame.font.SysFont("bahnschrift", 50)
fontbig = pygame.font.SysFont("arial", 80, bold=True)

background_image_path = "arkaplan.jpg" 
bg_image = None

if os.path.exists(background_image_path):
    try:
        loaded_img = pygame.image.load(background_image_path)
        bg_image = pygame.transform.scale(loaded_img, (LOGICAL_WIDTH, LOGICAL_HEIGHT))
    except:
        print("Resim yüklenemedi.")

# --- YARDIMCI FONKSİYONLAR ---

def update_window():
    global screen
    target_res = RESOLUTIONS[CURRENT_RES_INDEX]
    flags = pygame.FULLSCREEN if IS_FULLSCREEN else 0
    screen = pygame.display.set_mode(target_res, flags)

def get_virtual_mouse_pos():
    mx, my = pygame.mouse.get_pos()
    real_w, real_h = screen.get_size()
    scale_x = LOGICAL_WIDTH / real_w
    scale_y = LOGICAL_HEIGHT / real_h
    return mx * scale_x, my * scale_y

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def draw_key_icon(surface, text, x, y, width=60, height=60, color=(50, 50, 70)):
    key_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, color, key_rect, border_radius=10)
    pygame.draw.rect(surface, (150, 150, 150), key_rect, 2, border_radius=10)
    draw_text(text, font, WHITE, surface, x + width // 2, y + height // 2)

# --- MENÜ SAYFALARI ---

def main_menu():
    while True:
        if bg_image:
            virtual_surface.blit(bg_image, (0, 0))
        else:
            virtual_surface.fill((20, 20, 40))

        mx, my = get_virtual_mouse_pos()
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
                    # Tıklama sesi
                    if click_sfx: click_sfx.play()

        button_width = 350
        button_height = 70
        spacing = 20
        start_y = SCREEN_HEIGHT // 2 - 100
        center_x = SCREEN_WIDTH // 2
        
        btn_local_rect = pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height)
        btn_online_rect = pygame.Rect(center_x - button_width // 2, start_y + (button_height + spacing), button_width, button_height)
        btn_settings_rect = pygame.Rect(center_x - button_width // 2, start_y + (button_height + spacing) * 2, button_width, button_height)
        btn_controls_rect = pygame.Rect(center_x - button_width // 2, start_y + (button_height + spacing) * 3, button_width, button_height)

        # Yerel Oyun
        if btn_local_rect.collidepoint((mx, my)):
            pygame.draw.rect(virtual_surface, GREEN_HOVER, btn_local_rect, border_radius=15)
            if click:
                try:
                    # SES SEVİYESİNİ (VOLUME_LEVEL) GÖNDERİYORUZ
                    competitivesnake.gameLoop(screen, volume=VOLUME_LEVEL)
                    update_window()
                except Exception as e:
                    print(f"Hata: {e}")
        else:
            pygame.draw.rect(virtual_surface, GREEN_BUTTON, btn_local_rect, border_radius=15)
        draw_text('YEREL OYUN', font, WHITE, virtual_surface, btn_local_rect.centerx, btn_local_rect.centery)
        
        # Online Oyun
        if btn_online_rect.collidepoint((mx, my)):
            pygame.draw.rect(virtual_surface, PURPLE_HOVER, btn_online_rect, border_radius=15)
            if click:
                online_menu()
        else:
            pygame.draw.rect(virtual_surface, PURPLE_BUTTON, btn_online_rect, border_radius=15)
        draw_text('ONLINE OYUN', font, WHITE, virtual_surface, btn_online_rect.centerx, btn_online_rect.centery)

        # Ayarlar
        if btn_settings_rect.collidepoint((mx, my)):
            pygame.draw.rect(virtual_surface, (100, 100, 100), btn_settings_rect, border_radius=15)
            if click:
                settings_menu()
        else:
            pygame.draw.rect(virtual_surface, (70, 70, 70), btn_settings_rect, border_radius=15)
        draw_text('AYARLAR', font, WHITE, virtual_surface, btn_settings_rect.centerx, btn_settings_rect.centery)

        # Kontroller
        if btn_controls_rect.collidepoint((mx, my)):
            pygame.draw.rect(virtual_surface, (0, 150, 200), btn_controls_rect, border_radius=15)
            if click:
                controls_menu()
        else:
            pygame.draw.rect(virtual_surface, (0, 100, 150), btn_controls_rect, border_radius=15)
        draw_text('KONTROLLER', font, WHITE, virtual_surface, btn_controls_rect.centerx, btn_controls_rect.centery)

        draw_text('COMPETITIVE SNAKE', fontbig, (255, 215, 0), virtual_surface, center_x, SCREEN_HEIGHT // 2 - 250)
        draw_text('Çıkmak için [ESC]', pygame.font.SysFont("bahnschrift", 20), WHITE, virtual_surface, center_x, SCREEN_HEIGHT - 50)

        scaled_surface = pygame.transform.smoothscale(virtual_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.update()

def online_menu():
    user_text = ''
    input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 200, 200, 50)
    color_input = COLOR_INACTIVE
    active = False 
    status_msg = ""
    status_color = WHITE
    cursor_visible = True
    last_blink_time = pygame.time.get_ticks()
    CURSOR_BLINK_INTERVAL = 500

    while True:
        if bg_image:
            virtual_surface.blit(bg_image, (0, 0))
            s = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            s.set_alpha(200)
            s.fill((0,0,0))
            virtual_surface.blit(s, (0,0))
        else:
            virtual_surface.fill((20, 20, 40))

        mx, my = get_virtual_mouse_pos()
        click = False
        center_x = SCREEN_WIDTH // 2
        
        current_time = pygame.time.get_ticks()
        if current_time - last_blink_time > CURSOR_BLINK_INTERVAL:
            cursor_visible = not cursor_visible
            last_blink_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                    if click_sfx: click_sfx.play() # SES
                    if input_rect.collidepoint((mx, my)):
                        active = not active
                        cursor_visible = True
                        status_msg = "" 
                    else:
                        active = False
                    color_input = COLOR_ACTIVE if active else COLOR_INACTIVE

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        pass 
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        if event.unicode.isnumeric() and len(user_text) < 5:
                            user_text += event.unicode
                
                if event.key == pygame.K_ESCAPE:
                    return 

        draw_text('ONLINE LOBİ', fontbig, (255, 215, 0), virtual_surface, center_x, 80)
        
        if status_msg != "":
            draw_text(status_msg, font, status_color, virtual_surface, center_x, 140)

        draw_text('ODA ID (Sadece Katılmak İçin):', font, WHITE, virtual_surface, center_x, 170)
        
        pygame.draw.rect(virtual_surface, color_input, input_rect, 2, border_radius=5)
        text_surface = font.render(user_text, True, WHITE)
        virtual_surface.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))

        if active and cursor_visible:
            txt_width = text_surface.get_width()
            cursor_x = input_rect.x + 10 + txt_width
            pygame.draw.line(virtual_surface, WHITE, (cursor_x, input_rect.y + 10), (cursor_x, input_rect.y + 40), 2)

        btn_width, btn_height = 300, 80
        host_rect = pygame.Rect(center_x - btn_width // 2, 300, btn_width, btn_height)
        
        if host_rect.collidepoint((mx, my)):
            pygame.draw.rect(virtual_surface, (50, 150, 255), host_rect, border_radius=15)
            if click:
                status_msg = "Sunucuya bağlanılıyor..."
                status_color = WHITE
                scaled_surface = pygame.transform.smoothscale(virtual_surface, screen.get_size())
                screen.blit(scaled_surface, (0, 0))
                pygame.display.update()

                try:
                    n = Network("MAKE")
                    if n.p is not None:
                        status_msg = f"Oda ID: {n.game_id} - Bekleniyor..."
                        status_color = GREEN_HOVER
                        competitivesnake.online_game_loop(screen, n, volume=VOLUME_LEVEL)
                    else:
                        status_msg = "Sunucuya bağlanılamadı!"
                        status_color = (255, 50, 50)
                except Exception as e:
                    print(e)
                    status_msg = "Bağlantı Hatası!"
                    status_color = (255, 50, 50)
        else:
            pygame.draw.rect(virtual_surface, BLUE_BUTTON, host_rect, border_radius=15)
        
        draw_text("ODA KUR (HOST)", font, WHITE, virtual_surface, host_rect.centerx, host_rect.centery)

        join_rect = pygame.Rect(center_x - btn_width // 2, 400, btn_width, btn_height)
        
        if join_rect.collidepoint((mx, my)):
            pygame.draw.rect(virtual_surface, (255, 150, 50), join_rect, border_radius=15)
            if click:
                if len(user_text) < 1:
                    status_msg = "Lütfen bir Oda ID giriniz!"
                    status_color = (255, 50, 50)
                else:
                    status_msg = f"Odaya giriliyor: {user_text}..."
                    status_color = WHITE
                    scaled_surface = pygame.transform.smoothscale(virtual_surface, screen.get_size())
                    screen.blit(scaled_surface, (0, 0))
                    pygame.display.update()

                    try:
                        n = Network("JOIN", room_id=user_text)
                        if n.p is not None:
                            competitivesnake.online_game_loop(screen, n, volume=VOLUME_LEVEL)
                        else:
                            status_msg = "Oda bulunamadı veya dolu!"
                            status_color = (255, 50, 50)
                    except:
                        status_msg = "Sunucu Hatası!"
                        status_color = (255, 50, 50)
        else:
            pygame.draw.rect(virtual_surface, ORANGE_BUTTON, join_rect, border_radius=15)

        draw_text("ODAYA KATIL", font, WHITE, virtual_surface, join_rect.centerx, join_rect.centery)

        back_rect = pygame.Rect(center_x - 100, SCREEN_HEIGHT - 120, 200, 60)
        if back_rect.collidepoint((mx, my)):
            pygame.draw.rect(virtual_surface, GREEN_HOVER, back_rect, border_radius=15)
            if click:
                return
        else:
            pygame.draw.rect(virtual_surface, GREEN_BUTTON, back_rect, border_radius=15)
        
        draw_text("GERİ", font, WHITE, virtual_surface, back_rect.centerx, back_rect.centery)

        scaled_surface = pygame.transform.smoothscale(virtual_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.update()


def settings_menu():
    global IS_FULLSCREEN, CURRENT_RES_INDEX, VOLUME_LEVEL
    slider_width = 300
    dragging_slider = False

    while True:
        if bg_image:
            virtual_surface.blit(bg_image, (0, 0))
            s = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            s.set_alpha(200)
            s.fill((0,0,0))
            virtual_surface.blit(s, (0,0))
        else:
            virtual_surface.fill((20, 20, 40))

        mx, my = get_virtual_mouse_pos()
        click = False
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

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
                    slider_rect = pygame.Rect(center_x - slider_width // 2, center_y + 80, slider_width, 30)
                    if slider_rect.collidepoint((mx, my)):
                        dragging_slider = True
                    else:
                        # Slider dışındaki tıklamalar için ses
                        if click_sfx: click_sfx.play()

            if event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False

        if dragging_slider:
            slider_start_x = center_x - slider_width // 2
            rel_x = mx - slider_start_x
            VOLUME_LEVEL = rel_x / slider_width
            if VOLUME_LEVEL < 0: VOLUME_LEVEL = 0
            if VOLUME_LEVEL > 1: VOLUME_LEVEL = 1
            
            # --- SES SEVİYESİNİ CANLI GÜNCELLE ---
            if click_sfx:
                click_sfx.set_volume(VOLUME_LEVEL)

        draw_text('AYARLAR', fontbig, (255, 215, 0), virtual_surface, center_x, 80)

        # Tam Ekran
        draw_text('Tam Ekran:', font, WHITE, virtual_surface, center_x - 100, center_y - 100)
        checkbox_rect = pygame.Rect(center_x + 50, center_y - 120, 40, 40)
        pygame.draw.rect(virtual_surface, WHITE, checkbox_rect, 2)
        if IS_FULLSCREEN:
            pygame.draw.rect(virtual_surface, GREEN_BUTTON, checkbox_rect.inflate(-10, -10))
        
        if checkbox_rect.collidepoint((mx, my)):
            if click:
                IS_FULLSCREEN = not IS_FULLSCREEN
                update_window()

        # Çözünürlük
        draw_text('Çözünürlük:', font, WHITE, virtual_surface, center_x - 100, center_y - 20)
        
        left_arrow = pygame.Rect(center_x + 20, center_y - 40, 40, 40)
        draw_text('<', font, WHITE, virtual_surface, left_arrow.centerx, left_arrow.centery)
        if left_arrow.collidepoint((mx, my)) and click:
            CURRENT_RES_INDEX -= 1
            if CURRENT_RES_INDEX < 0: CURRENT_RES_INDEX = len(RESOLUTIONS) - 1
            update_window()

        res_text = f"{RESOLUTIONS[CURRENT_RES_INDEX][0]} x {RESOLUTIONS[CURRENT_RES_INDEX][1]}"
        draw_text(res_text, font, (200, 200, 255), virtual_surface, center_x + 130, center_y - 20)

        right_arrow = pygame.Rect(center_x + 200, center_y - 40, 40, 40)
        draw_text('>', font, WHITE, virtual_surface, right_arrow.centerx, right_arrow.centery)
        if right_arrow.collidepoint((mx, my)) and click:
            CURRENT_RES_INDEX += 1
            if CURRENT_RES_INDEX >= len(RESOLUTIONS): CURRENT_RES_INDEX = 0
            update_window()

        # Ses Slider
        draw_text(f'Ses Seviyesi: %{int(VOLUME_LEVEL * 100)}', font, WHITE, virtual_surface, center_x, center_y + 40)
        bar_rect = pygame.Rect(center_x - slider_width // 2, center_y + 90, slider_width, 6)
        pygame.draw.rect(virtual_surface, (100, 100, 100), bar_rect, border_radius=3)
        
        fill_width = int(slider_width * VOLUME_LEVEL)
        fill_rect = pygame.Rect(center_x - slider_width // 2, center_y + 90, fill_width, 6)
        pygame.draw.rect(virtual_surface, GREEN_BUTTON, fill_rect, border_radius=3)
        
        handle_x = (center_x - slider_width // 2) + fill_width
        pygame.draw.circle(virtual_surface, WHITE, (handle_x, center_y + 93), 10)

        back_rect = pygame.Rect(center_x - 100, SCREEN_HEIGHT - 100, 200, 60)
        if back_rect.collidepoint((mx, my)):
            pygame.draw.rect(virtual_surface, GREEN_HOVER, back_rect, border_radius=15)
            if click: return
        else:
            pygame.draw.rect(virtual_surface, GREEN_BUTTON, back_rect, border_radius=15)
        draw_text("GERİ", font, WHITE, virtual_surface, back_rect.centerx, back_rect.centery)

        scaled_surface = pygame.transform.smoothscale(virtual_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.update()

def controls_menu():
    while True:
        mx, my = get_virtual_mouse_pos()
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
                    if click_sfx: click_sfx.play() # SES

        if bg_image:
            virtual_surface.blit(bg_image, (0, 0))
            s = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            s.set_alpha(220)
            s.fill((0,0,0))
            virtual_surface.blit(s, (0,0))
        else:
            virtual_surface.fill((20, 20, 40))

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        draw_text('KONTROLLER', fontbig, (255, 215, 0), virtual_surface, center_x, 80)
        line_start = (center_x, center_y - 140)
        line_end = (center_x, center_y + 80)
        pygame.draw.line(virtual_surface, (100, 100, 120), line_start, line_end, 2)

        p1_center_x = center_x + 280  
        p2_center_x = center_x - 280

        draw_text("YEŞİL YILAN", font, (50, 255, 80), virtual_surface, p1_center_x, center_y - 120)
        draw_key_icon(virtual_surface, "^", p1_center_x - 30, center_y - 60)
        draw_key_icon(virtual_surface, "<", p1_center_x - 100, center_y + 10)
        draw_key_icon(virtual_surface, "v", p1_center_x - 30, center_y + 10)
        draw_key_icon(virtual_surface, ">", p1_center_x + 40, center_y + 10)

        draw_text("KIRMIZI YILAN", font, (255, 50, 50), virtual_surface, p2_center_x, center_y - 120)
        draw_key_icon(virtual_surface, "W", p2_center_x - 30, center_y - 60)
        draw_key_icon(virtual_surface, "A", p2_center_x - 100, center_y + 10)
        draw_key_icon(virtual_surface, "S", p2_center_x - 30, center_y + 10)
        draw_key_icon(virtual_surface, "D", p2_center_x + 40, center_y + 10)

        info_y = center_y + 150
        draw_text("GENEL", font, WHITE, virtual_surface, center_x, info_y)
        draw_text("[ P ] - Oyunu Duraklat", pygame.font.SysFont("bahnschrift", 25), WHITE, virtual_surface, center_x, info_y + 40)
        draw_text("[ ESC ] - Çıkış / Geri", pygame.font.SysFont("bahnschrift", 25), WHITE, virtual_surface, center_x, info_y + 70)

        back_btn_rect = pygame.Rect(center_x - 100, SCREEN_HEIGHT - 100, 200, 60)
        
        if back_btn_rect.collidepoint((mx, my)):
            pygame.draw.rect(virtual_surface, GREEN_HOVER, back_btn_rect, border_radius=15)
            if click: 
                return
        else:
            pygame.draw.rect(virtual_surface, GREEN_BUTTON, back_btn_rect, border_radius=15)
            
        draw_text("GERİ", font, WHITE, virtual_surface, back_btn_rect.centerx, back_btn_rect.centery)
        
        scaled_surface = pygame.transform.smoothscale(virtual_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.update()

        
if __name__ == "__main__":
    main_menu()