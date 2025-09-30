import pygame, sys, random, time

pygame.init()

# Ekrāns un HUD
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 900
HUD_HEIGHT = 60
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man Style Game")

FPS = 60
CLOCK = pygame.time.Clock()

# Krāsas
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)

font = pygame.font.SysFont("Arial", 25)

# Lielāka karte: 1 = siena, 0 = ceļš
MAP = [
    "1111111111111111111111111",
    "1000000000000010000000001",
    "1011111111111011101111101",
    "1010000000001000000000101",
    "1010111110111111011110101",
    "1000100000000000000010001",
    "1001101111110111111011101",
    "1000001000000000001000001",
    "1011111011110111111011101",
    "1000000000000001000000001",
    "1111111111111111111111111"
]

ROWS = len(MAP)
COLS = len(MAP[0])
TILE = min(SCREEN_WIDTH // COLS, (SCREEN_HEIGHT - HUD_HEIGHT) // ROWS)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(TILE + TILE // 2, HUD_HEIGHT + TILE * 5 + TILE // 2, TILE - 10, TILE - 10)
        self.speed = 8
    # ... pārējās metodes ...

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE - 10, TILE - 10)
        self.speed = 4
    # ... pārējās metodes ...

# Player sākuma pozīcija (uz ceļa, nevis sienas)
player = Player()
player.rect.center = (TILE * 12, HUD_HEIGHT + TILE * 9)

# Enemy sākuma pozīcijas (divās dažādās vietās)
enemies = [
    Enemy(TILE * 2, HUD_HEIGHT + TILE * 1),
    Enemy(TILE * 22, HUD_HEIGHT + TILE * 7)
]


# Obstacles un dots
obstacles = []
dots = []
for r, row in enumerate(MAP):
    for c, t in enumerate(row):
        x, y = c * TILE, HUD_HEIGHT + r * TILE
        if t == "1":
            obstacles.append(pygame.Rect(x, y, TILE, TILE))
        else:
            dots.append(pygame.Rect(x + TILE // 2 - 5, y + TILE // 2 - 5, 10, 10))

# Player klase
class Player:
    def __init__(self):
        self.rect = pygame.Rect(TILE + TILE // 2, HUD_HEIGHT + TILE * 5 + TILE // 2, TILE - 10, TILE - 10)
        self.speed = 8

    def move(self, keys):
        dx = dy = 0
        if keys[pygame.K_LEFT]: dx = -self.speed
        if keys[pygame.K_RIGHT]: dx = self.speed
        if keys[pygame.K_UP]: dy = -self.speed
        if keys[pygame.K_DOWN]: dy = self.speed

        # X kustība
        self.rect.x += dx
        for ob in obstacles:
            if self.rect.colliderect(ob):
                self.rect.x -= dx
        # Y kustība
        self.rect.y += dy
        for ob in obstacles:
            if self.rect.colliderect(ob):
                self.rect.y -= dy

    def draw(self, win):
        pygame.draw.rect(win, BLUE, self.rect)

# Enemy klase (vienkāršs AI – seko player)
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE - 10, TILE - 10)
        self.speed = 4

    def move(self, player):
        dx = dy = 0
        if player.rect.centerx > self.rect.centerx:
            dx = self.speed
        if player.rect.centerx < self.rect.centerx:
            dx = -self.speed
        if player.rect.centery > self.rect.centery:
            dy = self.speed
        if player.rect.centery < self.rect.centery:
            dy = -self.speed

        # X kustība
        self.rect.x += dx
        for ob in obstacles:
            if self.rect.colliderect(ob):
                self.rect.x -= dx
        # Y kustība
        self.rect.y += dy
        for ob in obstacles:
            if self.rect.colliderect(ob):
                self.rect.y -= dy

    def draw(self, win):
        pygame.draw.rect(win, RED, self.rect)

# Init objekti
player = Player()
enemies = [
    Enemy(TILE * 10, HUD_HEIGHT + TILE * 1),
    Enemy(TILE * 20, HUD_HEIGHT + TILE * 7)
]

score = 0
last_score_time = time.time()
start_time = time.time()
PAUSED = False

# Spēles cikls
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            PAUSED = not PAUSED

    if not PAUSED:
        keys = pygame.key.get_pressed()
        player.move(keys)

        for e in enemies:
            e.move(player)

        # Savāc dotus
        for dot in dots[:]:
            if player.rect.colliderect(dot):
                dots.remove(dot)
                score += 1

        # Score ik pa 10s
        if time.time() - last_score_time >= 10:
            score += 1
            last_score_time = time.time()

        # Sadursmes ar enemy
        for e in enemies:
            if player.rect.colliderect(e.rect):
                score = 0
                player = Player()
                dots = []
                for r, row in enumerate(MAP):
                    for c, t in enumerate(row):
                        if t == "0":
                            dots.append(pygame.Rect(
                                c * TILE + TILE // 2 - 5,
                                HUD_HEIGHT + r * TILE + TILE // 2 - 5,
                                10, 10
                            ))
                break

        # Zīmēšana
        WIN.fill(GRAY)
        pygame.draw.rect(WIN, WHITE, (0, HUD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT))

        for ob in obstacles:
            pygame.draw.rect(WIN, BLACK, ob)
        for dot in dots:
            pygame.draw.ellipse(WIN, YELLOW, dot)

        player.draw(WIN)
        for e in enemies:
            e.draw(WIN)

        # HUD
        elapsed_time = int(time.time() - start_time)
        WIN.blit(font.render(f"Score: {score}", True, BLACK), (10, 10))
        WIN.blit(font.render(f"Time: {elapsed_time}s", True, BLACK), (SCREEN_WIDTH - 150, 10))

    else:
        WIN.blit(font.render("PAUSE - ESC to resume", True, RED), (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))

    pygame.display.update()
    CLOCK.tick(FPS)





