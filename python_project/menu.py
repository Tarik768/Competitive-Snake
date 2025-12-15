import pygame
import sys
import os
import competitivesnake # Senin kaydettiğin oyun dosyası (aynı klasörde olmalı)

pygame.init()

# --- EKRAN AYARLARI ---
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Snake Menü')

# --- RENKLER ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_BUTTON = (0, 200, 0)
GREEN_HOVER = (0, 255, 0)
TEXT_COLOR = (240, 240, 240)
PURPLE_BUTTON = (128, 0, 128)
PURPLE_HOVER = (150, 50, 150)
COLOR_INACTIVE = (100, 100, 120) # Tıklanmamış kutu rengi
COLOR_ACTIVE = (200, 200, 255)   # Tıklanmış kutu rengi
BLUE_BUTTON = (0, 100, 200)      # Host butonu
ORANGE_BUTTON = (200, 100, 0)    # Join butonu

# --- AYAR DEĞİŞKENLERİ ---
IS_FULLSCREEN = True
CURRENT_RES_INDEX = 0
RESOLUTIONS = [
    (1920, 1080),
    (1366, 768),
    (1280, 720),
    (800, 600)
]
# Başlangıçta ekran boyutuna en uygun olanı seçmeye çalışabiliriz ama şimdilik varsayılan 0
VOLUME_LEVEL = 0.5 # 0.0 ile 1.0 arasında ses seviyesi



# --- FONT ---
font = pygame.font.SysFont("bahnschrift", 50)
fontbig = pygame.font.SysFont("arial", 80, bold=True)

# --- ARKA PLAN RESMİ AYARI ---
# Buraya resminin adını yaz (Örn: "background.jpg"). 
# Resim dosyası kodla aynı klasörde olmalı.
background_image_path = "arkaplan.jpg" 
bg_image = None

# Resim varsa yükle, yoksa hata verme devam et
if os.path.exists(background_image_path):
    try:
        loaded_img = pygame.image.load(background_image_path)
        # Resmi ekran boyutuna ölçekle
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

