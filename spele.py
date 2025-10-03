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
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)

font = pygame.font.SysFont("Arial", 25)

# Karte: 1 = siena, 0 = ceļš
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
    "1110111111111101111011111",
    "1000100000000000000010001",
    "1011101111111111111011101",
    "1000001000001000000010001",
    "1011111011111111111011101",
    "1000000000000000000000001",
    "1111111111111111111111111"
]

ROWS = len(MAP)
COLS = len(MAP[0])
TILE = min(SCREEN_WIDTH // COLS, (SCREEN_HEIGHT - HUD_HEIGHT) // ROWS)

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


# -------- Helper: atrast drošu spawn --------
def get_random_spawn(size, avoid_rect=None):
    while True:
        r = random.randint(0, ROWS - 1)
        c = random.randint(0, COLS - 1)
        if MAP[r][c] == "0":  # tikai uz ceļa
            rect = pygame.Rect(
                c * TILE + TILE // 2 - size // 2,
                HUD_HEIGHT + r * TILE + TILE // 2 - size // 2,
                size, size
            )
            if avoid_rect and rect.colliderect(avoid_rect):
                continue  # neliek player vietā
            return rect


# -------- Klases --------
class Player:
    def __init__(self):
        self.rect = get_random_spawn(TILE - 10)
        self.speed = 8
        self.color = (0, 0, 255)
        self.last_color_change = time.time()

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

    def update_color(self):
        if time.time() - self.last_color_change > 0.5:  # maina krāsu ik pēc 0.5s
            self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            self.last_color_change = time.time()

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)


class Enemy:
    def __init__(self, speed, color, avoid_rect):
        self.rect = get_random_spawn(TILE - 10, avoid_rect)
        self.speed = speed
        self.color = color

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
        pygame.draw.rect(win, self.color, self.rect)


# -------- Init --------
player = Player()

enemies = [
    Enemy(2, (255, 0, 0), player.rect),      # sarkans
    Enemy(3, (0, 255, 0), player.rect),      # zaļš
    Enemy(4, (255, 165, 0), player.rect),    # oranžs
    Enemy(5, (128, 0, 128), player.rect)     # violets
]

score = 0
last_score_time = time.time()
start_time = time.time()
PAUSED = False


# -------- Spēles cikls --------
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
        player.update_color()

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
                enemies = [
                    Enemy(2, (255, 0, 0), player.rect),
                    Enemy(3, (0, 255, 0), player.rect),
                    Enemy(4, (255, 165, 0), player.rect),
                    Enemy(5, (128, 0, 128), player.rect)
                ]
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
        WIN.blit(font.render("PAUSE - ESC to resume", True, (255, 0, 0)), (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))

    pygame.display.update()
    CLOCK.tick(FPS)
