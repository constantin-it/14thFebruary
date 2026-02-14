import pygame
import random
import sys
import os

# Инициализация Pygame и миксера
pygame.init()
pygame.mixer.init()

# Константы
WIDTH, HEIGHT = 800, 400
FPS = 60

# Музыка победы
VICTORY_MUSIC = "motorbreath.mp3"
if not os.path.exists(VICTORY_MUSIC):
    # Если файла нет, можно попробовать найти любое другое mp3 в папке
    for file in os.listdir("."):
        if file.endswith(".mp3"):
            VICTORY_MUSIC = file
            break

# Цвета
METAL_BLACK = (10, 10, 10)
HEART_RED = (255, 0, 64)
THRASH_PINK = (255, 0, 255)
WHITE = (255, 255, 255)
GRAY = (68, 68, 68)
GOLD = (255, 215, 0)

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Love 'Em All: Тур примирения (Improved)")
clock = pygame.time.Clock()

# Шрифты
font_main = pygame.font.SysFont('Courier New', 24, bold=True)
font_ui = pygame.font.SysFont('Courier New', 18)
font_big = pygame.font.SysFont('Courier New', 48, bold=True)
font_quote = pygame.font.SysFont('Arial', 20, italic=True)

# Загрузка изображений
splash_img = None
if os.path.exists("metageth.png"):
    try:
        splash_img = pygame.image.load("metageth.png")
        splash_img = pygame.transform.scale(splash_img, (250, 150))
    except:
        pass

beer_img = None
if os.path.exists("beer.png"):
    try:
        beer_img = pygame.image.load("beer.png").convert_alpha()
        beer_img = pygame.transform.scale(beer_img, (30, 40))
    except:
        pass

pick_img = None
if os.path.exists("pick.png"):
    try:
        pick_img = pygame.image.load("pick.png").convert_alpha()
        pick_img = pygame.transform.scale(pick_img, (35, 35))
    except:
        pass

# Цитаты
JAMES_QUOTES = ["YEAH!", "BEER!", "LOVE!", "METALLICA!", "MASTER!"]
DAVE_QUOTES = ["MEGADETH!", "RIFFS!", "PEACE!", "HATE!", "LOVE!"]

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.life = 30
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 2)

class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 60

    def update(self):
        self.y -= 1
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            surf = font_quote.render(self.text, True, self.color)
            surface.blit(surf, (self.x, self.y))

class Player:
    def __init__(self, x, color, name, controls):
        self.rect = pygame.Rect(x, 300, 40, 60)
        self.color = color
        self.name = name
        self.vy = 0
        self.is_jumping = False
        self.is_sliding = False
        self.slide_timer = 0
        self.controls = controls # {'jump': K_a, 'slide': K_l}

    def update(self):
        # Гравитация и прыжок
        self.vy += 1
        self.rect.y += self.vy
        if self.rect.y > 300:
            self.rect.y = 300
            self.vy = 0
            self.is_jumping = False

        # Скольжение
        if self.is_sliding:
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.is_sliding = False
                self.rect.height = 60
                self.rect.y = 300
            else:
                self.rect.height = 30
                self.rect.y = 330

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        label = font_ui.render(self.name[0], True, WHITE)
        surface.blit(label, (self.rect.x + 15, self.rect.y - 20))