def update_window():
    global screen, bg_image, SCREEN_WIDTH, SCREEN_HEIGHT
    
    target_res = RESOLUTIONS[CURRENT_RES_INDEX]
    SCREEN_WIDTH, SCREEN_HEIGHT = target_res
    
    flags = pygame.FULLSCREEN if IS_FULLSCREEN else 0
    screen = pygame.display.set_mode(target_res, flags)
    
    # Arka planı yeni boyuta göre yeniden ölçekle
    if os.path.exists(background_image_path):
        try:
            loaded_img = pygame.image.load(background_image_path)
            bg_image = pygame.transform.scale(loaded_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            pass

def main_menu():
    while True:
        # 1. Arka Plan
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((20, 20, 40))

        mx, my = pygame.mouse.get_pos()
        click = False 

        # Event Loop
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

        # --- BUTON AYARLARI ---
        button_width = 350
        button_height = 60 # Yükseklikleri biraz azalttık sığması için
        spacing = 20       # Aralarındaki boşluk
        start_y = SCREEN_HEIGHT // 2 - 100
        center_x = SCREEN_WIDTH // 2
        
        # Butonlar Listesi (Rect oluşturma)
        btn_local_rect = pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height)
        btn_online_rect = pygame.Rect(center_x - button_width // 2, start_y + (button_height + spacing), button_width, button_height)
        btn_settings_rect = pygame.Rect(center_x - button_width // 2, start_y + (button_height + spacing) * 2, button_width, button_height)
        btn_controls_rect = pygame.Rect(center_x - button_width // 2, start_y + (button_height + spacing) * 3, button_width, button_height)

        # --- 1. YEREL OYUN ---
        if btn_local_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, GREEN_HOVER, btn_local_rect, border_radius=15)
            if click:
                try:
                    competitivesnake.gameLoop(screen)
                    # Oyun bitince pencere ayarlarını koru (Çünkü oyun içinde değişmiş olabilir)
                    update_window() 
                except Exception as e:
                    print(f"Oyun hatası: {e}")
        else:
            pygame.draw.rect(screen, GREEN_BUTTON, btn_local_rect, border_radius=15)
        draw_text('YEREL OYUN', font, WHITE, screen, btn_local_rect.centerx, btn_local_rect.centery)

        # --- 2. ONLINE OYUN ---
        if btn_online_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, PURPLE_HOVER, btn_online_rect, border_radius=15)
            if click:
                online_menu()
        else:
            pygame.draw.rect(screen, PURPLE_BUTTON, btn_online_rect, border_radius=15)
        draw_text('ONLINE OYUN', font, WHITE, screen, btn_online_rect.centerx, btn_online_rect.centery)

        # --- 3. AYARLAR (YENİ) ---
        if btn_settings_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, (100, 100, 100), btn_settings_rect, border_radius=15) # Gri ton
            if click:
                settings_menu()
        else:
            pygame.draw.rect(screen, (70, 70, 70), btn_settings_rect, border_radius=15)
        draw_text('AYARLAR', font, WHITE, screen, btn_settings_rect.centerx, btn_settings_rect.centery)

        # --- 4. KONTROLLER ---
        if btn_controls_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, (0, 150, 200), btn_controls_rect, border_radius=15)
            if click:
                controls_menu()
        else:
            pygame.draw.rect(screen, (0, 100, 150), btn_controls_rect, border_radius=15)
        draw_text('KONTROLLER', font, WHITE, screen, btn_controls_rect.centerx, btn_controls_rect.centery)

        # Başlık (Biraz daha yukarı taşıdık)
        draw_text('COMPETITIVE SNAKE', fontbig, (255, 215, 0), screen, center_x, SCREEN_HEIGHT // 2 - 220)
        
        # Alt Bilgi
        draw_text('Çıkmak için [ESC]', pygame.font.SysFont("bahnschrift", 20), WHITE, screen, center_x, SCREEN_HEIGHT - 50)

        pygame.display.update()

def controls_menu(): # Kontrollerin gösterildiği ekran
    while True:
        # Arkaplan ve karartma
        if bg_image:
            screen.blit(bg_image, (0, 0))
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(220) # Biraz daha koyu yaptım okunurluk için
            s.fill((0,0,0))
            screen.blit(s, (0,0))
        else:
            screen.fill((20, 20, 40))

        mx, my = pygame.mouse.get_pos()
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # --- BAŞLIK ---
        draw_text('KONTROLLER', fontbig, (255, 215, 0), screen, center_x, 80)

        # --- AYRAÇ ÇİZGİSİ ---
        # Ekranın tam ortasına dikey çizgi (Başlık altından tuşların altına kadar)
        line_start = (center_x, center_y - 140)
        line_end = (center_x, center_y + 80)
        pygame.draw.line(screen, (100, 100, 120), line_start, line_end, 2)

        # --- KONUMLANDIRMA AYARLARI ---
        # Mesafeyi açmak için 200 yerine 280 kullandık
        p1_center_x = center_x + 280  
        p2_center_x = center_x - 280

        # --- OYUNCU 1 (YEŞİL - SAĞ) ---
        draw_text("YEŞİL YILAN", font, (50, 255, 80), screen, p1_center_x, center_y - 120)
        
        # Yön Tuşları (Konumlar p1_center_x'e göre ayarlı)
        draw_key_icon(screen, "^", p1_center_x - 30, center_y - 60) # UP
        draw_key_icon(screen, "<", p1_center_x - 100, center_y + 10) # LEFT
        draw_key_icon(screen, "v", p1_center_x - 30, center_y + 10) # DOWN
        draw_key_icon(screen, ">", p1_center_x + 40, center_y + 10) # RIGHT

        # --- OYUNCU 2 (KIRMIZI - SOL) ---
        draw_text("KIRMIZI YILAN", font, (255, 50, 50), screen, p2_center_x, center_y - 120)
        
        # WASD Tuşları (Konumlar p2_center_x'e göre ayarlı)
        draw_key_icon(screen, "W", p2_center_x - 30, center_y - 60)
        draw_key_icon(screen, "A", p2_center_x - 100, center_y + 10)
        draw_key_icon(screen, "S", p2_center_x - 30, center_y + 10)
        draw_key_icon(screen, "D", p2_center_x + 40, center_y + 10)

        # --- GENEL BİLGİLER ---
        info_y = center_y + 150
        draw_text("GENEL", font, WHITE, screen, center_x, info_y)
        draw_text("[ P ] - Oyunu Duraklat", pygame.font.SysFont("bahnschrift", 25), WHITE, screen, center_x, info_y + 40)
        draw_text("[ ESC ] - Çıkış / Geri", pygame.font.SysFont("bahnschrift", 25), WHITE, screen, center_x, info_y + 70)

        # --- GERİ BUTONU (ALT ORTA) ---
        btn_width = 200
        btn_height = 60
        # Ekranın en altından 100 piksel yukarıda, ortalanmış
        back_btn_rect = pygame.Rect(center_x - btn_width // 2, SCREEN_HEIGHT - 100, btn_width, btn_height)

        if back_btn_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, GREEN_HOVER, back_btn_rect, border_radius=15)
            if click:
                return # Ana menüye dön
        else:
            pygame.draw.rect(screen, GREEN_BUTTON, back_btn_rect, border_radius=15)
        
        # Buton yazısını ortala
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

def online_menu():
    # --- GİRİŞ KUTUSU DEĞİŞKENLERİ ---
    user_text = 'Oyuncu 1' 
    input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 180, 200, 50)
    color_input = COLOR_INACTIVE
    active = False 

    # --- İMLEÇ (CURSOR) DEĞİŞKENLERİ --- # YENİ EKLENDİ
    cursor_visible = True
    last_blink_time = pygame.time.get_ticks()
    CURSOR_BLINK_INTERVAL = 500 # 500ms (Yarım saniye)

    while True:
        # Arkaplan
        if bg_image:
            screen.blit(bg_image, (0, 0))
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(200)
            s.fill((0,0,0))
            screen.blit(s, (0,0))
        else:
            screen.fill((20, 20, 40))

        mx, my = pygame.mouse.get_pos()
        click = False
        center_x = SCREEN_WIDTH // 2
        
        # --- ZAMAN GÜNCELLEMESİ --- # YENİ EKLENDİ
        current_time = pygame.time.get_ticks()
        if current_time - last_blink_time > CURSOR_BLINK_INTERVAL:
            cursor_visible = not cursor_visible # Görünürlüğü tersine çevir
            last_blink_time = current_time

        # --- EVENT LOOP ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                    if input_rect.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color_input = COLOR_ACTIVE if active else COLOR_INACTIVE
                    # Tıklandığı an imleci görünür yap ki kullanıcı tepkiyi hemen görsün
                    cursor_visible = True 

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        active = False 
                        color_input = COLOR_INACTIVE
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        if len(user_text) < 12:
                            user_text += event.unicode
                
                if event.key == pygame.K_ESCAPE:
                    return 

        # --- BAŞLIK ---
        draw_text('ONLINE LOBİ', fontbig, (255, 215, 0), screen, center_x, 80)

        # --- İSİM GİRME ALANI ---
        draw_text('İSİM GİRİNİZ:', font, WHITE, screen, center_x, 150)
        
        # Kutuyu çiz
        pygame.draw.rect(screen, color_input, input_rect, 2, border_radius=5)
        
        # Metni çiz
        text_surface = font.render(user_text, True, WHITE)
        screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))

        # --- İMLEÇ ÇİZİMİ --- # YENİ EKLENDİ
        # Sadece kutu aktifse ve zamanlayıcı 'görünür' diyorsa çiz
        if active and cursor_visible:
            # Metnin genişliğini al ki imleci metnin sonuna koyabilelim
            txt_width = text_surface.get_width()
            cursor_x = input_rect.x + 10 + txt_width
            # Dikey çizgi çiz
            pygame.draw.line(screen, WHITE, (cursor_x, input_rect.y + 10), (cursor_x, input_rect.y + 40), 2)

        # --- BUTONLAR ---
        btn_width, btn_height = 300, 80
        
        # 1. ODA KUR (HOST)
        host_rect = pygame.Rect(center_x - btn_width // 2, 300, btn_width, btn_height)
        if host_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, (50, 150, 255), host_rect, border_radius=15)
            if click:
                print(f"HOST MODU BAŞLATILIYOR... İsim: {user_text}")
        else:
            pygame.draw.rect(screen, BLUE_BUTTON, host_rect, border_radius=15)
        draw_text("ODA KUR (HOST)", font, WHITE, screen, host_rect.centerx, host_rect.centery)

        # 2. ODAYA KATIL (JOIN)
        join_rect = pygame.Rect(center_x - btn_width // 2, 400, btn_width, btn_height)
        if join_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, (255, 150, 50), join_rect, border_radius=15)
            if click:
                print(f"JOIN MODU SEÇİLDİ... İsim: {user_text}")
        else:
            pygame.draw.rect(screen, ORANGE_BUTTON, join_rect, border_radius=15)
        draw_text("ODAYA KATIL", font, WHITE, screen, join_rect.centerx, join_rect.centery)

        # --- GERİ BUTONU ---
        back_rect = pygame.Rect(center_x - 100, SCREEN_HEIGHT - 120, 200, 60)
        if back_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, GREEN_HOVER, back_rect, border_radius=15)
            if click:
                return
        else:
            pygame.draw.rect(screen, GREEN_BUTTON, back_rect, border_radius=15)
        draw_text("GERİ", font, WHITE, screen, back_rect.centerx, back_rect.centery)

        pygame.display.update()

