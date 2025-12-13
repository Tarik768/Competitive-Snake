import pygame
import sys
import os
import competitivesnake  # Senin kaydettiğin oyun dosyası (aynı klasörde olmalı)

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

# --- FONT ---
font = pygame.font.SysFont("bahnschrift", 50)

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

def main_menu():
    while True:
        # 1. Arka Plan Çizimi
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((20, 20, 40)) # Resim yoksa koyu lacivert yap

        # 2. Fare Konumunu Al
        mx, my = pygame.mouse.get_pos()

        # 3. Buton Tanımlama (Ekranın tam ortası)
        button_width = 300
        button_height = 80
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = SCREEN_HEIGHT // 2 - button_height // 2
        
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # 4. Buton Etkileşimi (Hover ve Tıklama)
        if button_rect.collidepoint((mx, my)):
            # Fare üzerindeyse daha parlak yeşil yap
            pygame.draw.rect(screen, GREEN_HOVER, button_rect, border_radius=15)
            if click:
                # OYUNU BAŞLAT
                try:
                    competitivesnake.gameLoop() # Diğer dosyadaki fonksiyonu çağırıyoruz
                    # Oyun bitip buraya dönerse ekranı tekrar kendine göre ayarlasın
                    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                except Exception as e:
                    print(f"Oyun başlatılırken hata: {e}")
        else:
            # Fare üzerinde değilse normal yeşil
            pygame.draw.rect(screen, GREEN_BUTTON, button_rect, border_radius=15)

        # 5. Yazıları Çiz
        # Buton üzerindeki yazı
        draw_text('OYUNA BAŞLA', font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Başlık yazısı (Butonun üstünde)
        draw_text('COMPETITIVE SNAKE', font, (255, 215, 0), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150)
        
        # Çıkış bilgisi
        draw_text('Çıkmak için ESC', pygame.font.SysFont("bahnschrift", 20), WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

        # 6. Olay Döngüsü (Event Loop)
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

        pygame.display.update()

# Menüyü başlat
if __name__ == "__main__":
    main_menu()