class Obstacle:
    def __init__(self, speed):
        self.type = random.choice(['ego', 'grudge'])
        self.speed = speed
        if self.type == 'ego':
            self.rect = pygame.Rect(WIDTH, 320, 30, 40)
            self.color = (255, 68, 68)
        else:
            self.rect = pygame.Rect(WIDTH, 250, 60, 20)
            self.color = THRASH_PINK

    def update(self):
        self.rect.x -= self.speed

    def draw(self, surface):
        if self.type == 'ego':
            if beer_img:
                surface.blit(beer_img, (self.rect.x, self.rect.y))
            else:
                # Резервный вариант, если картинка не загрузилась
                points = [
                    (self.rect.x, self.rect.y + self.rect.height),
                    (self.rect.x + self.rect.width // 2, self.rect.y),
                    (self.rect.x + self.rect.width, self.rect.y + self.rect.height)
                ]
                pygame.draw.polygon(surface, self.color, points)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

class Heart:
    def __init__(self, speed):
        self.rect = pygame.Rect(WIDTH, random.randint(200, 300), 35, 35)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

    def draw(self, surface):
        if pick_img:
            surface.blit(pick_img, (self.rect.x, self.rect.y))
        else:
            # Простое сердечко (резервный вариант)
            label = font_ui.render("❤️", True, HEART_RED)
            surface.blit(label, (self.rect.x, self.rect.y))

def show_menu(title, subtitle, btn_text):
    while True:
        screen.fill(METAL_BLACK)
        
        # Заголовок
        title_surf = font_big.render(title, True, HEART_RED)
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 50))
        
        # Картинка
        if splash_img:
            screen.blit(splash_img, (WIDTH//2 - 125, 110))
        
        # Подзаголовок
        sub_surf = font_ui.render(subtitle, True, WHITE)
        screen.blit(sub_surf, (WIDTH//2 - sub_surf.get_width()//2, 270 if splash_img else 150))
        
        # Подсказка по клавишам
        key_hint = font_ui.render("нажмите [ПРОБЕЛ] или [ENTER], чтобы играть", True, WHITE)
        screen.blit(key_hint, (WIDTH//2 - key_hint.get_width()//2, 295 if splash_img else 180))
        
        # Кнопка
        pygame.draw.rect(screen, HEART_RED, (WIDTH//2 - 100, 330 if splash_img else 250, 200, 40))
        btn_surf = font_main.render("ИГРАТЬ", True, WHITE)
        screen.blit(btn_surf, (WIDTH//2 - btn_surf.get_width()//2, 335 if splash_img else 255))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                btn_y = 330 if splash_img else 250
                if WIDTH//2 - 100 <= x <= WIDTH//2 + 100 and btn_y <= y <= btn_y + 40:
                    return

def main():
    show_menu("LOVE 'EM ALL", "Управляй Джеймсом [A] и Дейвом [L]", "ИГРАТЬ")
    
    james = Player(100, HEART_RED, "James", pygame.K_a)
    dave = Player(200, THRASH_PINK, "Dave", pygame.K_l)
    
    obstacles = []
    hearts = []
    particles = []
    texts = []
    
    score = 0
    health = 100
    thrash_value = 0
    speed = 5
    frame = 0

    running = True
    while running:
        screen.fill(METAL_BLACK)
        # Фон-градиент
        pygame.draw.rect(screen, (26, 0, 13), (0, 0, WIDTH, HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and not james.is_jumping:
                    james.vy = -15
                    james.is_jumping = True
                    # Искры при прыжке
                    for _ in range(10): particles.append(Particle(james.rect.centerx, james.rect.bottom, WHITE))
                if event.key == pygame.K_l and not dave.is_sliding:
                    dave.is_sliding = True
                    dave.slide_timer = 30
                    # Искры при скольжении
                    for _ in range(5): particles.append(Particle(dave.rect.centerx, dave.rect.bottom, THRASH_PINK))

        # Спавн
        frame += 1
        if frame % max(20, 80 - int(speed)) == 0:
            obstacles.append(Obstacle(speed))
        if frame % 150 == 0:
            hearts.append(Heart(speed))

        # Обновление
        james.update()
        dave.update()
        
        for p in particles[:]:
            p.update()
            if p.life <= 0: particles.remove(p)
            
        for t in texts[:]:
            t.update()
            if t.life <= 0: texts.remove(t)

        for obs in obstacles[:]:
            obs.update()
            
            # Разделение ответственности за препятствия:
            # Джеймс отвечает за "Эго" (шипы)
            # Дейв отвечает за "Обиды" (высокие блоки)
            hit_james = (obs.type == 'ego' and james.rect.colliderect(obs.rect))
            hit_dave = (obs.type == 'grudge' and dave.rect.colliderect(obs.rect))

            if hit_james or hit_dave:
                health -= 10
                # Искры при столкновении
                for _ in range(20): particles.append(Particle(obs.rect.centerx, obs.rect.centery, HEART_RED))
                obstacles.remove(obs)
                if health <= 0:
                    show_menu("ТУР ОКОНЧЕН", f"Счет: {int(score)}. Братство утеряно...", "ПОПРОБОВАТЬ СНОВА")
                    main()
                    return
            elif obs.rect.x < -100:
                obstacles.remove(obs)

        for h in hearts[:]:
            h.update()
            if james.rect.colliderect(h.rect):
                score += 100
                thrash_value += 10
                texts.append(FloatingText(james.rect.x, james.rect.y, random.choice(JAMES_QUOTES), WHITE))
                hearts.remove(h)
            elif dave.rect.colliderect(h.rect):
                score += 100
                thrash_value += 10
                texts.append(FloatingText(dave.rect.x, dave.rect.y, random.choice(DAVE_QUOTES), WHITE))
                hearts.remove(h)
            elif h.rect.x < -100:
                hearts.remove(h)
                
            if thrash_value >= 100:
                if os.path.exists(VICTORY_MUSIC):
                    try:
                        pygame.mixer.music.load(VICTORY_MUSIC)
                        pygame.mixer.music.set_volume(0.2) # Устанавливаем громкость на 20%
                        pygame.mixer.music.play(-1, 34.0) # Зацикливаем, начинаем с 34 сек
                    except:
                        pass
                show_menu("ПОБЕДА!", "Супергруппа сформирована! 🤘", "ИГРАТЬ ЕЩЕ")
                pygame.mixer.music.stop()
                main()
                return

        score += 0.1
        speed += 0.002 # Быстрее ускорение

        # Отрисовка
        pygame.draw.line(screen, GRAY, (0, 360), (WIDTH, 360), 2)
        james.draw(screen)
        dave.draw(screen)
        for obs in obstacles: obs.draw(screen)
        for h in hearts: h.draw(screen)
        for p in particles: p.draw(screen)
        for t in texts: t.draw(screen)

        # UI
        score_txt = font_ui.render(f"Очки: {int(score)}", True, WHITE)
        health_txt = font_ui.render(f"Братство: {health}%", True, WHITE)
        screen.blit(score_txt, (20, 20))
        screen.blit(health_txt, (WIDTH - 150, 20))

        # Трэш-метр
        pygame.draw.rect(screen, GRAY, (WIDTH//2 - 100, 20, 200, 20))
        pygame.draw.rect(screen, HEART_RED, (WIDTH//2 - 100, 20, min(200, thrash_value * 2), 20))
        thrash_lbl = font_ui.render("Трэш-метр примирения", True, WHITE)
        screen.blit(thrash_lbl, (WIDTH//2 - thrash_lbl.get_width()//2, 45))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