def settings_menu():
    global IS_FULLSCREEN, CURRENT_RES_INDEX, VOLUME_LEVEL
    
    # Slider Ayarları
    slider_width = 300
    slider_height = 10
    dragging_slider = False

    while True:
        # Arkaplan
        if bg_image:
            screen.blit(bg_image, (0, 0))
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(200)
            s.fill((0,0,0))
            screen.blit(s, (0,0))
        else:
            screen.fill((20, 20, 40))

        mx, my = pygame.mouse.get_pos()
        click = False
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return # Geri dön
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                    # Slider tıklama kontrolü
                    slider_rect = pygame.Rect(center_x - slider_width // 2, center_y + 80, slider_width, 30)
                    if slider_rect.collidepoint((mx, my)):
                        dragging_slider = True
            if event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False

        # Slider sürükleme mantığı
        if dragging_slider:
            slider_start_x = center_x - slider_width // 2
            # Mouse pozisyonunu 0 ile 1 arasına normalize et
            rel_x = mx - slider_start_x
            VOLUME_LEVEL = rel_x / slider_width
            # Sınırla (0 ile 1 arasında kalsın)
            if VOLUME_LEVEL < 0: VOLUME_LEVEL = 0
            if VOLUME_LEVEL > 1: VOLUME_LEVEL = 1

        # --- BAŞLIK ---
        draw_text('AYARLAR', fontbig, (255, 215, 0), screen, center_x, 80)

        # --- 1. TAM EKRAN (CHECKBOX) ---
        draw_text('Tam Ekran:', font, WHITE, screen, center_x - 100, center_y - 100)
        checkbox_rect = pygame.Rect(center_x + 50, center_y - 120, 40, 40)
        
        pygame.draw.rect(screen, WHITE, checkbox_rect, 2)
        if IS_FULLSCREEN:
            # İçine tik at (küçük bir kare ile)
            pygame.draw.rect(screen, GREEN_BUTTON, checkbox_rect.inflate(-10, -10))
        
        if checkbox_rect.collidepoint((mx, my)):
            if click:
                IS_FULLSCREEN = not IS_FULLSCREEN
                update_window() # Anlık uygula

        # --- 2. ÇÖZÜNÜRLÜK (SELECTOR) ---
        draw_text('Çözünürlük:', font, WHITE, screen, center_x - 100, center_y - 20)
        
        # Sol Ok
        left_arrow = pygame.Rect(center_x + 20, center_y - 40, 40, 40)
        draw_text('<', font, WHITE, screen, left_arrow.centerx, left_arrow.centery)
        if left_arrow.collidepoint((mx, my)) and click:
            CURRENT_RES_INDEX -= 1
            if CURRENT_RES_INDEX < 0: CURRENT_RES_INDEX = len(RESOLUTIONS) - 1
            update_window() # Değiştir ve uygula

        # Değer
        res_text = f"{RESOLUTIONS[CURRENT_RES_INDEX][0]} x {RESOLUTIONS[CURRENT_RES_INDEX][1]}"
        draw_text(res_text, font, (200, 200, 255), screen, center_x + 130, center_y - 20)

        # Sağ Ok
        right_arrow = pygame.Rect(center_x + 200, center_y - 40, 40, 40)
        draw_text('>', font, WHITE, screen, right_arrow.centerx, right_arrow.centery)
        if right_arrow.collidepoint((mx, my)) and click:
            CURRENT_RES_INDEX += 1
            if CURRENT_RES_INDEX >= len(RESOLUTIONS): CURRENT_RES_INDEX = 0
            update_window() # Değiştir ve uygula

        # --- 3. SES AYARI (SLIDER) ---
        draw_text(f'Ses Seviyesi: %{int(VOLUME_LEVEL * 100)}', font, WHITE, screen, center_x, center_y + 40)
        
        # Çizgi (Barın arkası)
        bar_rect = pygame.Rect(center_x - slider_width // 2, center_y + 90, slider_width, 6)
        pygame.draw.rect(screen, (100, 100, 100), bar_rect, border_radius=3)
        
        # Doluluk oranı (Renkli kısım)
        fill_width = int(slider_width * VOLUME_LEVEL)
        fill_rect = pygame.Rect(center_x - slider_width // 2, center_y + 90, fill_width, 6)
        pygame.draw.rect(screen, GREEN_BUTTON, fill_rect, border_radius=3)

        # Tutamaç (Handle - Yuvarlak)
        handle_x = (center_x - slider_width // 2) + fill_width
        pygame.draw.circle(screen, WHITE, (handle_x, center_y + 93), 10)


        # --- GERİ BUTONU ---
        back_rect = pygame.Rect(center_x - 100, SCREEN_HEIGHT - 100, 200, 60)
        if back_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, GREEN_HOVER, back_rect, border_radius=15)
            if click:
                return
        else:
            pygame.draw.rect(screen, GREEN_BUTTON, back_rect, border_radius=15)
        
        draw_text("GERİ", font, WHITE, screen, back_rect.centerx, back_rect.centery)

        pygame.display.update()

# Menüyü başlat
if __name__ == "__main__":
    main_menu()
